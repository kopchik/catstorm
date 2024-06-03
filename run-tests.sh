#!/bin/bash

die() {
  echo "$@" >&2
  exit 1
}

for file in `find ./tests/interpreter -name '*.ls'`
do
   echo "running $file"
   catstorm -b $file || die "failed on $file"
done
