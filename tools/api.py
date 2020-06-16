#!/usr/bin/python3
# -*- coding: utf-8 -*-
__author__ = "Zacharias El Banna"

from os   import path as ospath
from sys  import path as syspath, exit
from json import loads, dumps, load
from time import time
syspath.append(ospath.abspath(ospath.join(ospath.dirname(__file__), '..','..')))
from rims.core.common import rest_call
from argparse import ArgumentParser
parser = ArgumentParser(prog='api', description = 'CLI API call program')
parser.add_argument('api', metavar='module/function', help = 'API module/function')
parser.add_argument('args', metavar='argument', help = 'API argument', nargs='?')
parser.add_argument('-n','--node',    help = 'Node unless local (X-Route)', required = False)
parser.add_argument('-c','--config',  help = 'Config unless config.json', default='../config.json')
input = parser.parse_args()
timestamp = int(time())
try:    args = loads(input.args)
except: args = {}
header = {'X-Route':input.node} if input.node else {}
try:
 with open(ospath.abspath(ospath.join(ospath.dirname(__file__), input.config))) as f:
  header['X-Token'] = load(f).get('token',None)
except: header['X-Token'] = None
started="Executing:%s(%s)"%(input.api,args)
print(started)
try: res = rest_call("http://127.0.0.1:8080/internal/%s"%input.api, aArgs = args, aTimeout = 300, aDataOnly = False, aVerify = True, aHeader = header)
except Exception as e: output = e.args[0]
else:
 output = res['data']
 for x in res['info'].items():
  print("%s: %s"%x)
print("Time spent: %i\n%s\n%s"%(int(time()) - timestamp,'_'*len(started),dumps(output,indent=4, sort_keys=True)))
