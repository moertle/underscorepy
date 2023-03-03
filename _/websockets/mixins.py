#
# (c) 2015-2023 Matthew Shaw
#
# Authors
# =======
# Matthew Shaw <mshaw.cx@gmail.com>
#

import _


class EchoMixin:
    def on_message(self, msg):
        for ws in self.websockets:
            if ws is self:
                continue
            ws.write_message(msg)


__all__ = _.all(dir(), suffix='Mixin')
