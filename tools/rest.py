#!/usr/bin/python3
# -*- coding: utf-8 -*-
__author__ = "Zacharias El Banna"
__version__ = "5.2GA"
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
 if len(argv) < 2:
  print(argv[0] + " <URL> [<json-arg>]")
  exit(0)
 else:
  timestamp = int(time())
  try: args = loads(argv[2])
  except: args = {}
  started = "Executing:%s(%s)"%(argv[1],args)
  print(started)
  from zdcp.core.common import rest_call
  try:
   res = rest_call(argv[1],args, aTimeout = 300) 
  except Exception as e:
   output = e.args[0]
  else:
   output = res['data']
   for x in res['info'].items():
    print("%s: %s"%x)
  timespent = int(time()) - timestamp
  print("Time spent: %i"%(timespent))
  print("_" * len(started))
  print(dumps(output,indent=4, sort_keys=True))
