"""ESXi API module. PRovides interworking with ESXi device module to provide esxi VM interaction

Relies on snmp communities settings:
- read  (read community)
- write (write community)

"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

#
def list(aDict, aCTX):
 """Function docstring for list TBD

 Args:
  - ip (required)
  - sort (optional)

 Output:
 """
 ret = {}
 from rims.devices.esxi import Device
 try:
  esxi = Device(aDict['ip'], aCTX)
  ret['data'] = esxi.get_vm_list(aDict.get('sort','name'))
 except Exception as err:
  ret['error'] = repr(err)
  ret['data'] = []
 return ret

#
#
def op(aDict, aCTX):
 """Function docstring for op TBD

 Args:
  - ip (required)
  - user_id (required)
  - id (required)
  - next-state (required)
  - snapshot (optional)

 Output:
 """
 from rims.devices.esxi import Device
 ret = {'id':aDict['id'],'status':'OK'}
 with Device(aDict['ip'], aCTX) as esxi:
  try:
   if aDict['next-state'] == 'vmsvc-snapshot.create':
    from time import strftime
    esxi.ssh_send("vim-cmd vmsvc/snapshot.create %s 'Portal Snapshot' '%s'"%(aDict['id'],strftime("%Y%m%d")))
    ret['state'] = esxi.get_vm_state(aDict['id'])
    ret['state_id'] = esxi.get_state_str(ret['state'])
   elif aDict['next-state'] == 'vmsvc-snapshot.revert':
    esxi.ssh_send("vim-cmd vmsvc/snapshot.revert %s %s suppressPowerOff"%(aDict['id'],aDict.get('snapshot')))
   elif aDict['next-state'] == 'vmsvc-snapshot.remove':
    esxi.ssh_send("vim-cmd vmsvc/snapshot.remove %s %s"%(aDict['id'],aDict.get('snapshot')))
   elif "vmsvc-" in aDict['next-state']:
    from time import sleep
    vmop = aDict['next-state'].partition('-')[2]
    esxi.ssh_send("vim-cmd vmsvc/%s %s"%(vmop,aDict['id']))
    sleep(2)
    ret['state'] = esxi.get_vm_state(aDict['id'])
    ret['state_id'] = esxi.get_state_str(ret['state'])
   elif aDict['next-state'] == 'poweroff':
    esxi.ssh_send("poweroff")
  except Exception as err:
   ret['status'] = 'NOT_OK'
   ret['error'] = repr(err)
 return ret

#
#
def logs(aDict, aCTX):
 """Function retrieves ESXi logs

 Args:
  - ip (required)
  - count (optional)

 Output:
 """
 from subprocess import check_output
 ret = {'status':'OK'}
 ip  = aDict['ip']
 count = aDict.get('count','30')
 try:
  ret['data'] = check_output("tail -n %s %s | tac"%(count,aCTX.settings['esxi']['logformat'].format(ip)), shell=True).decode().split('\n')
 except Exception as e:
  ret['status'] = 'NOT_OK'
  ret['error'] = repr(e)
 return ret

#
#
def snapshots(aDict, aCTX):
 """Function docstring for snapshots TBD

 Args:
  - ip (required)
  - user_id (required)
  - id (required)

 Output:
 """
 from rims.devices.esxi import Device
 ret = {'status':'OK', 'data':[],'highest':0}
 with Device(aDict['ip'],aCTX) as esxi:
  data = {}
  snapshots = esxi.ssh_send("vim-cmd vmsvc/snapshot.get %s"%aDict['id'])
  for field in snapshots.splitlines():
   if "Snapshot" in field:
    parts = field.partition(':')
    key = parts[0].strip()
    val = parts[2].strip()
    if key[-4:] == 'Name':
     data['name'] = val
    elif key[-10:] == 'Desciption':
     data['desc'] = val
    elif key[-10:] == 'Created On':
     data['created'] = val
    elif key[-2:] == 'Id':
     data['id'] = val
     if int(val) > ret['highest']:
      ret['highest'] = int(val)
    elif key[-5:] == 'State':
     # Last!
     data['state'] = val
     ret['data'].append(data)
     data = {}
 return ret
