#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Zacharias El Banna"
__version__ = "18.02.09GA"
__status__ = "Production"


from json import loads, dumps
from os   import path as ospath, listdir
from sys  import path as syspath,exit,stdout
from importlib import import_module 
restdir = ospath.abspath(ospath.join(ospath.dirname(__file__), '..','rest'))

def formatting(restfile,fun,args):
 size = len(fun) + 2
 print "%s %s %s"%("#"*(20 - size/2),fun,"#"*(20 - size/2 - size%2))
 print "#"
 if len(args['required']) > 0:
  print "# Required arguments:"
  for key,value in args['required'].iteritems():
   stdout.write("#  - %s"%key)
   stdout.write("\n" if value == True else " (optional)\n")
  print "#"
 for tp in ['optional','pop','undecoded']:
  if len(args[tp]) > 0:
   print "# %s arguments:"%tp.title()
   if type(args[tp]) is list:
    keys = args[tp]
   if type(args[tp]) is dict:
    keys = args[tp].keys()
   for key in keys:
     print "#  - %s"%key
   print "#"

 print "#\n"

def analyze(restfile):
 print restfile
 with open(ospath.abspath(ospath.join(restdir,restfile)),'r') as file:
  line_no = 0
  fun = None
  args = {'required':{},'optional':{},'pop':{},'undecoded':[]} 
  for line in file:
   line_no += 1
   line = line.rstrip()
   if line[0:4] == 'def ':
    if fun:
     formatting(restfile,fun,args)
     args = {'required':{},'optional':{},'pop':{},'undecoded':[]}
    fun = line[4:-8].lstrip()
   elif fun and "aDict" in line:
     parts = line.split('aDict')
     # print "%s:%s"%(fun,parts)
     for part in parts[1:]:
      if part[0:2] == "['":
       end = part.index("]")
       argument = part[2:end-1]
       args['required'][argument] = (args['optional'].get(argument) is None) 
      elif part[0:6] == ".get('":
       end = part[6:].index("'")
       argument = part[6:6+end]
       if not args['required'].get(argument):
        args['optional'][argument] = True
      elif part[0:7]== ".keys()" or part[0] == ")":
       pass
      elif part[0:6] == ".pop('":
       end = part[6:].index("'")
       argument = part[6:6+end]
       if not args['required'].get(argument) and not args['optional'].get(argument):
        args['pop'][argument] = True
      else:
       args['undecoded'].append({'function':fun,'part':part,'line':line_no})
   #else:
   # print "%s:<pass>:%s"%(restfile,line)

  formatting(restfile,fun,args)


if __name__ == "__main__":
 from sys import argv, exit
 if len(argv) == 2:
  analyze(argv[1] + ".py")
 else:
  for restfile in listdir(restdir):
   if restfile[-3:] == 'pyc':
    continue
   print "Analyzing file %s"%restfile
   analyze(restfile)
 exit(0)

