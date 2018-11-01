#!/bin/bash
#
# convert <color> <'#from'> <'#to'>
#
# Using linux tool ImageMagick
# https://www.imagemagick.org/Usage/color_basics
#
for file in btn*.$1.png;
do
 echo "Converting $file"
 convert $file -fill $3 -opaque $2 $file.new.png
 rm $file
 mv $file.new.png $file
done

