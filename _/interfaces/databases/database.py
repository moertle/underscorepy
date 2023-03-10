#
# (c) 2015-2023 Matthew Shaw
#
# Authors
# =======
# Matthew Shaw <mshaw.cx@gmail.com>
#

import _

from .schema import Schema

class Database:
    @classmethod
    async def _(cls, name, **kwds):
        self = cls()
        _.databases[name] = self
        await self.init(name, **kwds)

    async def init(self, **kwds):
        pass

    async def close(self):
        pass

    async def find(self, table, params=None, sort=None):
        raise NotImplementedError

    async def find_one(self, table, id_column, _id):
        raise NotImplementedError

    async def insert(self, table, id_column, values):
        raise NotImplementedError

    async def insert_unique(self, table, id_column, values):
        raise NotImplementedError

    async def upsert(self, table, id_column, values):
        raise NotImplementedError

    async def update(self, table, id_column, values):
        raise NotImplementedError

    async def delete(self, table, values, column='id'):
        raise NotImplementedError

    def schema(self, name):
        return Schema(self, name)
