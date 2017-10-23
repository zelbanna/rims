#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Program docstring.
Creates a package specific container, partly using settings from a .json file
"""
__author__ = "Zacharias El Banna"
__version__ = "17.10.4"
__status__ = "Production"

def convertSettings(aFile):
 from json import load
 try:
  with open(aFile) as f:
   config = load(f)
  with open("PackageContainer.py",'w') as f:
   for name,category in config.iteritems():
    f.write("{}={}\n".format(name,repr(category)))
   f.write("file={}\n".format(repr(aFile)))
   f.write("def log_msg(amsg):\n")
   f.write(" from time import localtime, strftime\n")
   f.write(" with open(generic['logformat'], 'a') as f:\n")
   f.write(repr("  f.write(unicode('{} : {}\n'.format(strftime('%Y-%m-%d %H:%M:%S', localtime()), amsg)))")[1:-1] + "\n")
  # Brute way of compiling ...
  print "Parsed settings and wrote PackageContainer"
 except Exception as err:
  print "Error handling settings files: {}".format(str(err))

if __name__ == "__main__":
 from sys import argv
 if len(argv) < 2:
  print "Usage: {} <json file>".format(argv[0])
 else:
  convertSettings(argv[1])
