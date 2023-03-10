#
# (c) 2015-2023 Matthew Shaw
#
# Authors
# =======
# Matthew Shaw <mshaw.cx@gmail.com>
#

import tornado.web

import _


class Handler(_.handlers.Protected):
    @tornado.web.authenticated
    async def get(self, name, session_id=None):
        self.set_status(204)

    @tornado.web.authenticated
    async def delete(self, name, session_id=None):
        self.set_status(204)
