#
# (c) 2015-2023 Matthew Shaw
#
# Authors
# =======
# Matthew Shaw <mshaw.cx@gmail.com>
#

import logging

import tornado.web

import _


class DbLogin(_.logins.Login):
    _table    = 'users'
    _username = 'username'
    _password = 'password'

    @classmethod
    async def init(cls, name):
        try:
            db = _.database[cls._database]
        except AttributeError:
            raise _.error('No database specified for %s', name)

        # if only one login specified use short argument
        prefix = f'{name}-' if len(_.config['logins']) > 1 else ''

        _.argparser.add_argument(f'--{prefix}add-user',
            metavar='<arg>', nargs=2,
            help='create or update user with password'
            )

        _.argparser.add_argument(f'--{prefix}list-users',
            action='store_true',
            help='list users'
            )

        kwds = dict(_.config[name])
        table = {
            cls._username: 'TEXT UNIQUE NOT NULL',
            cls._password: 'TEXT NOT NULL',

        }
        table.update(kwds)
        table.pop('database', None)
        table.pop('table',    None)
        table.pop('defaults', None)

        for key,value in table.items():
            if value is None:
                table[key] = 'TEXT NOT NULL'

        rows = ', '.join(f'{k} {v}' for k,v in table.items())
        statement = f'CREATE TABLE IF NOT EXISTS {cls._table}({rows})'
        try:
            await db.execute(statement)
        except _.error as e:
            logging.error('\n\n%s\n', statement)
            raise

        kwds = {
            'name'     : name,
            'database' : cls._database,
            'table'    : cls._table,
            'username' : cls._username,
            'password' : cls._password,
        }
        cls.handler = type(f'{name}_handler', (DBLoginRecords,_.handlers.Protected), kwds)

    @classmethod
    async def args(cls, name):
        try:
            db = _.database[cls._database]
        except AttributeError:
            raise _.error('No database specified for %s', name)

        # if only one login specified use short argument
        prefix = f'{name}_' if len(_.config['logins']) > 1 else ''

        add_user = getattr(_.args, f'{prefix}add_user')
        if add_user:
            username,password = add_user
            password = _.auth.simple_hash(username + password)

            record = dict((k,None) for k in _.config[name])
            record.pop('database', None)
            record.pop('table',    None)

            record[cls._username] = username
            record[cls._password] = password

            callback = getattr(_.application, f'on_{name}_add_user', None)
            if callback is None:
                callback = getattr(_.application, 'on_dblogin_add_user', None)
            if callback:
                await _.wait(callback(name, record))

            await db.upsert(cls._table, cls._username, record)
            _.application.stop()

        if getattr(_.args, f'{prefix}list_users'):
            for user in await db.find(cls._table):
                print(user[cls._username])
            _.application.stop()

    @classmethod
    async def check(cls, username, password):
        if password:
            password = _.auth.simple_hash(username + password)

        try:
            db = _.database[cls._database]
        except KeyError:
            raise tornado.web.HTTPError(500, f'database "{cls._database}" not defined in ini file')
        except AttributeError:
            raise tornado.web.HTTPError(500, 'database not specified in ini file')

        try:
            record = await db.find_one(cls._table, cls._username, username)
        except _.error as e:
            logging.warning('%s', e)
            record = None

        if record is None:
            logging.warning('No user: %s', username)
            return None

        if password != record.get(cls._password, '!'):
            logging.warning('Bad password: %s', username)
            return None

        record.pop(cls._password)
        return record

    async def post(self, name):
        username = self.get_argument('username', None)
        password = self.get_argument('password', None)

        if username is None or password is None:
            raise tornado.web.HTTPError(500)

        user = await self.check(username, password)
        if user:
            await self.on_login_success(user)
        else:
            await self.on_login_failure()


class DBLoginRecords(_.handlers.Protected):
    async def prepare(self):
        await _.handlers.Protected.prepare(self)
        try:
            self.db = _.database[self.database]
        except KeyError:
            raise tornado.web.HTTPError(500, f'database "{self.database}" not defined in ini file')
        except AttributeError:
            raise tornado.web.HTTPError(500, 'database not specified in ini file')

    # READ
    @tornado.web.authenticated
    async def get(self, username=None):
        if username:
            record = await self.db.find_one(self.table, self.username, username)
            record.pop(self.password, None)
            self.write(record)
        else:
            records = await self.db.find(self.table)
            data = []
            for record in records:
                record = dict(record)
                record.pop(self.password, None)
                data.append(record)
            self.write({'data':data})

    # UPDATE
    @tornado.web.authenticated
    async def put(self, username=None):
        try:
            user = json.loads(self.request.body)
        except json.decoder.JSONDecodeError:
            raise tornado.web.HTTPError(500)

        username = user.get(self.username, None)
        password = user.get(self.password, None)
        if not username or not password:
            raise tornado.web.HTTPError(500)

        record = dict((k,None) for k in _.config[self.name])
        record.pop('database', None)
        record.pop('table',    None)
        record.update(user)

        callback = getattr(_.application, f'on_{self.name}_update', None)
        if callback is None:
            callback = getattr(_.application, 'on_dblogin_update', None)
        if callback:
            await _.wait(callback(self.name, record))

        if record[self.password] == password:
            password = _.auth.simple_hash(username + password)
            record[self.password] = password

        await self.db.insert(self.table, self.username, record)
        self.set_status(204)

    # DELETE
    @tornado.web.authenticated
    async def delete(self, username=None):
        self.set_status(204)
        await self.db.delete(self.table, self.username, username)

        callback = getattr(_.application, f'on_{self.name}_delete', None)
        if callback is None:
            callback = getattr(_.application, 'on_dblogin_delete', None)
        if callback:
            await _.wait(callback(self, self.name, username))
