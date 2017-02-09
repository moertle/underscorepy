
import abc
import collections
import os
import sys

from google.protobuf.message    import Message
from google.protobuf.reflection import GeneratedProtocolMessageType

import _.pb

from . import convert
from . import options_pb2
from . import storage_pb2

from .meta import Pb


class AbstractPb(GeneratedProtocolMessageType, abc.ABCMeta):
    'Allow the mixing on Messages and Pb'


def wrap(module, wrapper=Pb):
    for name in module.DESCRIPTOR.message_types_by_name:
        msg = getattr(module, name)
        yield wrap_descriptor(msg.DESCRIPTOR, wrapper)


def wrap_descriptor(descriptor, wrapper=Pb):
    dct = {
        'DESCRIPTOR' : descriptor,
        'MESSAGE'    : _iterate(descriptor, wrapper),
    }

    return AbstractPb(descriptor.name, (Message,wrapper), dct)


def load(modroot, wrapper=Pb):
    messages = collections.OrderedDict()

    root = os.path.dirname(modroot.__file__)

    sys.path.insert(0, root)

    for base,diretories,filenames in os.walk(root):
        base = base[len(root)+1:]

        for filename in filenames:
            if not filename.endswith('_pb2.py'):
                continue

            path = os.path.join(base, filename)[:-3]
            path = path.replace(os.path.sep, '.')

            module = __import__(path)
            for attr in path.split('.')[1:]:
                module = getattr(module, attr)

            options = module.DESCRIPTOR.GetOptions()
            version = options.Extensions[options_pb2.version] or None
            project = options.Extensions[options_pb2.project] or None

            for message in _.pb.wrap(module, wrapper):
                if version:
                    message.VERSION = version

                if project:
                    message.PROJECT = project

                path =  message.DESCRIPTOR.full_name.rsplit('.',1)
                if len(path) > 1:
                    path,name = path[0],path[1]
                    messages[path + '.' + name] = message
                    setattr(modroot, name, message)
                else:
                    name = path[0]
                    messages[name] = message
                    setattr(modroot, name, message)

    del sys.path[0]
    return messages


def _iterate(descriptor, wrapper=Pb):
    options = descriptor.GetOptions()

    d = wrapper.__dictcls__()
    d['name']      = descriptor.name
    d['full_name'] = descriptor.full_name.replace('.', '_')

    if options.HasExtension(options_pb2.display):
        d['display'] = str(options.Extensions[options_pb2.display])

    if options.HasExtension(options_pb2.msg_type):
        d['msg_type'] = str(options.Extensions[options_pb2.msg_type])

    if options.HasExtension(storage_pb2.table):
        d['table'] = options.Extensions[storage_pb2.table]

    fkey = options.Extensions[storage_pb2.fkey]
    if fkey:
        d['fkey'] = [str(f) for f in fkey]

    d['fields'] = wrapper.__dictcls__()
    for field in descriptor.fields:
        f = d['fields'][field.name] = wrapper.__dictcls__()

        f['name'] = field.name
        f['type'] = field.type

        if field.label is field.LABEL_REQUIRED:
            f['required'] = True
        elif field.label is field.LABEL_REPEATED:
            f['repeated'] = True

        options = field.GetOptions()
        if options.HasExtension(options_pb2.label):
            f['label'] = str(options.Extensions[options_pb2.label])
        if options.HasExtension(options_pb2.hidden):
            f['hidden'] = options.Extensions[options_pb2.hidden]
        if options.HasExtension(options_pb2.convert):
            f['convert'] = str(options.Extensions[options_pb2.convert])

        if field.has_default_value:
            convert = f.get('convert', None)
            if convert:
                f['default'] = from_proto(f.get('convert', None), field.default_value)
            else:
                f['default'] = field.default_value

        if field.type is field.TYPE_MESSAGE:
            if field.message_type.full_name == descriptor.full_name:
                f['recursive'] = True
            else:
                wrap_descriptor(field.message_type, wrapper)
                f['msg'] = _iterate(field.message_type)

    return d
