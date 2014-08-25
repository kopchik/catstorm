main = progname, args ->
  assert TRUE == TRUE
  assert FALSE == FALSE
  assert TRUE != FALSE
  x = 0
  if FALSE
    assert 0
  if TRUE
    x = 1
  assert x == 1

  ret 0
