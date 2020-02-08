"""ESXi API module. PRovides interworking with ESXi device module to provide esxi VM interaction

Config section: snmp
- read  (read community)
- write (write community)
- timeout

"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

from rims.devices.esxi import Device

#
def list(aCTX, aArgs = None):
 """Function docstring for list TBD

 Args:
  - id (required)
  - sort (optional)

 Output:
 """
 ret = {}
 try:
  esxi = Device(aCTX, aArgs['id'])
  ret['data'] = esxi.get_vm_list(aArgs.get('sort','name'))
 except Exception as err:
  ret['status'] = 'NOT_OK'  
  ret['info'] = repr(err)
  ret['data'] = []
 else:
  ret['status'] = 'OK'
 return ret

#
#
def info(aCTX, aArgs = None):
 """Function info returns state information for VM

 Args:
  - id (required)
  - vm_id (required)
  - op (optional). 'update' will update the cached information about the VM (mapping)

 Output:
 """
 ret = {'vm_id':aArgs['vm_id'],'id':aArgs['id']}
 try:
  esxi = Device(aCTX, aArgs['id'])
  ret['data'] = esxi.get_info(aArgs['vm_id'])
 except Exception as err:
  ret['status'] = 'NOT_OK'
  ret['info'] = repr(err)
 else:
  ret['status'] = 'OK'
  with aCTX.db as db:
   if (db.do("SELECT dvu.device_id, dvu.host_id, dvu.snmp_id, dvu.server_uuid, dev.hostname AS device_name, dvu.vm FROM device_vm_uuid AS dvu LEFT JOIN devices AS dev ON dev.id = dvu.device_id WHERE device_uuid = '%s'"%ret['data']['device_uuid']) == 1):
    ret['data'].update(db.get_row())
    vm = ret['data'].pop('vm',None)
    if aArgs.get('op') == 'update' or vm != ret['data']['name']:
     ret['update'] = (db.do("UPDATE device_vm_uuid SET vm = '%s', config = '%s', snmp_id = '%s' WHERE device_uuid = '%s'"%(ret['data']['name'], ret['data']['config'], aArgs['vm_id'],  ret['data']['device_uuid'])) == 1)
 return ret

#
#
def map(aCTX, aArgs = None):
 """ Function maps or retrieves VM to device ID mapping

 Args:
  - device_uuid (required)
  - device_id (optional required)
  - op (optional)

 Output:
 """
 ret = {'device_uuid':aArgs['device_uuid']}
 op = aArgs.pop('op',None)
 with aCTX.db as db:
  if op == 'update':
   try:    aArgs['device_id'] = int(aArgs['device_id'])
   except: pass
   else:   ret['update'] = (db.do("UPDATE device_vm_uuid SET device_id = '%(device_id)s' WHERE device_uuid = '%(device_uuid)s'"%aArgs) == 1)
  ret['device_id'] = db.get_val('device_id') if (db.do("SELECT device_id FROM device_vm_uuid WHERE device_uuid = '%(device_uuid)s'"%aArgs) > 0) else None
 return ret

#
#
def control(aCTX, aArgs = None):
 """Function control provides VM operation control

 Args:
  - id (required)
  - vm_id (required)
  - op (required), 'create/revert/remove/list' (for snapshots on VM id's) 'on/off/reboot/shutdown/suspend' (for VM id's)
  - uuid (optional)
  - snapshot (optional)

 Output:
 """
 with Device(aCTX, aArgs['id']) as esxi:
  if aArgs['op'] in ['on','off','reboot','shutdown','suspend']:
   ret = esxi.vm_operation(aArgs['op'],aArgs['vm_id'],aUUID = aArgs.get('uuid'))
  else:
   ret = esxi.snapshot(aArgs['op'],aArgs['vm_id'], aArgs.get('snapshot'))
 return ret
