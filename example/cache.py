
import _

class TestCache(_.caches.Cache):
    async def init(self, **kwds):
        pass
        #print('#' * 80)
        #print('# TestCache')
        #print('#', kwds)
        #print('#' * 80)

    async def cookie_secret(self):
        return b'weaksauce'
