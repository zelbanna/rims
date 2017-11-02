#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"


if __name__ == "__main__":
 from sys import argv, exit
 if len(argv) < 3:
  print argv[0] + " <rest-module> <function> [<json-arg>]"
  exit(0)

 from json import loads, dumps
 from os   import path as ospath
 from sys  import path as syspath
 from importlib import import_module 
 syspath.append(ospath.abspath(ospath.join(ospath.dirname(__file__), '../..')))
 rest = argv[1]
 fun  = argv[2]
 try:
  args = loads(argv[3])
 except:
  args = None
 print "Executing:{}_{}({})".format(rest,fun,args)
 try:
  module = import_module(rest)
  res    = getattr(module,fun,lambda x: {'res':'ERROR', 'type':'FUNCTION_NOT_FOUND' })(args)
  print dumps(res, indent=4, sort_keys=True)
 except Exception, e:
  print "Error [{}:{}]".format(type(e).__name__,str(e))
