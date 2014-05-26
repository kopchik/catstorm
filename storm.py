#!/usr/bin/env python3

from pratt import parse as pratt_parse
from grammar import EXPR, PROG
from log import logfilter
from peg import tokenize
from frame import Frame
from sys import exit
import argparse


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('-t', '--tokens', action='store_const', const=True,
                      default=False, help="show tokens")
  parser.add_argument('-a', '--ast', action='store_const', const=True,
                      default=False, help="show abstract syntax tree")
  parser.add_argument('-d', '--debug', action='store_const', const=True,
                      default=False, help="show intermediate output")
  parser.add_argument('-n', '--dry-run', action='store_const', const=True,
                      default=False, help="do not execute the program")
  parser.add_argument('-c', '--check-types', action='store_const', const=True,
                      default=False, help="perform type inference and checking (disabled by default)")
  # parser.add_argument('input', help="path to file")
  parser.add_argument('-r', '--raw', help="specify raw expression to execute",
                      nargs="*")
  parser.add_argument('cmd', nargs="*")
  args = parser.parse_args()

  logfilter.rules = [
    # ('interpreter.*', False),
    # ('indent.*', False)
  ]

  if args.debug: logfilter.default = True
  else:          logfilter.default = False

  if args.raw:
    with Frame() as frame:
      for src in args.raw:
        if args.debug:
          print("parsing:", src)
        tokens = tokenize(src)
        if args.tokens:
          print(tokens)
        prog, r = PROG.match(tokens)
        # print(tokens)
        # prog = pratt_parse(tokens)
        # print(prog)
        # print("PROG", prog)
        result = prog.eval(frame)
        print("result:", result)
    exit("DONE")

  with open(args.input) as fd:
    src = fd.read()

  # split source into tokens
  tokens = tokenize(src)
  if args.tokens:
    print(tokens)
  # parse indentation
  ast = indent_parse(tokens)
  # finalize AST generation
  ast = parse(ast)
  if args.ast:
    print(pretty_fmt(ast))
  # form main() arguments
  cmd = [args.input]+args.cmd
  # run the program
  if not args.dry_run:
    exit(run(ast, cmd, check_types=args.check_types))