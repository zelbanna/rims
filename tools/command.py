#!/usr/bin/python3
# -*- coding: utf-8 -*-
__author__ = "Zacharias El Banna"

from os   import path as ospath
from sys  import path as syspath, exit, argv
syspath.append(ospath.abspath(ospath.join(ospath.dirname(__file__), '..','..')))

if __name__ == "__main__":
 if len(argv) < 3:
  print(argv[0] + " <config.json> func [<json-arg>]")
  exit(0)

 from json import dumps,loads
 from time import time
 from importlib import import_module
 from zdcp.core.engine import Context
 from zdcp.core.common import DB, rest_call

 ctx = Context(aConfigFile = argv[1])

 if ctx.node == 'master':
  settings = ctx.node_settings('master')
 else:
  settings = rest_call("%s/settings/fetch/%s"%(ctx.config['master'],ctx.node))['data']['settings']
 ctx.settings.update(settings)

 timestamp = int(time())
 try:    args = loads(argv[3])
 except: args = {}
 mod,_,fun = argv[2].partition('_')
 started = "Executing:%s(%s)"%(fun,args)
 print(started)
 try:
  module = import_module("zdcp.rest.%s"%mod)
  output = getattr(module,fun,None)(args,ctx)
 except Exception as e: output = e.args[0]
 print("Time spent: %i\n%s\n%s"%(int(time()) - timestamp,'_'*len(started),dumps(output,indent=4, sort_keys=True)))
