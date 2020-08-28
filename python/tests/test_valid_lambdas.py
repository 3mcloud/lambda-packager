# pylint: disable=all

# Built Ins
import os
import zipfile
import glob

# 3rd Party
import pytest

# Owned
import entrypoint

def test_code_directory(lambda_paths, environments, context_modified_environ, monkeypatch, glob_ignore_worked):
    lambda_path = lambda_paths['code_directory_example']
    lambda_env = environments['code_directory_example']
    with context_modified_environ(**lambda_env):
        monkeypatch.setattr(os, "getcwd", lambda: lambda_path)
        # Lets create the zip
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            entrypoint.create_artifact()
        assert False
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 0

        # Now to do some testing on the zipfile itself.
        zip_file_name = os.getenv('ARTIFACT_NAME', 'deployment.zip')
        workspace = os.getenv('CI_WORKSPACE', os.getcwd())
        code_dir = os.getenv('LAMBDA_CODE_DIR', 'src')
        glob_ignore = os.getenv('GLOB_IGNORE', "*.pyc,__pycache__")
        build_dir = os.getenv('CONTAINER_BUILD_DIRECTORY', '/build')

        with zipfile.ZipFile(os.path.join(workspace, zip_file_name)) as f:
            root_level_files = {e.split('/')[0] for e in f.namelist()}

        assert glob_ignore_worked(workspace, build_dir, glob_ignore)

        # Making sure all root level files and directories are inside the zip file.
        _, directories, files = next(os.walk(os.path.join(lambda_path, 'code')))
        for f in files:
            root_level_files.remove(f)
        for d in directories:
            root_level_files.remove(d)
        assert len(root_level_files) > 3 # Are there more files then the stuff we explicitly listed?

        _, dirs, __ = next(os.walk(lambda_path))
        assert 'zip_files' in dirs
        _, __, zip_files = next(os.walk(os.path.join(lambda_path, 'zip_files')))
        assert 'code.zip' in zip_files

def test_no_requirements(lambda_paths, environments, context_modified_environ, monkeypatch, glob_ignore_worked):
    lambda_path = lambda_paths['no_requirements']
    lambda_env = environments['no_requirements']
    with context_modified_environ(**lambda_env):
        monkeypatch.setattr(os, "getcwd", lambda: lambda_path)
        # Lets create the zip
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            entrypoint.create_artifact()
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 0

        # Now to do some testing on the zipfile itself.
        zip_file_name = os.getenv('ARTIFACT_NAME', 'deployment.zip')
        workspace = os.getenv('CI_WORKSPACE', os.getcwd())
        code_dir = os.getenv('LAMBDA_CODE_DIR', 'src')
        glob_ignore = os.getenv('GLOB_IGNORE', "*.pyc,__pycache__")
        build_dir = os.getenv('CONTAINER_BUILD_DIRECTORY', '/build')

        with zipfile.ZipFile(os.path.join(workspace, zip_file_name)) as f:
            root_level_files = {e.split('/')[0] for e in f.namelist()}

        assert glob_ignore_worked(workspace, build_dir, glob_ignore)

        # Making sure all root level files and directories are inside the zip file.
        _, directories, files = next(os.walk(lambda_path))
        files = set(files)
        directories = set(directories)
        assert 'deployment.zip' in files
        files.remove('deployment.zip')
        root_level_files = root_level_files - files
        root_level_files = root_level_files - directories
        assert not root_level_files

def test_simple_with_reqs_txt(lambda_paths, environments, context_modified_environ, monkeypatch, glob_ignore_worked):
    lambda_path = lambda_paths['simple_requirements']
    lambda_env = environments['simple_requirements']
    with context_modified_environ(**lambda_env):
        monkeypatch.setattr(os, "getcwd", lambda: lambda_path)
        # Lets create the zip
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            entrypoint.create_artifact()
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 0

        # Now to do some testing on the zipfile itself.
        zip_file_name = os.getenv('ARTIFACT_NAME', 'deployment.zip')
        workspace = os.getenv('CI_WORKSPACE', os.getcwd())
        code_dir = os.getenv('LAMBDA_CODE_DIR', 'src')
        glob_ignore = os.getenv('GLOB_IGNORE', "*.pyc,__pycache__")
        build_dir = os.getenv('CONTAINER_BUILD_DIRECTORY', '/build')

        with zipfile.ZipFile(os.path.join(workspace, zip_file_name)) as f:
            root_level_files = {e.split('/')[0] for e in f.namelist()}

        assert glob_ignore_worked(workspace, build_dir, glob_ignore)

        # Making sure all root level files and directories are inside the zip file.
        _, directories, files = next(os.walk(lambda_path))
        files = set(files)
        assert 'deployment.zip' in files
        files.remove('deployment.zip')
        for f in files:
            root_level_files.remove(f)
        for d in directories:
            root_level_files.remove(d)
        assert len(root_level_files) > 3 # Are there more files then the stuff we explicitly listed?

