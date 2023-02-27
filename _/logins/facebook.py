#
# (c) 2015-2023 Matthew Shaw
#
# Authors
# =======
# Matthew Shaw <mshaw.cx@gmail.com>
#

import datetime

import _

import tornado.auth
import tornado.web


FBURL = '%s://%s/login/facebook?next=%s'

class Facebook(_.logins.Login, tornado.auth.FacebookGraphMixin):
    async def get(self):
        next_url = tornado.escape.url_escape(self.get_argument('next', '/'))

        url = f'{self.request.protocol}://{self.request.host}/login/facebook?next={next_url}'

        code = self.get_argument('code', None)

        if code:
            self.get_authenticated_user(
                redirect_uri  = url,
                client_id     = self.api_key,
                client_secret = self.secret,
                code          = code,
                callback      = self._on_auth
                )
        else:
            self.authorize_redirect(
                redirect_uri = url,
                client_id    = self.api_key,
                extra_params = {'scope': 'email'}
                )

    async def _on_auth(self, fbuser):
        if not fbuser:
            raise tornado.web.HTTPError(500, 'Facebook authentication failed')

        profile = _.db.FindProfile('fbid', fbuser['id'])
        if not profile:
            self.facebook_request(
                '/me',
                access_token = fbuser['access_token'],
                callback     = self._on_me
            )
        else:
            self.set_secure_cookie('session_id', str(profile['uid']))
            self.redirect(self.get_argument('next', '/'))

    async def _on_me(self, fbuser):
        profile = _.db.FindProfile('email', fbuser['email'])
        if not profile:
            profile = dict(
                email      = fbuser['email'],
                display    = fbuser['name'],
                fbid       = fbuser['id'],
                firstLogin = int(time.time() * 1000)
            )

            await self.application.onLogin(self, profile)
            #uid = _.db.SaveProfile(profile)
            self.set_secure_cookie('session_id', str(uid))

        else:
            self.set_secure_cookie('session_id', str(profile['uid']))
            # TODO: update facebook id

        self.redirect(self.get_argument('next', '/'))

