
import abc
import collections
import json

import bson
import bson.json_util

import _.pb

_.pb.convert.to_proto.set   ( 'oid', lambda v: str(v)           )
_.pb.convert.from_proto.set ( 'oid', lambda v: bson.ObjectId(v) )


class MongoPb(_.pb.meta.Pb):
    _id = None

    __dictcls__ = bson.SON
    __bytecls__ = staticmethod(bson.Binary)

    def __getitem__(self, name):
        if name == '_id':
            return self._id
        return super(MongoPb, self).__getitem__(name)

    # attribute interface; wraps sub-messages in Pb class
    def __getattribute__(self, name):
        if name == '_id':
            return object.__getattribute__(self, '_id')
        return super(MongoPb, self).__getattribute__(name)

    def __setattr__(self, name, attr):
        if name == '_id':
            return object.__setattr__(self, name, attr)

        if name.startswith('_MongoPb__'):
            return object.__setattr__(self, name, attr)

        return super(MongoPb, self).__setattr__(name, attr)

    def __delitem__(self, name):
        if name == '_id':
            self._id = None
        return super(MongoPb, self).__delitem__(name)

    def __contains__(self, name):
        if name == '_id':
            return self._id != None
        return super(MongoPb, self).__contains__(name)

    def __iter__(self):
        if self._id is not None:
            yield '_id'
        yield super(MongoPb, self).__iter__()

    def keys(self):
        keys = super(MongoPb, self).keys()
        if self._id != None:
            keys.insert(0, '_id')
        return keys

    def values(self):
        values = super(MongoPb, self).values()
        if self._id != None:
            values.insert(0, self._id)
        return values

    def items(self):
        items = super(MongoPb, self).items()
        if self._id != None:
            items.insert(0, ('_id',self._id))
        return items

    def iteritems(self):
        if self._id != None:
            yield ('_id', self._id)
        yield super(MongoPb, self).iteritems()

    def update(self, obj, msg=None):
        reinsert = False
        tmp_id = None
        if '_id' in obj:
            self._id = obj['_id']
            del obj['_id']
            reinsert = True
        try:
            return super(MongoPb, self).update(obj, msg)
        finally:
            if reinsert:
                obj['_id'] = self._id

    def json(self, **kwds):
        return bson.json_util.dumps(self.son(), **kwds)

    @classmethod
    def load_json(cls, obj):
        return cls().update(json.loads(obj, object_hook=bson.json_util.object_hook))
