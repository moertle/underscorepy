
import _


class CacheHandler(_.handlers.Protected):
    @tornado.web.authenticated
    async def get(self, name, session_id=None):
        self.set_status(204)

    @tornado.web.authenticated
    async def delete(self, name, session_id=None):
        self.set_status(204)
