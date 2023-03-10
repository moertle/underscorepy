#
# (c) 2015-2023 Matthew Shaw
#
# Authors
# =======
# Matthew Shaw <mshaw.cx@gmail.com>
#

import functools
import binascii

import _


def basic(realm='Authentication'):
    def basic_auth(method):
        @functools.wraps(method)
        async def wrapper(self, *args, **kwds):
            auth = self.request.headers.get('Authorization', '')
            if auth.startswith('Basic '):
                auth = binascii.a2b_base64(auth[6:]).decode('utf-8')
                username,password = auth.split(':', 1)
                component = _.config.get(_.name, 'basic', fallback=None)
                if not component:
                    raise _.HTTPError(500, 'No component specified for basic auth')
                try:
                    login = _.logins[component]
                except KeyError:
                    raise _.HTTPError(500, 'Invalid component specified for basic auth')
                success = await login.check(username, password)
                if success:
                    return method(self, *args, **kwds)
            self.set_status(401)
            self.set_header('WWW-Authenticate', f'Basic realm={realm}')
            self.finish()
        return wrapper
    return basic_auth
