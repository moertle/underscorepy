
import _


class Cache:
    @classmethod
    async def _(cls, instance, **kwds):
        self = cls()
        await self.init(**kwds)
        _.component.cache[instance] = self
