#
# (c) 2015-2023 Matthew Shaw
#
# Authors
# =======
# Matthew Shaw <mshaw.cx@gmail.com>
#

import _


class Record:
    @classmethod
    async def _(cls, name, **kwds):
        self = cls()
        _.record[name] = self
        try:
            await self.init(name, **kwds)
        except TypeError as e:
            raise _.error('%s', e)
