#!/usr/bin/env python

from setuptools import setup, find_packages

version = 'v3.1.0'
setup(name='perimeterx-python-wsgi-gae',
      version=version,
      license='MIT',
      description='PerimeterX WSGI middleware for Goolge App Engine',
      author='Johnny Tordgeman',
      author_email='johnny@perimeterx.com',
      url='https://github.com/PerimeterX/perimeterx-python-wsgi',
      download_url='https://github.com/PerimeterX/perimeterx-python-wsgi/tarball/' + version,
      packages=find_packages(exclude=['dev', 'test*']),
      package_data={'perimeterx': ['templates/*']},
      install_requires=['pystache>=0.5.1,<=0.5.4', 'requests>=2.18.4,<=2.20.1', 'requests-toolbelt'],
      classifiers=['Intended Audience :: Developers',
                   'Programming Language :: Python :: 2.7'])
