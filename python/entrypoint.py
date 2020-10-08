"""
Pip installs and zips the lambda into a package.
"""

# Built In
import os
import re
import sys
import shutil
import logging
import uuid
import subprocess
import json
from subprocess import PIPE
from shutil import which
from typing import Set
from pathlib import Path
from os.path import join, split
from ast import literal_eval
from functools import lru_cache
from multiprocessing import Process

# 3rd Party
import requirements
import yaml

# Owned

LOGGER = logging.getLogger(__name__)
FORMAT = "%(levelname)s: %(message)s"
logging.basicConfig(format=FORMAT)
LOGGER.setLevel(logging.INFO)

BYTES_PER_MB = 1048576

def extract_container_variables(container_vars: dict) -> dict:
    """
    Given a dictionary which contains the container variables, this function will
    either pull them out or assign defaults and return them as a dictionary.
    """
    # ==============================================================================================
    # DEFAULTS FOR ENVIRONMENT VARIABLES
    defaults = { # Change defaults here
        'DEFAULT_CODE_DIR': 'src',
        'DEFAULT_ARTIFACT_PATH': 'deployment.zip',
        'DEFAULT_BUILD_DIR': '/build',
        'DEFAULT_WORKSPACE': os.getcwd() ,
        'DEFAULT_REQS_FILE': 'requirements.txt',
        'DEFAULT_SETUP_FILE': 'setup.py',
        'DEFAULT_GLOB_IGNORE': "*.pyc,__pycache__",
        'DEFAULT_MAX_LAMBDA_SIZE': str(50 * BYTES_PER_MB),
        'DEFAULT_FAIL_ON_TOO_BIG': 'False',
        'DEFAULT_SSH_FLIP': 'False',
    }
    # ==============================================================================================

    container_variables = {
        "code_path": container_vars.get('LAMBDA_CODE_DIR', defaults['DEFAULT_CODE_DIR']),
        "artifact_path": container_vars.get('ARTIFACT_NAME', defaults['DEFAULT_ARTIFACT_PATH']),
        "build_path": container_vars.get('CONTAINER_BUILD_DIRECTORY',
                                         defaults['DEFAULT_BUILD_DIR']),
        "workspace_path": container_vars.get('CI_WORKSPACE', defaults['DEFAULT_WORKSPACE']),
        "reqs_file_path": container_vars.get('REQUIREMENTS_FILE', defaults['DEFAULT_REQS_FILE']),
        "setup_file_path": container_vars.get('SETUP_FILE', defaults['DEFAULT_SETUP_FILE']),
        "glob_ignore_str": container_vars.get('GLOB_IGNORE', defaults['DEFAULT_GLOB_IGNORE']),
        "max_lambda_size": int(
            container_vars.get('MAX_LAMBDA_SIZE_BYTES', defaults['DEFAULT_MAX_LAMBDA_SIZE'])
        ),
        "fail_on_too_big": literal_eval(str(
            container_vars.get('FAIL_ON_TOO_BIG', defaults['DEFAULT_FAIL_ON_TOO_BIG'])
        )),
        "ssh_flip": literal_eval(str(container_vars.get('SSH_FLIP', defaults['DEFAULT_SSH_FLIP']))),
    }

    return container_variables

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

def copy_to_build_dir(variables: dict) -> (Set[int], str):
    """
    Copy files from the source directory and paste
    them in the destination directory.
    Args:
        `variables` dict keys used:
            workspace_path: The path of the workspace we are working within (absolute).
            build_path: The path of the build directory (Relative to the workspace or absolute).
            code_path: The path to the code directory.
                (Relative to the build directory or absolute).
    Returns:
        Tuple:
            [0]: A set of error codes if any occured. If no errors occured it will only return {0}.
            [1]: The UUID assigned to the build as a string.
    """
    try:
        build_id = uuid.uuid4().hex
        LOGGER.info("UUID (%s) assigned to packager build for code %s",
                    build_id, variables['code_path'])
        full_build_path = join(variables['workspace_path'], variables['build_path'], build_id)
        # First remove the build directory if it exists
        if os.path.exists(full_build_path):
            shutil.rmtree(full_build_path)

        # Then copy the files over to the build directory.
        shutil.copytree(
            join(variables['workspace_path'], variables['code_path']),
            full_build_path,
            ignore=shutil.ignore_patterns('*.zip')
        )
        return {0}, build_id
    except Exception: # pylint: disable=broad-except
        LOGGER.exception("Copying files to build directory failed:")
    return {1}, build_id

