#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Program docstring.
Creates a settings container from a .json file
"""
__author__ = "Zacharias El Banna"
__version__ = "17.6.1GA"
__status__ = "Production"

def convertSettings(aFile):
 from json import load
 from os import remove
 try:
  with open(aFile) as f:
   config = load(f)
  with open("SettingsContainer.py",'w') as f:
   for name,cathegory in config.iteritems():
    for key, entry in cathegory.iteritems():
     f.write("{}_{} = '{}'\n".format(name,key,entry))
    f.write("\n")
  # Brute way of compiling ...
  import SettingsContainer
  remove("SettingsContainer.py")
  print "Parsed settings and wrote SettingsContainer"
 except Exception as err:
  print "Error handling settings files: {}".format(str(err))

if __name__ == "__main__":
 from sys import argv
 if len(argv) < 2:
  print "Usage: {} <json file>".format(argv[0])
 else:
  convertSettings(argv[1])
