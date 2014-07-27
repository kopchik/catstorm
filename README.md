catstorm
========

Catstorm is my another attempt to make my own programming
language. It should be as easy as python, but more feature-
rich, expression-oriented and with hope to have a good FFI
(foreign function interface).



Design Goals
------------

1. Be safe, compact and friendly
1. Static typing
1. ML-like syntax (inspired by LiveScript (and LiveScript was inspired by Haskell))
1. Expression-oriented
1. Algebraic Data Types (ADT)
1. Translates into C
1. Public/Protected/Private attributes of the classes
1. Custom operators
1. Full threading support
1. Garbage collection (Boehm GC)
1. Built-in linter
1. Built-in regexp support
1. Built-in shell commands invocation
1. Function overloading
1. UTF8 strings
1. Substitute vars in strings: "Hello, {username}!"
1. All programs can be opened as libraries
1. No header files needed, everything is in elf (possibly in compressed format).
1. Keep it simple (to learn, to read, to extend)
1. Error-resistant coding
1. Minimize number of keywords and namespace pollution


At the moment there is only interpreter.
Here is the full set of features available:

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
