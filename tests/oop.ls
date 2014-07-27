::class Class
  new = ->
    @attr = 1

 main = name, args ->
  obj = Class
  p ("obj created")
  obj.attr
