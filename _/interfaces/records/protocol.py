
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
