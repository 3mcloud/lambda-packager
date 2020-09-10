"""
Pip installs and zips the lambda into a package.
"""

# Built In
import os
import re
import sys
import shutil
import logging
import subprocess
from subprocess import PIPE
from shutil import which
from typing import Set
from pathlib import Path
from os.path import join, split
from ast import literal_eval
from functools import lru_cache

# 3rd Party
import requirements

# Owned

LOGGER = logging.getLogger(__name__)
FORMAT = "%(levelname)s: %(message)s"
logging.basicConfig(format=FORMAT)
LOGGER.setLevel(logging.INFO)

BYTES_PER_MB = 1048576

@lru_cache(maxsize=32)
def has_ssh(ssh_domain: str) -> bool:
    """
    Check that the user has ssh access to the given ssh domain
    First it will verify if ssh is installed in $PATH
    then check if we can authenticate to ssh_domain
    over ssh. Returns False if either of these are untrue

    Example ssh_domain: git@github.com
    """
    result = None
    if which('ssh') is not None:
        result = subprocess.Popen(['ssh', '-Tq', ssh_domain, '2>', '/dev/null'])
        result.communicate()
    if not result or result.returncode == 255:
        return False
    return True

def flip_ssh(requirment_file_path: str) -> list:
    """
    Attempt to authenticate with ssh to github.com
    If permission is denied then flip the ssh dependencies
    to https dependencies automatically.
    """
    expression = re.compile(r'ssh://git@')
    domain_search = re.compile(r"(?<=ssh://)(.*?)(?=/)")
    LOGGER.info("Scanning requirements and looking for SSH requirements.")
    with open(requirment_file_path) as req_file:
        reqs = []
        for req in requirements.parse(req_file):
            ssh_domain = domain_search.search(req.line)
            if ssh_domain and not has_ssh(ssh_domain.group(1)):
                reqs.append(expression.sub('https://', req.line) + '\n')
                LOGGER.info(
                    "No access to domain %s:\n"
                    "       Swapping:\n"
                    "           - %s\n"
                    "       For:\n"
                    "           - %s\n", ssh_domain.group(1), req.line, reqs[-1])
            else:
                reqs.append(req.line + '\n')
    with open(requirment_file_path, 'w') as req_file:
        req_file.writelines(reqs)
    # Not authenticated via ssh. Change ssh to https dependencies

def copy_to_build_dir(workspace_path: str, build_path: str, code_path: str) -> Set[int]:
    """
    Copy files from the source directory and paste
    them in the destination directory.
    Args:
        workspace_path: The path of the workspace we are working within (absolute).
        build_path: The path of the build directory (Relative to the workspace or absolute).
        code_path: The path to the code directory. (Relative to the build directory or absolute).
    Returns:
        A set of error codes if any occured. If no errors occured it will only return {0}.
    """
    try:
        full_build_path = join(workspace_path, build_path)
        # First remove the build directory if it exists
        if os.path.exists(full_build_path):
            shutil.rmtree(full_build_path)

        # Then copy the files over
        shutil.copytree(
            join(workspace_path, code_path),
            full_build_path,
            ignore=shutil.ignore_patterns('*.zip')
        )
        return {0}
    except Exception as err: # pylint: disable=broad-except
        LOGGER.info("Copying files to build directory failed: %s", err)
    return {1}

def pip_install(workspace_path: str, build_path: str,
                reqs_file_path: str, setup_file_path: str, ssh_flip: bool) -> Set[int]:
    """
    Pip installs to the temporary build directory. Can do either requirements.txt
    or setup.py.

    Args:
        workspace_path: (str)
            The path of the workspace we are working within (absolute).
        build_path: (str)
            The path of the build directory (Relative to the workspace or absolute).
        reqs_file_path: (str)
            The path to the requirements file. Irrelavent if you are using a
            setup.py file. (Relative to the build directory or absolute).
        setup_file_path: (str)
            The path to setup.py file. Irrelavent if you are using a
            requirements.txt. (Relative to the build directory or absolute).
    Returns:
        A set of error codes if any occured. If no errors occured it will only return {0}.
    """
    error_codes = set()
    setup_file_path = join(workspace_path, build_path, setup_file_path)
    reqs_file_path = join(workspace_path, build_path, reqs_file_path)

    try:
        LOGGER.info("Pip installing...")
        if os.path.exists(reqs_file_path):
            if ssh_flip:
                LOGGER.info("FLIP_SSH enabled...")
                flip_ssh(reqs_file_path)
            complete_instance = subprocess.run(
                f"pip3 install -r {reqs_file_path}  -t {join(workspace_path, build_path)}/",
                shell=True,
                check=True,
                stdout=PIPE, stderr=PIPE
            )
            LOGGER.info("\n%s", complete_instance.stdout.decode())
        elif os.path.exists(setup_file_path):
            complete_instance = subprocess.run(
                f"pip3 install -t {join(workspace_path, build_path)}/"
                f" {join(split(setup_file_path)[0], '.')}",
                shell=True,
                check=True,
                stdout=PIPE, stderr=PIPE
            )
            LOGGER.info("\n%s", complete_instance.stdout.decode())
        else:
            LOGGER.info(
                "\n==================================================================\n"
                "Could not find packages to install in either:\n"
                "    Requirements File: %s\n"
                "    Setup File: %s\n"
                "Assuming no requirements needed...\n"
                "==================================================================",
                reqs_file_path, setup_file_path
            )
            error_codes.add(0)
        # Change execution permissions
        complete_instance = subprocess.run(
            f"chmod -R 755 {join(workspace_path, build_path)}",
            shell=True,
            check=True,
        )
        error_codes.add(complete_instance.returncode)


    except subprocess.CalledProcessError as err:
        LOGGER.error("Pip install and permission changing failed: \n%s", err.stderr.decode())
        error_codes.add(err.returncode)

    return error_codes

