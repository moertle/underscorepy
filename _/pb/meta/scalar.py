
from .. import convert


class Scalar(object):
    def __init__(self, container, subtype):
        self.container  = container
        self.to_proto   = convert.to_proto.get(subtype)
        self.from_proto = convert.from_proto.get(subtype)

    def __len__(self):
        return self.container.__len__()

    def append(self, value):
        if self.to_proto:
            value = self.to_proto(value)
        self.container.append(value)

    def remove(self, value):
        if self.to_proto:
            value = self.to_proto(value)
        self.container.remove(value)

    def removeall(self):
        for x in xrange(len(self.container)):
            del self.container[0]

    def __getitem__(self, idx):
        value = self.container.__getitem__(idx)
        if self.from_proto:
            value = self.from_proto(value)
        return value

    def __str__(self):
        return self.container.__str__()

    def __repr__(self):
        return self.container.__repr__()
