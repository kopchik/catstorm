#!/usr/bin/env storm.py

main = progname, args ->
  data = [[1,2],[3,4]]
  for i,j in data
    "{i},{j}"
  ret 0
