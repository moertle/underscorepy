#!/usr/bin/env python

import os

from setuptools import setup

exec(compile(open('_/py/version.py').read(),'version.py','exec'))

setup(
    name               = 'underscorepy',
    namespace_packages = ['_'],
    author             = __author__,
    author_email       = __email__,
    version            = __version__,
    license            = __license__,
    url                = 'http://underscorepy.org',
    description        = '_.py Core library',
    long_description   = open('README.rst').read(),
    packages = [
        '_.py',
        ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 2.7',
        ]
    )
