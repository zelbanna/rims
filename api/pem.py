"""PEM API module. Implements PEM methods"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

#
#
def list(aCTX, aArgs):
 """ Function provides PEM management for a device

 Args:
  - device_id (required)
  - lookup (optional) bool

 Output:
  - data
 """
 ret = {}
 id = aArgs['device_id']
 select = ['dp.*']
 tables = ['device_pems AS dp']
 if aArgs.get('lookup'):
  select.append('devices.hostname AS pdu_name')
  tables.append('devices ON dp.pdu_id = devices.id')
 with aCTX.db as db:
  db.query("SELECT %s FROM %s WHERE device_id = %s"%(', '.join(select),' LEFT JOIN '.join(tables),id))
  ret['data'] = db.get_rows()
 return ret

#
#
def info(aCTX, aArgs):
 """ Function provides pem management for a PEM

 Args:
  - id (required)
  - device_id (optional required). Used when entering a new PEM
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
    ret['update'] = (db.update_dict('device_pems',aArgs,'id=%s'%id) > 0)
   else:
    ret['update'] = (db.insert_dict('device_pems',aArgs) > 0)
    id = db.get_last_id() if ret['update'] else 'new'

  if not id == 'new':
   ret['found'] = (db.query("SELECT * FROM device_pems WHERE id = %s"%id) > 0)
   ret['data'] = db.get_row()
  else:
   ret['data'] = {'id':'new','device_id':aArgs['device_id'], 'name':'PEM','pdu_id':None,'pdu_slot':0,'pdu_unit':0}

  if ret.get('update') and not (ret['data']['pdu_id'] in [None,'NULL']):
   from importlib import import_module
   db.query("SELECT hostname FROM devices WHERE id = %s"%ret['data']['device_id'])
   hostname = db.get_val('hostname')
   # Slot id is RIMS slot ID, so we need to look up pdu_slot => pdu_info.X_slot_id
   db.query("SELECT INET6_NTOA(ia.ip) AS ip, devices.hostname, dt.name AS type, pi.%(pdu_slot)s_slot_id AS pdu_slot FROM devices LEFT JOIN device_types AS dt ON devices.type_id = dt.id LEFT JOIN ipam_addresses AS ia ON devices.ipam_id = ia.id LEFT JOIN pdu_info AS pi ON devices.id = pi.device_id WHERE devices.id = %(pdu_id)s"%ret['data'])
   pdu_info = db.get_row()
   try:
    module = import_module("rims.devices.%s"%pdu_info['type'])
    pdu = getattr(module,'Device',None)(aCTX, ret['data']['pdu_id'],pdu_info['ip'])
    pdu_res = pdu.set_name( int(pdu_info['pdu_slot']), int(ret['data']['pdu_unit']) , "%s-%s"%(hostname,ret['data']['name']) )
    ret['result'] = pdu_res
   except Exception as e:
    ret['status'] = 'NOT_OK'
    ret['info'] = str(e)
   else:
    ret['status'] = 'OK'
 return ret

#
#
def delete(aCTX, aArgs):
 """ Function deletes a PEM

 Args:
  - id (required)

 Output:
 """
 ret = {}
 with aCTX.db as db:
  ret['deleted'] = (db.execute("DELETE FROM device_pems WHERE id = %s"%aArgs['id']) == 1)
  ret['status'] = 'OK' if ret['deleted'] else 'NOT_OK'
 return ret
