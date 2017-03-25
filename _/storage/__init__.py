
from .records import *

from . import engines

class Instances(object):
    def __getitem__(self, name):
        try:
            return getattr(self, name)
        except AttributeError:
            raise KeyError

    def __setitem__(self, name, value):
        setattr(self, name, value)

instances = Instances()
