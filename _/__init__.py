#
# (c) 2015-2023 Matthew Shaw
#
# Authors
# =======
# Matthew Shaw <mshaw.cx@gmail.com>
#

import asyncio
import os

root = os.path.dirname(__file__)
root = os.path.join(root, '..')
root = os.path.abspath(root)

stop = asyncio.Event()

# a generic error class for throwing exceptions
class error(Exception):
    def __init__(self, fmt, *args):
        self.message = fmt % args

    def __str__(self):
        return self.message

from .utils import *

from . import version
from . import settings
from . import auth
from . import components
from . import handlers
from . import websockets

from .application import Application
