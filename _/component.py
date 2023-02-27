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
            importPath = f'_.components.{componentType}.{component}'

        try:
            module = importlib.import_module(importPath)
        except Exception as e:
            logging.error('Import %s: %s', component, e)
            continue

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

        try:
            await cls._(name, **kwds)
        except Exception as e:
            logging.warn('Component: %s', e)
            raise

class Cache:
    @classmethod
    async def _(cls, instance, **kwds):
        self = cls()
        await self.init(**kwds)
        _.component.cache[instance] = self


class Database:
    @classmethod
    async def _(cls, instance, **kwds):
        self = cls()
        await self.init(**kwds)
        _.component.database[instance] = self

    async def init(self, **kwds):
        pass

    async def close(self):
        pass

    async def find(self, table, params=None, sort=None):
        raise NotImplementedError

    async def findOne(self, table, _id, id_column='id'):
        raise NotImplementedError

    async def insert(self, table, values, id_column='id'):
        raise NotImplementedError

    async def insertUnique(self, table, values, id_column='id'):
        raise NotImplementedError

    async def upsert(self, table, values, id_column='id'):
        raise NotImplementedError

    async def update(self, table, values, id_column='id'):
        raise NotImplementedError

    async def delete(self, table, values, column='id'):
        raise NotImplementedError


class Login(tornado.web.RequestHandler):
    @classmethod
    async def _(cls, instance, **kwds):
        # create a dynamic child class with kwds from the ini file
        _.component.login[instance] = type(cls.__name__, (cls,), kwds)

    @classmethod
    async def check(cls, username, password):
        return None


class Session:
    @classmethod
    async def _(cls, instance, **kwds):
        if _.component.session:
            logging.warn('Overwriting session')
        self = cls()
        await self.init(**kwds)
        _.component.session = self

    async def save_session(self, session_id):
        pass

    async def load_session(self, session_id):
        pass
