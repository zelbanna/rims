#!/usr/bin/python3
# -*- coding: utf-8 -*-
__author__ = "Zacharias El Banna"

from os   import path as ospath
from sys  import path as syspath, argv, exit
syspath.append(ospath.abspath(ospath.join(ospath.dirname(__file__), '..','..')))

if __name__ == "__main__":
 if len(argv) < 2:
  print(argv[0] + " module/func [<json-arg>]")
  exit(0)

 from json import loads, dumps, load
 from time import time
 from rims.core.common import rest_call
 timestamp = int(time())
 try:    args = loads(argv[2])
 except: args = {}
 try:
  with open(ospath.abspath(ospath.join(ospath.dirname(__file__), '..','config.json'))) as f:
   token = load(f).get('token',None)
 except:
  token = None
 started = "Executing:%s(%s)"%(argv[1],args)
 print(started)
 try:  res = rest_call("http://127.0.0.1:8080/internal/%s"%argv[1], aArgs = args, aTimeout = 300, aDataOnly = False, aVerify = True, aHeader = {'X-Token':token})
 except Exception as e: output = e.args[0]
 else:
  output = res['data']
  for x in res['info'].items():
   print("%s: %s"%x)
 print("Time spent: %i\n%s\n%s"%(int(time()) - timestamp,'_'*len(started),dumps(output,indent=4, sort_keys=True)))
