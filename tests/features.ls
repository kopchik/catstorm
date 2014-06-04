# This is just a comment
# :: MyType = Tag1 | Tag2 Int Double



main =  progname, argv -> p "Hello, {argv}"
        p "You've just launched {progname}"
        assert 1 + 1 == 2
        assert "a" + "b"  == "ab"
        assert 1+2*2 == 5
        assert (1+2)*2 == 6
        assert (1 if 2 else 3) == 1
        assert (2 if 0 else 3) == 3

        succ = arg -> arg + 1
        assert succ . succ . 1 == 3
        assert succ . 0 $ succ $ succ == 3

        add = val,i -> add . (val+1),(i-1) if i>0 else val
        p (add . 2,3)

        assert [1,2,3] == [1,2,3]

        a = 1
        ret if a else 0
        p "You will never see this line!"