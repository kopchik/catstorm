::adt Op =  Unary Op | Binary Left, Right
main = name, args ->
  x = Unary . 1
  y = Unary . 2
  z = Binary . 3,4

  p "{x} {y} {z}"

  match x
    | Unary . x => p "The Unary {x}"
    | Binary . a,b => p "HEY {a} {b}"
  0
