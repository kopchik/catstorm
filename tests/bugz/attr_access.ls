#!/usr/bin/env storm.py

# /usr/local/bin/storm.py:130: <module>():
# /home/exe/github/catstorm/interpreter.py:585: Func.Call(self, args, frame):
# /home/exe/github/catstorm/interpreter.py:604: Block.eval(self, frame):
# /home/exe/github/catstorm/interpreter.py:321: Print.eval(self, frame):
# /home/exe/github/catstorm/interpreter.py:585: Func.Call(self, args, frame):
# /home/exe/github/catstorm/interpreter.py:604: Block.eval(self, frame):
# /home/exe/github/catstorm/interpreter.py:346: Add.eval(self, frame):
# /home/exe/github/catstorm/interpreter.py:61: Str.Add(self, other):
# AttributeError: 'Obj' object has no attribute 'value'

::class Class
  New = value ->
    @value = value
  to_str = ->
    "the " + @value

main = progname, argv ->
  o = Class . "test"
  assert (o@to_str!) == "the test"
  ret 0