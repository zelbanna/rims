"""NoDHCP API module. Implements dummy DHCP server"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__type__ = "DHCP"

#
#
#
def status(aCTX, aArgs):
 """Function docstring for leases. No OP

 Args:
  - type (required)

 Output:
  - data
 """
 return {'data':None, 'status':'OK' }

#
def sync(aCTX, aArgs):
 """No OP

 Args:
  - id (required). Server id on master node

 Output:
  - code. (error code, optional)
  - output. (output from command)
  - status. (operation result)
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
def parameters(aCTX, aArgs):
 """ Function provides parameter mapping of anticipated config vs actual

 Args:

 Output:
  - status
  - parameters
 """
 settings = aCTX.config['services'].get('nodhcp',{})
 params = []
 return {'status':'OK' if all(p in settings for p in params) else 'NOT_OK','parameters':{p:settings.get(p) for p in params}}

#
#
def start(aCTX, aArgs):
 """ Function provides start behavior

 Args:

 Output:
  - status
 """
 return {'status':'NO OP'}

#
#
def stop(aCTX, aArgs):
 """ Function provides stop behavior

 Args:

 Output:
  - status
 """
 return {'status':'NO OP'}

