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

async def load(component_type):
    if component_type not in _.config:
        return

    for name in _.config[component_type]:
        component = _.config[component_type][name]
        if component is None:
            component = name

        if component.startswith('+'):
            try:
                component,attr = component.rsplit('.', 1)
            except ValueError:
                attr = None
            import_path = component[1:]
        else:
            attr = None
            import_path = f'_.{component_type}.{component}'

        try:
            module = importlib.import_module(import_path)
        except ModuleNotFoundError:
            raise _.error('Unknown module: %s', import_path)

        cls = None
        if not attr:
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if not isinstance(attr, type):
                    continue
                if not hasattr(attr, '_'):
                    continue
                cls = attr
        else:
            cls = getattr(module, attr)

        if not cls:
            logging.error('%s: %s module not found', component, component_type)
            continue

        try:
            kwds = dict(_.config[name])
        except KeyError:
            kwds = {}

        await cls._(name, **kwds)
