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
 def macToInt(aMAC):
  try:
   return int(aMAC.replace(':',''),16)
  except:
   return 0
 ret = {'status':'OK'}
 up = [macToInt(x) for x in aArgs.get('up',[])]
 dn = [macToInt(x) for x in aArgs.get('down',[])]
 print(up)
 print(dn)
 with aCTX.db as db:
  ret['up'] = db.execute(f"UPDATED interfaces SET state = 'up' WHERE mac IN ({','.join(up)})")
  ret['down'] = db.execute(f"UPDATED interfaces SET state = 'down' WHERE mac IN ({','.join(dn)})")
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
 return {'status':'OK' }

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
