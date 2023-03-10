
import functools

import tornado.web

import _


def filter(filter_func):
    def _filter(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwds):
            if filter_func(self):
                return method(self, *args, **kwds)
            raise tornado.web.HTTPError(403)
        return wrapper
    return _filter


def filter_user(filter_func):
    def _filter_user(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwds):
            if self.current_user:
                if filter_func(self.current_user):
                    return method(self, *args, **kwds)
            raise tornado.web.HTTPError(403)
        return wrapper
    return _filter_user

current_user = filter_user(lambda current_user: True)
protected    = filter_user(lambda current_user: True)

__all__ = _.all()
