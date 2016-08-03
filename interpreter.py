from pratt import pratt_parse, pratt_parse1, prefix, \
  infix, infix_r, postfix, nullary, ifelse, brackets, subscript
from ast import Leaf, Unary, Binary, Node, ListNode
from log import Log

from itertools import chain, repeat
import re

log = Log("interpreter")


##############
# MISC STUFF #
##############

class ReturnException(Exception):
  """ To be raised by ret operator. """


class NoMatch(Exception):
  """ To be raised by Switch/Case expressions. """


class NoAttr(Exception):
  """ When class or object doesn't have the attr. """


##############
# DATA TYPES #
##############

class CallWrap:
  def __init__(self, meth):
    self.meth = meth

  def Call(self, *args):
    r = self.meth()
    return r


class CallPython:
  """ Mixin that adds GetAttr to a class. This allows to work
      with objects that are not instances of Class/Obj.
      E.g., str.tokenize! would not work without this because
      Str is not an instance of Class/Obj.
  """

  def GetAttr(self, name):
    if isinstance(name, Var):
      name = name.to_py_str()
    assert isinstance(name, str)
    pymeth = getattr(self, name)
    return CallWrap(pymeth)


class Value(Leaf, CallPython):
  """ Base class for values. """

  def eval(self, frame):
    return self

  def Eq(self, other):
    return TRUE if self.value == other.value else FALSE

  def NotEq(self, other):
    return TRUE if self.value != other.value else FALSE

  def Gt(self, other):
    return TRUE if self.value > other.value else FALSE

  def Lt(self, other):
    return TRUE if self.value < other.value else FALSE

  def Add(self, other):
    return self.__class__(self.value + other.value)

  def Sub(self, right):
    return self.__class__(self.value - right.value)

  def Mul(self, right):
    return self.__class__(self.value * right.value)

  def to_bool(self):
    return TRUE if self.value else FALSE

  def to_str(self, frame=None):
    return Str(repr(self.value))

  def to_py_str(self):
    return str(self.value)

  def __repr__(self):
    return self.to_py_str()


class Var(Leaf):
  def Assign(self, value, frame):
    # self.value actually holds the name
    frame[self.value] = value
    return value

  def eval(self, frame):
    return frame[self.value]

  def to_py_str(self):
    return self.value

  def __str__(self):
    return str(self.value)


class Bool(Value):
  def __init__(self, value, name):
    super().__init__(value)
    self.name = name

  def eval(self, frame):
    return self

  def to_bool(self):
    return self

  def to_str(self, frame=None):
    return Str(self.name)

  def __repr__(self):
    return self.name

  def __bool__(self):
    return self.value

TRUE  = Bool(True, 'TRUE')
FALSE = Bool(False, 'FALSE')


@nullary('TRUE')
def return_true(whatever):
  return TRUE

@nullary('FALSE')
def return_false(whatever):
  return FALSE


@nullary('NONE')
class TheNone(Value):
  def to_bool(self):
    return FALSE

  def to_str(self, frame=None):
    return Str("NONE")

  def __repr__(self):
    return "NONE"
NONE = TheNone()


class Int(Value):
  def __init__(self, value):
    if isinstance(value, Int):
      value = value.value
    super().__init__(int(value))

  def Minus(self):
    return Int(-self.value)

  def to_py_int(self):
    return self.value


class Str(Value):
  def GetItem(self, attr):
    if isinstance(attr, Int):
      value = self.value[attr.to_py_int()]
    else:
      raise Exception("don't know how to access item %s" % attr)
    return self.__class__(value)

  def Iter(self):
    return Iter(Str(char) for char in self.value)

  def strip(self, frame=None):
    return Str(self.value.strip())

  def len(self):
    return Int(len(self.value))

  def tokenize(self, frame=None):
    result = Array()
    pattern = r"""\s*
       (?P<number>\d+)
      |(?P<id>\w+)
      |"(?P<string>(?:\\.|[^"\\])*)"
      |(?P<op>\S)
      """
    for match in re.findall(pattern, self.value.strip(), re.VERBOSE):
      number, id, string, op = match
      if number:
        e = Array(Str("number"), Int(number))
      elif id:
        e = Array(Str("id"), Str(id))
      elif string:
        e = Array(Str("string"), Str(string))
      elif op:
        e = Array(Str("op"), Str(op))
      result.Append(e)
    return result


