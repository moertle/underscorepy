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


class Db(_.logins.Login):
    table    = 'users'
    username = 'username'
    password = 'password'

    @classmethod
    async def load(cls, name):
        _.argparser.add_argument(f'--{name}-add-user',
            metavar='<arg>', nargs=2,
            help='create or update user with password'
            )

        _.argparser.add_argument(f'--{name}-list-users',
            action='store_true',
            help='list users'
            )

    @classmethod
    async def args(cls, name):
        db = _.database[cls.database]

        add_user = getattr(_.args, f'{name}_add_user')
        if add_user:
            username,password = add_user
            password = _.auth.simple_hash(username + password)

            record = dict(_.config[name])
            record.pop('database', None)
            record.pop('table',    None)

            record[cls.username] = username
            record[cls.password] = password
            await db.upsert(cls.table, record)
            _.stop.set()

        if getattr(_.args, f'{name}_list_users'):
            for user in await db.find(cls.table):
                print(user[cls.username])
            _.stop.set()

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
            record = await db.findOne(cls.table, username, cls.username)
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

    async def post(self):
        username = self.get_argument('username', None)
        password = self.get_argument('password', None)
        next_url = self.get_argument('next', '/')

        if username is None or password is None:
            raise tornado.web.HTTPError(500)

        user = await self.check(username, password)
        if user is None:
            self.clear_cookie('session_id')
            self.render('login.html', message='Invalid Login', next_url=next_url)
        else:
            await self.application.on_login(self, user)
            self.redirect(next_url)
