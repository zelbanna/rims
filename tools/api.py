#!/usr/bin/python3
# -*- coding: utf-8 -*-
__author__ = "Zacharias El Banna"

from argparse import ArgumentParser
from json import loads, dumps, load
from os   import path as ospath
from sys  import path as syspath
from time import time
syspath.insert(1,ospath.abspath(ospath.join(ospath.dirname(__file__), '..','..')))
from rims.core.common import rest_call
parser = ArgumentParser(prog='api', description = 'CLI API call program')
parser.add_argument('api', metavar='module/function', help = 'API module/function')
parser.add_argument('args', metavar='argument', help = 'API argument', nargs='?')
parser.add_argument('-n','--node',    help = 'Node unless local (X-Route)', required = False)
parser.add_argument('-c','--config',  help = 'Config unless config.json', default='../config.json')
parsedinput = parser.parse_args()
timestamp = int(time())
try:
 args = loads(parsedinput.args)
except:
 args = {}
header = {'X-Route':parsedinput.node} if parsedinput.node else {}
try:
 with open(ospath.abspath(ospath.join(ospath.dirname(__file__), parsedinput.config))) as f:
  header['X-Token'] = load(f).get('token',None)
except:
 header['X-Token'] = None
started=f"Executing:{parsedinput.api}({args})"
print(started)
try:
 res = rest_call(f"http://127.0.0.1:8080/internal/{parsedinput.api}", aArgs = args, aTimeout = 300, aDataOnly = False, aVerify = True, aHeader = header)
except Exception as e:
 output = e.args[0]
else:
 output = res['data']
 for k,v in res['info'].items():
  print(f"{k}: {v}")
print(f"Time spent: {int(time()) - timestamp}\n{'_'*len(started)}\n{dumps(output,indent=4, sort_keys=True)}")
