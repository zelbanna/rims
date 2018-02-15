#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Zacharias El Banna"
__version__ = "18.02.09GA"
__status__ = "Production"


def formatting(restfile,data):
 size = len(data['function']) + 2
 # print "%s %s %s"%("#"*(20 - size/2),data['function'],"#"*(20 - size/2 - size%2))
 print "def %s(%s):"%(data['function'],data['arg'])
 print "    \"\"\"Function description for %s TBD\n"%data['function']
 print "    Args:"
 if len(data['required']) > 0:
  for key,value in data['required'].iteritems():
   print "        %s (required%s"%(key,")" if value == True else " - optional indication)")
 if len(data['optional']) > 0:
  for key,value in data['optional'].iteritems():
   print "        %s (optional%s"%(key,")" if value == True else " - required actually)")
 print ""
 print "    Extra:"
 if len(data['pop']) > 0:
  for key in data['pop'].keys():
   print "        %s (pop)"%(key)
 if len(data['undecoded']) > 0:
  for value in data['undecoded']:
   print "        %s (undecoded - line:%s)"%(value['part'],value['line'])
 print ""
 print "    \"\"\""
 print "#####################################################"

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
