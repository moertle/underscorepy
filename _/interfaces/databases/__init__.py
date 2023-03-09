
import _
print(_)

from . import database
from . import schema

_.interfaces.Database = database.Database

print(_.interfaces)
print()