#
# (c) 2015-2023 Matthew Shaw
#
# Authors
# =======
# Matthew Shaw <mshaw.cx@gmail.com>
#

import time
import logging

import tornado.escape

import _


try:
    import ldap
except ImportError:
    raise _.error('Missing LDAP module')


class Slap(_.component.Login):
    def post(self):
        username = self.get_argument('username', '')
        username = tornado.escape.xhtml_escape(username)
        password = self.get_argument('password', '')

        try:
            dn = self.dn.format(username)
            ldap_server = ldap.initialize(self.uri)
            ldap_server.bind_s(dn, password)

            self.set_secure_cookie('session_id', username)
            ldap_server.unbind()

        except ldap.NO_SUCH_OBJECT:
            logging.warn('Could not find record for user: %s', username)

        except ldap.INVALID_CREDENTIALS:
            logging.warn('Invalid credentials for user: %s', username)

        except ldap.SERVER_DOWN:
            logging.warn('Could not connect to LDAP server: %s', self.uri)

        self.redirect(self.get_argument('next', '/'))
