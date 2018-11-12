import sys

try:
    import lldb
    import PyQt4
    import OpenGL
except ImportError as e:
    print >> sys.stderr, str(e)
else:
    del lldb
    del PyQt4
    del OpenGL
finally:
    del sys
