#!/usr/bin/env catstorm

# catstorm:130: <module>():
# /home/exe/github/catstorm/interpreter.py:585: Func.Call(self, args, frame):
# /home/exe/github/catstorm/interpreter.py:604: Block.eval(self, frame):
# /home/exe/github/catstorm/interpreter.py:321: Print.eval(self, frame):
# /home/exe/github/catstorm/interpreter.py:585: Func.Call(self, args, frame):
# /home/exe/github/catstorm/interpreter.py:604: Block.eval(self, frame):
# /home/exe/github/catstorm/interpreter.py:346: Add.eval(self, frame):
# /home/exe/github/catstorm/interpreter.py:61: Str.Add(self, other):
# AttributeError: 'Obj' object has no attribute 'value'

#running tests/bugz/attr_access.ls
#catstorm:130: <module>():
#/home/exe/github/catstorm/interpreter.py:610: Func.Call(self, args, frame):
#/home/exe/github/catstorm/interpreter.py:629: Block.eval(self, frame):
#/home/exe/github/catstorm/interpreter.py:881: Assert.eval(self, frame):
#/home/exe/github/catstorm/interpreter.py:349: Eq.eval(self, frame):
#/home/exe/github/catstorm/interpreter.py:457: Parens.eval(self, frame):
#/home/exe/github/catstorm/interpreter.py:510: Call0.eval(self, frame):
#/home/exe/github/catstorm/interpreter.py:610: Func.Call(self, args, frame):
#/home/exe/github/catstorm/interpreter.py:629: Block.eval(self, frame):
#/home/exe/github/catstorm/interpreter.py:350: Add.eval(self, frame):
#/home/exe/github/catstorm/interpreter.py:713: Self.eval(self, frame):
#/home/exe/github/catstorm/frame.py:28: Frame.__getitem__(self, key):
#/home/exe/github/catstorm/frame.py:28: Frame.__getitem__(self, key):
#/home/exe/github/catstorm/frame.py:24: Frame.__getitem__(self, key):
#KeyError: 'self'


::class Class
  New = value ->
    @value = value
  to_str = ->
    "the " + @value

main = progname, argv ->
  o = Class . "test"
  assert (o@to_str!) == "the test"
  ret 0
