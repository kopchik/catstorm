#!/usr/bin/env python3
from peg import RE, SYM, ANY, SOMEOF, MAYBE, CSV, test
from interpreter import Int, Str, Func, Var, TypeExpr, Class, ForLoop
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
FLOATCONST = RE(r'\d+\.\d*', 'FLOATCONST', conv=float)
INTCONST = RE(r'\d+', 'INTCONST', conv=Int)
STRCONST = RE(r'"((?:\"|.)*)"', 'STRCONST', conv=Str)
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
  op = SYM(sym, conv=symap[sym])
  operators.append(op)
  opmap[sym] = op
OPS = ANY(*operators)

# SOME COMMONLY USED SYMBOLS
ASSIGN = opmap.get('=', SYM('='))
BITOR = opmap.get('|', SYM('|'))
COMMA = opmap.get(',', SYM(','))
LAMBDA = opmap.get('->', SYM('->'))
COLON = opmap.get(':', SYM(':'))
NEWTYPE = SYM('::')

# CLASS STUFF
CLASS = NEWTYPE%None + SYM('class')%None + ID

# EXPRESSIONS
EXPR = SOMEOF(OPS, ID/Var, CONST)

# FUNCTIONS
FUNC = ID%'name' + ASSIGN%None + MAYBE(CSV(ID, sep=COMMA))%'args' + LAMBDA%None + MAYBE(EXPR%'body')

# FOR LOOP
FORLOOP = KW('for ') + EXPR + KW('in ') + EXPR + MAYBE(COLON)

# A PROGRAM IS ... A BUNCH OF FUNCTIONS, CLASSES AND EXPRESSIONS
PROG = COMMENT%None | FUNC/Func | EXPR/pratt_parse | FORLOOP/ForLoop | CLASS/Class


if __name__ == '__main__':
  test(COMMENT, "# test", verbose=True)
