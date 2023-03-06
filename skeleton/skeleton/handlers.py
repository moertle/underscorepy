
import _
import tornado.web


class Records(_.handlers.Protected):
    @tornado.web.authenticated
    async def get(self, record, record_id=None):
        if not record_id:
            records = await self.application.db.find(record)
            self.write(dict(data=[dict(r) for r in records]))
        else:
            record = await self.application.db.find_one(record, record_id, 'username')
            self.write(record)
