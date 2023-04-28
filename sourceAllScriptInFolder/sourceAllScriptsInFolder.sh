#!/bin/bash

for file in `dirname $BASH_SOURCE`/*.sh; do
  if [[ "`basename $file`" != "`basename $BASH_SOURCE`" ]]; then
    source "$file"
  fi
done
