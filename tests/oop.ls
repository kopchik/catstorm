::class Class
  New = ->
    @value = 1

 main = name, args ->
  obj1 = Class!
  obj2 = Class!
  obj1@obj2 = obj2
  assert obj1@value == obj1@obj2@value

  ::class Print
    New = arg ->
        @arg = arg
  print = Print . 1
  assert print@arg == 1

  ret 0