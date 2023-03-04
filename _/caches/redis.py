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

import tornado.web

import _

try:
    import redis.asyncio as redis
except ImportError:
    raise _.error('Missing redis module')


class Redis(_.caches.Cache):
    async def init(self, name, **kwds):
        if 'socket_connect_timeout' not in kwds:
            kwds['socket_connect_timeout'] = 3

        if 'socket_timeout' not in kwds:
            kwds['socket_timeout'] = 3

        self.connection = redis.Redis(**kwds)
        await self.connection.ping()

        kwds = {
            'name' : name,
        }
        self.handler = type(f'{name}_handler', (RedisSessionRecords,_.handlers.Protected), kwds)

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
        session_id = super(Redis, self).save_session(session)
        async with self.connection.pipeline(transaction=True) as pipe:
            await pipe.set(f'session/{session_id}', json.dumps(session))
            await pipe.expire(f'session/{session_id}', self.expires * 3600)
            await pipe.execute()

    async def load_session(self, session_id):
        session = await self.connection.get(f'session/{session_id}')
        if not session:
            return None
        return json.loads(session)

    # fall through for calling redis functions directly
    def __getattr__(self, attr):
        return getattr(self.connection, attr)


class RedisSessionRecords(_.handlers.Protected):
    @tornado.web.authenticated
    async def get(self, session_id=None):
        if session_id:
            session = await self.redis.get(f'session/{session_id}')
            if not session:
                raise tornado.web.HTTPError(404)
            session = json.loads(session)
            self.write(session)
        else:
            data = []
            session_ids = await self.redis.keys('session/*')
            for session_id in session_ids:
                session = await self.redis.get(session_id)
                data.append(json.loads(session))
            data.sort(key=lambda d: d['time'])
            self.write({'data':data})
        self.finish()

    @tornado.web.authenticated
    async def post(self):
        try:
            status = json.loads(self.request.body)
        except json.decoder.JSONDecodeError:
            raise tornado.web.HTTPError(500)
        self.set_status(204)

        callback = getattr(_.application, f'on_{name}_update', None)
        if callback is None:
            callback = getattr(_.application, 'on_redis_update', None)
        if callback:
            await _.wait(callback(name, record))

    @tornado.web.authenticated
    async def delete(self, session_id=None):
        self.set_status(204)
        if session_id:
            await self.redis.delete('session/' + session_id)
            callback = getattr(_.application, f'on_{name}_delete', None)
            if callback is None:
                callback = getattr(_.application, 'on_redis_delete', None)
            if callback:
                await _.wait(callback(name, record))
