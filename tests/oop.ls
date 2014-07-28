::class Class
  New = value ->
    @value = 1
  test = ->
    p "test OK"

 main = name, args ->
  obj = Class . 1
  p obj@value
