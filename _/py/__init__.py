
# a generic error class for throwing exceptions
class error(Exception):
    def __init__(self, fmt, *args):
        self.message = fmt % args

    def __str__(self):
        return self.message

from .version  import *
from .io       import *
from .settings import *
