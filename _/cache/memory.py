#
# (c) 2015-2023 Matthew Shaw
#
# Authors
# =======
# Matthew Shaw <mshaw.cx@gmail.com>
#

import json

import _


class Memory(_.cache.Cache, dict):
    async def init(self, **kwds):
        pass

    async def save_session(self, session_id, session):
        self[session_id] = json.dumps(session)

    async def load_session(self, session_id):
        print('@' * 40)
        print(self)
        print('@' * 40)
        session = self.get(session_id, None)
        if not session:
            return None
        return json.loads(session)
