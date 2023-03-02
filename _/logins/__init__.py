
import urllib

import tornado.web

import _

from .oauth2 import OAuth2


class Login(tornado.web.RequestHandler):
    @classmethod
    async def _(cls, name, **kwds):
        # create a dynamic child class with kwds from the ini file
        # add a reference to the component name accessible by the new type
        kwds['name'] = name
        _.login[name] = type(cls.__name__, (cls,), kwds)
        await _.login[name].init(name)

    @classmethod
    async def init(cls, name):
        pass

    @classmethod
    async def args(cls, name):
        pass

    @classmethod
    async def check(cls, username, password):
        raise NotImplementedError

    def initialize(self):
        self.next_url = self.get_argument('next', '/')
        self.redirect_uri = f'{self.request.protocol}://{self.request.host}/login/{self.name}?next={self.next_url}'

    async def on_login_success(self, record):
        fn = getattr(self.application, f'on_login_{self.name}', self.application.on_login)
        try:
            session = await _.wait(fn(self, record))
            await _.wait(_.sessions.save_session(session))
            self.set_secure_cookie('session_id', session['session_id'], expires_days=1)
        except NotImplementedError:
            raise tornado.web.HTTPError(500, 'on_login method not implemented') from None
        self.redirect(self.next_url)

    async def on_login_failure(self, message='Invalid Login'):
        url = self.get_login_url()
        url += "?" + urllib.parse.urlencode(dict(message=message, next_url=self.next_url))
        self.clear_cookie('session_id')
        self.redirect(url)
