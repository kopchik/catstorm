main = prog, args ->
  a = [1, 2+1]
  a[0] = 0
  assert a == [0, 3]

  gen = depth ->
    [] if depth == 0 else [gen . (depth-1)]
  assert gen . 2 == [[[]]]


  ret 0
