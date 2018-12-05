#!/usr/bin/env python

from setuptools import setup, find_packages

version = 'v2.0.2'
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
      install_requires=['pycrypto==2.6.1', 'pystache==0.5.4', 'requests==2.20.1', 'setuptools==40.6.2'],
      classifiers=['Intended Audience :: Developers',
                   'Programming Language :: Python :: 2.7'])
