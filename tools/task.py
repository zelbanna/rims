#!/usr/bin/python3
# -*- coding: utf-8 -*-

from os   import path as ospath, getcwd
from sys  import path as syspath, argv, exit
from json import loads,load,dumps
from time import time
from argparse import ArgumentParser

basepath = ospath.abspath(ospath.join(ospath.dirname(__file__), '..','..'))
syspath.insert(1, basepath)
from rims.core.common import rest_call

parser = ArgumentParser(description = 'Interface to RIMS task system', prog = 'task.py')
parser.add_argument('config', help = 'RIMS config file')
parser.add_argument('-n','--node',   help = 'Node to run on', required = False, default = 'master')
parser.add_argument('-a','--add',    nargs = 1, help = 'Add JSON file with task info', required = False)
parser.add_argument('-d','--delete', nargs = 1, help = 'Id of task to delete', required = False)
parser.add_argument('-l','--list',   help = 'List tasks', required = False, action = 'store_true')
input = parser.parse_args()

if   input.add:
 func = 'add'
 with open(input.add[0],'r') as f:
  args = load(f)
elif input.delete:
 func = 'delete'
 args = {'id':input.delete}
elif input.list:
 func = 'list'
 args = {}
else:
 parser.print_help()
 exit(0)

args['node'] = input.node
with open(input.config,'r') as f:
 config = load(f)
 token = config.get('token',None)

started = "Executing:system_task_%s(%s)"%(func, args)
try:
 output = rest_call("%s/internal/master/task_%s"%(config['master'],func),aArgs = args, aTimeout = 300, aDataOnly = True, aHeader = {'X-Token':token})
except Exception as e:
 output = e.args[0]
print(started)
print("_" * len(started))
print(dumps(output,indent=4, sort_keys=True))
