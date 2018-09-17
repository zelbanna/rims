#!/usr/bin/python
# -*- coding: utf-8 -*-

from json import loads,load,dumps,dump
from os import remove, chmod, listdir, path as ospath
from sys import path as syspath, argv,exit
pkgdir = ospath.abspath(ospath.dirname(__file__))
basedir = ospath.abspath(ospath.join(pkgdir,'..'))
syspath.insert(1, basedir)
from importlib import import_module
from zdcp.Settings import SC
from zdcp.core.common import DB
from zdcp.core.genlib import simple_arg_parser
module =  import_module("zdcp.rest.system")
module.__add_globals__({'ospath':ospath,'loads':loads,'dumps':dumps,'import_module':import_module,'SC':SC})

input = simple_arg_parser(argv)
if   input.get('a'):
 fun = getattr(module,"task_add",None)
 with open(input['a'],'r') as f:
  args = load(f)
 args['node'] = input.get('n',args.get('node','master'))
elif input.get('d'):
 fun = getattr(module,"task_delete",None)
 args= {'id':input['d']}
elif input.get('l'):
 fun = getattr(module,"task_list",None)
 args = {'node':input.get('n','master')}
elif input.get('s'):
 fun = getattr(module,"task_state",None)
 args = {'id':input['i'],'state':input['s']}
else:
 print "%s: [-n(ode) <node-name>] -a(dd) <JSON file>| -d(elete) <id>| -l(ist) | -s(status) [0|1 to change state] -i <id>"%argv[0]
 exit(0)

print dumps(fun(args),indent=4, sort_keys=True)
exit(0)
