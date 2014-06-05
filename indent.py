#!/usr/bin/env python3
def indent_parse(text):
  it = text.splitlines()
  blk, _, _ = process(annotate(preprocess(it)), 0, [])
  return blk


class Str(str):
  def __new__(cls, lineno, s):
    self = str.__new__(cls, s)
    self.lineno = lineno
    return self


def annotate(it):
  """ Annotate text lines with indendation. """
  for i, line in enumerate(it, 1):
    depth = len(line) - len(line.lstrip())
    yield Str(i, line.strip()), depth


def process(it, cur, blk):
  """ it  -- iterator
      cur -- current indent level
      blk -- block data append to
  """
  for line, pos in it:
    # print("got", line, pos, cur)
    if pos == cur:
      # print(cur, "0appending", line)
      blk.append(line)
    elif pos < cur:
      # print(cur, "1returning", blk, pos, line)
      return blk, pos, [line]
    elif pos > cur:
      ret, pos, rem = process(it, pos,[line])
      if pos < cur:
        # print(cur, "2returning", blk+[ret], pos, rem)
        return blk+[ret], pos, rem
      else:
        # print(cur, "3appending", ret, "and", rem)
        blk.append(ret)
        blk+= rem
  return blk, pos, []


def preprocess(it):
  """ Remove blank lines, merge lines ending with \. """
  buf = ''
  for line in it:
    if line.isspace() or not line:
      continue
    if line.endswith('\\'):
      buf += line.strip('\\')
      continue
    if buf:
      yield buf+line
      buf = ''
      continue
    yield line
  assert not buf, "last non-empty line contains '\\'"


if __name__ == '__main__':
  data = """\
1
  2
    3 \\
    4
  2
"""
  it = data.splitlines()
  it = annotate(preprocess(it))
  print(process(it, 0, []))