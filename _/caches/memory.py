#
# (c) 2015-2023 Matthew Shaw
#
# Authors
# =======
# Matthew Shaw <mshaw.cx@gmail.com>
#

import os
import json

import _


class Memory(_.caches.Cache):
    async def init(self, **kwds):
        self.mem = {}

    def cookie_secret(self):
        return os.urandom(32)

    def save_session(self, session):
        session_id = super(Memory, self).save_session(session)
        self.mem[session_id] = json.dumps(session)

    def load_session(self, session_id):
        session = self.mem.get(session_id, None)
        if not session:
            return None
        return json.loads(session)
