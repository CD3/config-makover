#!/usr/bin/env python

from setuptools import setup, find_packages
import versioneer

DESCRIPTION = "Config file reader and validator powered by Mako"
LONG_DESCRIPTION = open('README.md').read()

setup(name='config-makover',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      author='C.D. Clark III',
      url='https://github.com/CD3/config-makover',
      license="MIT License",
      platforms=["any"],
      packages=find_packages(),
     )
