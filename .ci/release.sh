#!/usr/bin/env bash
# Exit at first failure command
set -e

# Constants
ROOT_DIR=$(readlink -f $(dirname $(dirname $0)))
TARGET_BRANCH=master
ENCRYPTION_UUID='fcfd164fbc57'

function get_version() {
   cat "${ROOT_DIR}/VERSION"
}

function git_configure() {
    http_github_repo=$(git config remote.origin.url)
    ssh_github_repo=${http_github_repo/https:\/\/github.com\//git@github.com:}
    git config user.name "Travis CI"
    git config user.email "travis@travis-ci.org"
    git remote set-url origin "${ssh_github_repo}"
}

function ssh_agent() {
    key_var="encrypted_${ENCRYPTION_UUID}_key"
    iv_var="encrypted_${ENCRYPTION_UUID}_iv"
    openssl aes-256-cbc \
        -K ${!key_var} -iv ${!iv_var} \
        -in ${ROOT_DIR}/.ci/travis-deploy-key.enc -out ${ROOT_DIR}/.ci/travis-deploy-key \
        -d
    chmod 600 ${ROOT_DIR}/.ci/travis-deploy-key
    eval $(ssh-agent -s)
    ssh-add .ci/travis-deploy-key
    ssh-add -l
}

VERSION=$(get_version)
test $CI == true && ssh_agent || echo 'Skip ssh agent configuration'
test $CI == true && git_configure || echo 'Skip git configuration'
git clean -df
git checkout master
git tag -a "v${VERSION}" -m "Version ${VERSION}"
git push --tags