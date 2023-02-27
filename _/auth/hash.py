#
# (c) 2015-2023 Matthew Shaw
#
# Authors
# =======
# Matthew Shaw <mshaw.cx@gmail.com>
#

import base64
import hashlib


def simple_hash(value):
    value = value.encode('utf-8')
    for i in range(99999):
        value = hashlib.sha512(value).digest()
    return base64.b64encode(value).decode('ascii')

def check(username, password):
    pass
