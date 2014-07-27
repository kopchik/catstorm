::class Class
  new = ->
    @attr = 1
    #p @attr

 main = name, args ->
  obj = Class
  p obj%attr
