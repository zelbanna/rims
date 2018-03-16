#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Zacharias El Banna"
__version__ = "18.03.16"
__status__ = "Production"


def formatting(restfile,data,globals):
 size = len(data['function']) + 2
 # print "%s %s %s"%("#"*(20 - size/2),data['function'],"#"*(20 - size/2 - size%2))
 print "#\n#\ndef %s(%s):"%(data['function'],data['arg'])
 print " \"\"\"Function docstring for %s TBD\n"%data['function']
 print " Args:"
 if len(data['required']) > 0:
  for key,value in data['required'].iteritems():
   print "  - %s (required%s"%(key,")" if value == True else " - optional indication)")
 if len(data['optional']) > 0:
  for key,value in data['optional'].iteritems():
   print "  - %s (optional%s"%(key,")" if value == True else " - required actually)")
 print "\n Output:"
 if len(data['pop']) > 0 or len(data['undecoded']) > 0:
  print "\n Extra:"
 if len(data['pop']) > 0:
  for key in data['pop'].keys():
   print "  - %s (pop)"%(key)
 if len(data['undecoded']) > 0:
  for value in data['undecoded']:
   if value.get('part'):
    print "  -  %s (undecoded - line:%s)"%(value['part'],value['line'])
   if value.get('error'):
    print "  -  %s (error - line:%s)"%(value['error'],value['line'])
 print " \"\"\""
 print "Module dependencies:"
 if len(globals) > 0:
  for value in globals:
   print "- %s (global import)"%(value)
 if len(data['imports']) > 0:
  for value in data['imports']:
   print "- %s (function import)"%(value)
 print "********************************************************"

def analyze(aFile):
 syspath.append(ospath.abspath(ospath.join(ospath.dirname(__file__), '..','..')))
 from sdcp.rest.tools import rest_analyze
 print "############# Analyzing file: %s.py ################"%(aFile)
 res = rest_analyze({'file':aFile + ".py"})
 if len(res['global']) > 0:
  print "#\n# Global imports:"
  for glob in res['global']:
   print "#  - %s"%glob
  print "#"
 for fun in res['functions']:
  formatting(res['file'],fun,res['global'])

if __name__ == "__main__":
 from os   import path as ospath, listdir
 from sys  import path as syspath, argv, exit
 from json import loads, dumps 
 restdir = ospath.abspath(ospath.join(ospath.dirname(__file__), '..','rest'))
 if len(argv) == 2:
  analyze(argv[1])
 else:
  for restfile in listdir(restdir):
   if restfile[-3:] == 'pyc':
    continue
   analyze(restfile[0:-3])
 exit(0)
