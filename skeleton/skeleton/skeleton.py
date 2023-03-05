
import logging
import time
import uuid

import _

from . import handlers

class SkeletonSocket(_.websockets.Protected):
    def on_message(self, msg):
        logging.info('websocket: %s', msg)
        self.write_message(msg)


class Skeleton(_.Application):
    async def initialize(self):
        self.websockets = {}

        self.db = _.database['sqlite']

        self.patterns = [
            ( r'/records/users/([a-z]*)',    handlers.Users ),
            ( r'/records/([a-z]+)/([a-z]*)', handlers.Records ),
            ( r'/ws',       SkeletonSocket, { 'websockets' : self.websockets } ),
            ( r'/([a-z]*)', _.handlers.Protected ),
            ]

        self.status_task  = self.periodic(10, self.status)
        #self.status_task.cancel()

    async def status(self):
        logging.info('Periodic: %s', time.ctime())

    async def on_dblogin_update(self, handler, name, record):
        'allow apps to make adjustments to the record before calling sql statement'
        print(name, record)

    async def on_login(self, handler, user):
        session = {
            'session_id' : str(uuid.uuid4()),
            'username'   : user['username'],
            'agent'      : handler.request.headers.get('User-Agent', ''),
            'ip'         : handler.request.remote_ip,
            'time'       : int(time.time() * 1000),
            }
        return session

    async def is_session_expired(self, session, expires):
        created = session['time'] / 1000
        elapsed = (time.time() - created) / 3600
        return elapsed > expires
