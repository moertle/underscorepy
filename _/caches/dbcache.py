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

import tornado.web

import _


class DbCache(_.caches.Cache):
    config  = 'config'
    key_col = 'key'
    key     = 'cookie'
    val_col = 'value'

    table      = 'sessions'
    session_id = 'session_id'

    async def init(self, name, **kwds):
        self.db = _.database[self.database]

        if not hasattr(_.application, 'is_session_expired'):
            raise _.error('Application does not have is_session_expired function defined')

        await self.db.execute(
            f'''CREATE TABLE IF NOT EXISTS {self.config} (
                {self.key_col} TEXT UNIQUE NOT NULL,
                {self.val_col} TEXT
                )'''
            )

        table = {
            self.session_id : 'TEXT UNIQUE NOT NULL',
        }
        table.update(kwds)
        table.pop('database', None)
        table.pop('table',    None)

        for key,value in table.items():
            if value is None:
                table[key] = 'TEXT NOT NULL'

        rows = ', '.join(f'{k} {v}' for k,v in table.items())
        statement = f'CREATE TABLE IF NOT EXISTS {self.table}({rows})'

        try:
            await self.db.execute(statement)
        except _.error as e:
            logging.error('\n\n%s\n', statement)
            raise

        # interval comes from the [sessions] section of the ini
        _.application.periodic(self.interval, self.clear)

        kwds = dict(
            name       = name,
            db         = self.db,
            table      = self.table,
            session_id = self.session_id,
            )
        self.handler = type(f'{name}_handler', (DbCacheSessions,_.handlers.Protected), kwds)

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
                logging.debug('Removing expired session: %s', record[self.session_id])
                await self.db.delete(self.table, record[self.session_id], self.session_id)


class DbCacheSessions(_.handlers.Protected):
    @tornado.web.authenticated
    async def get(self, session_id=None):
        if session_id:
            record = await self.db.find_one(self.table, session_id, self.session_id)
            self.write(record)
        else:
            records = await self.db.find(self.table)
            data = []
            for record in records:
                record = dict(record)
                data.append(record)
            self.write({'data':data})

    @tornado.web.authenticated
    async def delete(self, session_id=None):
        self.set_status(204)
        if session_id:
            await self.db.delete(self.table, session_id, self.session_id)

            callback = getattr(_.application, f'on_{name}_delete', None)
            if callback is None:
                callback = getattr(_.application, 'on_dbcache_delete', None)
            if callback:
                await _.wait(callback(name, record))
