#!/usr/bin/env python
import traceback
import inspect
import sys

from useful import __version__ as version
assert version >= (1,11)
from useful.mstring import s, prints


def prettybt():
  exctype, exc_val, tb = sys.exc_info()
  frames = inspect.getinnerframes(tb)
  for frame, file, line, funcname, *other in frames:
    args = frame.f_code.co_varnames
    prints("${file}:${line}: ${funcname}${args}")
    f_locals = frame.f_locals
    if 'self' in f_locals:
      klass = f_locals['self'].__class__.__name__
      prints("${file}:${line}: ${klass}.${funcname}${args}")
    else:
      prints("${file}:${line}: ${funcname}${args}")
    tb = tb.tb_next
  prints("${exctype.__name__}: ${exc_val}")


if __name__ == '__main__':
  class X:
    def eval(self, arg=[1,2,3]):
      raise Exception("bada boom")

  try:
    x = X()
    x.eval()
  except Exception as err:
    prettybt()
