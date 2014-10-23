#!/usr/bin/env python3
from peg import RE, SYM, ANY, SOMEOF, MAYBE, CSV, test
from interpreter import Int, StrTPL, Func, Var, NewADT, \
  Class, If, ForLoop, Case
from pratt import symap, pratt_parse


# BITS AND PIECES
EOL = RE(r'$')

def KW(keyword):
  """ Consumes keyword from input, but returns Nothing. """
  return SYM(keyword)%None


# COMMENTS
SHELLCOMMENT = RE(r'\#.*', "COMMENT")
CPPCOMMENT   = RE(r'//.*', "COMMENT")
CCOMMENT     = RE(r'/\*.*?\*/', "COMMENT")
COMMENT = SHELLCOMMENT | CCOMMENT | CPPCOMMENT

# DATA AND TYPES
ID = RE(r'[A-Za-z][A-Za-z0-9_]*', 'ID')
FLOATCONST = RE(r'\d+\.\d*', 'FLOAT', conv=float)
INTCONST = RE(r'\d+', 'INT', conv=Int)
STRCONST   = RE(r'"((?:\\.|[^"\\])*)"', 'STRCONST', conv=StrTPL)
SHELLCMD   = RE(r'`(.*?)`', 'SHELLCMD')
REGEX      = RE(r'/(.*?)/', 'REGEX')
CONST = FLOATCONST | INTCONST | STRCONST | SHELLCMD | REGEX

# OPERATORS
operators = []
opmap = {}  # map symbols to ast nodes (or so)
""" We sort elements because for PEG parsers first-match-wins.
    We must be sure that, e.g., '->' will be parsed as '->' and not
    as '-' and '>'. For this, we first try longer operators.        """
for sym in sorted(symap.keys(), key=len, reverse=True):
  op = SYM(sym, conv=symap[sym], prio=1)
  operators.append(op)
  opmap[sym] = op
OPS = ANY(*operators)

def MAKEKW(sym, **kwargs):
  return opmap.get(sym, SYM(sym, **kwargs))%None

# SOME COMMONLY USED SYMBOLS
ASSIGN  = MAKEKW('=')
PIPE    = MAKEKW('|', prio=0)
COMMA   = opmap.get(',', SYM(','))
LAMBDA  = MAKEKW('->', prio=2)
COLON   = opmap.get(':', SYM(':'))
# THEN    = opmap.get('=>', SYM('=>'))
NEWTYPE = MAKEKW('::', prio=2)

# CLASS STUFF
CLASS = NEWTYPE + KW('class') + ID

# ADT
UNION = ID%'name' & MAYBE(CSV(ID, sep=COMMA))%'members'
ADT = NEWTYPE + SYM('adt')%None + ID%'name' + ASSIGN%None + CSV(UNION,sep=PIPE)%'variants'

# EXPRESSIONS
EXPR = SOMEOF(OPS, ID/Var, CONST)

# FUNCTIONS
FUNC = ID%'name' + ASSIGN%None + MAYBE(CSV(ID, sep=COMMA))%'args' + LAMBDA%None + MAYBE(EXPR%'body')

# FOR LOOP
FORLOOP = KW('for ') + EXPR + KW('in ') + EXPR + MAYBE(COLON)

# A PROGRAM IS ... A BUNCH OF FUNCTIONS, CLASSES AND EXPRESSIONS
PROG = COMMENT%None | FUNC/Func | EXPR/pratt_parse | FORLOOP/ForLoop | CLASS/Class | ADT/NewADT


if __name__ == '__main__':
  test(COMMENT, "# test", verbose=True)
