"""Opengear REST module. Provides interworking with (through SNMP) opengear console server"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

#
#
def inventory(aRT, aArgs):
 """Function docstring for inventory TBD

 Args:
  - device_id (required)

 Output:
  - data (inventory)
 """
 from rims.devices.opengear import Device
 ret = {}
 id = aArgs['device_id']
 console = Device(aRT, id)
 ret['data'] = console.get_inventory();
 with aRT.db as db:
  ret['extra'] = db.get_row() if (db.query("SELECT * FROM console_info WHERE device_id = '%s'"%id) > 0) else {'access_url':'telnet://%s'%console.get_ip(),'port':6000}
 return ret

#
#
def info (aRT, aArgs):
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
 with aRT.db as db:
  if op == 'update':
   if 'port' in aArgs:
    try: aArgs['port'] = int(aArgs['port'])
    except: aArgs['port'] = 6000
   db.update_dict('console_info',aArgs,"device_id = '%s'"%id)
  if (db.query("SELECT * FROM console_info WHERE device_id = '%s'"%id) > 0):
   ret['data'] = db.get_row()
  else:
   ip = db.get_val('ip') if (db.query("SELECT INET6_NTOA(ia.ip) AS ip FROM devices LEFT JOIN ipam_addresses AS ia ON devices.ipam_id = ia.id WHERE devices.id = '%s'"%id) == 1) else '0.0.0.0'
   db.execute("INSERT INTO console_info SET device_id = '%s', access_url = 'telnet://%s'"%(id,ip))
   ret['data'] = {'id':id, 'access_url':'telnet://%s'%ip, 'port':6000 }
 return ret