class StrTPL(Value):
  """ Performs string expansion on eval() and returns Str obj.
  """
  replace = {r'\"':'"', r'\n': '\n', r'\t': '\t'}

  def __init__(self, value):
    self.value = str(value)  # TODO: do we need this?

  def eval(self, frame):
    # TODO: cannot import from top level due to circual dependences
    from peg import tokenize
    from grammar import PROG
    # perform string expansion
    string = self.value
    expressions = re.findall("\{(.+?)\}", string, re.M)
    for rawexpr in expressions:
        tokens = tokenize(rawexpr)
        expr, r = PROG.match(tokens)   # TODO: perform rewrite
        result = expr.eval(frame)
        as_str = result.to_str(frame=frame).to_py_str()
        string = string.replace("{%s}" % rawexpr, as_str)
    # replace special symbols
    for k,v in self.replace.items():
      string = string.replace(k, v)
    return Str(string)


class Iter(CallPython):
  def __init__(self, arr):
    self.iter = chain(arr, repeat(None))

  def eval(self, frame):
    return self

  def Iter(self):
    return self

  def next(self, frame=None):
    # TODO: stop iteration?
    return next(self.iter)

  def to_str(self, frame):
    return Str("<iter %s>" % id(self))


class Array(ListNode, CallPython):
  def GetItem(self, value, frame=None):
    if isinstance(value, Int):
      return self[value.to_py_int()]
    elif isinstance(value, Colon):
      # slice in form somevar[start:stop]
      if len(value) == 2:
        start, stop = value
        ret = self[start.to_py_int():stop.to_py_int()]
        return Array(*ret)
      # slice in form somevar[start:stop:step]
      elif len(Colon) == 3:
        raise NotImplemented("TODO: implement step")
    else:
     raise Exception("do not know how to apply subscript %s to %s" % \
                    (value, self))

  def SetItem(self, key, value):
    assert isinstance(key, Int)
    self[key.to_py_int()] = value
    return self

  def Append(self, value):
    if not isinstance(value, (Value, Array)):
      log.critical("xxx")
    self.append(value)
    return value

  def Eq(self, other):
    if  isinstance(other, Array) \
    and len(self) == len(other) \
    and all(a.Eq(b) for a, b in zip(self, other)):
      return TRUE
    return FALSE

  def Iter(self, frame=None):
    return Iter(self)

  def len(self, frame=None):
    return Int(len(self))

  def to_str(self, frame={}):
    return Str('[' + ", ".join(e.to_str(frame=frame).to_py_str() for e in self) + ']')

  def to_bool(self):
    return TRUE if self.value else FALSE

  def to_py_str(self):
    return self.to_str().to_py_str()


@brackets('[',']')
class ArrayNode(ListNode, CallPython):
  def __init__(self, arg=None):
    if arg is None: return
    if isinstance(arg, Comma):
      self.extend(arg)
    else:
      self.append(arg)

  def eval(self, frame):
    return Array(*[e.eval(frame) for e in self])


class Tuple(Array):
  def forbidden_operation(self, *args, **kwargs):
    raise Exception("Tuples are immutable, dude")
  Append = SetItem = forbidden_operation

  def Print(self, frame):
    return '(' + ", ".join(e.to_str() for e in self) + ')'  # TODO: reuse code from Array


#############
# OPERATORS #
#############

@prefix('ret ', 0)
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
    if isinstance(value, Obj):
      with frame as newframe:
        newframe['this'] = value
        to_str = value.GetAttr('to_str')
        s = to_str.Call([], newframe).to_py_str()
    else:
      s = value.to_str(frame=frame).to_py_str()
    print("P>", s)
    return value


def newinfix(sym, prio, methname, sametype=True, right=False):
  class Infix(Binary):
    def eval(self, frame):
      left = self.left.eval(frame)
      right = self.right.eval(frame)
      # TODO
      # if sametype:
      #   assert issubclass(type(left), type(right)), \
      #     "Left and right operands of ({} {} {}) must have same type.\n" \
      #     "(Or latter is subclass of former). Got {} and {}." \
      #     .format(left, sym, right, type(left), type(right))
      try:
        meth = getattr(left, methname)
      except AttributeError:
        raise Exception("{} does not have {} method, " \
                        "operation ({}) not supported".format(left, methname, sym))
      return meth(right)
  func = infix_r if right else infix
  Infix = func(sym, prio)(Infix)
  Infix.__name__ = Infix.__qualname__ = methname
  return Infix


