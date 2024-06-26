#!/usr/bin/env python3

import argparse
import sys

from .frame import Frame
from .grammar import PROG
from .indent_parser import indent_parse
from .interpreter import (
    Array,
    Assign,
    Attr,
    Block,
    Call,
    Call0,
    CallObj,
    Comma,
    DictTPL,
    GetAttr,
    Int,
    Print,
    SetAttr,
    Str,
    This,
    Var,
)
from .log import Log, logfilter
from .peg import tokenize
from .pratt import precedence
from .prettybt import prettybt
from .syntax_tree import BaseNode, pprint

log = Log("main")


def parse(tree, blk, tokens):
    """Traverse raw AST tree and parse it."""
    for e in tree:
        if isinstance(e, list):
            assert hasattr(prog, "body"), f"cannot add statement {e} to {prog}"
            parse(e, prog.body, tokens)
        else:
            try:
                tokens = tokenize(e)
                prog, r = PROG.match(tokens)
                if r != len(tokens):
                    raise Exception("Not all tokens were consumed. Trailing garbage?")
                if not prog:  # skip comments # TODO: make it better
                    continue
                blk.append(prog)
            except Exception as err:
                raise Exception(f"line {e.lineno}: {e}\n{err}")


def traverse(tree, f):
    for i, e in enumerate(tree):
        r = f(e)
        if isinstance(r, BaseNode):
            traverse(r, f)
        tree[i] = r


def rewrite(tree):
    def set_attr(elem):
        if not isinstance(elem, Assign) or not isinstance(elem.left, Attr):
            return elem
        obj = elem.left.left
        attr_name = elem.left.right.value
        value = elem.right
        return SetAttr(obj, attr_name, value)

    traverse(tree, set_attr)

    def get_attr(elem):
        if not isinstance(elem, This):
            return elem
        assert isinstance(elem.arg, Var), type(elem.arg)
        obj = Var("this")
        attr_name = elem.arg.value
        return GetAttr(obj, attr_name)

    traverse(tree, get_attr)

    def set_attr(elem):
        if not isinstance(elem, Assign) or not isinstance(elem.left, GetAttr):
            return elem
        obj = elem.left.obj
        attr_name = elem.left.attr_name
        value = elem.right
        return SetAttr(obj, attr_name, value)

    traverse(tree, set_attr)

    empty_args = Comma(flatten=False)

    def call_obj0(e):
        """Call object method without args."""
        if isinstance(e, Call0) and isinstance(e.arg, Attr):
            arg = e.arg
            obj = arg.left
            meth_name = arg.right.value
            return CallObj(obj, meth_name, empty_args)
        else:
            return e

    traverse(tree, call_obj0)

    def comma_args(e):
        """Ensure function arguments is a list."""
        if isinstance(e, Call) and not isinstance(e.right, Comma):
            callee = e.left
            args = Comma(e.right, flatten=False)
            return Call(callee, args)
        else:
            return e

    traverse(tree, comma_args)

    def call_obj(e):
        """Methods are called with CallObj, not Call."""
        if isinstance(e, Call) and isinstance(e.left, Attr):
            arg = e.left
            obj = arg.left
            meth_name = arg.right.value
            args = e.right
            # if not isinstance(args, Comma):
            #   args = Comma(args, flatten=False)
            return CallObj(obj, meth_name, args)
        else:
            return e

    traverse(tree, call_obj)

    def dict_rewrite(e):
        if isinstance(e, DictTPL) and isinstance(e[0], Comma):
            items = e[0]
            del e[0]
            e.extend(items)
        return e

    traverse(tree, dict_rewrite)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--tokens",
        action="store_const",
        const=True,
        default=False,
        help="show tokens",
    )
    parser.add_argument(
        "-a",
        "--ast",
        action="store_const",
        const=True,
        default=False,
        help="show abstract syntax tree",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_const",
        const=True,
        default=False,
        help="show intermediate output",
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_const",
        const=True,
        default=False,
        help="do not execute the program",
    )
    parser.add_argument(
        "-p",
        "--op-prio",
        action="store_const",
        const=True,
        default=False,
        help="print operator precedence",
    )
    parser.add_argument(
        "-b",
        "--pretty-bt",
        action="store_const",
        const=True,
        default=True,
        help="print python exceptions with custom backtrace formatter",
    )
    parser.add_argument(
        "-l",
        "--recursion-limit",
        action="store_const",
        const=True,
        default=False,
        help="set strict recursion limit (for debugging)",
    )
    # parser.add_argument('-c', '--check-types', action='store_const', const=True,
    # default=False, help="perform type inference and checking (disabled by
    # default)")
    parser.add_argument(
        "-r", "--raw", help="specify raw expression to execute", nargs="*"
    )
    parser.add_argument("cmd", nargs="*")

    args = parser.parse_args()
    if args.debug:
        print("arguments:", args)

    if args.op_prio:
        prec = sorted(precedence, key=lambda x: x[2])
        for typ, op, prio in prec:
            print("{:<10} {:4}   {}".format(op, prio, typ))

    if not (args.cmd or args.raw):
        if args.dry_run:
            sys.exit("Nothing to do, bye! :-*")
        sys.exit("please specify [input] or --raw ..")
    if args.cmd and args.raw:
        sys.exit("[input] and --raw are mutually exclusive")

    logfilter.rules = [
        # ('interpreter.*', False),
        # ('indent.*', False)
    ]

    if args.debug:
        logfilter.default = True
    else:
        logfilter.default = False

    if args.recursion_limit:
        sys.setrecursionlimit(55)

    if args.pretty_bt:
        sys.excepthook = prettybt

    # INPUT FROM COMMAND LINE
    if args.raw:
        with Frame() as frame:
            for i, src in enumerate(args.raw, 1):
                # parse
                if args.debug:
                    print("parsing:", src)
                tokens = tokenize(src)
                if args.tokens:
                    print("tokens:", tokens)
                prog, r = PROG.match(tokens)
                prog = Block(prog)

                if args.ast:
                    print("BEFORE TREE REWRITE")
                    print(pprint(prog))

                rewrite(prog)

                if args.ast:
                    print("AFTER TREE REWRITE")
                    print(pprint(prog))

                # execute
                if not args.dry_run:
                    result = prog.eval(frame)
                    print("result of expr %s:" % i, result)
        sys.exit()

    # INPUT FROM FILE
    # parse the file
    with open(args.cmd[0]) as f:
        src = f.read()
    indented = indent_parse(src)
    mainblk = Block()
    parse(indented, mainblk, args.tokens)

    if args.ast:
        print("BEFORE TREE REWRITE")
        print(pprint(mainblk))

    rewrite(mainblk)

    if args.ast:
        print("AFTER TREE REWRITE")
        print(pprint(mainblk))

    # exit if code execution not required
    if args.dry_run:
        sys.exit(0)

    # execute the code
    with Frame() as frame:
        mainblk.eval(frame)
        progname = Str(args.cmd[0])
        cmd = [Str(s) for s in args.cmd[1:]]
        ret = frame["main"].Call((progname, Array(*cmd)), frame)

    # make proper exit status
    if isinstance(ret, Int):
        sys.exit(ret.value)
    else:
        Print(ret).eval({}) and exit(1)


if __name__ == "__main__":
    main()
