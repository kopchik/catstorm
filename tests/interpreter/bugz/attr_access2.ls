#!/usr/bin/env catstorm

::class Test
  New =  ->
    @someattr = 1

  to_str = ->
    ret @someattr
    # "{@someattr}"


main = progname, argv ->
  test = Test!
  p test
  ret 0
