#!/usr/bin/env python3

from pratt import pratt_parse
from indent import indent_parse
from log import Log, logfilter
from grammar import PROG, operators
from peg import tokenize
from frame import Frame
from ast import pprint

from interpreter import Block, Int, Str, Array, Print

from sys import exit, setrecursionlimit
import argparse

log = Log("main")

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
  parser.add_argument('-l', '--recursion-limit', action='store_const', const=True,
                      default=False, help="set strict recursion limit (for debugging)")
  # parser.add_argument('-c', '--check-types', action='store_const', const=True,
  #                     default=False, help="perform type inference and checking (disabled by default)")
  parser.add_argument('-r', '--raw', help="specify raw expression to execute",
                      nargs="*")
  parser.add_argument('cmd', nargs="*")
  args = parser.parse_args()
  if args.debug:
    print("arguments:", args)

  if not (args.cmd or args.raw):
    exit("please specify [input] or --raw ..")
  if args.cmd and args.raw:
    exit("[input] and --raw are mutually exclusive")


  logfilter.rules = [
    # ('interpreter.*', False),
    # ('indent.*', False)
  ]

  if args.debug: logfilter.default = True
  else:          logfilter.default = False

  if args.recursion_limit:
    setrecursionlimit(40)

  if args.debug:
    prio = []
    # import pdb; pdb.set_trace()
    for op in operators:
      op = op.conv
      if hasattr(op, 'lbp'):
        prio.append((op, op.lbp))
      if hasattr(op, 'rbp'):
        prio.append((op, op.rbp))
    prio.sort(key=lambda x: x[1])
    for sym, op in prio:
      print("{:<10} {}".format(sym.sym, op))
    # log.debug("registered operators: %s" % )

  # INPUT FROM COMMAND LINE
  if args.raw:
    with Frame() as frame:
      for i, src in enumerate(args.raw, 1):
        # parse
        if args.debug:
          print("parsing:", src)
        tokens = tokenize(src)
        if args.tokens:
          print(tokens)
        prog, r = PROG.match(tokens)
        if args.ast:
          print(pprint(prog))
        # execute
        if not args.dry_run:
          result = prog.eval(frame)
          print("result of expr %s:" % i, result)
    exit()


  # INPUT FROM FILE
  # parse the file
  def traverse(tree, blk):
    """ Traverse raw AST tree and parse it. """
    for e in tree:
        if isinstance(e, list):
          assert hasattr(prog, 'body'), "cannot add statement %s to %s" % (e, prog)
          traverse(e, prog.body)
        else:
          try:
            tokens = tokenize(e)
            if args.tokens:
              print(tokens)
            prog, r = PROG.match(tokens)  # TODO: check r
            if r != len(tokens):
              raise Exception("Not all tokens were consumed. Trailing garbage?")
            if not prog:  # skip comments # TODO: make it better
              continue
            blk.append(prog)
          except Exception as err:
            raise Exception("line %s: %s\n%s" %(e.lineno, e, err))

  with open(args.cmd[0]) as fd:
    src = fd.read()
  indented = indent_parse(src)
  mainblk = Block()
  traverse(indented, mainblk)
  if args.ast:
    print(pprint(mainblk))

  if args.dry_run:
    exit(0)

  # execute the code
  with Frame() as frame:
    mainblk.eval(frame)
    progname = Str(args.cmd[0])
    cmd = [Str(s) for s in args.cmd[1:]]
    ret = frame['main'].Call((progname, Array(*cmd)), frame)

  # make proper exit status
  if isinstance(ret, Int):
    exit(ret.value)
  else:
    Print(ret).eval({}) and exit(1)
