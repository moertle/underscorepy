#
# (c) 2015-2023 Matthew Shaw
#
# Authors
# =======
# Matthew Shaw <mshaw.cx@gmail.com>
#

import tornado.web

import _

from .template import Template

class Protected(Template):
    async def prepare(self):
        if _.sessions is None:
            raise tornado.web.HTTPError(500, 'No session component specified')

        self.session = None
        session_id = self.get_secure_cookie('session_id', max_age_days=1)
        if session_id:
            session_id = session_id.decode('utf-8')
            self.session = await _.wait(_.sessions.load_session(session_id))

    def get_current_user(self):
        return self.session

    @tornado.web.authenticated
    def get(self, template=None):
        super(Protected, self).get(template)
