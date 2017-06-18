#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Setup module.
"""
from setuptools import setup, find_packages

AUTHORS = {
    'patralla@gmail.com': 'Patrick Allain'
}
GITHUB = dict(
    user='Patouche',
    repository='pydocktors'
)
VERSION = open('VERSION').readline().strip()

setup(
    name=GITHUB['repository'],
    version=VERSION,
    packages=find_packages(exclude=['it.tests', 'tests', 'examples']),
    description='Simple docker decorator',
    long_description=open('README.rst').read(),
    author=', '.join(AUTHORS.values()),
    author_email=', '.join(AUTHORS.keys()),
    install_requires=[
        'docker>=2.0.0'
    ],
    url='https://github.com/{user}/{repository}'.format(
        user=GITHUB['user'],
        repository=GITHUB['user'],
    ),
    download_url='https://github.com/{user}/{repository}/archive/v{version}.tar.gz'.format(
        user=GITHUB['user'],
        repository=GITHUB['user'],
        version=VERSION
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
