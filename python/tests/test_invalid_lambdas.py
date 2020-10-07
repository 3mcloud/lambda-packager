# pylint: disable=all

# Built Ins
import os
import zipfile
import glob

# 3rd Party
import pytest

# Owned
import entrypoint

def test_too_big(erroring_lambda_paths, erroring_environments,
                 context_modified_environ, monkeypatch, caplog):
    lambda_path = erroring_lambda_paths['too_big']
    lambda_env = erroring_environments['too_big']
    with context_modified_environ(**lambda_env):
        monkeypatch.setattr(os, "getcwd", lambda: lambda_path)
        # Lets create the zip
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            entrypoint.create_single_artifact()
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1
        assert "deployment.zip is to big to fit in a lambda." in caplog.text
