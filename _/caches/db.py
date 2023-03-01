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


class DbCache(_.caches.Cache):
    config  = 'config'
    key_col = 'key'
    key     = 'cookie'
    val_col = 'value'

    table      = 'sessions'
    session_id = 'session_id'

    async def init(self, **kwds):
        print('DB CACHE:', kwds)
        self.db = _.database[self.database]
        print(self.db)

    async def cookie_secret(self):
        secret = await self.db.findOne(self.config, self.key, self.key_col)
        if not secret:
            secret = base64.b64encode(os.urandom(32))
            record = {
                self.key_col : self.key,
                self.val_col : secret,
            }
            await self.db.upsert(self.config, record)
        return secret

    async def save_session(self, session_id, session):
        await self.db.upsert(self.table, session)

    async def load_session(self, session_id):
        session = await self.db.findOne(self.table, session_id, self.session_id)
        return json.loads(session) if session else None
