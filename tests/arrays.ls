main = prog, args ->
  a = [1,2+1]
  p a[0:1]
  a[4] = 0
  assert a = [0,3]