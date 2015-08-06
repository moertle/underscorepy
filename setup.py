#!/usr/bin/env python

import os

from setuptools import setup

execfile('_/py/version.py')

setup(
    name = 'underscorepy',
    namespace_packages = ['_'],
    author = __author__,
    author_email = 'moertle@gmail.com',
    url = 'http://underscorepy.org',
    long_description = open('README.rst').read(),
    version = __version__,
    description = 'Core library for underscorepy plugins',
    license = 'MIT',
    packages = [
        '_.py',
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python :: 2.7",
    ]
)
