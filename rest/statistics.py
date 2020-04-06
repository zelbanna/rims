"""Statistics API module. Implements device statistics methods"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

#
#
def list(aCTX, aArgs = None):
 """ Function provides stats for a device

 Args:
  - device_id (required)
  - lookup (optional) bool

 Output:
  - data
 """
 ret = {}
 id = aArgs['device_id']
 select = ['ds.*']
 tables = ['device_statistics AS ds']
 with aCTX.db as db:
  db.do("SELECT %s FROM %s WHERE device_id = %s"%(', '.join(select),' LEFT JOIN '.join(tables),id))
  ret['data'] = db.get_rows()
 return ret

#
#
def info(aCTX, aArgs = None):
 """ Function provides data point management for a device

 Args:
  - id (required)
  - device_id (optional required). Used when entering a new data point
  - op (optional)
  - <data>

 Output:
  - <data>
  - update (optional)
 """
 ret = {}
 id = aArgs.pop('id',None)
 op = aArgs.pop('op',None)
 with aCTX.db as db:
  if op == 'update':
   if not id == 'new':
    ret['update'] = (db.update_dict('device_statistics',aArgs,'id=%s'%id) > 0)
   else:
    ret['update'] = (db.insert_dict('device_statistics',aArgs) > 0)
    id = db.get_last_id() if ret['update'] else 'new'

  if not id == 'new':
   ret['found'] = (db.do("SELECT * FROM device_statistics WHERE id = %s"%id) > 0)
   ret['data'] = db.get_row()
  else:
   ret['data'] = {'id':'new','device_id':aArgs['device_id'], 'measurement':"",'tags':"",'name':"",'oid':""}
 return ret

#
#
def delete(aCTX, aArgs = None):
 """ Function deletes a data point

 Args:
  - id (required)

 Output:
 """
 ret = {}
 with aCTX.db as db:
  ret['deleted'] = (db.do("DELETE FROM device_statistics WHERE id = %s"%aArgs['id']) == 1)
  ret['status'] = 'OK' if ret['deleted'] else 'NOT_OK'
 return ret

#
#
def lookup(aCTX, aArgs = None):
 """ Function looks up device type based data points

 Args:
 - device_id

 Output:
 """
 id = aArgs['device_id']
 ret = {'inserts':0}
 from importlib import import_module
 with aCTX.db as db:
  if (db.do("SELECT INET_NTOA(ia.ip) AS ip, dt.name AS type FROM devices LEFT JOIN device_types AS dt ON devices.type_id = dt.id LEFT JOIN device_interfaces AS di ON di.interface_id = devices.management_id LEFT JOIN ipam_addresses AS ia ON ia.id = di.ipam_id WHERE devices.id = %s"%id) > 0):
   info = db.get_row()
   try:
    module = import_module("rims.devices.%s"%info['type'])
    device = getattr(module,'Device',None)(aCTX, id, info['ip'])
    for ddp in device.get_data_points():
     ret['inserts'] += db.do("INSERT INTO device_statistics (device_id,measurement,tags,name,oid) VALUES(%i,'%s','%s','%s','%s') ON DUPLICATE KEY UPDATE id = id"%(int(id),ddp[0],ddp[1],ddp[2],ddp[3]),True)
   except Exception as e:
    ret['status'] = 'NOT_OK'
    ret['info'] = str(e)
   else:
    ret['status'] = 'OK'
    ret['result'] = '%s data points inserted'%ret['inserts']
  else:
   ret['status'] = 'NOT_OK'
   ret['info'] = 'device info not found'
 return ret
