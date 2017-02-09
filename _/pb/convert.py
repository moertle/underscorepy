
from . import options_pb2


def access(decorated):
    '''
    Decorator to add pseudo-member functions to non-class functions
    '''

    decorated.converters = {}

    def setter(converter, fn):
        decorated.converters[converter] = fn

    def getter(converter):
        return decorated.converters.get(converter, None)

    decorated.set = setter
    decorated.get = getter

    return decorated


@access
def from_proto(field, value):
    transform = from_proto.get(field.GetOptions().Extensions[options_pb2.convert])
    return transform(value) if transform else value


@access
def to_proto(field, value):
    transform = to_proto.get(field.GetOptions().Extensions[options_pb2.convert])
    return transform(value) if transform else value
