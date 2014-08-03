from pratt import pratt_parse1, prefix, \
  infix, infix_r, postfix, nullary, ifelse, brackets
from ast import Leaf, Unary, Binary, Node, ListNode
from log import Log
import re

log = Log("interpreter")

##############
# MISC STUFF #
##############

class ReturnException(Exception):
  """ To be raised by ret operator """


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

  def Gt(self, other, frame):
    return TRUE if self.value > other.value else FALSE

  def Bool(self, frame):
    return TRUE if self.value else FALSE

  def Add(self, other, frame):
    return self.__class__(self.value + other.value)

  def Sub(self, right, frame):
    return self.__class__(self.value - right.value)

  def Mul(self, right, frame):
    return self.__class__(self.value * right.value)

  def Print(self, frame):
    return str(self.value)


class TRUE:
  def Bool(self, frame):
    return self

  def Print(self, frame):
    return self.__class__.__name__

  def eval(self, frame):
    return self

  def __bool__(self):
    return True
TRUE = TRUE()

class FALSE:
  def Bool(self, frame):
    return self
  def __bool__(self):
    return False
FALSE = FALSE()


@nullary('NONE')
class NONE:
 pass


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

@prefix('ret', 0)
class Ret(Unary):
  def eval(self, frame):
    value = self.arg.eval(frame)
    raise ReturnException(value)


@prefix('p ', 0)
class Print(Unary):
  def eval(self, frame):
    value = self.arg.eval(frame)
    if hasattr(value, 'Print'):
      print(">", value.Print(frame))
    else:
      print(">", value)
    return value


def newinfix(sym, prio, methname, sametype=True, right=False):
  class Infix(Binary):
    def eval(self, frame):
      left = self.left.eval(frame)
      right = self.right.eval(frame)
      if sametype:
        assert type(left) == type(right), \
          "Left and right operands of ({} {} {}) must have same type.\n" \
          "Got {} and {}." \
          .format(left, sym, right, type(left), type(right))
      try:
        meth = getattr(left, methname)
      except AttributeError:
        raise Exception("{} does not have {} method, " \
                        "operation ({}) not supported".format(left, methname, sym))
      return meth(right, frame)
  func = infix_r if right else infix
  Infix = func(sym, prio)(Infix)
  Infix.__name__ = Infix.__qualname__ = methname
  return Infix


newinfix('+', 20, 'Add')
newinfix('-', 20, 'Sub')
newinfix('*', 30, 'Mul')
newinfix('==', 4, 'Eq')
newinfix('>', 3, 'Gt')


@brackets('[',']')
class Array(ListNode):
  def __init__(self, *args):
    # TODO: dirty code, separate it into "fabrics"
    if len(args) == 1:
      arg = args[0]
      if isinstance(arg, Comma):
        for e in arg:
          self.append(e)
      else:
        self.append(arg)
    else:
      for e in args:
        self.append(e)

  def eval(self, frame):
    return self

  def Print(self, frame):
    return ", ".join(e.Print(frame) for e in self)

  def Eq(self, other, frame):
    if  isinstance(other, Array) \
    and len(self) == len(other) \
    and all(a.Eq(b, frame) for a,b in zip(self,other)):
      return TRUE
    return FALSE


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
    r = Int(0)  # TODO: return NONE
    for expr in self:
      try:
        r = expr.eval(frame)
      except ReturnException as e:
        r = e.args[0]
        break
    return r


#######################
# CLASSED AND OBJECTS #
#######################
classes = {}
savedobj = None


class Obj(dict):
  """ Instance of the class (actually, it's dict). """
  def __getitem__(self, name):
    try:
      return super().__getitem__(name)
    except KeyError:
      return self['Class'][name]

  def SetAttr(self, name, value, frame):
    self[name] = value
    return value

  def Print(self, frame):
    cls = self.__class__.__name__
    return "(obj %s of %s)" % (cls, self)


class Class(Node):
  """ Define new class. """
  fields = ['name', 'body']

  def __init__(self, name):
    self.name = name
    self.body = Block()
    classes[name] = self

  def eval(self, frame):
    frame[self.name] = self
    return self

  def __getitem__(self, methname):
    for member in self.body:
      if isinstance(member, Func) and member.name == methname:
        return member
    raise Exception("No such member \"%s\" in class %s" % (methname, self.name))

  def Call(self, args, frame):
    global savedobj
    obj = Obj()
    obj['Class'] = self
    savedobj = obj
    self['New'].Call(args, frame)
    return obj


@prefix('@', 1)
class Self(Unary):
  def eval(self, frame):
    obj = savedobj
    if isinstance(self.arg, Assign):
      name = self.arg.left.value
      value = self.arg.right.eval(frame)
      obj[name] = value
    else:
      value = obj[self.arg.value]
    return value


@infix('@', 5)
class Attr(Binary):
  def eval(self, frame):
    obj = self.left.eval(frame)
    attr = self.right.value
    return obj[attr]


class Func(Node):
  fields = ['name', 'args', 'body']
  def __init__(self, name, args, body=[]):
    self.name = name
    if not args: args = []
    self.args = args
    log.func.debug("pratt_parse on %s" % body)
    self.body = Block(pratt_parse1(body)) if body else Block()

  def eval(self, frame):
    frame[self.name] = self
    return self

  def Call(self, args, frame):
    assert len(args) == len(self.args), \
      "The number of arguments must match the function signature.\n" \
      "Got {} ({}) instead of {} ({})." \
      .format(len(args), args, len(self.args), self.args)
    for k, v in zip (self.args, args):
      frame[k] = v
    return self.body.eval(frame)

  def Print(self, frame):
    return "<func %s>" % self.name


class Var(Leaf):
  type = None

  def Assign(self, value, frame):
    # self.value actually holds the name
    print("!!! TODO: method is not called", self.value)
    frame[self.value] = self
    return value

  def eval(self, frame):
    return frame[self.value]

  def __str__(self):
    return str("<%s>" % self.value)


@postfix('!', 3)
class Call0(Unary):
  def eval(self, frame):
    callee = self.arg.eval(frame)
    assert isinstance(callee, (Func, Class)), \
      "I can only call functions and classes, " \
      "got %s instead" % callee
    with frame as newframe:
      return callee.Call([], newframe)


@infix('$', 5)  # TODO: does not work
def call_r(left, right):
  return Call(right, left)


@infix_r(' . ', 5)
class Call(Binary):
  def eval(self, frame):
    callee = self.left.eval(frame)
    assert isinstance(callee, (Func, Class)), \
      "I can only call functions and classes, got %s instead" % func
    args = self.right.eval(frame)
    # TODO: this should be done in PEG and it should not be list but Comma!
    if not isinstance(args, list):
      args = [args]
    with frame as newframe:
      return callee.Call(args, newframe)


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