def pip_install(variables: dict, build_id: str) -> Set[int]:
    """
    Pip installs to the temporary build directory. Can do either requirements.txt
    or setup.py.
    Args:
        `variables` dict keys used:
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
        build_id: (str)
            The UUID assigned to the build, needed to find the appropriate build directory.

    Returns:
        A set of error codes if any occured. If no errors occured it will only return {0}.
    """
    error_codes = set()
    setup_file_path = join(
        variables['workspace_path'],
        variables['build_path'],
        build_id,
        variables['setup_file_path']
    )
    reqs_file_path = join(
        variables['workspace_path'],
        variables['build_path'],
        build_id,
        variables['reqs_file_path']
    )
    target_path = join(
        variables['workspace_path'],
        variables['build_path'],
        build_id
    )

    try:
        LOGGER.info("Pip installing for %s...", build_id)
        if os.path.exists(reqs_file_path):
            if variables['ssh_flip']:
                LOGGER.info("FLIP_SSH enabled...")
                flip_ssh(reqs_file_path)
            complete_instance = subprocess.run(
                f"pip3 install -r {reqs_file_path} -t {target_path}/",
                shell=True,
                check=True,
                stdout=PIPE, stderr=PIPE
            )
            LOGGER.info("\n%s", complete_instance.stdout.decode())
        elif os.path.exists(setup_file_path):
            complete_instance = subprocess.run(
                f"pip3 install -t {target_path}/"
                f" {join(split(setup_file_path)[0], '.')}",
                shell=True,
                check=True,
                stdout=PIPE, stderr=PIPE
            )
            LOGGER.info("Pip installed %s, \n%s", build_id, complete_instance.stdout.decode())
        else:
            LOGGER.info(
                "\n==================================================================\n"
                "Could not find packages to install in either:\n"
                "    Requirements File: %s\n"
                "    Setup File: %s\n"
                "for build id: %s\n"
                "Assuming no requirements needed...\n"
                "==================================================================",
                reqs_file_path, setup_file_path, build_id
            )
            error_codes.add(0)
        # Change execution permissions
        complete_instance = subprocess.run(
            f"chmod -R 755 {target_path}",
            shell=True,
            check=True,
        )
        error_codes.add(complete_instance.returncode)


    except subprocess.CalledProcessError as err:
        LOGGER.error("Pip install and permission changing failed: \n%s", err.stderr.decode())
        error_codes.add(err.returncode)

    return error_codes

