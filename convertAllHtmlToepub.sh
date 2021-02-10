#!/bin/bash
for f in *.html
do  
  # cut out the first col form xxx.html
  name=$(echo "$f"|cut -f 1 -d '.')
  echo $name
  # need to install pandoc first
  pandoc -f html -t epub3 -o ${name}.epub ${name}.html
done