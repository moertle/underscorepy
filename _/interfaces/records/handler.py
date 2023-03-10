# (c) 2015-2023 Matthew Shaw
#
# Authors
# =======
# Matthew Shaw <mshaw.cx@gmail.com>
#

import tornado.web

import _

from _.handlers.protected import Protected


class Handler(Protected):
    @tornado.web.authenticated
    async def get(self, record, record_id=None):
        if not record_id:
            records = await self._record._db.find(record)
            self.write(dict(data=[dict(r) for r in records]))
        else:
            record = await self._record._db.find_one(record, self._record._primary_key, record_id)
            self.write(record)

    @tornado.web.authenticated
    async def put(self, record, record_id=None):
        try:
            data = json.loads(self.request.body)
        except json.decoder.JSONDecodeError:
            raise tornado.web.HTTPError(500)

        await _.wait(self._record.put(record_id, data, self.request))
        self.set_status(204)

    @tornado.web.authenticated
    async def delete(self, record, record_id=None):
        if not record_id:
            raise tornado.web.HTTPError(500)

        data = await self._record._db.find_one(record, self._record._primary_key, record_id)
        if not data:
            raise tornado.web.HTTPError(404)

        await self._record._db.delete(record, self._record._primary_key, record_id)
        await _.wait(self._record.delete(record_id, data, self.request))
        self.set_status(204)
