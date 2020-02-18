#!/bin/bash
#
# convert <color> <'#color code'>
#
# Using blue as basis for color conversion
#
# Using linux tool ImageMagick
# https://www.imagemagick.org/Usage/color_basics
#
for file in btn*.blue.png;
do
 echo "Converting ${file%.blue.png}"
 convert $file -fill $2 -opaque '#3E84F4' ${file%.blue.png}.$1.png
done
