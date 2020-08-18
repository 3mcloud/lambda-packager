"""
Pip installs and zips the lambda into a package.
"""

# Built In
import os
import sys
import subprocess
from typing import Set
from pathlib import Path
from os.path import join, split
from ast import literal_eval
import shutil

# 3rd Party

# Owned

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
        print(f"Copying files to build directory failed: {err}")
    return {1}

def pip_install(workspace_path: str, build_path: str,
                reqs_file_path: str, setup_file_path: str) -> Set[int]:
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
        print("Pip installing...", flush=True)
        if os.path.exists(reqs_file_path):
            complete_instance = subprocess.run(
                f"pip3 install -r {reqs_file_path}  -t {join(workspace_path, build_path)}/",
                shell=True,
                check=True
            )
            error_codes.add(complete_instance.returncode)
        elif os.path.exists(setup_file_path):
            complete_instance = subprocess.run(
                f"pip3 install -t {join(workspace_path, build_path)}/"
                f" {join(split(setup_file_path)[0], '.')}",
                shell=True,
                check=True
            )
            error_codes.add(complete_instance.returncode)
        else:
            print(
                "==================================================================\n"
                "Could not find packages to install in either:\n"
                f"    Requirements File: {reqs_file_path}\n"
                f"    Setup File: {setup_file_path}\n"
                "==================================================================",
                flush=True
            )
            error_codes.add(1)
        # Change execution permissions
        complete_instance = subprocess.run(
            f"chmod -R 755 {join(workspace_path, build_path)}",
            shell=True,
            check=True
        )
        error_codes.add(complete_instance.returncode)


    except subprocess.CalledProcessError as err:
        print(f"Pip install and permission changing failed: {err}")
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
        print(
            "==========================================================================\n"
            f"Zip size for {split(artifact_path)[1]} - {zip_size / 1000000}MB"
            f" / {lambda_max_size / 1000000}MB\n"
            "==========================================================================\n",
            flush=True,
        )
    except Exception as err: # pylint: disable=broad-except
        print(f"Zipping package failed: {err}")
        error_codes.add(1)

    if fail_on_too_big and zip_size > lambda_max_size:
        print(
            "==========================================================================\n"
            f"ERROR - Lambda: {split(artifact_path)[1]} is to big to fit in a lambda. \n"
            "Please remove some packages.\n"
            f"Current size: {zip_size}B - Max Size: {lambda_max_size}B\n"
            "==========================================================================\n",
            flush=True)
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
    max_lambda_size = int(os.getenv('MAX_LAMBDA_SIZE_BYTES', '50000000'))
    fail_on_too_big = literal_eval(os.getenv('FAIL_ON_TOO_BIG', 'False'))
    # =============================================================================

    error_codes = copy_to_build_dir(workspace, build_dir, code_dir)
    if not error_codes.issubset({0}):
        sys.exit(1)
    error_codes = pip_install(workspace, build_dir, reqs_file, setup_file)
    if not error_codes.issubset({0}):
        sys.exit(1)
    error_codes = zip_directory(
        workspace, build_dir, glob_ignore, artifact_path, max_lambda_size, fail_on_too_big
    )
    if not error_codes.issubset({0}):
        sys.exit(1)
    sys.exit(0)

if __name__ == '__main__':
    create_artifact()
