
import _

class Database:
    @classmethod
    async def _(cls, instance, **kwds):
        self = cls()
        await self.init(**kwds)
        _.components.database[instance] = self

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
