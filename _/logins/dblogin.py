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
    table    = 'users'
    username = 'username'
    password = 'password'

    @classmethod
    async def init(cls, name):
        _.argparser.add_argument(f'--{name}-add-user',
            metavar='<arg>', nargs=2,
            help='create or update user with password'
            )

        _.argparser.add_argument(f'--{name}-list-users',
            action='store_true',
            help='list users'
            )

        kwds = {
            'name'     : name,
            'database' : cls.database,
            'table'    : cls.table,
            'username' : cls.username,
            'password' : cls.password,
        }
        cls.handler = type(f'{name}_handler', (DBLoginRecords,_.handlers.Protected), kwds)

    @classmethod
    async def args(cls, name):
        try:
            db = _.database[cls.database]
        except AttributeError:
            raise _.error('No database specified for %s', name)

        add_user = getattr(_.args, f'{name}_add_user')
        if add_user:
            username,password = add_user
            password = _.auth.simple_hash(username + password)

            record = dict(_.config[name])
            record.pop('database', None)
            record.pop('table',    None)

            record[cls.username] = username
            record[cls.password] = password

            callback = getattr(_.application, f'on_{name}_update', None)
            if callback is None:
                callback = getattr(_.application, 'on_dblogin_update', None)
            if callback:
                await _.wait(callback(None, name, record))

            await db.upsert(cls.table, record)
            _.application.stop()

        if getattr(_.args, f'{name}_list_users'):
            for user in await db.find(cls.table):
                print(user[cls.username])
            _.application.stop()

    @classmethod
    async def check(cls, username, password):
        if password:
            password = _.auth.simple_hash(username + password)

        try:
            db = _.database[cls.database]
        except KeyError:
            raise tornado.web.HTTPError(500, f'database "{cls.database}" not defined in ini file')
        except AttributeError:
            raise tornado.web.HTTPError(500, 'database not specified in ini file')

        try:
            record = await db.find_one(cls.table, username, cls.username)
        except _.error as e:
            logging.warning('%s', e)
            record = None

        if record is None:
            logging.warning('No user: %s', username)
            return None

        if password != record.get(cls.password, '!'):
            logging.warning('Bad password: %s', username)
            return None

        record.pop(cls.password)
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
    async def get(self, name, username=None):
        if username:
            record = await self.db.find_one(self.table, username, self.username)
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
    async def put(self, name, username=None):
        try:
            user = json.loads(self.request.body)
        except json.decoder.JSONDecodeError:
            raise tornado.web.HTTPError(500)

        username = user.get(self.username)
        password = user.get(self.password)
        if not username or not password:
            raise tornado.web.HTTPError(500)

        record = dict(_.config[name])
        record.pop('database', None)
        record.pop('table',    None)
        record.update(user)
        record[self.username] = username
        record[self.password] = password

        callback = getattr(_.application, f'on_{name}_update', None)
        if callback is None:
            callback = getattr(_.application, 'on_dblogin_update', None)
        if callback:
            await _.wait(callback(self, name, record))

        if record[self.password] == password:
            password = _.auth.simple_hash(username + password)
            record[self.password] = password

        await self.db.insert(self.table, record, self.username)
        self.set_status(204)

    # DELETE
    @tornado.web.authenticated
    async def delete(self, name, username=None):
        self.set_status(204)
        await self.db.delete(self.table, username, self.username)

        callback = getattr(_.application, f'on_{name}_delete', None)
        if callback is None:
            callback = getattr(_.application, 'on_dblogin_delete', None)
        if callback:
            await _.wait(callback(self, name, username))
