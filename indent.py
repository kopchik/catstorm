#!/usr/bin/env python3

def annotate(text):
  """ Annotate text lines with indendation. """
  for line in text.splitlines():
    if line.isspace() or not line: continue
    depth = len(line) - len(line.lstrip())
    yield line.strip(), depth


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


def indent_parse(text):
  blk, _, _ = process(annotate(text), 0, [])
  return blk


if __name__ == '__main__':
  data = """\
1
  2
    3
    4
  2
"""
  print(data)
  it = annotate(data)
  print(process(it, 0, []))