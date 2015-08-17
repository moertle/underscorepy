
import sys
import os

import _.py


class Paths(object):
    def __init__(self, **kwds):
        for k,v in kwds.iteritems():
            setattr(self, k, v)

    #def __getattr__(self, attribute):
    #    try:
    #        return object.__getattribute__(self, attribute)
    #    except AttributeError:
    #        return os.path.join(_.py.prefix, attribute, _.py.namespace)

    def __call__(self, toplevel, *args):
        return os.path.join(self.prefix, toplevel, self.namespace, *args)
