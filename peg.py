#!/usr/bin/env python3
from collections import OrderedDict
from useful.mystruct import Struct
import re


class NoMatch(Exception):
  pass

symbols = []


def tokenize(text, pos=0):
  ''' Split input into a bunch of annotated tokens. '''
  result = []
  mysymbols = sorted(symbols, key=lambda x: x.pattern.pattern, reverse=True)
  while pos < len(text):
    for p in mysymbols:
      try:
        r, pos = p.tokenize(text, pos)
        result.append((r, p))
        break
      except NoMatch:
        pass
    else:
      raise NoMatch("cannot tokenize at pos %s, text: %s" % (pos, text))
  return result


#####################
# PARSER PRIMITIVES #
#####################

class Grammar:
  def __add__(self, other):
    if isinstance(self, ALL):
      self.things += [other]
      return self
    return ALL(self, other)

  def __or__(self, other):
    if isinstance(self, ANY):
      self.things += [other]
      return self
    return ANY(self, other)

  def __mod__(self, other):
    return Attr(self, attr=other)


class RE(Grammar):
  def __init__(self, pattern, name=None, conv=str):
    self.pattern = re.compile("\s*(%s)" % pattern)
    self.conv = conv
    self.name = name
    symbols.append(self)

  def tokenize(self, text, pos=0):
    m = self.pattern.match(text[pos:])
    if not m:
      raise NoMatch("syntax error", text, pos)
    text = m.groups()[-1]
    newpos = pos + m.end()
    return self.conv(text), newpos

  def match(self, tokens, pos=0):
    if pos >= len(tokens):
      raise NoMatch
    datum, tag = tokens[pos]
    if tag != self:
      raise NoMatch("%s != %s for %s" % (tag, self, datum))
    return datum, pos+1

  def __repr__(self):
    if self.name:
      return self.name
    cls = self.__class__.__name__
    return "%s(\"%s\", %s)" % \
      (cls, self.pattern.pattern, self.conv)


class SYM(RE):
  def __init__(self, symbol, *args, **kwargs):
    super().__init__(re.escape(symbol), *args, **kwargs)



########################
# HIGHER-ORDER PARSERS #
########################

class Composer(Grammar):
  def __init__(self, *things):
    self.things = list(things)

  def __repr__(self):
    cls  = self.__class__.__name__
    return "%s(%s)" % (cls, self.things)


class Attr(Composer):
  def __init__(self, thing, attr):
    super().__init__(thing)
    assert isinstance(attr, str) or attr == None, \
      "Attribute name should be a string or None"
    self.attr = attr

  def match(self, tokens, pos=0):
    r, pos = self.things[0].match(tokens, pos)
    if self.attr is None:
      return {}, pos
    return {self.attr: r}, pos 


class ALL(Composer):
  def match(self, tokens, pos=0):
    result = []
    for thing in self.things:
      r, pos = thing.match(tokens, pos)
      result += [r]
    return result, pos


class ANY(Composer):
  """ First match wins
  """
  def match(self, tokens, pos=0):
    for thing in self.things:
      try:
        return thing.match(tokens, pos)
      except NoMatch:
        pass
    raise NoMatch("syntax error", tokens, pos)


class SOMEOF(Composer):
  def match(self, tokens, pos=0):
    result = []
    while True:
      for thing in self.things:
        try:
          r, pos = thing.match(tokens, pos)
          result += [r]
          break  # break is neccessary because it's a PEG parser and the order does matter
        except NoMatch:
          pass
      else:
        break
    if not result:
      raise NoMatch("syntax error", tokens, pos)
    return result, pos


class MAYBE(Composer):
  def match(self, tokens, pos=0):
    assert len(self.things) == 1, "accepts only one arg"
    try:
      r, pos = self.things[0].match(tokens, pos)
      return r, pos
    except NoMatch:
      return [], pos


class CSV(Composer):
  def __init__(self, *args, sep=None,**kwargs):
    super().__init__(*args, **kwargs)
    assert sep, "sep is mandatory parameter"
    self.sep = sep

  def match(self, tokens, pos=0):
    result = []
    while True:
      try:
        r, pos = self.things[0].match(tokens, pos)
        result.append(r)
        r, pos = self.sep.match(tokens, pos)
      except NoMatch:
        if not result:
          raise
        break
    return result, pos


def test(expr, text):
  tokens = tokenize(text)
  print(tokens)
  r, pos = (expr).match(tokens)
  if pos != len(tokens):
    print("not all chars were consumed. Pattern:\n",
          expr, "\ntext:\n", text)
  print(r)
  return r


if __name__ == '__main__':
  INT = RE(r'\d+', 'INTCONST', conv=int)
  PLUS = SYM('+')
  test(INT, "1")
  test(SOMEOF(PLUS, INT), '+1')
  test(SOMEOF(PLUS, INT)%'expr', '+1')