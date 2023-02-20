#!/usr/bin/env python3


class Block:
    def __init__(
        self, sep="", lvl=0, prepend=None, append=None, comment=None, parent=None
    ):
        self.content = []
        self._prepend = prepend
        self._append = append
        self._sep = sep
        self._lvl = lvl
        self._comment = comment
        self._parent = parent

    def add(self, line):
        self.content.append(line)

    def newblock(self, *args, **kwargs):
        blk = self.__class__(*args, **kwargs, parent=self)
        return blk

    def to_str(self):
        lines = []
        indent = f"{'  '*self._lvl}"
        if self._prepend:
            lines.append(self._prepend)

        for data in self.content:
            if isinstance(data, Block):
                lines.extend(data.to_str())
            else:
                data = f"{indent}{data}{self._sep}"
                lines.append(data)

        if self._append:
            lines.append(self._append)

        return lines

    def __repr__(self):
        name = self.__class__.__name__
        return f"{name}()"

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._parent.add(self)


class CBlock(Block):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        super().__init__(*args, **kwargs)

    def cblock(self):
        return self.newblock(prepend="{", append="}", sep=";", lvl=self._lvl + 1)


if __name__ == "__main__":
    b = CBlock()
    b.add("void test()")
    with b.cblock() as nested:
        nested.add(r'printf("hello, hell")')
    print("\n".join(b.to_str()))
