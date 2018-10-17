#!/usr/bin/python3
# -*- coding: utf-8 -*-

from os   import path as ospath
from sys  import path as syspath, argv, exit
from json import loads,load,dumps
from time import time
syspath.insert(1, ospath.abspath(ospath.join(ospath.dirname(__file__), '..','..')))
from zdcp.core.genlib import simple_arg_parser
from zdcp.core.common import rest_call

input = simple_arg_parser(argv)
if   input.get('a'):
 func = "add"
 with open(input['a'],'r') as f:
  args = load(f)
 args['node'] = input.get('n',args.get('node','master'))
elif input.get('d'):
 func = "delete"
 args = {'id':input['d'],'node':input.get('n','master')}
elif input.get('l'):
 func = "list"
 args = {'node':input.get('n','master')}
else:
 print("%s: <settings.json> [-n(ode) <node-name>] -a(dd) <JSON file>| -d(elete) <id>| -l(ist)"%argv[0])
 exit(0)

with open(argv[1],'r') as f:
 settings = load(f)
started = "Executing:system_task_%s(%s)"%(func,args)
try:
 output = rest_call("%s/api/system/task_%s"%(settings['system']['master'],func),args, aTimeout = 300)['data']
except Exception as e:
 output = e.args[0]
print(started)
print("_" * len(started))
print(dumps(output,indent=4, sort_keys=True))

