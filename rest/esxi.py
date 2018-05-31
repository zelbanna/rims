"""ESXi API module. PRovides interworking with ESXi device module to provide esxi VM interaction"""
__author__ = "Zacharias El Banna"
__version__ = "18.05.31GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

#
def list(aDict):
 """Function docstring for list TBD

 Args:
  - ip (required)
  - sort (optional)

 Output:
 """
 ret = {}
 from sdcp.devices.esxi import Device
 try:
  esxi = Device(aDict['ip'])
  ret['data'] = esxi.get_vm_list(aDict.get('sort','name'))
 except Exception as err:
  ret['error'] = str(err)
  ret['data'] = []
 return ret 

#
#
def op(aDict):
 """Function docstring for op TBD

 Args:
  - ip (required)
  - user_id (required)
  - id (required)
  - next-state (required)
  - snapshot (optional)

 Output:
 """
 from sdcp.devices.esxi import Device
 ret = {'id':aDict['id'],'res':'OK'}
 with Device(aDict['ip']) as esxi:
  try:
   if aDict['next-state'] == 'vmsvc-snapshot.create':
    from time import strftime
    esxi.ssh_send("vim-cmd vmsvc/snapshot.create %s 'Portal Snapshot' '%s'"%(aDict['id'],strftime("%Y%m%d")),aDict['user_id'])
    ret['state'] = esxi.get_vm_state(aDict['id'])
    ret['state_id'] = esxi.get_state_str(ret['state'])
   elif aDict['next-state'] == 'vmsvc-snapshot.revert':
    esxi.ssh_send("vim-cmd vmsvc/snapshot.revert %s %s suppressPowerOff"%(aDict['id'],aDict.get('snapshot')),aDict['user_id'])
   elif aDict['next-state'] == 'vmsvc-snapshot.remove':
    esxi.ssh_send("vim-cmd vmsvc/snapshot.remove %s %s"%(aDict['id'],aDict.get('snapshot')),aDict['user_id'])
   elif "vmsvc-" in aDict['next-state']:
    from time import sleep
    vmop = aDict['next-state'].partition('-')[2]
    esxi.ssh_send("vim-cmd vmsvc/%s %s"%(vmop,aDict['id']),aDict['user_id'])
    sleep(2)
    ret['state'] = esxi.get_vm_state(aDict['id'])
    ret['state_id'] = esxi.get_state_str(ret['state'])
   elif aDict['next-state'] == 'poweroff':
    esxi.ssh_send("poweroff",aDict['user_id'])
  except Exception as err:
   ret['res'] = 'NOT_OK'
   ret['error'] = str(err)
 return ret

#
#
def logs(aDict):
 """Function docstring for logs TBD

 Args:
  - hostname (required)
  - count (optional)

 Output:
 """
 from subprocess import check_output
 from sdcp.SettingsContainer import SC
 ret = {'res':'OK'}
 hostname = aDict['hostname']
 count = aDict.get('count','30')
 try:
  ret['data'] = check_output("tail -n %s %s | tac"%(count,SC['esxi']['logformat'].format(hostname)), shell=True).split('\n')
 except Exception as e:
  ret['res'] = 'NOT_OK'
  ret['error'] = str(e)
 return ret

#
#
def snapshots(aDict):
 """Function docstring for snapshots TBD

 Args:
  - ip (required)
  - user_id (required)
  - id (required)

 Output:
 """
 from sdcp.devices.esxi import Device
 ret = {'res':'OK', 'data':[],'highest':0}
 with Device(aDict['ip']) as esxi:
  data = {}                  
  snapshots = esxi.ssh_send("vim-cmd vmsvc/snapshot.get %s"%aDict['id'],aDict['user_id'])
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
