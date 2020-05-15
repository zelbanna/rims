"""SRX API module. Implements SRX as authentication server"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__type__ = "AUTHENTICATION"

from rims.core.common import basic_auth

#
#
def status(aCTX, aArgs):
 """Function docstring for auth table status

 Args:

 Output:
  - data
 """
 settings = aCTX.config['srx']
 header = basic_auth(settings['username'],settings['password'])
 print(aCTX.rest_call("%s/get-system-information"%settings['url'],aHeader = header,aApplication = 'xml', aDataOnly = False))
 return {'data':None, 'status':'OK' }

#
#
def sync(aCTX, aArgs):
 """ Function checks the auth table and add/remove entries

 Args:
  - id (required). Server id on master node

 Output:
 """
 return {'status':'OK','output':'No OP'}

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
