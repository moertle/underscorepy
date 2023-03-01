#!/usr/bin/env python3

import sys
import os

import setuptools

exec(compile(open('skeleton/version.py').read(),'version.py','exec'))

setuptools.setup(
    name             = 'skeleton',
    version          = __version__,
    author           = __author__,
    author_email     = __email__,
    description      = '_.py skeleton',
    long_description = open('README.rst').read(),
    license          = 'TBD',
    packages         = setuptools.find_packages(),
    entry_points = {
        'console_scripts' : [
            'skeleton-server = skeleton:Skeleton.main',
            ]
        },
    include_package_data = True,
    install_requires = [
        'underscorepy',
        ],
    zip_safe = False
    )
