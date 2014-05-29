#!/usr/bin/env python3
from peg import RE, SYM, ANY, SOMEOF, MAYBE, CSV, test
from interpreter import Int, Str, Func, Expr, Var, TypeExpr
from pratt import symap, pratt_parse

# BITS AND PIECES
EOL = RE(r'$')

# COMMENTS
SHELLCOMMENT = RE(r'\#.*', "COMMENT")
CPPCOMMENT   = RE(r'//.*', "COMMENT")
CCOMMENT     = RE(r'/\*.*?\*/', "COMMENT")
COMMENT = SHELLCOMMENT | CCOMMENT | CPPCOMMENT


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
opmap = {}
""" We sort elements because for PEG parsers first-match-wins.
    We must be sure that, e.g., '->' will be parsed as '->' and not
    as '-' and '>'. For this, we first try longer operators.        """
for sym in sorted(symap.keys(), key=len, reverse=True):
  op = SYM(sym, conv=symap[sym])
  operators.append(op)
  opmap[sym] = op
OPS = ANY(*operators)


ASSIGN = opmap['=']
BITOR = opmap.get('|', SYM('|'))
COMMA = opmap.get(',', SYM(','))
LAMBDA = opmap.get('->', SYM('->'))

# EXPRESSIONS
EXPR = SOMEOF(OPS, ID/Var, CONST)
# TYPES
NEWTYPE = SYM('::')
TYPEDEF = TYPE%'tag' * (MAYBE(SOMEOF(TYPE))%'members')
TYPEXPR = NEWTYPE%None + TYPE%'name' + ASSIGN%None + CSV(TYPEDEF, sep=BITOR)%'variants'
# FUNCTIONS
FUNC = ID%'name' + ASSIGN%None + CSV(ID, sep=COMMA)%'args' + LAMBDA%None + EXPR%'body'
# THE PROGRAM IS ... A BUNCH OF FUNCTIONS AND TYPE EXPRESSIONS
PROG = COMMENT%None | FUNC/Func | TYPEXPR/TypeExpr | EXPR/Expr


if __name__ == '__main__':
  test(COMMENT, "# test", verbose=True)