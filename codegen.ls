#!/usr/bin/env storm.py

# This supposed to be a catstorm written ... in castorm.
# But right now it's a testing area for the language.

::class Print
  New = arg ->
    @arg = arg
  to_str = ->
    "print {@arg}"

::class Str
  New = value ->
    @value = value
  to_str = ->
    ret "STRRRRR"

nails = "(Print (Str \"test test test\"))"
# nails = "(Str \"test\")"


main = prog, args ->
  traverse = stream ->
    tokens = []
    for type, value in stream
      # p "{type} {value}"
      if (type == "id") or (type == "string")
        tokens <<< value
      if (type == "op" and value == "(")
        tokens <<< (traverse . stream)
      if (type == "op" and value == ")")
        if tokens[0] == "Str"
          # p tokens
          ret Str . tokens[1]
        if tokens[0] == "Print"
          ret Print . tokens[1]
        ret tokens
    ret tokens

  tokens = nails@tokenize!
  it = tokens@Iter!
  r = traverse . it
  x = r[0]
  p x@to_str!
  #p x@arg
  ret 0
