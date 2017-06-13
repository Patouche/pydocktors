#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from setuptools import setup, find_packages

authors = ['Patrick Allain']
github_user = 'Patouche'
github_repository = 'pydocktors'
version = open('VERSION').readline().strip()

setup(
    name=github_repository,
    version=version,
    packages=find_packages(exclude=['it.tests', 'tests', 'examples']),
    description='Simple docker decorator',
    long_description=open('README.rst').read(),
    author=', '.join(authors),
    author_email='patralla@gmail.com',
    install_requires=[
        'docker>=2.0.0'
    ],
    url='https://github.com/{user}/{repository}'.format(
        user=github_user,
        repository=github_repository,
    ),
    download_url='https://github.com/{user}/{repository}/archive/v{version}.tar.gz'.format(
        user=github_user,
        repository=github_repository,
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
