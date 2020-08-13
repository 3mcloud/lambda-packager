# pylint: disable=all

# Built Ins
import os
import zipfile

# 3rd Party
import pytest

# Owned
import entrypoint
# Test zip to big or zip propper size
# Test zip contains nested files
# Test zip remains executable
# Test reqs file
# Test setup.py file
# Test neither file
# Test relative and absolute paths
# Test invalid path


# @pytest.mark.parametrize("test_input,expected", [("3+5", 8), ("2+4", 6), ("6*9", 42)])
# def foo(test_input, expected)
def test_foo(lambda_paths, environments, context_modified_environ, monkeypatch):
    for name, path in lambda_paths.items():
        with context_modified_environ(**environments[name]):
            monkeypatch.setattr(os, "getcwd", lambda: path)
            with pytest.raises(SystemExit) as pytest_wrapped_e:
                    entrypoint.create_artifact()
            assert pytest_wrapped_e.type == SystemExit
            assert pytest_wrapped_e.value.code == 0

            zip_file_name = os.getenv('ARTIFACT_NAME', 'deployment.zip')
            workspace = os.getenv('CI_WORKSPACE', os.getcwd())
            code_dir = os.getenv('LAMBDA_CODE_DIR', 'src')

            with zipfile.ZipFile(os.path.join(workspace, zip_file_name)) as f:
                root_level_files = {e.split('/')[0] for e in f.namelist()}
                # sorted_file_names = list(sorted(root_level_files))
                # print("Root level zipped: ", sorted_file_names)
            assert len(root_level_files) > 10 # Make sure the root level has more then 10 files
            
            _, directories, files = next(os.walk(os.path.join(workspace, code_dir)))
            for directory in directories:
                assert directory in root_level_files
            for f in files:
                if f.endswith('.zip'):
                    continue
                assert f in root_level_files
                
                # print(os.getcwd())
            
    assert False
