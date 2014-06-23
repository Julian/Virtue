import sys


HAS_UNITTEST2 = sys.version_info[:2] > (2, 6)

if HAS_UNITTEST2:
    import unittest
else:
    import unittest2 as unittest
