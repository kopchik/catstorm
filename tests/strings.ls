main = progname, args ->
  a = 1
  b = 2
  # test interpolation with chaining
  s = " {a} {b} "@strip!
  assert s == "{a} {b}"
  # iteration
  s = "123"
  for char in s
    p char
  0
