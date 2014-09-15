import sys

version_info = sys.version_info[:2]
PY26 = version_info == (2, 6)
PY3 = version_info[0] == 3

if PY26:
    import unittest2 as unittest
else:
    import unittest

if PY3:
    from io import StringIO
else:
    from cStringIO import StringIO
