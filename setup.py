#!/usr/bin/env python

from setuptools import setup, find_packages

version = 'v3.1.0'
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
      install_requires=['pystache>=0.5.1,<=0.5.4', 'requests>=2.18.4,<=2.20.1', 'setuptools==40.6.2', 'Werkzeug==0.14.1', 'pycryptodome>=3.7.2, <4.0.0'],
      classifiers=['Intended Audience :: Developers',
                   'Programming Language :: Python :: 2.7'])
