#!/bin/bash

die() {
  echo "$@" >&2
  exit 1
}

FILEZ=tests/bugz/*.ls
for file in features.ls tests/bugz/*.ls
do
   echo "running $file"
   ./storm.py $file || die "failed on $file"
done
