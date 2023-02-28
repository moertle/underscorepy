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


class ArgParser(argparse.ArgumentParser):
    def exit(self, status=0, message=None):
        if message:
            self._print_message(message, sys.stderr)
        raise _.error('')

_.argparser = ArgParser(add_help=False)

_.argparser.add_argument('--ini', '-I',
    metavar='<path>',
    help='Specify additional ini file')

_.argparser.add_argument('--address', '-a',
    metavar='<address>',
    help = 'Interface to bind to')

_.argparser.add_argument('--port', '-p',
    metavar='<port>',
    type=int,
    help='Port to listen on')


_.config = configparser.SafeConfigParser(
    allow_no_value = True,
    interpolation  = None,
    )
_.config.optionxform = str


async def load(application, **kwds):

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

    _.paths = _.Paths(root=root, ns=_.ns)

    # if ns is not passed in use the supplied or derived ns
    iniFiles = []

    if _.ns:
        iniFiles.append(_.paths(f'{_.ns}.ini'))

    iniFiles.append(_.paths(f'{_.app}.ini'))

    # first pass at parsing args to get additional ini files
    args,remainder = _.argparser.parse_known_args()

    if args.ini:
        iniFiles.append(args.ini)

    try:
        ok = _.config.read(iniFiles)
    except configparser.ParsingError as e:
        raise _.error('Unable to parse file: %s', e)

    if not ok:
        raise _.error('Unable to read config file(s):\n  %s', '\n  '.join(iniFiles))

    try:
        await _.components.load('caches')
        await _.components.load('databases')
        await _.components.load('logins')
    except Exception as e:
        if _.args.debug:
            traceback.print_tb(e.__traceback__)
        raise _.error('%s', e)

    _.argparser.add_argument('--debug', '-D',
        action='store_true',
        help='Log verbose debugging information')

    _.argparser.add_argument('--version', '-V',
        action='store_true',
        help='Show version and exit'
        )

    _.argparser.add_argument('--help', '-h',
        action='help', default=argparse.SUPPRESS,
        help='Show help message')

    _.args = _.argparser.parse_args()

    if not _.args.address:
        _.args.address = _.config.get(_.app, 'address', fallback='127.0.0.1')

    if not _.args.port:
        _.args.port = _.config.getint(_.app, 'port', fallback=8080)
