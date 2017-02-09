
import sys

sys.modules['_'].web = sys.modules['_.web']

from . import auth
from . import util

from .application import Application

import _

_.settings.argparser.add_argument('--name',
    help='Specify a name for the instance')

_.settings.argparser.add_argument('--address', '-a',
    help = 'Interface to bind to')

_.settings.argparser.add_argument('--port', '-p',
    type=int,
    help='Port to bind to')

_.settings.argparser.add_argument('--newcookie',
    action='store_true',
    help='Generate a new cookie')
