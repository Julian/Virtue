import sys

if sys.version_info[0] == 2:
    PY2 = True
    from cStringIO import StringIO
else:
    PY2 = False
    from io import StringIO
