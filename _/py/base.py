

class Base(object):
    def __init__(self, **kwds):
        for key,value in kwds.iteritems():
            setattr(self, key, value)
