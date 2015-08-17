
import sys

import _

from . import util

# a generic error class for throwing exceptions
class error(Exception):
    def __init__(self, fmt, *args):
        self.message = fmt % args

    def __str__(self):
        return self.message


from .version  import *
from .base     import *
from .io       import *

from . import version
from . import io
from . import paths

_.error = error
_.paths = paths.Paths()
