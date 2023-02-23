from catstorm.indent_parser import indent_parse, StringWithLineNo
import pytest


class Test_indent_parse:
    def test_parsing_blocks(self):
        data = """\
        line 1
        line 2
            line 3 \\
            line 3 cont
        line 4
        """
        parsed_data = indent_parse(data)
        assert parsed_data == [
            ["line 1", "line 2", ["line 3             line 3 cont"], "line 4"]
        ]

    def test_line_numbers(self):
        data = "line 1\nline 2 \\\nline 2 cont\nline3"
        assert list(enumerate(indent_parse(data), 1)) == [
            (1, "line 1"),
            (2, "line 2 line 2 cont"),
            (3, "line3"),
        ]

    def test_last_line_has_slash(self):
        with pytest.raises(ValueError):
            indent_parse("test \\")


class Test_StringWithLineNo:
    def test_strip_preserves_lineno(self):
        s = StringWithLineNo("test", lineno=99)
        assert s.strip().lineno == 99
