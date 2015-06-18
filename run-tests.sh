#!/bin/bash

die() {
  echo "$@" >&2
  exit 1
}

for file in features.ls tests/*.ls tests/bugz/*.ls
do
   echo "running $file"
   ./storm.py -b $file || die "failed on $file"
done
