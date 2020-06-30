#!/usr/bin/python3
"""BLE bluetooth server. Heavily depends on gattool so requires all of those files.
See: https://bitbucket.org/OscarAcena/pygattlib/src/default/README.md
"""
__author__  = "Zacharias El Banna"

from argparse import ArgumentParser
from json import load
from os   import path as ospath
from sys  import path as syspath, exit as sysexit
from time import sleep
from gattlib import DiscoveryService
syspath.insert(1,ospath.abspath(ospath.join(ospath.dirname(__file__), '..','..')))
from rims.core.common import rest_call, RestException
parser = ArgumentParser(prog='ble', description = 'BLE runtime program')
parser.add_argument('-c','--config', help = 'Config unless config.json', default='../config.json')
parser.add_argument('-d','--device', help = 'Device', required = False, default='hci0')
parser.add_argument('-u','--url',    help = 'RIMS URL', required = False, default='http://127.0.0.1:8080')
parser.add_argument('-s','--sleep',  help = 'Sleeptime', required = False, default=40)
parser.add_argument('-t','--timeout',  help = 'Sleeptime', required = False, default=20)
args = parser.parse_args()
print(f"Starting BLE discovery with: device:{args.device}, sleep:{args.sleep}, timeout:{args.timeout}, URL:{args.url}")
try:
 with open(ospath.abspath(ospath.join(ospath.dirname(__file__), args.config))) as f:
  token = load(f).get('token',None)
except:
 token = None
service = DiscoveryService(args.device)
data = {}

while True:
 try:
  discovered = service.discover(int(args.timeout))
 except Exception as e:
  print(f"BLE Error: {e}")
  sysexit(1)
 else:
  try:
   res = rest_call(f"{args.url}/internal/services/ble/report", aArgs = {'devices':discovered}, aTimeout = 5, aHeader = {'X-Token':token, 'X-Log':False})
  except Exception as e:
   print(f"REST Error: {e}")
 sleep(int(args.sleep))
