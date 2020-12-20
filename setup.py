# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
# Package meta-data.
NAME = 'mypackage'
DESCRIPTION = 'My short description for my project.'
URL = 'https://github.com/gaonkar/enphase-envoy'
EMAIL = 'gaonkar@ieee.org'
AUTHOR = 'Shravan Gaonkar'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = '0.1.0'

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()
setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=readme,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
