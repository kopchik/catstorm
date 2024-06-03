from typing import Iterator


class StringWithLineNo(str):
    def __new__(cls, s, lineno=None):
        self = str.__new__(cls, s)
        self.lineno = lineno
        return self

    def strip(self, *args, **kwargs):
        return StringWithLineNo(str.strip(self, *args, **kwargs), self.lineno)


def indent_parse(raw_code):
    code = _add_line_numbers(raw_code)
    code = _merge_multline_statements(code)
    code = _skip_blank_lines(code)
    code = _add_indentation_depth(code)
    blk, _, _ = _parse_indented_blocks(code)
    return blk


def _add_line_numbers(raw_code: str) -> Iterator[StringWithLineNo]:
    for lineno, line in enumerate(raw_code.splitlines(), start=1):
        yield StringWithLineNo(line, lineno=lineno)


def _add_indentation_depth(it):
    for line in it:
        depth = len(line) - len(line.lstrip())
        yield line.strip(), depth


def _parse_indented_blocks(it, cur_block_level=0, blk=None):
    if blk is None:
        blk = []

    indent_level = cur_block_level
    for line, indent_level in it:
        if indent_level == cur_block_level:
            blk.append(line)
        elif indent_level < cur_block_level:
            return blk, indent_level, [line]
        elif indent_level > cur_block_level:
            ret, indent_level, remaining = _parse_indented_blocks(
                it, indent_level, [line]
            )
            if indent_level < cur_block_level:
                return blk + [ret], indent_level, remaining
            else:
                blk.append(ret)
                blk += remaining

    return blk, indent_level, []


def _merge_multline_statements(lines: list[StringWithLineNo]):
    buf = ""
    for line in lines:
        if line.endswith("\\"):
            buf += line.strip("\\")
            continue
        if buf:
            yield buf + line
            buf = ""
            continue
        yield line
    if buf:
        raise ValueError("last line contains '\\'")


def _skip_blank_lines(it):
    for line in it:
        if line.isspace() or not line:
            continue
        yield line
