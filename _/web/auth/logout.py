
import tornado.web


class Logout(tornado.web.RequestHandler):
    def get(self):
        self.clear_cookie('_uid')
        self.redirect(self.get_argument('next', '/'))
