#
# (c) 2015-2023 Matthew Shaw
#
# Authors
# =======
# Matthew Shaw <mshaw.cx@gmail.com>
#

import tornado.websocket

import _


class WebSocket(tornado.websocket.WebSocketHandler):
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
