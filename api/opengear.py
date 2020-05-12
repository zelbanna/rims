"""Opengear REST module. Provides interworking with (through SNMP) opengear console server"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

#
#
def inventory(aCTX, aArgs):
 """Function docstring for inventory TBD

 Args:
  - device_id (required)

 Output:
  - data (inventory)
 """
 from rims.devices.opengear import Device
 ret = {}
 id = aArgs['device_id']
 console = Device(aCTX, id)
 ret['data'] = console.get_inventory();
 with aCTX.db as db:
  ret['extra'] = db.get_row() if (db.do("SELECT * FROM console_info WHERE device_id = '%s'"%id) > 0) else {'access_url':'telnet://%s'%console.get_ip(),'port':6000}
 return ret

#
#
def info (aCTX, aArgs):
 """Function docstring for info TBD

 Args:
  - device_id (required)
  - op (optional)

 Output:
  - data
 """
 ret = {}
 id = aArgs['device_id']
 op = aArgs.pop('op',None)
 with aCTX.db as db:
  if op == 'update':
   if 'port' in aArgs:
    try: aArgs['port'] = int(aArgs['port'])
    except: aArgs['port'] = 6000
   db.update_dict('console_info',aArgs,"device_id = '%s'"%id)
  if (db.do("SELECT * FROM console_info WHERE device_id = '%s'"%id) > 0):
   ret['data'] = db.get_row()
  else:
   ip = db.get_val('ip') if (db.do("SELECT INET_NTOA(ia.ip) AS ip FROM devices LEFT JOIN interfaces AS di ON devices.management_id = di.interface_id LEFT JOIN ipam_addresses AS ia ON di.ipam_id = ia.id WHERE devices.id = '%s'"%id) == 1) else '0.0.0.0'
   db.do("INSERT INTO console_info SET device_id = '%s', access_url = 'telnet://%s'"%(id,ip))
   ret['data'] = {'id':id, 'access_url':'telnet://%s'%ip, 'port':6000 }
 return ret
