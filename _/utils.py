#
# (c) 2015-2023 Matthew Shaw
#
# Authors
# =======
# Matthew Shaw <mshaw.cx@gmail.com>
#

import asyncio
import importlib
import inspect
import logging
import os
import sys
import textwrap
import time

import _

def now():
    return int(time.time() * 1000)

async def wait(result):
    try:
        return result if not asyncio.iscoroutine(result) else await result
    except Exception as e:
        logging.exception("Unhandled exception")

prefix = lambda kwds,prepend='_': dict((f'{prepend}{k}',v) for k,v in kwds.items())

class Paths:
    def __init__(self, root=None, ns=None):
        self.root = root
        self.ns   = ns

    def __call__(self, *args):
        return os.path.join(self.root, self.ns, *args)

sql = lambda statement: textwrap.dedent(statement.strip())

# to pass _.function as a filter to the all function
function = type(lambda: None)


class MetaLoader:
    def find_spec(self, fullname, path, target=None):
        parts = fullname.split('.')
        if parts[0] != '_':
            return
        fullpath = os.path.join(_.root, *parts)
        if os.path.exists(fullpath + '.py'):
            loader = importlib.machinery.SourceFileLoader(fullname, fullpath+'.py')
            return importlib.util.spec_from_loader(fullname, loader)
        if not os.path.isdir(fullpath):
            return
        fullpath = os.path.join(fullpath, f'__{parts[-1]}__.py')
        if not os.path.exists(fullpath):
            return
        spec = importlib.machinery.ModuleSpec(fullname, self)
        spec.fullpath = fullpath
        return spec

    def create_module(self, spec):
        loader = importlib.machinery.SourceFileLoader(spec.name, spec.fullpath)
        spec   = importlib.util.spec_from_loader(loader.name, loader)
        module = importlib.util.module_from_spec(spec)
        module.__package__ = spec.name
        module.__path__    = [os.path.abspath(os.path.join(*spec.name.split('.')))]
        return module

    def exec_module(self, module):
        module.__loader__.exec_module(module)


sys.meta_path.insert(0, MetaLoader())


def all(instance=object, cls=None, prefix='', suffix=''):
    'overkill function for import * from module to limit what is imported'
    __all__ = []
    module = inspect.getmodule(inspect.currentframe().f_back)
    root = module.__name__.rsplit('.', 1)[0] + '.'
    for name in dir(module):
        # ignore built-ins
        if name.startswith('_'):
            continue
        # filter prefix and suffix if specified
        if not name.startswith(prefix):
            continue
        if not name.endswith(suffix):
            continue

        obj = getattr(module, name)

        # filter modules unless they are sub-modules
        if isinstance(obj, type(module)):
            if not obj.__name__.startswith(root):
                continue
        # a way to filter out "local" variables
        if not isinstance(obj, instance):
            continue
        # only include sub-classes if specified
        if cls and issubclass(obj, cls):
            continue

        __all__.append(name)
    return __all__

__all__ = all()
