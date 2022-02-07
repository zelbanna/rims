"""BLE API module. Paired with a BLE reporter it implements an interface to monitor bluetooth. Must be runnning on a DB node"""
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
  up = []
  dn = []
  for k in cache.keys():
   if aArgs['devices'].pop(k,False):
    cache[k] = 0
   elif cache[k] < 5:
    cache[k] += 1
   else:
    dn.append(k)
  for k in aArgs['devices'].keys():
   cache[k] = 0
   up.append(k)
  for k in dn:
   cache.pop(k,None)
  if up or dn:
   with aCTX.db as db:
    ret['up'] = db.execute(f"UPDATE interfaces SET state = 'up' WHERE mac IN ({','.join(str(int(k.replace(':',''),16)) for k in up)})") if up else 0
    ret['down'] = db.execute(f"UPDATE interfaces SET state = 'down' WHERE mac IN ({','.join(str(int(k.replace(':',''),16)) for k in dn)})") if dn else 0
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
 return {'cache':aCTX.cache.get('ble',{}), 'status':'OK' }

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
 settings = aCTX.config['services'].get('ble',{})
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
