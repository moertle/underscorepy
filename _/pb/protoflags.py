
import sys
import os

root = os.path.dirname(__file__)
root = os.path.join(root, '..', '..')
root = os.path.abspath(root)

sys.stdout.write('%s\n' % root)
