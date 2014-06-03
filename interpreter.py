from pratt import pratt_parse, prefix, infix, infix_r, postfix, ifelse, brackets
from ast import Leaf, Unary, Binary, Node, ListNode

import re


##############
# DATA TYPES #
##############

class Value(Leaf):
  type = None
  """ Base class for values. """

  def eval(self, frame):
    return self

  def Eq(self, other, frame):
    return TRUE if self.value == other.value else FALSE

  def Bool(self, frame):
    return TRUE if self.value else FALSE

  def Add(self, other, frame):
    return self.__class__(self.value + other.value)

  def Sub(self, right, frame):
    return self.__class__(self.value - right.value)

  def Mul(self, right, frame):
    return self.__class__(self.value * right.value)

  def Print(self, frame):
    return self.value


class TRUE:
  def __bool__(self):
    return True
TRUE = TRUE()

class FALSE:
  def __bool__(self):
    return False
FALSE = FALSE()


class Int(Value):
  def __init__(self, value):
    super().__init__(int(value))


class Str(Value):
  processed = False
  def eval(self, frame):
    if not self.processed:
      string = self.value
      replace = {r'\n': '\n', r'\t': '\t'}
      varnames = re.findall("\{([a-zA-Z\.]+)\}", string, re.M)
      for name in varnames:
          value = Var(name).eval(frame).Print(frame)
          string = string.replace("{%s}" % name, value)
      for k,v in replace.items():
        string = string.replace(k, v)
      self.value = string
      self.processed = True
    return self


#############
# OPERATORS #
#############

@prefix('p ', 0)
class Print(Unary):
  def eval(self, frame):
    value = self.arg.eval(frame)
    if hasattr(value, 'Print'):
      print(value.Print(frame))
    else:
      print(value)
    return value


def newinfix(sym, prio, methname, sametype=True, right=False):
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
  func = infix_r if right else infix
  Infix = func(sym, prio)(Infix)
  Infix.__name__ = Infix.__qualname__ = methname
  return Infix


newinfix('+', 20, 'Add')
newinfix('-', 20, 'Sub')
newinfix('*', 30, 'Mul')
newinfix('==', 10, 'Eq')

@brackets('[',']')
class Array(Unary):
  def eval(self, frame):
    return self

  def Print(self, frame):
    return self.arg.Print(frame)


@brackets('(',')')
class Parens(Unary):
  def eval(self, frame):
    return self.arg.eval(frame)


@infix(',', 5)
class Comma(ListNode):
  """ Parses comma-separated values. It flattens the list,
      e.g., Comma(1, Comma(2, 3)) transformed into Comma(1, 2, 3).
  """
  def __init__(self, left, right):
    values = []
    if isinstance(left, Comma):
      values += left + [right]
    else:
      values = [left, right]
    super().__init__(*values)

  def eval(self, frame):
    result = []
    for value in self:
      result.append(value.eval(frame))
    return result

  def Print(self, frame):
    return ", ".join(s.Print(frame) for s in self)


@infix_r('=', 2)
class Assign(Binary):
  def eval(self, frame):
    key = self.left.value
    value = self.right.eval(frame)
    # key.Assign(value, frame)
    frame[key] = value
    return value


class TypeExpr(ListNode):
  def __init__(self, name=None, variants=None):
    print("new ADT %s with the following variants:" % name)
    for variant in variants:
      print("VARIANT:", variant)


class Block(ListNode):
  def eval(self, frame):
    for expr in self:
      r = expr.eval(frame)
    return r


class Func:
  def __init__(self, name, args, body):
    self.name = name
    self.args = args
    self.body = Block(pratt_parse(body))

  def eval(self, frame):
    frame[self.name] = self
    return self

  def Call(self, args, frame):
    assert len(args) == len(self.args), \
      "The number of arguments must match function signature.\n" \
      "Got {} ({}) instead of {} ({})." \
      .format(len(args), args, len(self.args), self.args)
    for k, v in zip (self.args, args):
      frame[k] = v
    return self.body.eval(frame)

  def __repr__(self):
    return "({} {})".format(self.name, self.args)


class Var(Leaf):
  type = None

  def Assign(self, value, frame):
    # self.value actually holds the name
    print("!!! TODO: method is not called", self.value)
    frame[self.value] = self
    return value

  def eval(self, frame):
    try:
      return frame[self.value]
    except KeyError:
      raise Exception("unknown variable \"%s\"" % self.value)

  def __str__(self):
    return str(self.value)


class Expr:
  def __init__(self, *expr):
    self.expr = pratt_parse(expr)

  def eval(self, frame):
    return self.expr.eval(frame)

  def __repr__(self):
    return "({} {})".format(self.__class__.__name__, self.expr)


@postfix('!', 3)
class Call0(Unary):
  def eval(self, frame):
    func = self.arg.eval(frame)
    assert isinstance(func, Func), \
      "I can only call functions, got %s instead" % func
    with frame as newframe:
      return func.Call([], newframe)


@infix_r('@', 5)
class Call(Binary):
  def eval(self, frame):
    func = self.left.eval(frame)
    assert isinstance(func, Func), \
      "I can only call functions, got %s instead" % func
    args = self.right.eval(frame)
    if not isinstance(args, Comma):  # TODO: this should be done in PEG
      args = [args]
    with frame as newframe:
      return func.Call(args, newframe)

@ifelse(lbp=2)
class IfElse(Node):
  fields = ['iff', 'then', 'otherwise']
  def eval(self, frame):
    iff = self.iff.eval(frame)
    if iff.Bool(frame):
      return self.then.eval(frame)
    else:
      return self.otherwise.eval(frame)

@prefix('assert', 0)
class Assert(Unary):
  def eval(self, frame):
    r = self.arg.eval(frame)
    if not r:
      raise Exception("Assertion failed on %s" % self.arg)
    return r