#!/usr/bin/env storm.py

main = name, argv ->
  ::class MyClass
    New = v ->
      @v = 1
    test = x ->
      p "test side effect"

  object = MyClass . 1
  object@test . 1
  0
