main = progname, args ->
  # check if quoted strings are correctly parsed
  s = "\"!\""

  # test interpolation and chaining
  a = 1
  b = 2
  s = " {a} {b} "@strip!
  assert s == "{a} {b}"

  # iteration
  s = "123"
  a = []
  for char in s
    a <<< char
  assert a == ["1", "2", "3"]
  ret 0
