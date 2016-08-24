
import sys

import _

# a generic error class for throwing exceptions
class error(Exception):
    def __init__(self, fmt, *args):
        self.message = fmt % args

    def __str__(self):
        return self.message


from . import version
from . import io
from . import decorators
from . import settings
from . import components

from .piper import Piper