newinfix('+', 20, 'Add')
newinfix('-', 20, 'Sub')
newinfix('*', 30, 'Mul')
newinfix('==', 4, 'Eq')
newinfix('!=', 4, 'NotEq')
newinfix('>', 3,  'Gt')
newinfix('<', 3,  'Lt')
newinfix('<<<',3, 'Append', sametype=False)


@infix_r('=', 2)
class Assign(Binary):
  def eval(self, frame):
    # TODO: many cases are absolete with tree rewrite
    # code below tries to distinct between
    # assigning to variable and to class member
    value = self.right.eval(frame)
    if isinstance(self.left, Var):
      key = self.left
      key.Assign(value, frame)
    elif isinstance(self.left, Attr):
      raise Exception("This should be handled by SetAttr")
      owner = self.left.left.eval(frame)
      key = self.left.right
      owner.SetAttr(key, value)
    elif isinstance(self.left, Subscript):
      owner = self.left.left.eval(frame)
      key = self.left.right.eval(frame)
      owner.SetItem(key, value)
    else:
      # this is very unlikely and should be caused by syntax error
      raise Exception("don't know what to do with expression %s = %s" % (self.left, self.right))
    return value


#########
# LOGIC #
#########

@infix('and', 2)
class And(Binary):
  def eval(self, frame):
    left = self.left.eval(frame)
    if not left.to_bool():
      return FALSE
    right = self.right.eval(frame)
    return right


@infix('or', 2)
class Or(Binary):
  def eval(self, frame):
    left = self.left.eval(frame)
    if left.to_bool():
      return left
    right = self.right.eval(frame)
    return right


@prefix('not', 3)
class Not(Unary):
  def eval(self, frame):
    value = self.arg.eval(frame)
    if value.to_bool():
      return FALSE
    return TRUE


@prefix('-', 100)
class Minus(Unary):
  def eval(self, frame):
    arg = self.arg.eval(frame)
    return arg.Minus()


########################
# PARENS AND SUBSCRIPT #
########################

@subscript('[',']', 1000)
class Subscript(Binary):
  def eval(self, frame):
    left = self.left.eval(frame)
    right = self.right.eval(frame)
    return left.GetItem(right)


@brackets('(',')')
class Parens(Unary):
  def eval(self, frame):
    return self.arg.eval(frame)


##############
# CONTAINERS #
##############

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


@infix(':', 6)
class Colon(CharSepVals):
  pass


class Dict(ListNode):
  def __init__(self, d):
    self.values = d
  def eval(self, frame):
    return self
  def to_str(self, frame=None):
    return ",".join("%s:%s"%(k,v) for k,v in self.result.items())

@brackets('{','}')
class DictTPL(ListNode):
  def eval(self, frame):
    result = {}
    for key,value in self:
      key = key.eval(frame)
      value = value.eval(frame)
      result[key] = value
    return Dict(result)

  def to_str(self, frame=None):
    ",".join("%s:%s"%(k,v) for k,v in self.result.items())


#############
# CALL SMTH #
#############

@postfix('!', 3)
class Call0(Unary):
  def eval(self, frame):
    with frame as newframe:
      callee = self.arg.eval(newframe)
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
    accepted = (Func, Class, NewADT, Union)
    assert isinstance(callee, accepted) or issubclass(callee, accepted), \
      "I can only call functions and classes, got %s (%s) instead" % (callee, type(callee))
    args = self.right.eval(frame)
    if not isinstance(args, Comma):
      args = [args]  # TODO: it's not a comma class
    with frame as newframe:
      return callee.Call(args, newframe)

  def match(self, pattern, frame):
    union = self.left.eval(frame)
    print(union, "PATTERN", pattern)
    raise NoMatch


#######
# ADT #
#######

class NewADT(Node):
  fields = ['name', 'variants']

  def __init__(self, name=None, variants=[]):
    self.name = name
    self.variants = []
    for variant in variants:
      class NewUnion(Union):
        tag = variant['name']
        members = variant['members'] or []  # TODO: hack
      self.variants.append(NewUnion)

  def eval(self, frame):
    for Union in self.variants:
      frame[Union.tag] = Union
    return NONE


class Union(Node, CallPython):
  fields = ['tag', 'members', 'values']
  def __init__(self, values):
    self.values = values

  @classmethod
  def Call(cls, values, frame):
    l1, l2 = len(cls.members), len(values)
    assert l1 == l2, \
        "\"{tag}\" accepts {l1} arguments, but given {l2}" \
        .format(tag=cls.tag, l1=l1, l2=l2)
    self = cls(values)
    return self

  def to_str(self, frame=None):
    return Str(self.to_py_str())

  def to_py_str(self):
    values = ",".join(map(str,self.values))
    return "{} {}".format(self.tag, values)

  # def match(self, pattern, frame):

