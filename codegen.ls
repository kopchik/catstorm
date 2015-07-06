#!/usr/bin/env storm.py

# This supposed to be a catstorm written ... in castorm.
# But right now it's a testing area for the language.


# example how to traverse expressons
nails = "(Print (Str \"test test test\"))"
# nails = "(Str \"test\")"

traverse = stream ->
  tokens = []
  for type, value in stream
    # p "{type} {value}"
    if type == "id" or type == "string"
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


::class Print
  New = arg ->
    @arg = arg
  to_str = ->
    "Print({@arg})"


::class Str
  New = value ->
    @lbp = 0
    @value = value
  to_str = ->
    ret "Str({@value})"


::class Op
  New = value ->
    @lbp = 1
    @value = value
  to_str = ->
    ret "Op({@value})"


::class Parser
  New = tokens ->
    tokens = tokens@Iter!
    @tokens = tokens
    @nxt = tokens@next!
    @cur = tokens@next!

  advance = ->
  expr = ->
  to_str = ->
    "Parser({@tokens} {@cur} {@nxt})"


# convert string into a list of tokens
pass1 = str ->
  tokens = str@tokenize!
  result = []
  for type, value in tokens
    # p "{type} {value}"
    if type == "id"
      result <<< Str . value
    if type == "op"
      result <<< Op . value
  ret result


# perform operator priority parsing
pass2 = tokens ->
  TODO

main = prog, args ->
  src = "a + b"
  p tokens = pass1 . src

  p parser = Parser . tokens
  ret 0



  # it = tokens@Iter!
  # r = traverse . it
  # p r@to_str!
  # #p x@arg
  # ret 0
