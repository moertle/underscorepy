#!/usr/bin/env python3

from setuptools import setup

exec(compile(open('_/version.py').read(),'version.py','exec'))

setup(
    name               = 'underscorepy',
    author             = __author__,
    author_email       = __email__,
    version            = __version__,
    license            = __license__,
    url                = 'http://underscorepy.org',
    description        = 'underscore library',
    long_description   = open('README.rst').read(),
    packages = [
        '_',
        '_.storage',
        '_.storage.engines',
        '_.web',
        '_.web.auth',
        '_.web.handlers',
        ],
    package_data = {
        '_.pb': ['*.pb.*', '*.proto'],
        },
    install_requires = [
        'protobuf >= 3.6.0',
        'tornado  <  5.0.0',
        ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        ]
    )
