"""FDB API module. This module provides FDB interaction with network devices"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

#
#
def sync(aCTX, aArgs):
 """ Function retrieves switch table for a device and populate FDB table for caching

 Args:
  - id (required)
  - ip (optional).
  - type (optional). Device type

 Output:
 """
 from importlib import import_module
 try:
  module = import_module("rims.devices.%s"%aArgs.get('type','generic'))
  ret = getattr(module,'Device',None)(aCTX,aArgs['id'],aArgs.get('ip')).fdb()
 except Exception as e: ret = {'status':'NOT_OK','info':str(e)}
 else:
  if ret['status'] == 'OK':
   fdb = ret.pop('FDB',[])
   with aCTX.db as db:
    ret['deleted'] = db.execute("DELETE FROM fdb WHERE device_id = %s"%aArgs['id'])
    ret['insert']  = db.execute("INSERT INTO fdb (device_id, vlan, snmp_index, mac) VALUES %s"%','.join("(%s,%s,%s,%s)"%(aArgs['id'],x['vlan'],x['snmp'],x['mac']) for x in fdb)) if len(fdb) > 0 else 0
 return ret

#
#
def list(aCTX, aArgs):
 """ Function retrieves switch table cache

 Args:
  - field (optional)
  - search (optional)

 Output:
  - fdb
 """
 ret = {}
 with aCTX.db as db:
  fields = ['di.interface_id', 'di.name', 'LPAD(hex(fdb.mac),12,0) AS mac', 'fdb.snmp_index','fdb.vlan']
  joins = ['interfaces AS di ON di.device_id = fdb.device_id AND di.snmp_index = fdb.snmp_index']
  where = ['TRUE']
  extras = aArgs.get('extra')
  search = aArgs.get('search')
  if search:
   sfield = aArgs['field']
   if 'device_id' in sfield:
    where.append('fdb.device_id = %s'%search)
   elif 'mac' in sfield:
    try: where.append('fdb.mac = %i'%int(search.replace(':',""),16))
    except: pass

  if extras:
   if 'device_id' in extras:
    fields.append('fdb.device_id')
   if 'hostname' in extras:
    fields.append('devices.hostname')
    joins.append('devices ON fdb.device_id = devices.id')
   if 'oui' in extras:
    fields.append('oui.company AS oui')
    joins.append('oui ON oui.oui = (fdb.mac >> 24)')

  ret['count'] = db.query("SELECT %s FROM fdb LEFT JOIN %s WHERE %s"%(','.join(fields), ' LEFT JOIN '.join(joins), ' AND '.join(where)))
  ret['data'] = db.get_rows()
  for row in ret['data']:
   row['mac'] = ':'.join(row['mac'][i:i+2] for i in [0,2,4,6,8,10])
 return ret

#
#
def search(aCTX, aArgs):
 """ Function finds mac to host mapping

 Args:
  - mac (required)

 Output:
  - data
 """
 ret = {}
 try: mac = int(aArgs['mac'].replace(':',""),16)
 except:
  ret['status'] = 'NOT_OK'
  ret['info'] = 'Malformed MAC'
 else:
  ret = {}
  with aCTX.db as db:
   if (db.query("SELECT device_id, interface_id, name, description, oui.company AS oui FROM interfaces LEFT JOIN oui ON oui.oui = (%i >> 24) WHERE mac = %i ORDER BY snmp_index, name"%(mac,mac)) > 0):
    ret['interfaces'] = db.get_rows()
    db.query("SELECT id, hostname FROM devices WHERE id = %i"%ret['interfaces'][0]['device_id'])
    ret['device'] = db.get_row()
    ret['status'] = 'OK'
   else:
    ret['oui'] = db.get_val('company') if (db.query("SELECT company FROM oui WHERE oui.oui = (%i >> 24)"%mac) > 0) else 'N/A'
    ret['status'] = 'NOT_OK'
    ret['info'] = 'No device found'
 return ret

#
#
def check(aCTX, aArgs):
 """ Function initiate a check/fdb_sync on all network devices

 Args:

 Output:
 """
 ret = {}
 from importlib import import_module

 def __fdb_check(lCTX,lArgs):
  try:
   module = import_module("rims.devices.%s"%lArgs['type'])
   res = getattr(module,'Device',None)(aCTX, lArgs['id'], lArgs['ip']).fdb()
  except Exception as e: aCTX.log("FDB_CHECK_ERROR: %s (%s/%s)"%(str(e),lArgs['id'],lArgs['ip']))
  else:
   if res['status'] == 'OK':
    fdb = res.pop('FDB',[])
    with lCTX.db as db:
     db.execute("DELETE FROM fdb WHERE device_id = %s"%lArgs['id'])
     if(len(fdb) > 0):
      db.execute("INSERT INTO fdb (device_id, vlan, snmp_index, mac) VALUES %s"%','.join("(%s,%s,%s,%s)"%(lArgs['id'],x['vlan'],x['snmp'],x['mac']) for x in fdb))
  return True

 with aCTX.db as db:
  ret['status'] = 'OK'
  ret['count'] = db.query("SELECT devices.hostname, devices.id, INET6_NTOA(ia.ip) AS ip, dt.name AS type FROM devices LEFT JOIN interfaces AS di ON devices.management_id = di.interface_id LEFT JOIN ipam_addresses AS ia ON di.ipam_id = ia.id LEFT JOIN device_types AS dt ON devices.type_id = dt.id WHERE dt.base = 'network'")
  if ret['count'] > 0:
   sema = aCTX.semaphore(20)
   for dev in db.get_rows():
    aCTX.queue_api(__fdb_check,dev,sema)
   for i in range(20):
    sema.acquire()
 return ret
