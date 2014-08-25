catstorm
========

Catstorm is my another attempt to make my own programming
language. It should be as easy as python, but more feature-
rich, expression-oriented and with hope to have a good FFI
(foreign function interface).


Why another language
--------------------

Ever wanted to "upgrade" python with some nice features from
ruby or haskell? Me too :(. And here is my attempt.


Some examples
-------------

````LiveScript
main =  progname, argv -> p "Hello, {argv}"
        # string interpolation
        p "You've just launched {progname}"
        # basic arithmetic
        assert 1 + 1 == 2
        assert "a" + "b"  == "ab"
        assert 1+2*2 == 5
        assert (1+2)*2 == 6
        assert (1 if 2 else 3) == 1
        assert (2 if 0 else 3) == 3

        # function composition
        succ = arg -> arg + 1
        assert succ . succ . 1 == 3
        assert succ . 0 $ succ $ succ == 3

        # higher-order functions
        inc = x -> x+1
        apply = f, i -> f . i
        assert apply . inc, 1 == 2

        # recursion
        add = val,i -> add . (val+1),(i-1) \
                       if i>0 else val
        assert add . 2,3 == 5

        # working with list
        assert [1,2,3] == [1,2,3]

        # return statement and branching
        a = 1
        ret if a else 0
        p "You will never see this line!"
````


Design Highlights
-----------------

1. Keep it simple (to learn, to read, to extend)
1. Be safe, compact and friendly
1. Strong static typing
1. ML-like syntax (inspired by LiveScript (and LiveScript was inspired by Haskell))
1. Expression-oriented
1. Algebraic Data Types (ADT)
1. No type erasure for better introspection and debugging
1. Public/Protected/Private attributes of the classes
1. Custom operators
1. Coroutines
1. Garbage collection
1. Built-in linter
1. Built-in regexp support
1. Built-in shell commands invocation
1. Function overloading
1. UTF8 strings
1. Substitute vars in strings: "Hello, {username}!"
1. All programs can be opened as libraries
1. No header files needed, everything is in elf (possibly in compressed format).
1. Minimize number of keywords and namespace pollution

Implementation details
----------------------

1. Translates into C
1. Boehm GC used for garbage collection
1. ~~Code is specification~~ :)


### Data Types

* Immutable
    + Str
    + Int
    + Tuple
* Mutable
    + Array
    + Obj / Class
* Other
    + Func


Operator priority
-----------------

Operators are essential for this language. They must be
parsed in a proper way, e.g., "->" is not "-" and ">". To
deal with this, each operator given priority. "->" has
higher priority over "-" and ">".


TODO
----

### Expression parser

Better operator precedence:
````
traverse . nails@tokenize! => traverse . (nails@tokenize!)
```
