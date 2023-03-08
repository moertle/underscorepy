
import dataclasses
import datetime
import functools
import json

import _


def ignore(cls):
    setattr(cls, f'_handler', None)
    return cls

primary_key = functools.partial(dataclasses.field, metadata='primary_key')

class DataClass(_.records.Protocol):
    def _load(self, module, package):
        _.dataclasses = {}

        for name in dir(module):
            if name.startswith('__'):
                continue

            attr = getattr(module, name)

            if not isinstance(attr, type(DataClass)):
                # ignore objects that are not classes
                continue

            if not attr.__module__.startswith(package):
                # ignore classes outside of module root
                continue

            if not hasattr(attr, '__dataclass_fields__'):
                # make class a dataclass if it isn't already
                attr = dataclasses.dataclass(attr)
                setattr(module, name, attr)

            self._dataclass(name, attr)

    def _dataclass(self, name, dataclass):
        if hasattr(dataclass, '_handler'):
            return

        members = dict(
            _db    = self.db,
            _table = name,
            )

        table = self.schema.table(name)
        for field in dataclasses.fields(dataclass):
            column = table.column(field.name)
            column.type(_column_mapping.get(field.type))
            if field.metadata == 'primary_key':
                column.primary_key()
                members['_primary_key'] = field.name

        record   = type(name, (dataclass,Record), members)
        subclass = type(name, (_.records.Handler,), {'_record':record})
        _.dataclasses[name] = record
        _.application._record_handler(self.name, subclass)
        setattr(dataclass, '_handler', subclass)


class Record(_.records.Record):
    class Json(_.records.Record.Json):
        def default(self, obj):
            if hasattr(obj, '__dataclass_fields__'):
                return Record.dict(obj)
            return super(Json, self).default(obj)

    @classmethod
    def dict(cls, dataclass):
        return dataclasses.asdict(dataclass)

    @classmethod
    def load(cls, data):
        return cls(**json.loads(data))


_column_mapping = {
    str: 'TEXT',
    int: 'INTEGER'
    }
