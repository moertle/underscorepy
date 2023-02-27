#
# (c) 2015-2023 Matthew Shaw
#
# Authors
# =======
# Matthew Shaw <mshaw.cx@gmail.com>
#

import importlib
import logging

import tornado.web

import _


cache    = {}
database = {}
login    = {}
session  = None

async def load(componentType):
    if componentType not in _.config:
        return

    for name in _.config[componentType]:
        component = _.config[componentType][name]

        if component.startswith('+'):
            importPath = component[1:]
        else:
            importPath = f'_.{componentType}.{component}'

        module = importlib.import_module(importPath)

        cls = None
        for attrName in dir(module):
            attr = getattr(module, attrName)
            if not isinstance(attr, type):
                continue
            if not hasattr(attr, '_'):
                continue
            cls = attr

        if not cls:
            logging.error('%s: %s module not found', component, componentType)
            continue

        try:
            kwds = dict(_.config[name])
        except KeyError:
            kwds = {}

        await cls._(name, **kwds)
