#!/usr/bin/env bash
# Exit at first failure command
set -e

# Constants
ROOT_DIR=$(readlink -f $(dirname $(dirname $0)))
IMG_INTEG_TESTS=(
    'mysql'
    'alpine'
)
COMMANDS=(
    'sudo service mysql stop'
    'pip install -qr requirements.txt'
    'for img in "${IMG_INTEG_TESTS[@]}"; do docker pull "$img"; done'
    'nosetests -v it_tests tests --with-coverage --cover-erase --cover-package docktors'
    'pycodestyle --config .pycodestyle docktors it_tests tests'
    'flake8 --config .pycodestyle docktors it_tests tests'
    'pylint --rcfile .pylintrc *.py docktors'
    'test $CI == true && codecov || echo "Skipping test coverage"'
)

for cmd in "${COMMANDS[@]}"; do
    echo "Running : ${cmd}"
    eval "${cmd}"
done
