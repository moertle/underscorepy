#
# (c) 2015-2023 Matthew Shaw
#
# Authors
# =======
# Matthew Shaw <mshaw.cx@gmail.com>
#

import tornado.web


class LoginPage(tornado.web.RequestHandler):
    def initialize(self, template='login', **kwds):
        self.kwds = kwds
        self.template = template + '.html'

    def get(self, template=None):
        template = template + '.html' if template else self.template
        message  = self.get_argument('message', None)
        next_url = self.get_argument('next',    '/')
        self.render(template, message=message, next_url=next_url, **self.kwds)


class Logout(tornado.web.RequestHandler):
    def get(self):
        self.clear_cookie('session_id')
        self.redirect(self.get_argument('next', '/'))
