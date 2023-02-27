
import tornado.web

import _


class Login(tornado.web.RequestHandler):
    @classmethod
    async def _(cls, instance, **kwds):
        # create a dynamic child class with kwds from the ini file
        _.component.login[instance] = type(cls.__name__, (cls,), kwds)

    @classmethod
    async def check(cls, username, password):
        return None

