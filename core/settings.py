#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Program docstring.

Creates a settings container from a .json file

"""
__author__ = "Zacharias El Banna"
__version__ = "1.0GA"
__status__ = "Production"

from sys import argv
from json import load

if len(argv) < 2:
 print "Usage: {} <json file>".format(argv[0])
else:
 with open(argv[1]) as f:
  config = load(f)

 with open('SettingsContainer.py','w') as f:
  for name,cathegory in config.iteritems():
   f.write("##################### {:<8} ######################\n".format(name.upper()))
   for key, entry in cathegory.iteritems():
    f.write("{}_{} = '{}'\n".format(name,key,entry))
   f.write("\n")
