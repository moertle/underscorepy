
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

import _.py

argparser = argparse.ArgumentParser()

argparser.add_argument('--ini', '-I',
    help='Specify additional ini file')

argparser.add_argument('--debug', '-D',
    action='store_true',
    help='Print verbose debugging information')

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


def load(settings=None, namespace=None, root=None):
    _.py.namespace = namespace

    # inspect who called this function
    frames = inspect.getouterframes(inspect.currentframe())
    # get the caller frame
    frame = frames[-1]
    # get the path of the caller
    script_path = os.path.abspath(frame[1])

    script_name = os.path.basename(script_path).rsplit('.', 1)[0]

    if root is None:
        root = os.path.dirname(script_path)
        if root.endswith(os.path.sep + 'bin'):
            root = os.path.join(root, '..')

    root = os.path.abspath(root)

    if namespace is None:
        namespace = script_name

    _.py.paths = Paths(root=root, namespace=namespace)

    _.py.args = argparser.parse_args()

    # if settings is not passed in use the supplied or derived namespace
    settings = settings or namespace

    ini_files = [
        _.py.paths('etc', settings + '.ini'),
        _.py.paths('etc', settings + '.local.ini'),
    ]

    if _.py.args.ini:
        ini_files.append(_.py.args.ini)

    _.py.config = configparser.SafeConfigParser(dict_type=collections.OrderedDict)
    _.py.config.optionxform = str
    try:
        ok = _.py.config.read(ini_files)
    except configparser.ParsingError as e:
        raise _.py.error('Unable to parse file: %s', e)

    if not ok:
        raise _.py.error('Unable to read config file(s): %s', ini_files)

    file_name = script_name + '.log'
    full_path = _.py.paths('var', file_name)
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

    if _.py.args.debug:
        root.setLevel(logging.DEBUG)
        logfile.setLevel(logging.DEBUG)

    # call this here if there is no daemon option
    if not hasattr(_.py.args, 'daemon'):
        components()

    return

def components():
    # check if the config file specifies components
    if _.py.config.has_section('components'):
        for name in _.py.components.Registry:
            if _.py.config.has_option('components', name):
                logging.info('Loading %s components', name)
                _.py.components.Load(name)
    else:
        _.py.components.Registry.clear()

