#
# (c) 2015-2023 Matthew Shaw
#
# Authors
# =======
# Matthew Shaw <mshaw.cx@gmail.com>
#

import _

from _.interfaces.logins.oauth2 import OAuth2


class Google(OAuth2, _.interfaces.Login):
    @classmethod
    async def init(cls, name, **kwds):
        cls.scope = ['email']
        cls.extra = {'approval_prompt': 'auto'}

        await super(Google, cls).init(name, **kwds)
