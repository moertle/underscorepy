
import tornado.web


class Base(tornado.web.RequestHandler):
    def get_current_user(self):
        uid = self.get_secure_cookie('_uid')
        if uid is None:
            self.clear_cookie('_uid')
        return uid


from .index import *
from .      import ws
