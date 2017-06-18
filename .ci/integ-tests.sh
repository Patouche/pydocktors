#!/usr/bin/env bash
# Exit at first failure command
set -e

# Constants
ROOT_DIR=$(readlink -f $(dirname $(dirname $0)))
TARGET_BRANCH=master
IMG_INTEG_TESTS=(
    'mysql'
    'alpine'
)

sudo service mysql stop
pip install -qr requirements.txt
for img in "${IMG_INTEG_TESTS[@]}"; do docker pull "$img"; done
nosetests -v it.tests tests --with-coverage --cover-erase --cover-package docktors
pycodestyle --config .pycodestyle docktors it.tests tests
flake8 --config .pycodestyle docktors it.tests tests
pylint --rcfile .pylintrc *.py docktors
codecov