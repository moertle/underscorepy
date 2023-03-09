
import base64
import json
import uuid

import _

class Record:
    class Json(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, bytes):
                return base64.b64encode(obj).decode('ascii')
            if isinstance(obj, datetime.datetime):
                return str(obj)
            if isinstance(obj, uuid.UUID):
                return str(obj)
            return json.JSONEncoder.default(self, obj)

    def dump(self, **kwds):
        return json.dumps(self, cls=self.Json, separators=(',',':'), **kwds)

