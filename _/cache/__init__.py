
import _


class Cache:
    @classmethod
    async def _(cls, instance, **kwds):
        self = cls()
        await self.init(**kwds)
        _.components.cache[instance] = self

    async def close(self):
        pass

    async def cookie_secret(self):
        raise NotImplementedError

    async def save_session(self, session_id, session):
        raise NotImplementedError

    async def load_session(self, session_id):
        raise NotImplementedError
