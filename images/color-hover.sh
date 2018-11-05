#!/bin/bash
#
# convert <color> <'#color code'>
#
# Using blue as basis for color conversion
#
# Using linux tool ImageMagick
# https://www.imagemagick.org/Usage/color_basics
#
for file in btn*.$1.png;
do
 echo "Converting ${file%.$1.png}"
 convert $file -fill $2 -opaque '#FFFFFF' ${file%.$1.png}.$1.hover.png
done
