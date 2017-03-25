from __future__ import print_function
import pytest
import sys
import subprocess

PYTEST_ARGS = ['tests']
FLAKE8_ARGS = ['ormini', '--ignore=E501,F403,E122,E731,W292']


def exit_on_failure(ret):
    if ret:
        sys.exit(ret)


def flake8_main(args):
    print('Running flake8 code linting')
    ret = subprocess.call(['flake8'] + args)
    print('flake8 failed' if ret else 'flake8 passed')
    return ret


if __name__ == "__main__":
    exit_on_failure(pytest.main(PYTEST_ARGS))
    # exit_on_failure(flake8_main(FLAKE8_ARGS))