#!/usr/bin/env python

from setuptools import setup, find_packages

install_requires = open('./requirements.txt', 'r').readlines()
version = 'v2.0.1'
setup(name='perimeterx-python-wsgi',
      version=version,
      license='MIT',
      description='PerimeterX WSGI middleware',
      author='Ben Diamant',
      author_email='ben@perimeterx.com',
      url='https://github.com/PerimeterX/perimeterx-python-wsgi',
      download_url='https://github.com/PerimeterX/perimeterx-python-wsgi/tarball/' + version,
      packages=find_packages(exclude=['dev', 'test*']),
      package_data={'perimeterx': ['templates/*']},
      install_requires=install_requires,
      classifiers=['Intended Audience :: Developers',
                   'Programming Language :: Python :: 2.7'])
