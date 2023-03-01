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


_.cache    = {}
_.database = {}
_.login    = {}
_.support  = {}

async def load(componentType):
    if componentType not in _.config:
        return

    for name in _.config[componentType]:
        component = _.config[componentType][name]
        if component is None:
            component = name

        if component.startswith('+'):
            try:
                component,attr = component.rsplit('.', 1)
            except ValueError:
                attr = None
            importPath = component[1:]
        else:
            attr = None
            importPath = f'_.{componentType}.{component}'

        try:
            module = importlib.import_module(importPath)
        except ModuleNotFoundError:
            raise _.error('Unknown module: %s', importPath)

        cls = None
        if not attr:
            for attrName in dir(module):
                attr = getattr(module, attrName)
                if not isinstance(attr, type):
                    continue
                if not hasattr(attr, '_'):
                    continue
                cls = attr
        else:
            cls = getattr(module, attr)

        if not cls:
            logging.error('%s: %s module not found', component, componentType)
            continue

        try:
            kwds = dict(_.config[name])
        except KeyError:
            kwds = {}

        await cls._(name, **kwds)
