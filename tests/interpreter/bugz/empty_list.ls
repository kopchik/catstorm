# parser couldn't parse empty list
main = name, args ->
  list = [1,2,3]
  otherlist = []
  for e in list
    otherlist <<< e
  assert list == otherlist
  0