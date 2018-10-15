#!/usr/bin/python3
# -*- coding: utf-8 -*-
__author__ = "Zacharias El Banna"
__version__ = "5.2GA"
__status__ = "Production"

from os   import path as ospath
from sys  import path as syspath, exit, argv
syspath.append(ospath.abspath(ospath.join(ospath.dirname(__file__), '..','..')))

if __name__ == "__main__":
 if len(argv) < 3:
  print(argv[0] + " <settings.json> func [<json-arg>]")
  exit(0)

 from json import loads, dumps, load
 from time import time
 from importlib import import_module
 from zdcp.core.engine import Context
 from zdcp.core.common import DB, rest_call
 with open(argv[1]) as f:
  file = load(f)
 settings = {}
 for section,data in file.items():
  if not settings.get(section):
   settings[section] = {}
  for key,val in data.items():
   settings[section][key] = val['value']
 system = settings['system']
 port = system['port']
 if system['id'] == 'master':
  with DB(system['db_name'], system['db_host'], system['db_user'], system['db_pass']) as db:
   db.do("SELECT section,parameter,value FROM settings WHERE node = 'master'")
   db.do("SELECT section,parameter,value FROM settings WHERE node = 'master'")
   data = db.get_rows()
   db.do("SELECT 'nodes' AS section, node AS parameter, url AS value FROM nodes")
   data.extend(db.get_rows())
  for row in data:
   if not settings.get(row['section']):
    settings[row['section']] = {}
   settings[row['section']][row['parameter']] = row['value']
 else:
  ext = rest_call("%s/settings/fetch/%s"%(system['master'],system['id']))['settings']
  for section,data in ext.items():
   if not settings.get(section):
    settings[section] = {}
   for key,val in data.items():
    settings[section][key] = val

 ctx = Context(settings,None)
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
