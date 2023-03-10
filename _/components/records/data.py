
import dataclasses
import functools
import json

import _


def ignore(cls):
    setattr(cls, f'_handler', None)
    return cls

primary_key = functools.partial(dataclasses.field, metadata={'primary_key':True})

def references(foreign, key=None):
    return dataclasses.field(metadata={'references':foreign,'key':key})

def unique(*args):
    def wrap(cls):
        cls.__unique__ = args
        return cls
    return wrap


class Data(_.interfaces.Protocol):
    def _load(self, module, package):
        _.dataclasses = {}

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

    def _dataclass(self, name, dataclass):
        if hasattr(dataclass, '_handler'):
            return dataclass

        # make class a dataclass if it isn't already
        if not hasattr(dataclass, '__dataclass_fields__'):
            dataclass = dataclasses.dataclass(dataclass)

        if hasattr(dataclass, '__unique__'):
            print(dataclass.__unique__)


        members = dict(
            _db    = self.db,
            _table = name,
            )

        table = self.schema.table(name)
        for field in dataclasses.fields(dataclass):
            column = table.column(field.name)
            column.type(_column_mapping.get(field.type))
            if field.metadata.get('primary_key', False):
                column.primary_key()
                members['_primary_key'] = field.name

            reference = field.metadata.get('references', None)
            if reference:
                key = field.metadata.get('key', None)
                print(reference, key)
                column.references(reference.__name__, key)

        record   = type(name, (dataclass,Record), members)
        subclass = type(name, (_.records.Handler,), {'_record':record})
        _.dataclasses[name] = record
        _.application._record_handler(self.name, subclass)
        setattr(dataclass, '_handler', subclass)
        return dataclass

class Record(_.interfaces.Record):
    class Json(_.interfaces.Record.Json):
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
