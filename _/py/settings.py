
import sys
import os
import argparse
import collections
import logging
import time

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

import _

_.argparser = argparse.ArgumentParser()

_.argparser.add_argument('--ini', '-i',
    help='Specify additional ini file')

_.argparser.add_argument('--debug', '-d',
    action='store_true',
    help='Print verbose debugging information')

logging.basicConfig(
    format  = '%(asctime)s %(levelname)-8s %(message)s',
    datefmt = '%Y-%m-%d %H:%M:%S',
    level   = logging.INFO
    )


def load():
    parent = _.util.getParent()
    script_name = os.path.basename(parent)
    script_name = script_name.rsplit('.', 1)[0]

    if prefix is None:
        # get the filename of the caller
        # get the directory name of the file
        prefix = os.path.dirname(parent)

        if prefix.endswith(os.path.sep + 'bin'):
            prefix = os.path.join(prefix, '..')
            prefix = os.path.abspath(prefix)

    prefix = os.path.abspath(prefix)
    if _.prefix != prefix:
        _.prefix = prefix
        logging.debug('Setting prefix to "%s"', _.prefix)

    if namespace is None:
        namespace = script_name

    if namespace != _.namespace:
        _.namespace = namespace
        logging.debug('Setting namespace to "%s"', _.namespace)

    # if settings is not passed in use the supplied or derived namespace
    settings = settings or namespace

    _.args = _.argparser.parse_args()

    _.config = configparser.SafeConfigParser(dict_type=collections.OrderedDict)
    _.config.optionxform = str

    ini_files = [
        _.paths('etc', settings + '.ini'),
        _.paths('etc', settings + '.ini.local')
    ]

    if _.args.ini:
        ini_files.append(_.args.ini)

    try:
        ok = _.config.read(ini_files)
    except configparser.ParsingError as e:
        raise _.error('Unable to parse file: %s', e)

    if not ok:
        raise _.error('Unable to read config file(s): %s', ini_files)

    # setup file log
    file_name = '%s_%s.log' % (script_name, time.strftime('%Y%m%d_%H%M%S'))

    # hack back in single log file option without breaking existing code
    if _.config.has_section('logging'):
        if _.config.has_option('logging', 'append'):
            append = _.config.getboolean('logging', 'append')
            if append:
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

    if _.args.debug:
        root.setLevel(logging.DEBUG)
        logfile.setLevel(logging.DEBUG)

    # call this here if there is no daemon option
    if not hasattr(_.args, 'daemon'):
        _.module.load()

    return
