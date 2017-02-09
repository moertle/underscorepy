
import base64
import collections
import json

import _.pb

from .. import convert
from .. import options_pb2


class Pb(collections.MutableMapping):
    __dictcls__ = collections.OrderedDict
    __bytecls__ = staticmethod(base64.b64encode)

    def __getitem__(self, key):
        try:
            return self.__getattribute__(key)
        except AttributeError:
            raise KeyError(key)

    def __getattribute__(self, key):
        value = object.__getattribute__(self, key)

        DESCRIPTOR = object.__getattribute__(self, 'DESCRIPTOR')
        field = DESCRIPTOR.fields_by_name.get(key, None)
        if field:
            if field.label == field.LABEL_REPEATED:
                if field.type != field.TYPE_MESSAGE:
                    converter = field.GetOptions().Extensions[options_pb2.convert]
                    value = Scalar(value, converter)
            else:
                value = convert.from_proto(field, value)

        return value

    def __setitem__(self, key, value):
        try:
            return self.__setattr__(key, value)
        except AttributeError:
            raise KeyError(key)

    def __setattr__(self, key, value):
        field = self.DESCRIPTOR.fields_by_name.get(key, None)
        if field:
            value = convert.to_proto(field, value)
            if 12 == field.type:
                value = bytes(value)

        return object.__setattr__(self, key, value)

    def __delitem__(self, key):
        try:
            self.ClearField(key)
        except ValueError:
            raise KeyError(key)

    def __contains__(self, key):
        field = self.DESCRIPTOR.fields_by_name.get(key, None)
        if not field:
            return False

        # TODO: should contains report False for empty lists?
        # Users should check the length of the lists
        if field.label == field.LABEL_REPEATED:
            return True

        return self.HasField(key)

    def __len__(self):
        return len(msg.ListFields())

    def __iter__(self):
        for (field,value) in self.ListFields():
            yield field.name

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except:
            return default

    def keys(self):
        keys = []
        for (field,value) in self.ListFields():
            keys.append(field.name)
        return keys

    def values(self):
        values = []
        for (field,value) in self.ListFields():
            if field.type not in [field.TYPE_MESSAGE, field.TYPE_GROUP]:
                if field.label == field.LABEL_REPEATED:
                    value = [convert.from_proto(field, v) for v in value]
                else:
                    value = convert.from_proto(field, value)

            values.append(value)
        return values

    def items(self):
        items = []
        for (field,value) in self.ListFields():
            if field.type not in [field.TYPE_MESSAGE, field.TYPE_GROUP]:
                if field.label == field.LABEL_REPEATED:
                    value = [convert.from_proto(field, v) for v in value]
                else:
                    value = convert.from_proto(field, value)

            items.append((field.name, value))
        return items

    def iteritems(self):
        for (field,value) in self.ListFields():
            if field.type not in [field.TYPE_MESSAGE, field.TYPE_GROUP]:
                if field.label == field.LABEL_REPEATED:
                    value = [convert.from_proto(field, v) for v in value]
                else:
                    value = convert.from_proto(field, value)

            yield (field.name, value)

    def update(self, obj, msg=None):
        if msg is None:
            msg = self

        for (key,value) in obj.iteritems():
            try:
                if hasattr(value, 'items'):
                    self.update(value, msg[key])
                elif hasattr(value, 'append'):
                    if hasattr(msg[key], 'add'):
                        for v in value:
                            self.update(v, msg[key].add())
                    else:
                        for v in value:
                            msg[key].append(v)
                else:
                    msg[key] = value
            except KeyError as e:
                pass

        return msg

    def json(self, **kwds):
        return json.dumps(self.son(), **kwds)

    def son(self):
        def _empty(message):
            descriptor = message.DESCRIPTOR
            d = self.__dictcls__()
            for f in descriptor.fields:
                if f.name not in message.keys():
                    continue

                try:
                    value = getattr(message, f.name)
                except AttributeError:
                    continue

                if f.message_type:
                    if f.label == f.LABEL_REPEATED:
                        if 0 == len(value):
                            continue
                        d[f.name] = [_empty(v) for v in value]

                    elif value.ListFields():
                        d[f.name] = _empty(value)
                else:
                    if f.type == f.TYPE_BYTES and not f.GetOptions().HasExtension(options_pb2.convert):
                        if f.label == f.LABEL_REPEATED:
                            d[f.name] = [self.__bytecls__(v) for v in value]
                        else:
                            d[f.name] = self.__bytecls__(value)
                    else:
                        if f.label == f.LABEL_REPEATED:
                            d[f.name] = list(value)
                        else:
                            d[f.name] = value
            return d

        obj = _empty(self)
        return obj


from .scalar import Scalar