def test_simple_with_reqs_txt_flip_ssh(lambda_paths, environments, context_modified_environ,
                                       monkeypatch, glob_ignore_worked, caplog):
    lambda_path = lambda_paths['simple_requirements_ssh_flip']
    lambda_env = environments['simple_requirements_ssh_flip']
    with context_modified_environ(**lambda_env):
        monkeypatch.setattr(os, "getcwd", lambda: lambda_path)
        # Lets create the zip
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            entrypoint.create_artifact()
        assert pytest_wrapped_e.type == SystemExit
        # The zip will fail because the ssh/https url won't actually work.
        assert 'exit status 128: git clone -q https' in caplog.text
        assert pytest_wrapped_e.value.code == 1
        assert False

def test_simple_with_reqs_txt_flip_ssh_no_ssh(lambda_paths, environments, context_modified_environ,
                                              monkeypatch, glob_ignore_worked):
    lambda_path = lambda_paths['simple_requirements_no_ssh']
    lambda_env = environments['simple_requirements_no_ssh']
    with context_modified_environ(**lambda_env):
        monkeypatch.setattr(os, "getcwd", lambda: lambda_path)
        # Lets create the zip
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            entrypoint.create_artifact()
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 0

        # Now to do some testing on the zipfile itself.
        zip_file_name = os.getenv('ARTIFACT_NAME', 'deployment.zip')
        workspace = os.getenv('CI_WORKSPACE', os.getcwd())
        code_dir = os.getenv('LAMBDA_CODE_DIR', 'src')
        glob_ignore = os.getenv('GLOB_IGNORE', "*.pyc,__pycache__")
        build_dir = os.getenv('CONTAINER_BUILD_DIRECTORY', '/build')

        with zipfile.ZipFile(os.path.join(workspace, zip_file_name)) as f:
            root_level_files = {e.split('/')[0] for e in f.namelist()}

        assert glob_ignore_worked(workspace, build_dir, glob_ignore)

        # Making sure all root level files and directories are inside the zip file.
        _, directories, files = next(os.walk(lambda_path))
        files = set(files)
        assert 'deployment.zip' in files
        files.remove('deployment.zip')
        for f in files:
            root_level_files.remove(f)
        for d in directories:
            root_level_files.remove(d)
        assert len(root_level_files) > 3 # Are there more files then the stuff we explicitly listed?

def test_simple_setup(lambda_paths, environments, context_modified_environ,
                                              monkeypatch, glob_ignore_worked):
    lambda_path = lambda_paths['simple_setup_project']
    lambda_env = environments['simple_setup_project']
    with context_modified_environ(**lambda_env):
        monkeypatch.setattr(os, "getcwd", lambda: lambda_path)
        # Lets create the zip
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            entrypoint.create_artifact()
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 0

        # Now to do some testing on the zipfile itself.
        zip_file_name = os.getenv('ARTIFACT_NAME', 'deployment.zip')
        workspace = os.getenv('CI_WORKSPACE', os.getcwd())
        code_dir = os.getenv('LAMBDA_CODE_DIR', 'src')
        glob_ignore = os.getenv('GLOB_IGNORE', "*.pyc,__pycache__")
        build_dir = os.getenv('CONTAINER_BUILD_DIRECTORY', '/build')

        with zipfile.ZipFile(os.path.join(workspace, zip_file_name)) as f:
            root_level_files = {e.split('/')[0] for e in f.namelist()}

        assert glob_ignore_worked(workspace, build_dir, glob_ignore)

        # Making sure all root level files and directories are inside the zip file.
        _, directories, files = next(os.walk(lambda_path))
        files = set(files)
        assert 'deployment.zip' in files
        files.remove('deployment.zip')
        for f in files:
            root_level_files.remove(f)
        for d in directories:
            root_level_files.remove(d)
        assert len(root_level_files) > 3 # Are there more files then the stuff we explicitly listed?
