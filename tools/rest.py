#!/usr/bin/python3
# -*- coding: utf-8 -*-
__author__ = "Zacharias El Banna"

from argparse import ArgumentParser
from json import loads,dumps
from os   import path as ospath
from sys  import path as syspath, exit as sysexit
from time import time
syspath.insert(1, ospath.abspath(ospath.join(ospath.dirname(__file__), '..','..')))
from rims.core.common import rest_call, ssl_context

parser = ArgumentParser(prog='rest.py',description='Process REST calls')
parser.add_argument('url', help = 'REST URL')
parser.add_argument('-a','--args', help = 'Arguments', required = False, default = '{}')
parser.add_argument('-m','--method', help = 'Method, default GET or default POST if arguments supplied', required = False, default = 'POST')
parser.add_argument('-c','--app',    help = 'Content/Application type, default json', required = False, default = 'json')
parsedinput = parser.parse_args()

if not parsedinput.url:
 parser.print_help()
 sysexit(0)

timestamp = int(time())
try:
 args = loads(parsedinput.args)
except:
 args = {}
started = f"Executing:{parsedinput.url}({args})"
print(started)
try:
 res = rest_call(parsedinput.url, aArgs = args, aMethod = parsedinput.method, aApplication = parsedinput.app, aTimeout = 300, aDebug = True, aSSL = ssl_context() if (parsedinput.url[0:5] == 'https') else None)
except Exception as e:
 output = e.args[0]
else:
 output = res['data']
 for k,v in res['info'].items():
  print(f"{k}: {v}")
print(f"Time spent: {int(time()) - timestamp}\n{'_'*len(started)}\n{dumps(output,indent=4, sort_keys=True)}")
