#
# (c) 2015-2023 Matthew Shaw
#
# Authors
# =======
# Matthew Shaw <mshaw.cx@gmail.com>
#

import argparse
import collections
import configparser
import inspect
import logging
import os
import sys
import time

import _


_.argparser = argparse.ArgumentParser()


class Paths(object):
    def __init__(self, root=None, ns=None):
        self.root = root
        self.ns   = ns

    def __call__(self, *args):
        return os.path.join(self.root, self.ns, *args)


def load(application, **kwds):
    _.argparser.add_argument('--address', '-a',
        metavar='<address>',
        help = 'Interface to bind to')

    _.argparser.add_argument('--port', '-p',
        metavar='<port>',
        type=int,
        help='Port to listen on')

    _.argparser.add_argument('--ini', '-I',
        metavar='<path>',
        help='Specify additional ini file')

    _.argparser.add_argument('--debug', '-D',
        action='store_true',
        help='Print verbose debugging information')

    _.argparser.add_argument('--version', '-V',
        action='store_true',
        help='show version and exit'
        )

    _.args = _.argparser.parse_args()

    logging.basicConfig(
        format  = '%(asctime)s %(levelname)-8s %(message)s',
        datefmt = '%Y-%m-%d %H:%M:%S',
        level   = logging.DEBUG if _.args.debug else logging.INFO
        )

    # get the path of the caller
    caller = inspect.getfile(application.__class__)

    # get the directory of the script
    root = kwds.get('root', None)
    if root is None:
        root = os.path.dirname(caller)
    root = os.path.abspath(root)

    _.app = kwds.get('app', None)
    if _.app is None:
        # get the name of the script
        _.app = os.path.basename(caller)
        if _.app.endswith('.py'):
            _.app = _.app[:-3]

    _.ns = kwds.get('ns', _.app)
    if _.ns is None:
        _.ns = ''

    _.paths = Paths(root=root, ns=_.ns)

    # if ns is not passed in use the supplied or derived ns
    iniFiles = []

    if _.ns:
        iniFiles.append(_.paths(f'{_.ns}.ini'))

    iniFiles.append(_.paths(f'{_.app}.ini'))

    if _.args.ini:
        iniFiles.append(_.args.ini)

    _.config = configparser.SafeConfigParser(
        allow_no_value = True,
        interpolation  = None,
        )
    _.config.optionxform = str

    try:
        ok = _.config.read(iniFiles)
    except configparser.ParsingError as e:
        raise _.error('Unable to parse file: %s', e)

    if not ok:
        raise _.error('Unable to read config file(s):\n  %s', '\n  '.join(iniFiles))

    if not _.args.address:
        _.args.address = _.config.get(_.app, 'address', fallback='127.0.0.1')

    if not _.args.port:
        _.args.port = _.config.getint(_.app, 'port', fallback=8080)

    if _.config.getboolean(_.app, 'logging', fallback=False):
        fullPath = _.paths(f'{_.app}.log')
        fileLogger = logging.FileHandler(fullPath)
        fileLogger.setLevel(logging.DEBUG if _.args.debug else logging.INFO)
        fileLogger.setFormatter(
            logging.Formatter(
                fmt = '%(asctime)s %(levelname)-8s %(message)s',
                datefmt = '%Y-%m-%d %H:%M:%S',
                )
            )
        # add the handlers to the logger
        rootLogger = logging.getLogger()
        rootLogger.addHandler(fileLogger)
