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

  assert (TRUE and TRUE) == TRUE
  assert (FALSE or TRUE) == TRUE
  assert (TRUE or FALSE) == TRUE
  assert (0 or 1) == 1
  assert (1 or 0) == 1

  ret 0
