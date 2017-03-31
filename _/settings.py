
import argparse
import collections
import inspect
import logging
import os
import sys
import time

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

import _

argparser = argparse.ArgumentParser()


def log():
    logging.basicConfig(
        format  = '%(asctime)s %(levelname)-8s %(message)s',
        datefmt = '%Y-%m-%d %H:%M:%S',
        level   = logging.INFO
        )


class Paths(object):
    def __init__(self, **kwds):
        self.root      = None
        self.namespace = None
        for k,v in kwds.items():
            setattr(self, k, v)

    def __call__(self, toplevel, *args):
        return os.path.join(self.root, toplevel, self.namespace, *args)


def load(**kwds):
    argparser.add_argument('--ini', '-I',
        metavar='<path>',
        help='Specify additional ini file')

    argparser.add_argument('--debug', '-D',
        action='store_true',
        help='Print verbose debugging information')

    # inspect who called this function
    frames = inspect.getouterframes(inspect.currentframe())
    # get the caller frame
    frame = frames[-1]
    # get the path of the caller
    script_path = os.path.abspath(frame[1])

    script_name = os.path.basename(script_path).rsplit('.', 1)[0]

    root = kwds.get('root', None)
    if root is None:
        root = os.path.dirname(script_path)
        if root.endswith(os.path.sep + 'bin'):
            root = os.path.join(root, '..')

    root = os.path.abspath(root)

    try:
        namespace = kwds['namespace']
        if not namespace:
            namespace = ''
    except KeyError:
        namespace = script_name

    _.paths = Paths(root=root, namespace=namespace)

    _.settings.args,_.settings.args_remaining = argparser.parse_known_args()

    # if settings is not passed in use the supplied or derived namespace
    settings = kwds.get('settings', namespace or script_name)

    ini_files = [
        _.paths('etc', settings + '.ini'),
        _.paths('etc', settings + '.local.ini'),
    ]

    if _.settings.args.ini:
        ini_files.append(_.settings.args.ini)

    _.settings.config = configparser.SafeConfigParser(dict_type=collections.OrderedDict)
    _.settings.config.optionxform = str
    try:
        ok = _.settings.config.read(ini_files)
    except configparser.ParsingError as e:
        raise _.error('Unable to parse file: %s', e)

    if not ok:
        raise _.error('Unable to read config file(s): %s', ini_files)

    # underscore apps can explicit turn off logging
    if _.settings.config.getboolean('_', 'logging', fallback=True):
        file_name = script_name + '.log'
        full_path = _.paths('var', file_name)
        logfile = logging.FileHandler(full_path)
        logfile.setLevel(logging.INFO)
        logfile.setFormatter(
            logging.Formatter(
                fmt = '%(asctime)s %(levelname)-8s %(message)s',
                datefmt = '%Y-%m-%d %H:%M:%S',
                )
            )

        # add the handlers to the logger
        root = logging.getLogger()
        root.addHandler(logfile)

        if _.settings.args.debug:
            root.setLevel(logging.DEBUG)
            logfile.setLevel(logging.DEBUG)

    # check if the config file specifies components
    if _.settings.config.has_section('components'):
        for name in _.components.Registry:
            if _.settings.config.has_option('components', name):
                logging.info('Loading %s components', name)
                _.components.Load(name)
    else:
        _.components.Registry.clear()
