"""SRX API module. Implements SRX as authentication server"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__type__ = "AUTHENTICATION"

#
# Make use of SRX device instead
#
from rims.core.common import basic_auth

#
#
def status(aCTX, aArgs):
 """Function docstring for auth table status

 Args:

 Output:
  - data
 """
 ret = {}
 settings = aCTX.config['srx']
 header = basic_auth(settings['username'],settings['password'])
 try: res = aCTX.rest_call("%s/get-userfw-local-auth-table-all"%settings['url'],aHeader = header,aApplication = 'xml', aDataOnly = False)
 except Exception as e:
  ret['status'] = 'NOT_OK'
  ret['info'] = e.args[0]['data']
 else:
  ret['status'] = 'OK'
  ret['data'] = res['data']
 return ret

#
#
def sync(aCTX, aArgs):
 """ Function checks the auth table and add/remove entries

 Args:
  - id (required). Server id on master node

 Output:
 """
 ret = {}
 settings = aCTX.config['srx']
 header = basic_auth(settings['username'],settings['password'])
 try: res = aCTX.rest_call("%s/get-userfw-local-auth-table-all"%settings['url'], aHeader = header, aApplication = 'xml', aDataOnly = False)
 except Exception as e:
  ret['status'] = 'NOT_OK'
  print(str(e))
  ret['info'] = e.args[0]['data']
 else:
  ret['status'] = 'OK'
  add = []
  rem = []
  users = aCTX.node_function('master','authentication','active')(aArgs = {})['data']
  active = [{'ip':entry['ip-address'][0]['data'], 'alias':entry['user-name'][0]['data']} for entry in res['data']['user-identification'][0]['local-authentication-table'][0]['local-authentication-info']]
  for u in users:
   for a in active:
    if a['ip'] == u['ip'] and a['alias'] == u['alias']:
     # keep
     pass
    else:
     pass
     # continue
 return ret

#
#
def restart(aCTX, aArgs):
 """Function provides restart capabilities of service

 Args:

 Output:
  - code
  - output
  - result 'OK'/'NOT_OK'
 """
 return {'status':'OK','code':0,'output':""}

#
#
def authenticate(aCTX, aArgs):
 """ Function adds authentication entry

 Args:
  - alias
  - ip
  - token

 Output:
 """
 settings = aCTX.config['srx']
 return {'status':'OK'}

#
#
def invalidate(aCTX, aArgs):
 """ Function removes authentication entry

 Args:
  - alias
  - ip
  - token

 Output:
 """
 return {'status':'OK'}

#
#
def parameters(aCTX, aArgs):
 """ Function provides parameter mapping of anticipated config vs actual

 Args:

 Output:
  - status
  - parameters
 """
 settings = aCTX.config.get('srx',{})
 params = ['url','username','password']
 return {'status':'OK' if all(p in settings for p in params) else 'NOT_OK','parameters':{p:settings.get(p) for p in params}}
