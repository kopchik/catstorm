#!/usr/bin/env catstorm

# This supposed to be a catstorm written ... in castorm.
# But right now it's a testing area for the language.


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
    "(Print {@arg})"


::class Str
  New = value ->
    @lbp = 1
    @value = value
  nud = ->
    ret this
  to_str = ->
    ret "(Str {@value})"


::class Op
  New = value ->
    @lbp = 20
    @value = value
    @left = NONE
    @right = NONE

  # nud = ->
  #   ret this
  #   nudval = @parser@expr . @lbp
  #   p "NUDVAL: {nudval}"
  #   ret nudval

  led = left->
    @left = left
    @right = @parser@expr . @lbp
    this
  to_str = ->
    "({@value} {@left} {@right})"


::class END
  New = ->
    @lbp = 0
  to_str = ->
    "END"


# register('+', infix_r, 10, Class)


::class Parser
  New = tokens ->
    end = END!
    tokens <<< end
    p "tokens: {tokens}"
    for tok in tokens
      p "!{tok}"
      tok@parser = this
    @tokens = tokens@Iter!
    @cur = @nxt = NONE
    @shift!

  shift = ->
    @cur = @nxt
    @nxt = @tokens@next!

  expr = rbp ->
    @shift!
    left = @cur@nud!
    p "expr rbp={rbp} left:{left}"
    while rbp < @nxt@lbp
      @shift!
      left = @cur@led . left
    left

  to_str = ->
    "Parser({@tokens} {@cur} {@nxt})"


# convert string into a list of tokens
tokenize = str ->
  tokens = str@tokenize!
  result = []
  for type, value in tokens
    # p "{type} {value}"
    if type == "id"
      result <<< Str . value
    if type == "op"
      result <<< Op . value
  ret result


main = prog, args ->
  src = "a + b + c"
  p tokens = tokenize . src

  parser = Parser . tokens
  p parser@expr . 0
  ret 0