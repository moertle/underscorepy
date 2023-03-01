#!/usr/bin/env python3

import functools
import json
import logging
import sys
import time
import uuid

sys.path.insert(0, '..')

import _.auth
import _.websockets


class TestSocket(_.websockets.Base):
    def on_message(self, msg):
        print(msg)
        self.write_message('greetings from _.py')


class ProtectedSocket(_.websockets.Protected):
    def on_message(self, msg):
        print(msg)
        self.write_message('greetings from protected _.py')


class TestBasicAuth(_.handlers.Template):
    @_.auth.basic('Test')
    def get(self):
        self.write('Hello TestBasicAuth')


class TestApp(_.Application):
    async def initialize(self):
        self.websockets = {}
        self.accounts = _.database['accounts']
        self.redis    = _.cache['redis']
        self.mem      = _.cache['memory']

        self.patterns = [
            (r'/basic',       TestBasicAuth),
            (r'/pws',         ProtectedSocket, {'websockets':self.websockets}),
            (r'/ws',          TestSocket,      {'websockets':self.websockets}),
            (r'/(protected)', _.handlers.Protected),
            (r'/',            _.handlers.Template),
            ]

        self.cb_count = 3
        self.status_cb  = self.periodic(2, self.status)

    async def status(self):
        logging.info('Periodic: %s', time.ctime())
        self.cb_count -= 1
        if not self.cb_count:
            self.status_cb.cancel()
            logging.info('Cancelling periodic callback')

    async def cookie_secret(self):
        # the cache modules should provide a sane cookie secret
        # this is here to illustrate how to provide a custom one if need be
        return b'testcookiesecret'

    async def on_login(self, handler, user):
        user['last'] = int(time.time() * 1000)
        await self.accounts.update('users', user, 'username')
        session_id = str(uuid.uuid4())
        session = {
            'id'       : session_id,
            'username' : user['username'],
            'agent'    : handler.request.headers.get('User-Agent', ''),
            'ip'       : handler.request.remote_ip,
            'time'     : int(time.time() * 1000),
            }

        print('onLogin', session_id, session)
        await self.sessions.save_session(session_id, session)
        handler.set_secure_cookie('session_id', session_id, expires_days=1)


if '__main__' == __name__:
    TestApp()
