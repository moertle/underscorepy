#
# (c) 2015-2023 Matthew Shaw
#
# Authors
# =======
# Matthew Shaw <mshaw.cx@gmail.com>
#

import json

import _

class Redis(_.component.Session):
    async def init(self, cache):
        self.cache = _.component.cache[cache]

    async def save_session(self, session_id, session):
        async with self.cache.pipeline(transaction=True) as pipe:
            await pipe.set(f'session/{session_id}', json.dumps(session))
            await pipe.expire(f'session/{session_id}', 86400)
            await pipe.execute()

    async def load_session(self, session_id):
        session = await self.cache.get(f'session/{session_id}')
        if not session:
            return None
        return json.loads(session)
