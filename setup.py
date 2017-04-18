#!/usr/bin/env python

from setuptools import setup

version = 'v1.2.0'
setup(name='perimeterx-python-wsgi',
      version=version,
      description='PerimeterX WSGI middleware',
      author='Ben Diamant',
      author_email='ben@perimeterx.com',
      url='https://github.com/PerimeterX/perimeterx-python-wsgi',
      download_url='https://github.com/PerimeterX/perimeterx-python-wsgi/tarball/' + version,
      package_dir={'perimeterx': 'perimeterx'},
      install_requires=[
          "pystache"
      ]
      )
