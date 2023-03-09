
import _

# component instance containers
_.caches    = {}
_.databases = {}
_.records   = {}
_.logins    = {}
_.supports  = {}

from .components import load
