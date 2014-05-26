#!/usr/bin/env python3
from peg import RE, SYM, ANY, SOMEOF, MAYBE, CSV, test
from interpreter import Int, Str
from pratt import symap, parse

# BITS AND PIECES
EOL = RE(r'$')

# DATA AND TYPES
TYPE = RE(r'[A-Z][A-Za-z0-9_]*', 'TYPE')
ID = RE(r'[a-z_][A-Za-z0-9_]*', 'ID')
FLOATCONST = RE(r'\d+\.\d*', 'FLOATCONST', conv=float)
INTCONST = RE(r'\d+', 'INTCONST', conv=Int)
STRCONST   = RE(r'"(.*?)"', 'STRCONST', conv=Str)
SHELLCMD   = RE(r'`(.*?)`', 'SHELLCMD')
REGEX      = RE(r'/(.*?)/', 'REGEX')
CONST = FLOATCONST | INTCONST | STRCONST | SHELLCMD | REGEX


operators = []
""" We sort elements because for PEG parsers first-match-wins.
    We must be sure that, e.g., '->' will be parsed as '->' and not
    as '-' and '>'. For this, we first try longer operators.        """
for sym in sorted(symap.keys(), key=len, reverse=True):
  operators += [SYM(sym, conv=symap[sym])]
OPS = ANY(*operators)


ASSIGN = SYM('=')
BITOR = SYM('|')
COMMA = SYM(',')
LAMBDA = SYM('->')

# EXPRESSIONS
EXPR = SOMEOF(OPS, ID, CONST)
# TYPES
NEWTYPE = SYM('::')
TYPEDEF = TYPE%'tag' + MAYBE(SOMEOF(TYPE))%'members'
TYPEXPR = NEWTYPE + TYPE%'typname' + ASSIGN + CSV(TYPEDEF, sep=BITOR)%'variants'
# FUNCTIONS
FUNC = ID%'name' + ASSIGN%None + CSV(ID, sep=COMMA)%'args' + LAMBDA%None + EXPR%'body'
# THE PROGRAM IS ... A BUNCH OF FUNCTIONS AND TYPE EXPRESSIONS
PROG = FUNC%'funcdef' | TYPEXPR%'typexpr' | EXPR%'expr'


if __name__ == '__main__':
  # import sys; sys.setrecursionlimit(20)

  # test(EXPR, "(1+1) if 2+2 else 3")
  # test(TYPEXPR, ":: MyType = Tag1 Int | Tag2")
  # prog = test(PROG, "myfunc = x -> x + 1")
  # print(prog)
  
  def traverse(ast, d=0):
    print("traversing", ast)
    if isinstance(ast, dict):
      obj = {}
      for k,v in ast.items():
        v = traverse(v, d+1)
        # setattr(obj, k, v)
        obj[k] = v
      return obj
    elif isinstance(ast, list):
      result = {}
      traversed = [traverse(v, d+1) for v in ast]
      if all(isinstance(e, dict) for e in traversed):
        for e in traversed:
          result.update(e)
      return result if result else traversed
    else:
      return ast

  # r = traverse(prog)
  # print(r)
  # test(PROG, ":: MyNewType = Tag1 | Tag2 Int64 Double")
  toks = test(PROG, "x = a,b,c -> y")
  print(toks)
  # print(parse(toks['expr']))
  # parse([Int(1),Plus(), Int(2)])