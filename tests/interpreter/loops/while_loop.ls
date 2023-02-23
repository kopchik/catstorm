#!/usr/bin/env catstorm

main = progname, argv ->
  x = 0
  while x < 10
    x = x + 1
  assert x == 10
  ret 0
