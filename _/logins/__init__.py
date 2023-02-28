
import tornado.web

import _


class Login(tornado.web.RequestHandler):
    @classmethod
    async def _(cls, name, **kwds):
        # create a dynamic child class with kwds from the ini file
        _.login[name] = type(cls.__name__, (cls,), kwds)
        await _.login[name].load(name)

    @classmethod
    async def load(cls, name):
        pass

    @classmethod
    async def args(cls, name):
        pass

    @classmethod
    async def check(cls, username, password):
        raise NotImplementedError
