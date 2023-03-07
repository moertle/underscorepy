import os
import _
# for use with protoc and underscore apps,
# e.g. protoc -I `python3 -m _.records.protobuf`
root = os.path.dirname(_.__file__)
root = os.path.abspath(os.path.join(root, '..'))
print(root)