from pratt import *
from ast import *


class Int(Leaf):
  def __init__(self, value):
    super().__init__(int(value))

  def eval(self, frame):
    return self

  def Add(self, right, frame):
    return Int(self.value + right.value)

  def Sub(self, right, frame):
    return Int(self.value - right.value)

  def Print(self, frame):
    return self.value


class Str(Leaf):
  def eval(self, frame):
    return self

  def Add(self, other, frame):
    return Str(self.value + other.value)

  def Print(self, frame):
    return self.value


@prefix('p ', 0)
class Print(Unary):
  def eval(self, frame):
    value = self.arg.eval(frame)
    if hasattr(value, 'Print'):
      print(value.Print(frame))
    else:
      print(value)
    return value


def newinfix(sym, prio, methname, sametype=True):
  @infix(sym, prio)
  class Infix(Binary):
    def eval(self, frame):
      left = self.left.eval(frame)
      right = self.right.eval(frame)
      if sametype:
        assert type(left) == type(right), \
          "Left and right operands of ({}) must have same type.\n" \
          "Got {} and {}.".format(sym, type(left), type(right))
      try:
        meth = getattr(left, methname)
      except AttributeError:
        raise Exception("{} does not have {} method, \
                         operation ({}) not supported".format(left, methname, sym))
      return meth(right, frame)
  Infix.__name__ = Infix.__qualname__ = methname
  return Infix


newinfix('+', 20, 'Add')
newinfix('-', 20, 'Sub')