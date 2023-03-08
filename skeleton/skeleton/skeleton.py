
import dataclasses
import logging
import time
import uuid

import _

import skeleton


class Skeleton(_.Application):
    async def initialize(self):
        self.websockets = {}

        self.db = _.database['sqlite']
        self.data = _.record['data']

        audio = _.dataclasses['Audio'](device='cool',frequency=48000,bits=16,samples=2048)
        json = audio.dump()
        audio = _.dataclasses['Audio'].load(json)

        s = _.protobufs['Skeleton']()
        s.field1 = 'matt'
        s.field2 = 'shaw'
        json = s.dump()
        s2 = _.protobufs['Skeleton'].load(json)

        self.patterns = [
            ( r'/ws',       skeleton.handlers.Socket, { 'websockets' : self.websockets } ),
            ( r'/([a-z]*)', _.handlers.Protected ),
            ]

        #self.status_task  = self.periodic(10, self.status)
        #self.status_task.cancel()

    async def status(self):
        logging.info('Periodic: %s', time.ctime())

    async def on_dblogin_add_user(self, name, record):
        'make adjustments to the record before calling sql statement'
        record['disabled'] = False
        record['isadmin']  = True
        record['created']  = _.now()

    async def on_dblogin_update(self, handler, name, record):
        'allow apps to make adjustments to the record before calling sql statement'
        print(name)
        print(record)

    async def on_gitlab_login(self, handler, user):
        session = {
            'session_id' : str(uuid.uuid4()),
            'username'   : user['username'],
            'agent'      : handler.request.headers.get('User-Agent', ''),
            'ip'         : handler.request.remote_ip,
            'time'       : _.now(),
            }
        return session

    async def on_login(self, handler, user):
        user['last'] = int(time.time() * 1000)
        await self.db.update('users', 'username', user)

        session = {
            'session_id' : str(uuid.uuid4()),
            'username'   : user['username'],
            'agent'      : handler.request.headers.get('User-Agent', ''),
            'ip'         : handler.request.remote_ip,
            'time'       : _.now(),
            }
        return session

    async def is_session_expired(self, session, expires):
        created = session['time'] / 1000
        elapsed = (time.time() - created) / 3600
        return elapsed > expires
