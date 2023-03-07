#
# (c) 2015-2023 Matthew Shaw
#
# Authors
# =======
# Matthew Shaw <mshaw.cx@gmail.com>
#

import os
import json

import _


class Protobuf(_.records.Record):
    async def init(self, name, **kwds):
        print(f'>>> PROTOBUF: {name}: {kwds}')
