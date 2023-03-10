#
# (c) 2015-2023 Matthew Shaw
#
# Authors
# =======
# Matthew Shaw <mshaw.cx@gmail.com>
#

import logging
import os

import google.protobuf.message
import google.protobuf.json_format

import _

from . import Protobuf_pb2


class Record(_.records.Record):
    def __init__(self, _msg=None):
        self.__dict__['_msg'] = _msg if _msg else self._message()

    class Json(_.records.Record.Json):
        def default(self, obj):
            if hasattr(obj, 'DESCRIPTOR'):
                return Record.dict(obj)
            return super(Json, self).default(obj)

    @classmethod
    def dict(cls, message):
        return google.protobuf.json_format.MessageToDict(
            message,
            including_default_value_fields = True,
            preserving_proto_field_name    = True,
            )

    @classmethod
    def load(cls, data):
        msg = cls._message()
        google.protobuf.json_format.Parse(data, msg)
        return cls(msg)

    def __getattr__(self, name):
        return getattr(self._msg, name)

    def __setattr__(self, name, value):
        self._msg.__setattr__(name, value)

    def __str__(self):
        return self._msg.__str__()


class Protobuf(_.records.Protocol):
    def _load(self, module, package):
        _.protobuf = {}

        # iterate over all the members of the protobuf modules
        for member in dir(module):
            # all proto messages end with _pb2
            if not member.endswith('_pb2'):
                continue
            # get a handle to the pb2 module descriptor
            pb2 = getattr(module, member)

            # iterate over all the message definitions
            for name,descriptor in pb2.DESCRIPTOR.message_types_by_name.items():
                message = getattr(pb2, name)
                self._message(name, message)

    def _message(self, name, message):
        table_options = message.DESCRIPTOR.GetOptions()

        members = dict(message=message)

        if not table_options.Extensions[Protobuf_pb2.no_db]:
            members.update(dict(db=self.db, table=name))
            table = self.schema.table(name)
            if table_options.HasExtension(Protobuf_pb2.id):
                table.default_id(table_options.Extensions[Protobuf_pb2.id])

            # iterate over message to determine columns
            for field in message.DESCRIPTOR.fields:
                column = table.column(field.name)
                column.type(_column_mapping[field.type])

                col_options = field.GetOptions()
                # check if column should be a primary key
                if col_options.Extensions[Protobuf_pb2.pkey]:
                    column.primary_key()
                    members['primary_key'] = field.name
                # check for foreign key
                if col_options.HasExtension(Protobuf_pb2.ref):
                    table.foreign_key(col_options.Extensions[Protobuf_pb2.ref])
                if field.label is field.LABEL_REPEATED:
                    column.repeated()

        # Protobuf does not want you to subclass the Message
        # so we dynamically create a thin wrapper
        record  = type(name, (Record,), _.prefix(members))
        _.protobuf[name] = record

        add_handler = True
        # ignore messages explicitly defined as not a table
        if table_options.Extensions[Protobuf_pb2.no_handler]:
            add_handler = False

        if add_handler:
            members['record'] = record
            handler = type(name, (_.records.Handler,), _.prefix(members))
            _.application._record_handler(self.name, handler)


_column_mapping = [
    None,
    'DOUBLE PRECISION', # DOUBLE
    'REAL',             # FLOAT
    'BIGINT',           # INT64
    'NUMERIC',          # UINT64
    'INTEGER',          # INT32
    'NUMERIC',          # FIXED64
    'BIGINT',           # FIXED32
    'BOOLEAN',          # BOOL
    'TEXT',             # STRING
    'JSONB',            # GROUP
    'JSONB',            # MESSAGE
    'BYTEA',            # BYTES
    'BIGINT',           # UINT32
    'INTEGER',          # ENUM
    'INTEGER',          # SFIXED32
    'BIGINT',           # SFIXED64
    'INTEGER',          # SINT32
    'BIGINT',           # SINT64
    ]


if '__main__' == __name__:
    root = os.path.dirname(_.__file__)
    root = os.path.abspath(os.path.join(root, '..'))
    print(root)
