#
# (c) 2015-2023 Matthew Shaw
#
# Authors
# =======
# Matthew Shaw <mshaw.cx@gmail.com>
#

import _


class Cache:
    @classmethod
    async def _(cls, name, **kwds):
        self = cls()
        await self.init(**kwds)
        _.cache[name] = self

    async def close(self):
        pass

    async def cookie_secret(self):
        raise NotImplementedError

    async def save_session(self, session_id, session):
        raise NotImplementedError

    async def load_session(self, session_id):
        raise NotImplementedError
