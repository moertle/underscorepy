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
import typing

import sqlalchemy

import _
import _.records

class DbCache(_.caches.Cache):
    _config  = 'config'
    _key_col = 'key'
    _val_col = 'value'
    _key     = 'cookie'

    _table       = 'sessions'
    _session_col = 'session_id'

    async def init(self, component_name, database=None, **kwds):
        if not hasattr(_.application, 'is_session_expired'):
            raise _.error('Application does not have is_session_expired function defined')

        if database is None:
            if 1 == len(_.databases):
                database = list(_.databases.keys())[0]
            else:
                raise _.error('dbcache requires a database to be specified')
        self.db = _.databases[database]

        self.config_table = type(self._config, (_.records.RecordsInterface,self.db.Base,), {
            '__tablename__'   : self._config,
            '__annotations__' : {
                self._key_col : str,
                self._val_col : typing.Optional[str],
                },
            '__primary_key__' : self._key_col,
            self._key_col : sqlalchemy.orm.mapped_column(primary_key=True, init=False),
            self._val_col : sqlalchemy.orm.mapped_column(init=False),
            })

        annotations = {
            self._session_col : str,
            }
        # create the session table
        columns = {
            '__tablename__'   : self._table,
            '__annotations__' : annotations,
            '__primary_key__' : self._session_col,
            self._session_col : sqlalchemy.orm.mapped_column(primary_key=True, init=False),
            }
        for col,dbtype in kwds.items():
            if not dbtype:
                dbtype = 'str'
            annotations[col] = typing.Optional[__builtins__.get(dbtype)]
            columns[col] = sqlalchemy.orm.mapped_column(init=False)

        self.session_table = type(self._table, (_.records.RecordsInterface, self.db.Base,), columns)

        await self.db.create_tables()

        # interval comes from the [sessions] section of the ini
        _.application.periodic(self._interval, self.clear_stale_sessions)

        members = dict(
            component  = component_name,
            db         = self.db,
            cls        = self.session_table,
            table      = self._table,
            session_id = self._session_col,
            )
        subclass = type('Sessions', (Sessions,), _.prefix(members))
        _.application._record_handler('sessions', subclass)

    async def cookie_secret(self):
        # try to load exisiting cookie secret and return it
        secret = await self.db.find_one(self.config_table, self._key)
        if secret:
            secret = secret[self._val_col]
        else:
            # otherwise generate and store the cookie secret
            secret = base64.b64encode(os.urandom(32)).decode('ascii')
            config = self.config_table()
            config(**{self._key_col : self._key, self._val_col : secret})
            await self.db.upsert(config)
        return secret

    async def save_session(self, session):
        session = self.session_table._from_dict(**session)
        await self.db.upsert(session)

    async def load_session(self, session_id):
        session = await self.db.find_one(self.session_table, session_id)
        if not session:
            return None
        if await _.wait(_.application.is_session_expired(session, self._expires)):
            return None
        return session

    async def clear_session(self, session_id):
        session = await self.db.find_one(self.session_table, session_id)
        if session:
            await self.db.delete(session)

    async def clear_stale_sessions(self):
        for record in await self.db.find(self.session_table):
            if await _.wait(_.application.is_session_expired(record, self._expires)):
                logging.debug('Removing expired session: %s', record[self._session_col])
                await self.db.delete(record)


class Sessions(_.handlers.Protected):
    @_.auth.protected
    async def get(self, session_id=None):
        if session_id:
            record = await self._db.find_one(self._cls, session_id)
            self.write(record._as_dict())
        else:
            records = await self._db.find(self._cls)
            data = [r._as_dict() for r in records]
            self.write({'data':data})

    @_.auth.protected
    async def delete(self, session_id=None):
        if session_id:
            await self._db.delete(self._cls, session_id)

            callback = getattr(_.application, f'on_{self._component}_delete', None)
            if callback is None:
                callback = getattr(_.application, 'on_dbcache_delete', None)
            if callback:
                await _.wait(callback(self._component, session_id))
        self.set_status(204)
