
import _

class TestCache(_.cache.Cache):
    async def init(self, **kwds):
        print('>>> TEST:', kwds)

    async def cookie_secret(self):
        return b''
