#
# (c) 2015-2023 Matthew Shaw
#
# Authors
# =======
# Matthew Shaw <mshaw.cx@gmail.com>
#

import asyncio
import os


async def wait(result):
    return result if not asyncio.iscoroutine(result) else await result


class Paths(object):
    def __init__(self, root=None, ns=None):
        self.root = root
        self.ns   = ns

    def __call__(self, *args):
        return os.path.join(self.root, self.ns, *args)


all = lambda members, prefix='', suffix='': [
    member for member in members
    if not member.startswith('_')
       and member.startswith(prefix)
       and member.endswith(suffix)
    ]


__all__ = all(dir())
