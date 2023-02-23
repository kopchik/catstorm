#!/usr/bin/env python

"""
A more informative backtrace printer.

At least it includes class names.
"""

import inspect
import traceback


def prettybt(exctype, exc_val, tb):
    frames = inspect.getinnerframes(tb)
    for frame, file, line, funcname, *other in frames:
        arginfo = inspect.getargvalues(frame)
        args = ", ".join(arginfo.args)
        f_locals = frame.f_locals
        if "self" in f_locals:
            klass = f_locals["self"].__class__.__name__
            print(f"{file}:{line}: {klass}.{funcname}({args}):")
        else:
            print(f"{file}:{line}: {funcname}({args}):")
        tb = tb.tb_next
    print(f"{exctype.__name__}: {exc_val}")


if __name__ == "__main__":
    import sys

    sys.excepthook = prettybt

    class X:
        def eval(self, arg=[1, 2, 3]):
            raise Exception("bada boom")

    x = X()
    x.eval()
