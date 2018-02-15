#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Zacharias El Banna"
__version__ = "18.02.09GA"
__status__ = "Production"


def formatting(restfile,data):
 from sys import stdout
 size = len(data['function']) + 2
 print "%s %s %s"%("#"*(20 - size/2),data['function'],"#"*(20 - size/2 - size%2))
 print "#"
 if len(data['required']) > 0:
  print "# Required arguments:"
  for key,value in data['required'].iteritems():
   stdout.write("#  - %s"%key)
   stdout.write("\n" if value == True else " (optional)\n")
  print "#"
 for tp in ['optional','pop','undecoded']:
  if len(data[tp]) > 0:
   print "# %s arguments:"%tp.title()
   if type(data[tp]) is list:
    keys = data[tp]
   if type(data[tp]) is dict:
    keys = data[tp].keys()
   for key in keys:
     print "#  - %s"%key
   print "#"

 print "#\n"

if __name__ == "__main__":
 from os   import path as ospath, listdir
 from sys  import path as syspath, argv, exit
 from json import loads, dumps 
 restdir = ospath.abspath(ospath.join(ospath.dirname(__file__), '..','rest'))
 syspath.append(ospath.abspath(ospath.join(ospath.dirname(__file__), '..','..')))
 from sdcp.rest.sdcp import rest_analyze
 if len(argv) == 2:
  res = rest_analyze({'file':argv[1] + ".py"})
  for fun in res['functions']:
   formatting(res['file'],fun)
 else:
  for restfile in listdir(restdir):
   if restfile[-3:] == 'pyc':
    continue
   print "Analyzing file %s"%restfile
   print rest_analyze({'file':restfile})
 exit(0)
