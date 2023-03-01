
import logging
import time

import _


class SkeletonSocket(_.websockets.Protected):
    def on_message(self, msg):
        logging.info('websocket: %s', msg)
        self.write_message(msg)


class Skeleton(_.Application):
    async def initialize(self):
        self.websockets = {}
        self.db    = _.database['sqlite']

        self.patterns = [
            (r'/ws',       SkeletonSocket, {'websockets':self.websockets}),
            (r'/([a-z]*)', _.handlers.Protected),
            ]

        self.status_task  = self.periodic(2, self.status)
        #self.status_task.cancel()

    async def status(self):
        logging.info('Periodic: %s', time.ctime())

