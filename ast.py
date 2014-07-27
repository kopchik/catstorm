"""
It was imported from DeadScript.
It is a bit complicated to support iteration
over AST elements.

TODO: revise it, may be we do not need it anymore.
"""

class Leaf:
  """ Base class for AST elements that do not support
      iteration over them.
  """
  lbp = 1
  def __init__(self, value=None):
    assert not hasattr(self, 'fields'), \
      "Leaf subclass cannot have fields attribute (it's not a Node)"
    self.value = value
    super().__init__()

  def __repr__(self):
    cls = self.__class__.__name__
    return "%s(%s)" % (cls, self.value)

  def nud(self):
    return self

  def led(self, left):
    print("on the left", left)
    return left


class Node:
  """
  Base class for most syntax elements.
  Supports access to the elements through attributes or through iteration.
  Names of attributes to be specified in class.fields.
  """
  fields = []

  def __init__(self, *args):
    if len(args) != len(self.fields):
      raise Exception("Number of arguments mismatch defined fields")
    for name, value in zip(self.fields, args):
      setattr(self, name, value)

  def __setattr__(self, name, value):
    if name not in self.fields:
      raise AttributeError("Unknown attribute \"%s\" for %s (%s)" % (name, type(self), self.fields))
    super().__setattr__(name, value)

  def __dir__(self):
    return self.fields

  def __repr__(self):
    cls = self.__class__.__name__
    args = ", ".join("%s=%s"%(name, getattr(self,name)) for name in self.fields)
    return "%s(%s)" % (cls, args)


class ListNode(list):
  """ Represents a node that is just a list of something. """
  fields = None

  def __repr__(self):
    cls = self.__class__.__name__
    return "%s(%s)" % (cls, ", ".join(map(str,self)))


class Unary(Node):
  """ Base class for unary operators. """
  fields = ['arg']


class Binary(Node):
  """ Base class for binary operators. """
  fields = ['left', 'right']
