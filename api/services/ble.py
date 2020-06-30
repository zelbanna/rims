"""BLE API module. Paired with a BLE reporter it Implements an interface to monitor bluetooth. Must be runnning on a DB node"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__type__ = "BLUETOOTH"

#
#
def report(aCTX, aArgs):
 """Function provides interfaces for BLE status reports

 Args:
  - up (required). List of MAC for new devices
  - down (required). List of aged out MACs

 Output:
 """
 ret = {'status':'OK'}
 try:
  cache = aCTX.cache['ble']
 except Exception:
  cache = aCTX.cache['ble'] = {}
 finally:
  for k in cache.keys():
   cache[k] +=1
  if aArgs['up'] or aArgs['down']:
   up = [str(int(x.replace(':',''),16)) for x in aArgs['up']]
   dn = [str(int(x.replace(':',''),16)) for x in aArgs['down']]
   for k in aArgs['up']:
    cache[k] = 0
   with aCTX.db as db:
    ret['up'] = db.execute(f"UPDATE interfaces SET state = 'up' WHERE mac IN ({','.join(up)})") if up else 0
    ret['down'] = db.execute(f"UPDATE interfaces SET state = 'down' WHERE mac IN ({','.join(dn)})") if dn else 0
 return ret

#
#
def status(aCTX, aArgs):
 """Function report status of BLE service. No OP as BLE runs externally and no verification ATM

 Args:
  - type (required)

 Output:
  - data
 """
 return {'data':aCTX.cache.get('ble',{}), 'status':'OK' }

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
 """Function provides restart capabilities of BLE service, No OP ATM

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
 settings = aCTX.config.get('ble',{})
 params = []
 return {'status':'OK' if all(p in settings for p in params) else 'NOT_OK','parameters':{p:settings.get(p) for p in params}}
