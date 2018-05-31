#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Zacharias El Banna"
__version__ = "18.05.31GA"
__status__ = "Production"

def execute(argv):
 from json import loads, dumps
 from os   import path as ospath
 from sys  import path as syspath
 from importlib import import_module 
 (mod,_,fun) = argv[1].partition('_')
 try:  args = loads(argv[2])
 except: args = {}
 print "Executing:{}_{}({})".format(mod,fun,args)

 syspath.append(ospath.abspath(ospath.join(ospath.dirname(__file__), '..','..')))
 module = import_module("sdcp.rest.%s"%mod)
 module.__add_globals__({'ospath':ospath,'loads':loads,'dumps':dumps,'import_module':import_module})
 res    = getattr(module,fun,lambda x: {'res':'ERROR', 'type':'FUNCTION_NOT_FOUND' })(args)
 print dumps(res, indent=4, sort_keys=True)
 return 0

if __name__ == "__main__":
 from sys import argv, exit
 if len(argv) < 2:
  print argv[0] + " <rest-module_function> [<json-arg>]"
  exit(0)
 else:
  exit(execute(argv))
