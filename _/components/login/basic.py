
import functools
import binascii

import _

def basic(realm='Authentication'):
    def basic_auth(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            auth = self.request.headers.get('Authorization', '')
            if auth.startswith('Basic '):
                auth = binascii.a2b_base64(auth[6:]).decode('utf-8')
                username,password = auth.split(':', 1)
                if password == _.settings.args.password:
                    return method(self, *args, **kwargs)

            self.set_status(401)
            self.set_header('WWW-Authenticate', 'Basic realm=%s' % realm)
            self.finish()

        return wrapper
    return basic_auth

