"""ESXi API module. Provides interworking with ESXi device module to provide esxi VM interaction"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

from rims.devices.esxi import Device

#
def inventory(aCTX, aArgs):
 """Function docstring for inventory TBD

 Args:
  - device_id (required)
  - sort (optional)

 Output:
 """
 ret = {}
 try:
  esxi = Device(aCTX, aArgs['device_id'])
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
def vm_info(aCTX, aArgs):
 """Function info returns state information for VM

 Args:
  - device_id (required)
  - vm_id (required)
  - op (optional). 'update' will update the cached information about the VM (mapping)

 Output:
 """
 ret = {}
 try:
  esxi = Device(aCTX, aArgs['device_id'])
  ret['data'] = esxi.get_info(aArgs['vm_id'])
 except Exception as err:
  ret['status'] = 'NOT_OK'
  ret['info'] = repr(err)
 else:
  ret['status'] = 'OK'
  ret['interfaces'] = ret['data'].pop('interfaces',None)
  with aCTX.db as db:
   if (db.query("SELECT dvu.device_id, dvu.host_id, dvu.snmp_id, dvu.server_uuid, dev.hostname AS device_name, dvu.vm FROM device_vm_uuid AS dvu LEFT JOIN devices AS dev ON dev.id = dvu.device_id WHERE device_uuid = '%s'"%ret['data']['device_uuid']) == 1):
    ret['data'].update(db.get_row())
    vm = ret['data'].pop('vm',None)
    if(ret['data']['device_id']):
     db.query("SELECT interface_id, LPAD(hex(mac),12,0) AS mac, name FROM interfaces WHERE device_id = %s"%ret['data']['device_id'])
     ret['device'] = db.get_rows()
     for intf in ret['device']:
       intf['mac'] = ':'.join(intf['mac'][i:i+2] for i in [0,2,4,6,8,10]) if intf.get('mac') else '00:00:00:00:00:00'
     for vm_if in ret['interfaces'].values():
      if ret['device']:
       for i,dev_if in enumerate(ret['device']):
        if dev_if['mac'] == vm_if['mac']:
         vm_if.update({'interface_id':dev_if['interface_id'],'pos':i})
         break
       if 'pos' in vm_if:
        ret['device'].pop(vm_if['pos'])
        vm_if.pop('pos',None)
    if aArgs.get('op') == 'update' or vm != ret['data']['name']:
     ret['update'] = (db.execute("UPDATE device_vm_uuid SET vm = '%s', config = '%s', snmp_id = '%s' WHERE device_uuid = '%s'"%(ret['data']['name'], ret['data']['config'], aArgs['vm_id'],  ret['data']['device_uuid'])) == 1)
   else:
    ret['data']['device_id'] = None
 return ret

#
#
def vm_map(aCTX, aArgs):
 """ Function maps or retrieves VM to device ID mapping

 Args:
  - device_uuid (required)
  - device_id (optional required)
  - host_id (optional_reauired)
  - op (optional)

 Output:
 """
 ret = {}
 op = aArgs.pop('op',None)
 with aCTX.db as db:
  if op == 'update':
   ret['update'] = (db.execute("UPDATE device_vm_uuid SET device_id = '%(device_id)s', host_id = '%(host_id)s' WHERE device_uuid = '%(device_uuid)s'"%aArgs) == 1)
  ret['data'] = db.get_val('device_id') if (db.query("SELECT device_id FROM device_vm_uuid WHERE device_uuid = '%(device_uuid)s'"%aArgs) > 0) else ''
 return ret

#
#
def vm_op(aCTX, aArgs):
 """Function op provides VM operation control

 Args:
  - device_id (required)
  - vm_id (required)
  - op (required), 'on/off/reboot/shutdown/suspend'
  - uuid (optional)

 Output:
 """
 with Device(aCTX, aArgs['device_id']) as esxi:
  ret = esxi.vm_operation(aArgs['op'],aArgs['vm_id'],aUUID = aArgs.get('uuid'))
 return ret

#
#
def vm_snapshot(aCTX, aArgs):
 """Function snapshot provides VM snapshot control

 Args:
  - device_id (required)
  - vm_id (required)
  - op (required), 'create/revert/remove/list'
  - snapshot (optional)

 Output:
  - data (optional)
  - status
 """
 with Device(aCTX, aArgs['device_id']) as esxi:
  ret = esxi.snapshot(aArgs['op'],aArgs['vm_id'], aArgs.get('snapshot'))
 return ret

#
#
def parameters(aCTX, aArgs):
 """ Function provides parameter mapping of anticipated config vs actual

 Settings:
 - username
 - password
 Extra:
 snmp settings

 Args:

 Output:
  - status
  - parameters
 """
 settings = aCTX.config.get('esxi',{})
 settings.update(aCTX.config.get('snmp',{}))
 params = ['username','password','read','write','timeout']
 return {'status':'OK' if all(p in settings for p in params) else 'NOT_OK','parameters':{p:settings.get(p) for p in params}}
