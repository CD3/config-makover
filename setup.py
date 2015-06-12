#!/usr/bin/env python

from setuptools import setup, find_packages

DESCRIPTION = "Config file reader and validator powered by Mako"
LONG_DESCRIPTION = open('README.md').read()

setup(name='config-makover',
      version='0.0.0',
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      author='C.D. Clark III',
      url='https://github.com/CD3/config-makover',
      license="MIT License",
      platforms=["any"],
      packages=find_packages(),
     )
