
import os

import tornado.web

import _

from . import Base


class Template(Base):
    def initialize(self, template='index'):
        self.template = template + '.html'

    def get(self, template=None):
        template = template + '.html' if template else self.template
        self.render(template)


class Protected(Base):
    def initialize(self, template='index', **kwds):
        self.kwds = kwds
        self.template = template + '.html'

    @tornado.web.authenticated
    def get(self, template=None):
        template = template + '.html' if template else self.template
        self.render(template, **self.kwds)


class Source(Base):
    def get(self, src=''):
        srcdir = os.path.join(_.paths.root, 'src')
        src = os.path.join(srcdir, src)
        src = os.path.abspath(src)

        if not src.startswith(srcdir):
            raise tornado.web.HTTPError(404, 'Path escape attempt detected')

        try:
            data = open(src, 'rb').read()
        except:
            raise tornado.web.HTTPError(404, 'File not found')

        self.set_header('Content-Type', 'text/plain')
        self.write(data)