def zip_directory(workspace_path: str, build_path: str, # pylint: disable=too-many-arguments
                  glob_ignore_str: str, artifact_path: str, lambda_max_size: int,
                  fail_on_too_big: bool) -> Set[int]:
    """
    Zips the lambda and all its packages into a single zip file.

    Args:
        workspace_path: (str)
            The path of the workspace we are working within (absolute).
        build_path: (str)
            The path of the build directory (Relative to the workspace or absolute).
        glob_ignore_str: (str)
            A string with comma delimited glob expressions of things to ignore when zipping
            the package. Example: *.pyc,requirements.txt,__pycache__
        artifact_path: (str)
            The path and file name of the artifact to be saved. Example: /dist/deployment.zip
            (Relative to the workspace directory or absolute).
        lambda_max_size: (int)
            The size (in bytes) that the lambda should be less than or equal to. This is just
            used for messaging.
        fail_on_too_big: (bool)
            If set to True, the this function will add `1` to the returned error codes set if
            the zipped lambda is bigger than `lambda_max_size`.

    Returns:
        A set of error codes. If no errors occured it will only return {0} or {}.
    """
    error_codes = set()
    try:
        clean_build_path = join(workspace_path, build_path + '_clean')
        if os.path.exists(clean_build_path):
            shutil.rmtree(clean_build_path)
        # shutil.make_archive cant ignore files, so first
        # we will use shutil.copytree to move the files into a different directory
        # and ignore the ones we don't care about.
        shutil.copytree(
            join(workspace_path, build_path),
            clean_build_path,
            ignore=shutil.ignore_patterns(*glob_ignore_str.split(','))
        )

        # shutil.make_archive does not want the .zip extension
        zip_name = '.'.join(join(workspace_path, artifact_path).split('.')[:-1])
        shutil.make_archive(
            zip_name,
            "zip",
            clean_build_path
        )

        zip_size = Path(join(workspace_path, artifact_path)).stat().st_size
        LOGGER.info(
            "\n==========================================================================\n"
            "Zip size for %s - %sMB"
            " / %sMB\n"
            "==========================================================================\n",
            split(artifact_path)[1], zip_size / BYTES_PER_MB, lambda_max_size / BYTES_PER_MB
        )
    except Exception as err: # pylint: disable=broad-except
        LOGGER.info("Zipping package failed: %s", err)
        error_codes.add(1)

    if fail_on_too_big and zip_size > lambda_max_size:
        LOGGER.info(
            "\n==========================================================================\n"
            "ERROR - Lambda: %s is to big to fit in a lambda. \n"
            "Please remove some packages.\n"
            "Current size: %sB - Max Size: %sB\n"
            "==========================================================================\n",
            split(artifact_path)[1], zip_size, lambda_max_size)
        error_codes.add(1)

    return error_codes

def create_artifact():
    """
    The script that reads in all the environment variables and creates
    the artifact.
    """
    # =============================================================================
    # Environment variables:
    code_dir = os.getenv('LAMBDA_CODE_DIR', 'src')
    artifact_path = os.getenv('ARTIFACT_NAME', 'deployment.zip')
    build_dir = os.getenv('CONTAINER_BUILD_DIRECTORY', '/build')
    workspace = os.getenv('CI_WORKSPACE', os.getcwd())
    reqs_file = os.getenv('REQUIREMENTS_FILE', 'requirements.txt')
    setup_file = os.getenv('SETUP_FILE', 'setup.py')
    glob_ignore = os.getenv('GLOB_IGNORE', "*.pyc,__pycache__")
    max_lambda_size = int(os.getenv('MAX_LAMBDA_SIZE_BYTES', str(50 * BYTES_PER_MB)))
    fail_on_too_big = literal_eval(os.getenv('FAIL_ON_TOO_BIG', 'False'))
    ssh_flip = literal_eval(os.getenv('SSH_FLIP', 'False'))
    # =============================================================================

    error_codes = copy_to_build_dir(workspace, build_dir, code_dir)
    if not error_codes.issubset({0}):
        sys.exit(max(error_codes))
    error_codes = pip_install(workspace, build_dir, reqs_file, setup_file, ssh_flip)
    if not error_codes.issubset({0}):
        sys.exit(max(error_codes))
    error_codes = zip_directory(
        workspace, build_dir, glob_ignore, artifact_path, max_lambda_size, fail_on_too_big
    )
    if not error_codes.issubset({0}):
        sys.exit(max(error_codes))
    sys.exit(0)

if __name__ == '__main__':
    create_artifact()
