"""
Pip installs and zips the lambda into a package.
"""

# Built In
import os
import sys
import subprocess
from typing import List
from pathlib import Path
from os.path import join, split
from ast import literal_eval
import shutil

# 3rd Party

# Owned

# ============================================================================
# Environment variables:
CODE_DIR = os.getenv('LAMBDA_CODE_DIR', 'src')
ARTIFACT_PATH = os.getenv('ARTIFACT_NAME', 'deployment.zip')
BUILD_DIR = os.getenv('CONTAINER_BUILD_DIRECTORY', '/build')
WORKSPACE = os.getenv('CI_WORKSPACE', os.getcwd())
REQUIREMENTS_FILE = os.getenv('REQUIREMENTS_FILE', 'requirements.txt')
SETUP_FILE = os.getenv('SETUP_FILE', 'setup.py')
GLOB_IGNORE = os.getenv('GLOB_IGNORE', "*.pyc,requirements.txt,__pycache__")
MAX_LAMBDA_SIZE_BYTES = int(os.getenv('MAX_LAMBDA_SIZE_BYTES', '50000000'))
FAIL_ON_TOO_BIG = literal_eval(os.getenv('FAIL_ON_TOO_BIG', 'False'))
# ============================================================================


def zipdir(path, ziph):
    """
    Zips the lambda and all its packages into a single zip file.
    """
    clean_build_path = join(WORKSPACE, BUILD_DIR + '_clean')
    if os.path.exists(clean_build_path):
        shutil.rmtree(clean_build_path)
    # shutil.make_archive cant ignore files, so first
    # we will use shutil.copytree to move the files into a different directory
    # and ignore the ones we don't care about.
    shutil.copytree(
        join(WORKSPACE, BUILD_DIR),
        clean_build_path,
        ignore=shutil.ignore_patterns(*GLOB_IGNORE.split(','))
    )

    # shutil.make_archive does not want the .zip extension
    zip_name = '.'.join(join(WORKSPACE, ARTIFACT_PATH).split('.')[:-1])
    shutil.make_archive(
        zip_name,
        "zip",
        clean_build_path
    )

    zip_size = Path(join(WORKSPACE, ARTIFACT_PATH)).stat().st_size
    print(
        "==========================================================================\n"
        f"Zip size for {split(ARTIFACT_PATH)[1]} - {zip_size / 1000000}MB\n"
        "==========================================================================\n",
        flush=True,
    )
    if FAIL_ON_TOO_BIG and zip_size > MAX_LAMBDA_SIZE_BYTES:
        print(
            "==========================================================================\n"
            f"ERROR - Lambda: {split(ARTIFACT_PATH)[1]} is to big to fit in a lambda. \n"
            "Please remove some packages.\n"
            f"Current size: {zip_size}B - Max Size: {MAX_LAMBDA_SIZE_BYTES}B\n"
            "==========================================================================\n",
            flush=True)
        sys.exit(1)

def pip_install():
    """
    Pip install to the temporary build directory.
    """
    error_codes = set()
    setup_file_path = join(WORKSPACE, BUILD_DIR, SETUP_FILE)
    reqs_file_path = join(WORKSPACE, BUILD_DIR, REQUIREMENTS_FILE)
    print(WORKSPACE, BUILD_DIR, REQUIREMENTS_FILE, flush=True)
    try:
        print(f"Pip installing...", flush=True)
        if os.path.exists(reqs_file_path):
            complete_instance = subprocess.run(
                f"pip3 install -r {reqs_file_path} "
                f"-t {join(WORKSPACE, BUILD_DIR)}/",
                shell=True,
                check=True
            )
            error_codes.add(complete_instance.returncode)
        elif os.path.exists(setup_file_path):
            complete_instance = subprocess.run(
                f"pip3 install -t {join(WORKSPACE, BUILD_DIR)}/"
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
            f"chmod -R 755 {join(WORKSPACE, BUILD_DIR)}",
            shell=True,
            check=True
        )
        error_codes.add(complete_instance.returncode)


    except subprocess.CalledProcessError as err:
        print(f"Pip install and permission changing failed: {err}")
        error_codes.add(err.returncode)

    return error_codes

def copy_to_build_dir():
    """
    Copy files from the source directory and paste
    them in the destination directory.
    """
    build_path = join(WORKSPACE, BUILD_DIR)
    if os.path.exists(build_path):
        shutil.rmtree(build_path)
    shutil.copytree(join(WORKSPACE, CODE_DIR), build_path) 


if __name__ == '__main__':
    copy_to_build_dir()
    error_codes = pip_install()
    if not error_codes.issubset({0}):
        sys.exit(1)
    zipdir(join(WORKSPACE, BUILD_DIR), '')
