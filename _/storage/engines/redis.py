from __future__ import absolute_import

import sys
import logging

import tornado.ioloop
import tornado.gen

import _.storage

from . import Storage

try:
    import redis
except ImportError:
    raise _.error('Missing redis module')


class Redis(Storage):
    def __init__(self, **kwds):
        if 'port' in kwds:
            kwds['port'] = int(kwds['port'])

        if 'db' in kwds:
            kwds['db'] = int(kwds['db'])

        self.redis = redis.StrictRedis(**kwds)
        # ping the server to validate connection params
        self.redis.ping()

    def __call__(self):
        return self.redis
