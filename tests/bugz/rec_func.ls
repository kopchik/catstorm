main = name, args ->
  add = val,i -> add . (val+1),(i-1) \
                 if i>0 else val
  assert add . 2,3 == 5

