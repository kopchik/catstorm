#!/usr/bin/env storm.py

# This supposed to be a catstorm written ... in castorm.
# But right now it's a testing area for the language.

nails = "(Print (Str \"test\"))"

main = prog, args ->
  traverse = stream ->
    for type, value in stream
      p "{type}: {value}"
  traverse . (nails@tokenize!)
