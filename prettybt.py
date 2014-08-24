#!/usr/bin/env python

"""
A more informative backtrace printer.

At least it includes class names.
"""

import traceback
import inspect

from useful import __version__ as version
assert version >= (1,11)
from useful.mstring import s, prints


def prettybt(exctype, exc_val, tb):
  frames = inspect.getinnerframes(tb)
  for frame, file, line, funcname, *other in frames:
    arginfo = inspect.getargvalues(frame)
    args = ", ".join(arginfo.args)
    f_locals = frame.f_locals
    if 'self' in f_locals:
      klass = f_locals['self'].__class__.__name__
      prints("${file}:${line}: ${klass}.${funcname}(${args}):")
    else:
      prints("${file}:${line}: ${funcname}(${args}):")
    tb = tb.tb_next
  prints("${exctype.__name__}: ${exc_val}")


if __name__ == '__main__':
  import sys
  sys.excepthook = prettybt

  class X:
    def eval(self, arg=[1,2,3]):
      raise Exception("bada boom")

  x = X()
  x.eval()
