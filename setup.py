#!/usr/bin/env python3

from setuptools import setup

exec(compile(open('_/version.py').read(),'version.py','exec'))

setup(
    name                 = 'underscorepy',
    author               = __author__,
    author_email         = __email__,
    version              = __version__,
    license              = __license__,
    url                  = 'http://underscorepy.org',
    description          = 'underscore library',
    long_description     = open('README.rst').read(),
    packages             = setuptools.find_packages(),
    include_package_data = True,
    zip_safe             = False,
    install_requires = [
        'tornado',
        ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 3.7',
        ]
    )