#############
# FUNCTIONS #
#############

class Func(Node):
  fields = ['name', 'args', 'body']
  def __init__(self, name, args, body=[]):
    self.name = name
    self.args = args if args else []
    log.func.debug("pratt_parse on %s" % body)
    if body:
      self.body = Block(pratt_parse1(body))
    else:
      self.body = Block()

  def eval(self, frame):
    frame[self.name] = self
    return self

  def Call(self, args, frame):
    assert len(args) == len(self.args), \
      "The number of arguments must match the function signature.\n" \
      "Got {} ({}) instead of {} ({})." \
      .format(len(args), args, len(self.args), self.args)
    for k, v in zip(self.args, args):
      frame[k] = v
    return self.body.eval(frame)

  def to_str(self, frame=None):
    return Str("<func %s>" % self.name)


#########
# BLOCK #
#########

class Block(ListNode):
  def __init__(self, *args, catch_ret=True, **kwargs):
    self.catch_ret = catch_ret
    super().__init__(*args, **kwargs)

  def eval(self, frame):
    r = NONE
    for expr in self:
      try:
        r = expr.eval(frame)
      except ReturnException as e:
        if not self.catch_ret:
          raise
        r = e.args[0]
        break
    return r


#######################
# CLASSED AND OBJECTS #
#######################

classes = {}


class Class(Node):
  """ Define a new class. """
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
    obj = Obj()
    obj['Class'] = self
    with frame as newframe:
      newframe['this'] = obj
      self['New'].Call(args, newframe)
    return obj

  def to_str(self, frame=None):
    return Str(repr(self))

  def __repr__(self):
    return "<%s>" % self.name


class Obj(dict):
  """ Instance of the class (actually, it's a dict). """

  def GetAttr(self, name):
    if isinstance(name, Str):
      name = name.to_py_str()
    if name in self:
      return self[name]
    return self['Class'][name]

  def SetAttr(self, name, value):
    if isinstance(name, Str):
      name = name.to_py_str()
    elif isinstance(name, Var):
      name = name.value
    self[name] = value
    return value

  def to_str(self, frame):
    func = self.GetAttr(Str('to_str'))
    with frame as newframe:
      newframe['this'] = self
      return func.Call([], newframe)

  def to_py_str(self):
    return repr(self)

  def __repr__(self):
    return "(%s)" % (self['Class'].name)


## This code is not needed atm.
# class Bound:
#   """ Store methods bound to the specific object. """
#   def __init__(self, obj, attr):
#     self.obj = obj
#     self.attr = attr

#   def __getattr__(self, name):
#     return getattr(self.attr, name)

#   def Call(self, args, frame):
#     callee  = self.attr
#     with frame as newframe:
#       newframe['this'] = self.obj
#       if hasattr(callee, "Call"):
#         return callee.Call(args, newframe)
#       else:
#         return callee(newframe)


class GetAttr(Node):
  fields = ["obj", "attr_name"]
  def eval(self, frame):
    obj = self.obj.eval(frame)
    attr_name = self.attr_name
    assert isinstance(attr_name, str)
    return obj.GetAttr(attr_name)


class SetAttr(Node):
  fields = ["obj", "attr_name", "value"]
  def eval(self, frame):
    obj = self.obj.eval(frame)
    value = self.value.eval(frame)
    attr_name = self.attr_name
    assert isinstance(attr_name, str)
    obj.SetAttr(attr_name, value)


class CallObj(Node):
  fields = ["obj", "meth_name", "args"]
  def eval(self, frame):
    this = self.obj.eval(frame)
    args = self.args.eval(frame)
    with frame as newframe:
      newframe['this'] = this
      callee = this.GetAttr(self.meth_name)
      return callee.Call(args, newframe)


@prefix('@', 6)
class This(Unary):
  #TODO: absolete method after tree rewrite.
  def eval(self, frame):
    # import pdb; pdb.set_trace()
    this = frame['this']
    if isinstance(self.arg, Assign):
      name  = self.arg.left.value
      value = self.arg.right.eval(frame)
      return this.SetAttr(name, value)
    else:
      name = self.arg.value
      return this.GetAttr(name)


