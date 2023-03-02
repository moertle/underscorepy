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
        self.db = _.database[self.database]

    async def cookie_secret(self):
        secret = await self.db.find_one(self.config, self.key, self.key_col)
        if secret:
            secret = secret['value']
        else:
            secret = base64.b64encode(os.urandom(32))
            record = {
                self.key_col : self.key,
                self.val_col : secret,
            }
            await self.db.upsert(self.config, record)
        return secret

    async def save_session(self, session):
        super(DbCache, self).save_session(session)
        await self.db.upsert(self.table, session)

    async def load_session(self, session_id):
        record = await self.db.find_one(self.table, session_id, self.session_id)
        return record if record else None
