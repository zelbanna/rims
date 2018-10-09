#!/usr/bin/python3
# -*- coding: utf-8 -*-
__author__ = "Zacharias El Banna"
__version__ = "5.0GA"
__status__ = "Production"

from os   import path as ospath
from sys  import path as syspath
from json import loads, dumps
from time import time
syspath.append(ospath.abspath(ospath.join(ospath.dirname(__file__), '..','..')))
from zdcp.core.engine import Context

if __name__ == "__main__":
 from json import dumps
 from sys import argv, exit
 if len(argv) < 2 or (len(argv) > 2 and argv[2] == '-s'):
  print(argv[0] + " [-url] <URL>|<rest-module_function> [<json-arg>]")
  print("\nOptions:\n -url: Proper socket call, followed by URL\n")
  exit(0)
 else:
  timestamp = int(time())
  if argv[1] == '-url':
   try: args = loads(argv[3])
   except: args = {}
   started = "Executing:%s(%s)"%(argv[2],args)
   print(started)
   from zdcp.core.common import rest_call
   try:
    res = rest_call(argv[2],args, aTimeout = 300)
   except Exception as e:
    output = e.args[0]
   else:
    output = res['data']
    for x in res['info'].items():
     print("%s: %s"%x)
  else:
   from zdcp.Settings import Settings
   ctx = Context(Settings,None)
   from importlib import import_module
   (mod,_,fun) = argv[1].partition('_')
   try: args = loads(argv[2])
   except: args = {}
   started = "Executing:%s_%s(%s)"%(mod,fun,args)
   print(started)
   module = import_module("zdcp.rest.%s"%mod)
   function = getattr(module,fun,lambda x: {'res':'ERROR', 'type':'FUNCTION_NOT_FOUND' })
   output = function(args,ctx)
  timespent = int(time()) - timestamp
  print("Time spent: %i"%(timespent))
  print("_" * len(started))
  print(dumps(output,indent=4, sort_keys=True))