@infix('@', 5)
class Attr(Binary):
  #TODO: absolete method after tree rewrite
  def eval(self, frame):
    this = self.left.eval(frame)
    attr_name = self.right.value
    attr = this.GetAttr(attr_name)
    return attr


################
# CONTROL FLOW #
################

@ifelse(lbp=2)
class IfElse(Node):
  fields = ['cond', 'then', 'otherwise']
  def eval(self, frame):
    cond = self.cond.eval(frame)
    if cond.to_bool():
      return self.then.eval(frame)
    else:
      return self.otherwise.eval(frame)


@prefix('if', 1)
class If(Node):
  fields = ['clause', 'body']
  def __init__(self, clause, body=None):
    super().__init__(clause, body)
    self.clause = clause
    self.body = Block(catch_ret=False)
  def eval(self, frame):
    clause = self.clause.eval(frame).to_bool()
    if clause:
      return self.body.eval(frame)


@nullary('switch')
class Switch(Node):
  fields = ['body']

  def __init__(self, unused):
    self.body = Block(catch_ret=False)

  def eval(self, frame):
    for expr in self.body:
      try:
        return expr.eval(frame)
      except NoMatch:
        continue
    raise NoMatch("switch statement: no match")


@prefix('|',0)
class Guard(Unary):
  def eval(self, frame):
    return self.arg.eval(frame)

  def match(self, data, frame):
    return self.arg.match(data, frame)


@prefix('match', 0)
class Match(Node):
  fields = ['var', 'body']

  def __init__(self, var):
    self.var = var
    self.body = Block(catch_ret=False)

  def eval(self, frame):
    tag = self.var.eval(frame)
    for guard in self.body:
    #   assert isinstance(guard, Guard), \
    #       "body of match statement should have only Guards"
    #   try:
    #     return guard.match(data, frame)
    #   except NoMatch:
    #     pass
    # else:
    #   # raise NoMatch("cannot match %s" % data)
    #   return NONE

      case = guard.arg
      cond = case.cond
      pattern_name = cond.left.value
      pattern_args = cond.right
      if pattern_name == tag.tag:
        if not isinstance(pattern_args, Comma):
          pattern_args = [pattern_args]
        for name, value in zip(pattern_args, tag.values):
          frame[name.value] = value
        return case.body.eval(frame)
    return NONE


@infix('=>', 4)
class Case(Binary):
  fields = ['cond', 'body']

  def __init__(self, cond, body):
    self.cond = pratt_parse(cond)
    self.body = Block(pratt_parse(body), catch_ret=False)

  def eval(self, frame):
    if not self.cond.eval(frame).to_bool():
      raise NoMatch
    return self.body.eval(frame)

  def match(self, data, frame):
    with frame as newframe:
      self.cond.match(data, newframe)
      return self.body.eval(newframe)

#########
# LOOPS #
#########

class ForLoop(Node):
  fields = ['var', 'expr', 'body']
  def __init__(self, var, expr, body=None):
    self.var  = pratt_parse1(var)
    self.expr = pratt_parse1(expr)
    if body:
      self.body = Block(pratt_parse1(body), catch_ret=False)
    else:
      self.body = Block(catch_ret=False)
    log.forloop.debug("got var=%s expr=%s body=%s" \
                      % (self.var, self.expr, self.body))

  def eval(self, frame):
    expr = self.expr.eval(frame)
    iterator = expr.Iter()
    result = NONE
    with frame as newframe:
      while True:
        e = iterator.next()
        if e is None:
          break

        if isinstance(self.var, Var):
          self.var.Assign(e, newframe)
        elif isinstance(self.var, Comma):
          assert e.len().to_py_int() == len(self.var)
          for var, value in zip(self.var, e):
            var.Assign(value, newframe)
        else:
          raise Exception("invalid expr:", self.var)
        result = self.body.eval(newframe)
    return result


class WhileLoop(Node):
  fields = ['expr', 'body']
  def __init__(self, expr):
    self.expr = pratt_parse1(expr)
    self.body = Block(catch_ret=False)

  def eval(self, frame):
    while self.expr.eval(frame):
      self.body.eval(frame)

########
# MISC #
########

@prefix('assert', 0)
class Assert(Unary):
  def eval(self, frame):
    r = self.arg.eval(frame)
    if not isinstance(r, Bool):
      print("warning, asserting on not bool")
    if not r.to_bool():
      raise Exception("Assertion failed on %s" % self.arg)
    return r
