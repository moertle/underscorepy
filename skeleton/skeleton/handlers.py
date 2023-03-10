
import _.handlers.websockets
import tornado.web


class Socket(_.handlers.websockets.Protected):
    def on_message(self, msg):
        logging.info('websocket: %s', msg)
        self.write_message(msg)
