
# login methods are dynamically imported if auth is enabled

import logging

from .logout import Logout

import tornado.web
import _

@_.components.Register('auth')
class Authentication(tornado.web.RequestHandler):
    @classmethod
    def _pyConfig(cls, config):
        cls.URL = config.pop('login_page', '/login')
