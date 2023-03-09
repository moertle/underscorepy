#
# (c) 2015-2023 Matthew Shaw
#
# Authors
# =======
# Matthew Shaw <mshaw.cx@gmail.com>
#

import os

root = os.path.dirname(__file__)
root = os.path.join(root, '..')
root = os.path.abspath(root)

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

from .application import Application
