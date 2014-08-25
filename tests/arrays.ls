main = prog, args ->
  a = [1,2+1]
  a[0] = 0
  assert a == [0,3]

  ret 0
