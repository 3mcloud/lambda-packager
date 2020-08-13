"""
Pytest fixtures.
"""
# pylint: disable=all
# Built In
import os
from pathlib import Path
from os.path import join, split
import contextlib

# 3rd Party
from pytest import fixture

# Owned

@contextlib.contextmanager
def modified_environ(*remove, **update):
    """
    https://stackoverflow.com/a/34333710/8150685
    Temporarily updates the ``os.environ`` dictionary in-place.

    The ``os.environ`` dictionary is updated in-place so that the modification
    is sure to work in all situations.

    :param remove: Environment variables to remove.
    :param update: Dictionary of environment variables and values to add/update.
    """
    env = os.environ
    update = update or {}
    remove = remove or []

    # List of environment variables being updated or removed.
    stomped = (set(update.keys()) | set(remove)) & set(env.keys())
    # Environment variables and values to restore on exit.
    update_after = {k: env[k] for k in stomped}
    # Environment variables and values to remove on exit.
    remove_after = frozenset(k for k in update if k not in env)

    try:
        env.update(update)
        [env.pop(k, None) for k in remove]
        yield
    finally:
        env.update(update_after)
        [env.pop(k) for k in remove_after]

@fixture(scope='module')
def context_modified_environ():
    return modified_environ

@fixture(scope='module')
def lambda_paths():
    directores_to_ignore = {'__pycache__'}
    cur_path = Path(__file__).parent.absolute()
    lambdas_path = join(cur_path, 'tests', 'valid_example_lambdas')
    _, directories, __ = next(os.walk(lambdas_path))
    return {x: join(lambdas_path, x) for x in directories if x not in directores_to_ignore}

@fixture(scope='module')
def erroring_lambda_paths():
    directores_to_ignore = {'__pycache__'}
    cur_path = Path(__file__).parent.absolute()
    lambdas_path = join(cur_path, 'tests', 'erroring_example_lambdas')
    _, directories, __ = next(os.walk(lambdas_path))
    return {x: join(lambdas_path, x) for x in directories if x not in directores_to_ignore}



@fixture(scope='module')
def environments(lambda_paths):
    envs = dict()
    for key, val in lambda_paths.items():
        parameters = dict()
        with open(join(val, '.env')) as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split('=')
                    parameters[parts[0]] = '='.join(parts[1:])
        envs[key] = parameters
    return envs

@fixture(scope='module')
def erroring_environments(erroring_lambda_paths):
    envs = dict()
    for key, val in erroring_lambda_paths.items():
        parameters = dict()
        with open(join(val, '.env')) as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split('=')
                    parameters[parts[0]] = '='.join(parts[1:])
        envs[key] = parameters
    return envs

