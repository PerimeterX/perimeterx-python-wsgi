#!/usr/bin/env python

from setuptools import setup

version = 'v2.0.0'
setup(name='perimeterx-python-wsgi',
      version=version,
      license='MIT',
      description='PerimeterX WSGI middleware',
      author='Ben Diamant',
      author_email='ben@perimeterx.com',
      url='https://github.com/PerimeterX/perimeterx-python-wsgi',
      download_url='https://github.com/PerimeterX/perimeterx-python-wsgi/tarball/' + version,
      package_dir={'perimeterx': 'perimeterx'},
      install_requires=[
        "pystache==0.5.4", 'requests==2.20.1', 'setuptools==40.6.2', 'requests_mock==1.5.2',
        'pycrypto==2.6.1', 'mock==2.0.0', 'pylint'],
      classifiers=['Intended Audience :: Developers',
                   'Programming Language :: Python :: 2.7'])

