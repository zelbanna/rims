"""SRX API module. Implements SRX as authentication server"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__type__ = "AUTHENTICATION"

from rims.devices.srx import Device

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
 try:
  with Device(aCTX,settings['device_id'],settings['ip']) as dev:
   ret = dev.auth_table()
 except Exception as e:
  ret = {'status':'NOT_OK','info':str(e)}
 return ret

#
#
def sync(aCTX, aArgs):
 """ Function checks the auth table and add/remove entries

 Args:
  - id (required). Server id on master node

 Output:
 """
 pass

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
 params = ['device_id','ip']
 return {'status':'OK' if all(p in settings for p in params) else 'NOT_OK','parameters':{p:settings.get(p) for p in params}}
