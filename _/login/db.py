#
# (c) 2015-2023 Matthew Shaw
#
# Authors
# =======
# Matthew Shaw <mshaw.cx@gmail.com>
#


import base64
import hashlib
import logging
import os
import time

import tornado.web

import _


class Db(_.login.Login):
    table    = 'users'
    username = 'username'
    password = 'password'

    @classmethod
    async def check(cls, username, password):
        if password:
            password = _.auth.simple_hash(username + password)

        try:
            instance = _.component.database[cls.database]
        except KeyError:
            raise tornado.web.HTTPError(500, f'database "{cls.database}" not defined in ini file')
        except AttributeError:
            raise tornado.web.HTTPError(500, 'database not specified in ini file')

        try:
            record = await instance.findOne(cls.table, username, cls.username)
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
            return

        await self.application.onLogin(self, user)

        self.redirect(next_url)
