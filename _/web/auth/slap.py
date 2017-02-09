
import time
import logging

import _

import tornado.escape

from . import Authentication

try:
    import ldap
except ImportError:
    raise _.py.error('Missing LDAP module')

class Slap(Authentication):
    def get(self):
        next = self.get_argument('next', '/')
        self.render('login.html', next=next)

    def post(self):
        username = self.get_argument('username', '')
        username = tornado.escape.xhtml_escape(username)
        password = self.get_argument('password', '')

        ldap_dn  = _.settings.config.get('slap', 'dn')
        ldap_uri = _.settings.config.get('slap', 'uri')

        try:
            dn = ldap_dn.format(username)
            ldap_server = ldap.initialize(ldap_uri)
            ldap_server.bind_s(dn, password)

            self.set_secure_cookie('_uid', username)
            ldap_server.unbind()

        except ldap.NO_SUCH_OBJECT:
            logging.warn('Could not find record for user: %s', username)

        except ldap.INVALID_CREDENTIALS:
            logging.warn('Invalid credentials for user: %s', username)

        except ldap.SERVER_DOWN:
            logging.warn('Could not connect to LDAP server: %s', ldap_uri)

        self.redirect(self.get_argument('next', '/'))
