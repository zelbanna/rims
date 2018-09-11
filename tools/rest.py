#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Zacharias El Banna"
__version__ = "4.0GA"
__status__ = "Production"

from os   import path as ospath
from sys  import path as syspath
from json import loads, dumps
syspath.append(ospath.abspath(ospath.join(ospath.dirname(__file__), '..','..')))

if __name__ == "__main__":
 from json import dumps
 from sys import argv, exit
 if len(argv) < 2 or (len(argv) > 2 and argv[2] == '-s'):
  print argv[0] + " [-url] <URL>|<rest-module_function> [<json-arg>]"
  print "\nOptions:\n -url: Proper socket call, followed by URL\n"
  exit(0)
 else:
  if argv[1] == '-url':
   try: args = loads(argv[3])
   except: args = {}
   print "Executing:%s(%s)"%(argv[2],args)
   from zdcp.core.common import rest_call
   try:
    output = rest_call(argv[2],args)['data']
   except Exception as e:
    output = e[0]
  else:
   from zdcp.SettingsContainer import SC
   from importlib import import_module
   (mod,_,fun) = argv[1].partition('_')
   try: args = loads(argv[2])
   except: args = {}
   print "Executing:%s_%s(%s)"%(mod,fun,args)
   module = import_module("zdcp.rest.%s"%mod)
   module.__add_globals__({'ospath':ospath,'loads':loads,'dumps':dumps,'import_module':import_module,'SC':SC})
   function = getattr(module,fun,lambda x: {'res':'ERROR', 'type':'FUNCTION_NOT_FOUND' })
   output = function(args)
  print dumps(output,indent=4, sort_keys=True)

