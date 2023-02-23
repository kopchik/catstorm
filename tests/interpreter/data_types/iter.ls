#!/usr/bin/env storm.py

main = progname, args ->
  data = [[1,2], [3,4]]
  for i,j in data
    "{i},{j}"

  data = [[1,2]]
  for i, j in data
    assert "{i},{j}" == "1,2"

  ret 0
