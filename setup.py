# -*- coding: utf-8 -*-
from distutils.core import setup

with open('README.md') as f:
    readme = f.read()

with open('LICENSE.txt') as f:
    license = f.read()

setup(
    name='docktors',
    packages=['docktors'],
    version='0.0.1',
    description='Decorator for docker',
    long_description=readme,
    author='Patrick Allain',
    author_email='patralla@gmail.com',
    url='https://github.com/Patouche/pydoctors',
    download_url='https://github.com/Patouche/pydoctors/archive/0.0.1.tar.gz',
    keywords=['docker', 'decorator', 'testing', 'example'],
    classifiers=[],
    license=license,
)