def zip_directory(variables: dict, build_id: str) -> Set[int]:
    """
    Zips the lambda and all its packages into a single zip file.

    Args:
        `variables` dict keys used:
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
            max_lambda_size: (int)
                The size (in bytes) that the lambda should be less than or equal to. This is just
                used for messaging.
            fail_on_too_big: (bool)
                If set to True, the this function will add `1` to the returned error codes set if
                the zipped lambda is bigger than `max_lambda_size`.
        build_id: (str)
            The UUID assigned to the build, needed to find the appropriate build directory.

    Returns:
        A set of error codes. If no errors occured it will only return {0} or {}.
    """
    error_codes = set()
    try:
        clean_build_path = join(
            variables['workspace_path'],
            variables['build_path'],
            build_id + '_clean'
        )
        if os.path.exists(clean_build_path):
            shutil.rmtree(clean_build_path)
        # shutil.make_archive cant ignore files, so first
        # we will use shutil.copytree to move the files into a different directory
        # and ignore the ones we don't care about.
        shutil.copytree(
            join(variables['workspace_path'], variables['build_path'], build_id),
            clean_build_path,
            ignore=shutil.ignore_patterns(*variables['glob_ignore_str'].split(','))
        )

        # shutil.make_archive does not want the .zip extension
        zip_name = '.'.join(
            join(variables['workspace_path'], variables['artifact_path']
        ).split('.')[:-1])
        shutil.make_archive(
            zip_name,
            "zip",
            clean_build_path
        )

        zip_size = Path(
            join(variables['workspace_path'], variables['artifact_path'])
        ).stat().st_size
        LOGGER.info(
            "\n==========================================================================\n"
            "Zip size for %s - %sMB"
            " / %sMB\n"
            "==========================================================================\n",
            split(variables['artifact_path'])[1],
            zip_size / BYTES_PER_MB,
            variables['max_lambda_size'] / BYTES_PER_MB
        )
    except Exception: # pylint: disable=broad-except
        LOGGER.exception("Zipping package failed:")
        error_codes.add(1)

    if variables['fail_on_too_big'] and zip_size > variables['max_lambda_size']:
        LOGGER.info(
            "\n==========================================================================\n"
            "ERROR - Lambda: %s is to big to fit in a lambda. \n"
            "Please remove some packages.\n"
            "Current size: %sB - Max Size: %sB\n"
            "==========================================================================\n",
            split(variables['artifact_path'])[1], zip_size, variables['max_lambda_size'])
        error_codes.add(1)

    return error_codes

def create_artifact(variables, return_codes: Set[int]) -> None:
    """
    A function to be called as a processor. Handles creating an artifact and returning
    on errors. Return codes will be added to the passed in `return_codes` Set.
    """

    error_codes, build_id = copy_to_build_dir(variables)
    return_codes.update(error_codes)
    if not error_codes.issubset({0}):
        return

    error_codes = pip_install(variables, build_id)
    return_codes.update(error_codes)
    if not error_codes.issubset({0}):
        return

    error_codes = zip_directory(variables, build_id)
    return_codes.update(error_codes)
    return

def create_single_artifact():
    """
    Create a single artifact based on environment variables.
    """
    return_codes = set()
    variables = extract_container_variables(os.environ)
    create_artifact(variables, return_codes)
    if return_codes:
        sys.exit(max(return_codes))
    sys.exit(0)


def create_multiple_artifacts(manifest_file_path: str):
    """
    Create multiple files based on manifest file.
    """
    LOGGER.info("Manifest file specified. Attempting to package multiple artifacts.")
    workspace = os.getenv('CI_WORKSPACE', os.getcwd())

    full_manifest_path = os.path.join(workspace, manifest_file_path)
    try:
        with open(full_manifest_path) as file_pointer:
            if full_manifest_path.endswith('json'):
                manifest_object = json.load(file_pointer)
            else:
                manifest_object = yaml.safe_load(file_pointer)
    except Exception as err: # pylint: disable=broad-except
        LOGGER.error("Opening or parsing manifest file failed:\n%s", err)
        sys.exit(1)

    try:
        processes = list()
        for lambda_spec in manifest_object['Lambdas']:
            variables = extract_container_variables(lambda_spec)
            return_codes = set()
            process_pointer = Process(
                target=create_artifact,
                args=(variables, return_codes)
                )
            process_pointer.start()
            processes.append((process_pointer, return_codes))
        for proc, _ in processes:
            proc.join()
    except KeyError as err:
        LOGGER.error("Malformed Manifest File, could not find required key. Error: %s", err)

    all_codes = set()
    for _, return_codes in processes:
        all_codes.update(return_codes)
    if all_codes:
        sys.exit(max(all_codes))
    sys.exit(0)

if __name__ == '__main__':
    MANIFEST_FILE_PATH = os.getenv("MANIFEST_FILE", "")
    if MANIFEST_FILE_PATH:
        create_multiple_artifacts(MANIFEST_FILE_PATH)
    else:
        create_single_artifact()
