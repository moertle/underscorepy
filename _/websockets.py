#
# (c) 2015-2023 Matthew Shaw
#
# Authors
# =======
# Matthew Shaw <mshaw.cx@gmail.com>
#

import tornado.web
import tornado.websocket

import _


class Base(tornado.websocket.WebSocketHandler):
    def initialize(self, websockets):
        self.websockets = websockets

    def check_origin(self, origin):
        if _.args.debug:
            return True
        # TODO: let app specify origin policy
        return True

    def open(self):
        self.set_nodelay(True)
        self.websockets[id(self)] = self

    def on_close(self):
        self.websockets.pop(id(self), None)

    def on_message(self, msg):
        raise NotImplementedError


class Protected(Base):
    async def prepare(self):
        session_id = self.get_secure_cookie('session_id')
        if not session_id:
            raise tornado.web.HTTPError(403)

        session = await self.application.sessions.load_session(session_id)
        print(session)


class EchoMixin:
    def on_message(self, msg):
        for ws in self.websockets:
            if ws is self:
                continue
            ws.write_message(msg)


