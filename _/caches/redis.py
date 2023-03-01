#
# (c) 2015-2023 Matthew Shaw
#
# Authors
# =======
# Matthew Shaw <mshaw.cx@gmail.com>
#

import base64
import json
import os

import _

try:
    import redis.asyncio as redis
except ImportError:
    raise _.error('Missing redis module')


class Redis(_.caches.Cache):
    async def init(self, **kwds):
        if 'socket_connect_timeout' not in kwds:
            kwds['socket_connect_timeout'] = 3

        if 'socket_timeout' not in kwds:
            kwds['socket_timeout'] = 3

        self.connection = redis.Redis(**kwds)
        await self.connection.ping()

    async def close(self):
        await self.connection.close()
        self.connection = None

    async def cookie_secret(self):
        secret = await self.connection.get('cookie_secret')
        if not secret:
            secret = base64.b64encode(os.urandom(32))
            await self.connection.set('cookie_secret', secret)
        return secret

    async def save_session(self, session):
        session_id = super(DbCache, self).save_session(session)
        async with self.connection.pipeline(transaction=True) as pipe:
            await pipe.set(f'session/{session_id}', json.dumps(session))
            await pipe.expire(f'session/{session_id}', 86400)
            await pipe.execute()

    async def load_session(self, session_id):
        session = await self.connection.get(f'session/{session_id}')
        if not session:
            return None
        return json.loads(session)

    # fall through for calling redis functions directly
    def __getattr__(self, attr):
        return getattr(self.connection, attr)
