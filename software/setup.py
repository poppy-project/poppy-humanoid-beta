#!/usr/bin/env python

import re
import sys

from setuptools import setup, find_packages


def version():
    with open('poppytools/_version.py') as f:
        return re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", f.read()).group(1)

extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

setup(name='poppytools',
      version=version(),
      packages=find_packages(),

      install_requires=['pypot', 'numpy'],

      extras_require={
          'tools': [],  # Extras require: PyQt4 (not a PyPi packet)
          'server': ['bottle', 'tornado', 'zmq']
      },

      setup_requires=['setuptools_git >= 0.3', ],

      include_package_data=True,
      exclude_package_data={'': ['README', '.gitignore']},

      zip_safe=True,

      author='Matthieu Lapeyre, Pierre Rouanet',
      author_email='matthieu.lapeyre@gmail.com',
      description='Python tools for Poppy Control',
      url='https://github.com/poppy-project/poppy-software',
      license='GNU GENERAL PUBLIC LICENSE Version 3',
      **extra
      )
