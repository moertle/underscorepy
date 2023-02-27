
import logging

import _


class Session:
    @classmethod
    async def _(cls, instance, **kwds):
        if _.components.session:
            logging.warn('Overwriting session')
        self = cls()
        await self.init(**kwds)
        _.components.session = self

    async def save_session(self, session_id):
        pass

    async def load_session(self, session_id):
        pass
