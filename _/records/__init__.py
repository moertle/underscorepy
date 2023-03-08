#
# (c) 2015-2023 Matthew Shaw
#
# Authors
# =======
# Matthew Shaw <mshaw.cx@gmail.com>
#

import importlib
import json
import uuid

import tornado.web

import _


class Protocol:
    @classmethod
    async def _(cls, name, **kwds):
        self = cls()
        _.record[name] = self
        try:
            await self.init(name, **kwds)
        except TypeError as e:
            raise _.error('%s', e)

    async def init(self, name, module, database=None):
        try:
            imported = importlib.import_module(module)
        except ModuleNotFoundError:
            raise _.error('Unknown module: %s', module)

        if database is None:
            if 1 == len(_.database):
                database = list(_.database.keys())[0]
            else:
                raise _.error('dbcache requires a database to be specified')

        self.db   = _.database[database]
        self.name = name

        self.schema = self.db.schema(module)
        await _.wait(self._load(imported, module))
        await self.schema.apply()

    def _load(self, module, package):
        raise NotImplementedError


class Record:
    class Json(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, bytes):
                return base64.b64encode(obj).decode('ascii')
            if isinstance(obj, datetime.datetime):
                return str(obj)
            if isinstance(obj, uuid.UUID):
                return str(obj)
            return json.JSONEncoder.default(self, obj)

    def dump(self, **kwds):
        return json.dumps(self, cls=self.Json, separators=(',',':'), **kwds)


class Handler(_.handlers.Protected):
    @tornado.web.authenticated
    async def get(self, record, record_id=None):
        if not record_id:
            records = await self._record._db.find(self._record._table)
            self.write(dict(data=[dict(r) for r in records]))
        else:
            record = await self._record._db.find_one(self._record._table, self._record._primary_key, record_id)
            self.write(record)
