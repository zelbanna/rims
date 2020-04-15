#!/usr/bin/python3
# -*- coding: utf-8 -*-
__author__ = "Zacharias El Banna"

from os   import path as ospath, getcwd
from sys  import path as syspath, argv, exit
from argparse import ArgumentParser

basepath = ospath.abspath(ospath.join(ospath.dirname(__file__), '..','..'))
syspath.insert(1, basepath)

parser = ArgumentParser(prog='rest.py',description='Process REST calls')
parser.add_argument('url', help = 'REST URL')
parser.add_argument('args', help = 'Arguments', default = '{}')
parser.add_argument('-m','--method', help = 'Method, default GET or default POST if arguments supplied', required = False, default = 'POST')
parser.add_argument('-c','--app',    help = 'Content/Application type, default json', required = False, default = 'json')
input = parser.parse_args()

if not input.url:
 parser.print_help()
 exit(0)

from json import loads, dumps
from time import time
from rims.core.common import rest_call
timestamp = int(time())
try:    args = loads(input.args)
except: args = {}
started = "Executing:%s(%s)"%(argv[1],args)
print(started)
try:  res = rest_call(input.url, aArgs = args, aMethod = input.method, aApplication = input.app, aTimeout = 300, aDataOnly = False, aVerify = False if argv[1][0:5] == 'https' else True)
except Exception as e: output = e.args[0]
else:
 output = res['data']
 for x in res['info'].items():
  print("%s: %s"%x)
print("Time spent: %i\n%s\n%s"%(int(time()) - timestamp,'_'*len(started),dumps(output,indent=4, sort_keys=True)))
