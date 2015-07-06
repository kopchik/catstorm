# test access to python classes
main = name, args ->
  s = " abc "
  assert s@strip! == "abc"
  0