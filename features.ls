main =  progname, argv ->
        # string interpolation
        p "Hello, {argv}"
        p "You've just launched {progname}"
        p "I used it to show supported language features"
        p "and as integrated test."
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
        assert apply . inc,1 == 2

        # recursion and multi-line expressions
        add = val,i -> add . (val+1),(i-1) \
                       if i>0 else val
        assert add . 2,3 == 5

        # working with list
        assert [1,2,3] == [1,2,3]

        # object-oriented stuff
        ::class MyClass
          New = value ->
            @value = 1

        object = MyClass . 1
        assert object@value == 1

        # return statement and branching
        a = 1
        ret 0 if a else 1
        p "ACHTUNG, TEST FAILED!"
        1
