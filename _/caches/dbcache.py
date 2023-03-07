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
    _config  = 'config'
    _key_col = 'key'
    _key     = 'cookie'
    _val_col = 'value'

    _table      = 'sessions'
    _session_id = 'session_id'

    async def init(self, name, **kwds):
        self.db = _.database[self._database]

        if not hasattr(_.application, 'is_session_expired'):
            raise _.error('Application does not have is_session_expired function defined')

        await self.db.execute(
            f'''CREATE TABLE IF NOT EXISTS {self._config} (
                {self._key_col} TEXT UNIQUE NOT NULL,
                {self._val_col} TEXT
                )'''
            )

        table = {
            self._session_id : 'TEXT UNIQUE NOT NULL',
        }
        table.update(kwds)
        table.pop('database', None)
        table.pop('table',    None)

        for key,value in table.items():
            if value is None:
                table[key] = 'TEXT NOT NULL'

        rows = ', '.join(f'{k} {v}' for k,v in table.items())
        statement = f'CREATE TABLE IF NOT EXISTS {self._table}({rows})'

        try:
            await self.db.execute(statement)
        except _.error as e:
            logging.error('\n\n%s\n', statement)
            raise

        # interval comes from the [sessions] section of the ini
        _.application.periodic(self._interval, self.clear_stale_sessions)

        kwds = dict(
            name        = name,
            db          = self.db,
            _table      = self._table,
            _session_id = self._session_id,
            )
        self.handler = type(f'{name}_handler', (DbCacheSessions,_.handlers.Protected), kwds)

    async def cookie_secret(self):
        secret = await self.db.find_one(self._config, self._key_col, self._key)
        if secret:
            secret = secret['value']
        else:
            secret = base64.b64encode(os.urandom(32))
            record = {
                self._key_col : self._key,
                self._val_col : secret,
            }
            await self.db.upsert(self._config, self._key_col, record)
        return secret

    async def save_session(self, session):
        super(DbCache, self).save_session(session)
        await self.db.upsert(self._table, self._session_id, session)

    async def load_session(self, session_id):
        record = await self.db.find_one(self._table, self._session_id, session_id)
        if not record:
            return None
        if await _.wait(_.application.is_session_expired(record, self._expires)):
            return None
        return record

    async def clear_stale_sessions(self):
        for record in await self.db.find(self._table):
            if await _.wait(_.application.is_session_expired(record, self._expires)):
                logging.debug('Removing expired session: %s', record[self._session_id])
                await self.db.delete(self._table, self._session_id, record[self._session_id])


class DbCacheSessions(_.handlers.Protected):
    @tornado.web.authenticated
    async def get(self, session_id=None):
        if session_id:
            record = await self.db.find_one(self._table, self._session_id, session_id)
            self.write(record)
        else:
            records = await self.db.find(self._table)
            data = []
            for record in records:
                record = dict(record)
                data.append(record)
            self.write({'data':data})

    @tornado.web.authenticated
    async def delete(self, session_id=None):
        self.set_status(204)
        if session_id:
            await self.db.delete(self._table, self._session_id, session_id)

            callback = getattr(_.application, f'on_{name}_delete', None)
            if callback is None:
                callback = getattr(_.application, 'on_dbcache_delete', None)
            if callback:
                await _.wait(callback(name, record))
