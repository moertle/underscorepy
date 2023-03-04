#
# (c) 2015-2023 Matthew Shaw
#
# Authors
# =======
# Matthew Shaw <mshaw.cx@gmail.com>
#

import base64
import json
import logging
import os

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
        # interval comes from the [sessions] section of the ini
        _.application.periodic(self.interval, self.clear)

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
        if not record:
            return None
        if await _.wait(_.application.is_session_expired(record, self.expires)):
            return None
        return record

    async def clear(self):
        records = await self.db.find(self.table)
        for record in records:
            if await _.wait(_.application.is_session_expired(record, self.expires)):
                logging.debug('Removing expired session: %s', record['session_id'])
                await self.db.delete(self.table, record['session_id'], 'session_id')
