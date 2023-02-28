#
# (c) 2015-2023 Matthew Shaw
#
# Authors
# =======
# Matthew Shaw <mshaw.cx@gmail.com>
#

import os
import base64
import json

import _


class Db(_.caches.Cache):
    config  = 'config'
    key_col = 'key'
    key     = 'cookie'
    val_col = 'value'

    table      = 'sessions'
    session_id = 'session_id'

    async def init(self, **kwds):
        print('DB CACHE:', kwds)

    async def cookie_secret(self):
        secret = await db.findOne(cls.config, cls.key, cls.key_col)
        if not secret:
            secret = base64.b64encode(os.urandom(32))
            record = {
                cls.key_col : cls.key,
                cls.val_col : secret,
            }
            await db.upsert(cls.config, record)
        return secret

    async def save_session(self, session_id, session):
        await db.upsert(cls.table, session)

    async def load_session(self, session_id):
        session = await db.findOne(cls.table, session_id, cls.session_id)
        return json.loads(session) if session else None
