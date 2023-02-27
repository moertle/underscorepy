#
# (c) 2015-2023 Matthew Shaw
#
# Authors
# =======
# Matthew Shaw <mshaw.cx@gmail.com>
#

import _

try:
    import redis.asyncio as redis
except ImportError:
    raise _.error('Missing redis module')


class Redis(_.cache.Cache):
    async def init(self, **kwds):
        if 'socket_connect_timeout' not in kwds:
            kwds['socket_connect_timeout'] = 3

        if 'socket_timeout' not in kwds:
            kwds['socket_timeout'] = 3

        self.redis = redis.Redis(**kwds)
        await self.redis.ping()

    def __getattr__(self, attr):
        return getattr(self.redis, attr)
