from pratt import pratt_parse1, prefix, \
  infix, infix_r, postfix, nullary, ifelse, brackets, subscript
from ast import Leaf, Unary, Binary, Node, ListNode
from log import Log

from itertools import chain
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

class DirectAccess:
  """ Mixin that adds GetAttr to a class. This allows to work
      with objects that are not instances of Class/Obj.
      E.g., str.tokenize! would not work without it because
      Str is not an instance of Class/Obj.
  """

  def GetAttr(self, name, frame):
    assert isinstance(name, Var)
    name = name.to_py_str()
    return getattr(self, name)
    class Callable:
      def Call(self, args, frame):
        return meth(args, frame)
    return Callable()


class Value(Leaf, DirectAccess):
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
class NONECLS:
 def eval(self, frame):
  return NONE
 def Bool(self,frame):
  return FALSE
 def __repr__(self):
    return "NONE"
NONE = NONECLS()


class Int(Value):
  def __init__(self, value):
    if isinstance(value, Int):
      value = value.value
    super().__init__(int(value))

  def to_py_int(self):
    return self.value

  def Minus(self, frame):
    return Int(-self.value)


class Str(Value):
  def __init__(self, *args, process=True, **kwargs):
    self.process = process
    super().__init__(*args, **kwargs)

  def eval(self, frame):
    if not self.process:
      return self

    string = self.value
    replace = {r'\"':'"', r'\n': '\n', r'\t': '\t'}
    varnames = re.findall("\{([a-zA-Z\.]+)\}", string, re.M)
    for name in varnames:
        value = Var(name).eval(frame).Print(frame)
        string = string.replace("{%s}" % name, value)
    for k,v in replace.items():
      string = string.replace(k, v)
    return Str(string, process=False)

  def GetItem(self, attr, frame):
    if isinstance(attr, Int):
      value = self.value[attr.to_py_int()]
    else:
      raise Exception("don't know how to access item %s" % attr)
    return self.__class__(value)

  def Iter(self, frame):
    return Iter(Str(char) for char in self.value)

  def strip(self, frame):
    return Str(self.value.strip())

  def tokenize(self, frame):
    # pattern = r"\s*(?:(\d+)|(.))"
    # pattern = r"\s*(?:(\d+)|(\*\*|.))"
    pattern = r"""
       (?P<number>\d+)
      |(?P<id>\w+)
      |(?P<string>"(?:\\.|[^"\\])*")
      |(?P<op>\*\*|.)\s*
      """
    result = Array()
    for match in re.findall(pattern, self.value.strip(), re.VERBOSE):
      number, id, string, op = match
      if number:
        result.Append(Array(Str("number"), Int(number)))
      elif id:
        result.Append(Array(Str("id"), Str(id)))
      elif string:
        result.Append(Array(Str("string"), Str(string)))
      elif op:
        result.Append(Array(Str("op"), Str(op)))
    return result

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
    assert not isinstance(value, str), \
        "got instance of str, but it should be interpreter.Str"
    if hasattr(value, 'Print'):
      print("P>", value.Print(frame))
    else:
      print(" >", value)
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
newinfix('<<<',3, 'Append', sametype=False)


@prefix('-', 100)
class Minus(Unary):
  def eval(self, frame):
    arg = self.arg.eval(frame)
    return arg.Minus(frame)


class Iter:
  def __init__(self, arr):
    self.iter = iter(chain(arr, [None]))

  def eval(self, frame):
    return self

  def next(self, frame):
    return next(self.iter)


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
    for i, e in enumerate(self):
      e = e.eval(frame)
      self[i] = e
    return self

  def GetItem(self, value, frame):
    if isinstance(value, Int):
      return self[value.to_py_int()]
    elif isinstance(value, ColonSV):
      # if it is in form var[start:stop]
      if len(value) == 2:
        start, stop = value
        ret = self[start.to_py_int():stop.to_py_int()]
        return Array(*ret)
      # if it is in form var[start:stop:step]
      elif len(ColonSV) == 3:
        TODO
    else:
     raise Exception("do not know how to apply subscript %s to %s" % \
                           (value, self))

  def SetItem(self, key, value, frame):
    assert isinstance(key, Int)
    self[key.to_py_int()] = value
    return self

  def Append(self, value, frame=None):
    self.append(value)
    return value

  def Print(self, frame):
    return '[' + ", ".join(e.Print(frame) for e in self) + ']'

  def Eq(self, other, frame):
    if  isinstance(other, Array) \
    and len(self) == len(other) \
    and all(a.Eq(b, frame) for a,b in zip(self,other)):
      return TRUE
    return FALSE

  def Iter(self, frame):
    return Iter(self)

  def len(self):
    return len(self)


