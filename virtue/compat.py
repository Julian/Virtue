import sys


PY26 = sys.version_info[:2] == (2, 6)

if PY26:
    import unittest2 as unittest
else:
    import unittest
