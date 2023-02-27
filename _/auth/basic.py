#
# (c) 2015-2023 Matthew Shaw
#
# Authors
# =======
# Matthew Shaw <mshaw.cx@gmail.com>
#

import functools
import binascii

import tornado.web

import _


def basic(realm='Authentication'):
    def basic_auth(method):
        @functools.wraps(method)
        async def wrapper(self, *args, **kwargs):
            auth = self.request.headers.get('Authorization', '')
            if auth.startswith('Basic '):
                auth = binascii.a2b_base64(auth[6:]).decode('utf-8')
                username,password = auth.split(':', 1)
                component = _.config.get(_.app, 'basic', fallback=None)
                if not component:
                    raise tornado.web.HTTPError(500, 'No component specified for basic auth')
                try:
                    login = _.login[component]
                except KeyError:
                    raise tornado.web.HTTPError(500, 'Invalid component specified for basic auth')
                success = await login.check(username, password)
                if success:
                    return method(self, *args, **kwargs)
            self.set_status(401)
            self.set_header('WWW-Authenticate', f'Basic realm={realm}')
            self.finish()
        return wrapper
    return basic_auth
