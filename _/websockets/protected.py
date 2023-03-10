#
# (c) 2015-2023 Matthew Shaw
#
# Authors
# =======
# Matthew Shaw <mshaw.cx@gmail.com>
#

import tornado.web

import _

from . import WebSocket


class Protected(WebSocket):
    async def prepare(self):
        self.session_id = self.get_secure_cookie('session_id')
        if not self.session_id:
            raise tornado.web.HTTPError(403)
        self.session_id = self.session_id.decode('utf-8')

        self.session = await _.wait(_.sessions.load_session(self.session_id))
        if not self.session:
            raise tornado.web.HTTPError(403)
