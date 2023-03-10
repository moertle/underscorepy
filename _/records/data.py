
import collections
import dataclasses
import functools
import json

import _


class Record(_.records.Record):
    def __init__(self, **kwds):
        for kwd in kwds:
            setattr(self, kwd, kwds[kwd])

    class Json(_.records.Record.Json):
        def default(self, obj):
            if hasattr(obj, '__dataclass_fields__'):
                return Record.dict(obj)
            return super(Json, self).default(obj)

    @classmethod
    def dict(cls, data):
        return dataclasses.asdict(data)

    @classmethod
    def load(cls, msg):
        return cls(**json.loads(msg))


class Container(collections.UserDict):
    @staticmethod
    def no_db(cls):
        setattr(cls, f'_{cls.__name__}__no_db', True)
        return cls

    @staticmethod
    def no_handler(cls):
        setattr(cls, f'_{cls.__name__}__no_handler', True)
        return cls

    @staticmethod
    def no_pkey(cls):
        setattr(cls, f'_{cls.__name__}__no_pkey', True)
        return cls

    @staticmethod
    def pkey(arg=True):
        meta = {'pkey':True}
        if isinstance(arg, dataclasses.Field):
            meta.update(arg.metadata)
        return dataclasses.field(metadata=meta)

    @staticmethod
    def uniq(arg=True):
        meta = {'unique':True}
        if isinstance(arg, dataclasses.Field):
            meta.update(arg.metadata)
        return dataclasses.field(metadata=meta)

    @staticmethod
    def ref(foreign, key=None):
        return dataclasses.field(metadata={'ref':foreign,'key':key})


class Data(_.records.Protocol):
    async def init(self, module, database=None):
        _.data = Container()
        await super(Data, self).init(module, database)

    def _load(self, module, package):
        for name in dir(module):
            if name.startswith('__'):
                continue

            attr = getattr(module, name)

            # ignore objects that are not classes
            if not isinstance(attr, type(Data)):
                continue

            # ignore classes outside of module root
            if not attr.__module__.startswith(package):
                continue

            attr = self._dataclass(name, attr)
            setattr(module, name, attr)

    def _dataclass(self, name, cls):
        # make class a dataclass if it isn't already
        if not dataclasses.is_dataclass(cls):
            cls = dataclasses.dataclass(kw_only=True)(cls)

        members = dict()

        if not hasattr(cls, f'_{cls.__name__}__no_db'):
            members.update(dict(db=self.db, table=name))
            table = self.schema.table(name)
            for field in dataclasses.fields(cls):
                column = table.column(field.name)
                column.type(_column_mapping.get(field.type))

                if field.metadata.get('pkey', False):
                    column.primary_key()
                    members['primary_key'] = field.name

                unique = field.metadata.get('unique', False)
                if unique:
                    table.unique(field.name)

                reference = field.metadata.get('ref', None)
                if reference:
                    key = field.metadata.get('key', None)
                    column.references(reference.__name__, key)

            if hasattr(cls, f'_{cls.__name__}__no_pkey'):
                table.primary_key(None)

        record  = type(name, (cls,Record), _.prefix(members))
        _.data[name] = record

        if not hasattr(cls, f'_{cls.__name__}__no_handler'):
            members['record'] = record
            handler = type(name, (Handler,), _.prefix(members))
            _.application._record_handler(self.name, handler)
            setattr(cls, '_handler', handler)
        return cls


_column_mapping = {
    str:  'TEXT',
    int:  'INTEGER',
    bool: 'BOOLEAN',
    }


class Handler(_.records.Handler):
    async def get(self, record, record_id=None):
        try:
            await self._record.get(self, record, record_id=record_id)
        except AttributeError:
            await super(Handler, self).get(record, record_id)

    async def put(self, record, record_id=None):
        try:
            await self._record.put(self, record, record_id=record_id)
        except AttributeError:
            await super(Handler, self).put(record, record_id)

    async def delete(self, record, record_id=None):
        try:
            await self._record.delete(self, record, record_id=record_id)
        except AttributeError:
            await super(Handler, self).delete(record, record_id)