class Tuple(Array):
  def forbidden_operation(self, *args, **kwargs):
    raise Exception("Tuples are immutable, dude")
  Append = SetItem = forbidden_operation

  def Print(self, frame):
    return '(' + ", ".join(e.Print(frame) for e in self) + ')'  # TODO: reuse code from Array


@subscript('[',']', 1000)
class Subscript(Binary):
  def eval(self, frame):
    left = self.left.eval(frame)
    right = self.right.eval(frame)
    return left.GetItem(right, frame)


@brackets('(',')')
class Parens(Unary):
  def eval(self, frame):
    return self.arg.eval(frame)


class CharSepVals(ListNode):
  """ Parses <whatever>-separated values. It flattens the list,
      e.g., Comma(1, Comma(2, 3)) transformed into Comma(1, 2, 3).
      eval() returns new instance.
  """
  def __init__(self, *values, flatten=True):
    if flatten:
      assert len(values) == 2, "in flatten mode only two args accepted (left and right)"
      values = self.flatten(*values)
    super().__init__(*values)

  def flatten(self, left, right):
    values = []
    if isinstance(left, self.__class__):
      values += left + [right]
    else:
      values = [left, right]
    return values

  def eval(self, frame):
    values = []
    for e in self:
      values.append(e.eval(frame))
    return self.__class__(*values, flatten=False)


@infix(',', 5)
class Comma(CharSepVals):
  pass


@infix(':', 5)
class ColonSV(CharSepVals):
  pass


@infix_r('=', 2)
class Assign(Binary):
  def eval(self, frame):
    # code below tries to distinct between
    # assigning to variable and to class member
    value = self.right.eval(frame)
    if isinstance(self.left, Var):
      key = self.left
      key.Assign(value, frame)
    elif isinstance(self.left, Attr):
      owner = self.left.left.eval(frame)
      key = self.left.right
      owner.SetAttr(key, value, frame)
    elif isinstance(self.left, Subscript):
      owner = self.left.left.eval(frame)
      key = self.left.right.eval(frame)
      owner.SetItem(key, value, frame)
    else:
      # this is very unlikely and should be caused by syntax error
      raise Exception("don't know what to do with expression %s = %s" % (self.left, self.right))
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
  def GetAttr(self, name, frame):
    name = name.to_py_str()
    try:
      return self[name]
    except KeyError:
      return self['Class'][name]

  def SetAttr(self, name, value, frame):
    name = name.to_py_str()
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
    attr = self.right
    return obj.GetAttr(attr, frame)


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
    frame[self.value] = value
    return value

  def eval(self, frame):
    return frame[self.value]

  def to_py_str(self):
    return self.value

  def __str__(self):
    return str("<var %s>" % self.value)


@postfix('!', 3)
class Call0(Unary):
  def eval(self, frame):
    callee = self.arg.eval(frame)
    with frame as newframe:
      if hasattr(callee, "Call"):
        return callee.Call([], newframe)
      else:
        return callee(newframe)


@infix('$', 5)  # TODO: does not work
def call_r(left, right):
  return Call(right, left)


@infix_r(' . ', 5)
class Call(Binary):
  def eval(self, frame):
    callee = self.left.eval(frame)
    assert isinstance(callee, (Func, Class)), \
      "I can only call functions and classes, got %s (%s) instead" % (callee, type(callee))
    args = self.right.eval(frame)
    if not isinstance(args, Comma):
      args = [args]  # TODO: it's not a comma class
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


class ForLoop(Node):
  fields = ['var', 'expr', 'body']
  def __init__(self, var, expr, body=[]):
    self.var  = pratt_parse1(var)
    self.expr = pratt_parse1(expr)
    self.body = Block(pratt_parse1(body)) if body else Block()
    log.forloop.debug("got var=%s expr=%s body=%s" \
                      % (self.var, self.expr, self.body))

  def eval(self, frame):
    expr = self.expr.eval(frame)
    iterator = expr.Iter(frame)
    result = NONE
    with frame as newframe:
      while True:
        e = iterator.next(newframe)
        if e is None:
          break
        if isinstance(self.var, Var):
          self.var.Assign(e, newframe)
        elif isinstance(self.var, Comma):
          assert e.len() == len(self.var)
          for var, value in zip(self.var, e):
            var.Assign(value, newframe)
        else:
          raise Exception("invalid expr:", self.var)
        result = self.body.eval(newframe)
    return result
