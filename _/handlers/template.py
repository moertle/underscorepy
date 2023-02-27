#
# (c) 2015-2023 Matthew Shaw
#
# Authors
# =======
# Matthew Shaw <mshaw.cx@gmail.com>
#

import tornado.web


class Template(tornado.web.RequestHandler):
    def initialize(self, template='index', **kwds):
        self.kwds = kwds
        self.template = template + '.html'

    def get(self, template=None):
        template = template + '.html' if template else self.template
        self.render(template, **self.kwds)
