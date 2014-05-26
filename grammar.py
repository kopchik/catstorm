#!/usr/bin/env python3
from peg import *

# BITS AND PIECES
EOL = RE(r'$')

# KEWORDS
IF   = SYM('if', 'IF')
THEN = SYM('then', 'THEN')
ELSE = SYM('else', 'ELSE')
COMMA = SYM(',', 'COMMA')
BRANCH = IF | THEN | ELSE

# DATA AND TYPES
TYPE = RE(r'[A-Z][A-Za-z0-9_]*', 'TYPE')
ID = RE(r'[a-z_][A-Za-z0-9_]*', 'ID')
FLOATCONST = RE(r'\d+\.\d*', 'FLOATCONST', conv=float)
INTCONST = RE(r'\d+', 'INTCONST', conv=int)
STRCONST   = RE(r'"(.*)"', 'STRCONST')
SHELLCMD   = RE(r'`(.*)`', 'SHELLCMD')
REGEX      = RE(r'/(.*)/', 'REGEX')
CONST = FLOATCONST | INTCONST | STRCONST | SHELLCMD | REGEX

# OPERATORS
ASSIGN = SYM('=', 'ASSIGN')
PLUS = SYM('+', 'PLUS')
MINUS = SYM('-', 'MINUS')
MUL = SYM('*', 'MUL')
DIV = SYM('/', 'DIV')
ARITHMETIC = ASSIGN | PLUS | MINUS | MUL | DIV

EQ = SYM('==', 'EQ')
GT = SYM('>', 'GT')
LT = SYM('<', 'LT')
LE = SYM('<=', 'LE')
GE = SYM('>=', 'GE')
BOOL =  GE | LE | GT | LT | EQ

BITAND = SYM('&', 'BITAND')
BITOR = SYM('|', 'BITOR') 
BITXOR = SYM('^', 'BITXOR')
BITOPS = BITAND | BITOR | BITXOR

# SPECIAL
LAMBDA = SYM('->', 'LAMBDA')
NEWTYPE = SYM('::')
OPS = LAMBDA | ARITHMETIC | BITOPS | BOOL

# PARENS
LP = SYM('(')
RP = SYM(')')
PARENS = LP | RP

# EXPRESSIONS
EXPR = SOMEOF(OPS, PARENS, ID, BRANCH, CONST)
# TYPES
TYPEDEF = TYPE%'tag' + MAYBE(SOMEOF(TYPE))%'members'
TYPEXPR = NEWTYPE + TYPE%'typname' + ASSIGN + CSV(TYPEDEF, sep=BITOR)%'variants'
# FUNCTIONS
FUNC = CSV(ID, sep=COMMA)%'args' + LAMBDA + EXPR%'body'
# THE PROGRAM IS ... A BUNCH OF FUNCTIONS AND TYPE EXPRESSIONS
PROG = FUNC%'func' | TYPEXPR%'typexpr'

if __name__ == '__main__':
  # test(EXPR, "(1+1) if 2+2 else 3")
  # test(TYPEXPR, ":: MyType = Tag1 Int | Tag2")
  test(PROG, "x -> x+1")