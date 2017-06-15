
import tornado.web
import tornado.websocket


class Base(tornado.websocket.WebSocketHandler):
    def initialize(self, websockets=None):
        if websockets is None:
            self.websockets = self.application.websockets
        else:
            self.websockets = websockets

    def check_origin(self, origin):
        return True

    def open(self):
        self.stream.set_nodelay(True)
        self.websockets.add(self)

    def on_message(self, msg):
        pass

    def on_close(self):
        try:
            self.websockets.remove(self)
        except KeyError:
            pass


class Protected(Base):
    def open(self):
        if not self.get_secure_cookie('_uid'):
            raise tornado.web.HTTPError(403)
        super(Base, self).open()


class Broadcast(Base):
    def on_message(self, msg):
        for ws in self.websockets:
            if ws is self:
                continue
            ws.write_message(msg)
