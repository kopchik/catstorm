from pratt import *
from ast import *

class Int(Leaf):
  def __init__(self, value):
    super().__init__(int(value))

  def eval(self, frame):
    return self

  def Add(self, right, frame):
    assert isinstance(right, Int)
    return Int(self.value+right.value)

  def Sub(self, right, frame):
    assert isinstance(right, Int)
    return Int(self.value-right.value)


class Str(Leaf): pass


def newinfix(sym, prio, methname):
  @infix(sym, prio)
  class Infix(Binary):
    def eval(self, frame):
      left = self.left.eval(frame)
      right = self.right.eval(frame)
      return getattr(left, methname)(right, frame)

newinfix('+', 20, 'Add')
newinfix('-', 20, 'Sub')