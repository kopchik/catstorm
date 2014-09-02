main = name, args ->
  switch
    | (args@len! == 0) => p "No arguments provided"
    | (args@len! == 1) => p "One argument"
    | TRUE             => p "fall through"

  0