#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages


def get_version():
    version_content = open('VERSION').readline().strip()
    if not version_content:
        raise RuntimeError('Cannot find version if file version_content.')
    ci_branch = os.getenv('TRAVIS_BRANCH', None)
    ci_build = os.getenv('TRAVIS_BUILD_NUMBER', None)
    if ci_build and ci_branch != 'master':
        version_content = ''.join([version_content, '.', 'dev', ci_build])
    return version_content


user = 'Patouche'
repository = 'pydocktors'
version = get_version()

setup(
    name=repository,
    version=version,
    packages=find_packages(exclude=['it.tests', 'tests', 'examples']),
    description='Simple docker decorator',
    long_description=open('README.rst').read(),
    author='Patrick Allain',
    author_email='patralla@gmail.com',
    install_requires=[
        'docker>=2.0.0'
    ],
    url='https://github.com/{user}/{repository}'.format(
        user=user,
        repository=repository,
    ),
    download_url='https://github.com/{user}/{repository}/archive/v{version}.tar.gz'.format(
        user=user,
        repository=repository,
        version=version
    ),
    keywords=[
        'docker',
        'decorator',
        'testing',
        'example'
    ],
    classifiers=[],
    license=open('LICENSE').readline().strip(),
)
