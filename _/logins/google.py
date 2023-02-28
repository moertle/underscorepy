#
# (c) 2015-2023 Matthew Shaw
#
# Authors
# =======
# Matthew Shaw <mshaw.cx@gmail.com>
#

import tornado.auth
import tornado.web

import _

#
# Google authentication
#

_domains = []


class Google(_.logins.Login, tornado.auth.GoogleOAuth2Mixin):
    @classmethod
    def initialize(cls, *args, **kwargs):
        _domains.extend([d for d in kwargs.get('domains', '').split(' ') if d])

    async def get(self):
        if self.get_argument('openid.mode', None):
            await self.get_authenticated_user(self._on_auth)
            return
        self.authenticate_redirect()

    async def _on_auth(self, user):
        if not user:
            raise tornado.web.HTTPError(500, 'Google authentication failed')

        try:
            name,domain = user['email'].split('@', 1)
        except:
            raise tornado.web.HTTPError(500, 'Google authentication failed')

        if _domains and domain not in _domains:
            raise tornado.web.HTTPError(500, 'Invalid domain')

        await self.application.on_login(self, name)
        #self.set_secure_cookie('session_id', name)
        self.redirect(self.get_argument('next', '/'))

    def write_error(self, status_code, **kwargs):
        error = kwargs['exc_info'][1]

        self.set_header('Content-Type', 'text/html')
        self.finish('''
            <html>
                <head><title>%s</title></head>
                <body><p>%s</p></body>
            </html>''' % (status_code, error.log_message))
