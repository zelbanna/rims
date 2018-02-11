"""Module docstring.

ESXi API module

"""
__author__ = "Zacharias El Banna"
__version__ = "18.02.09GA"
__status__ = "Production"

#
def list(aDict):
 from ..devices.esxi import Device
 ip     = aDict['ip']
 sort   = aDict.get('sort','name')
 esxi   = Device(ip)
 return esxi.get_vm_list(sort)

#
#
def op(aDict):
 ret = {'id':aDict['id'],'name':aDict['name'],'res':'OK'}
 from ..devices.esxi import Device
 esxi = Device(aDict['ip'])
 try:
  if aDict['next-state'] == 'vmsvc-snapshot.create':
   from time import strftime
   with esxi:
    esxi.ssh_send("vim-cmd vmsvc/snapshot.create %s 'Portal Snapshot' '%s'"%(aDict['id'],strftime("%Y%m%d")),aDict['user_id'])
  elif "vmsvc-" in aDict['next-state']:
   vmop = aDict['next-state'].partition('-')[2]
   with esxi:
    esxi.ssh_send("vim-cmd vmsvc/%s %s"%(vmop,aDict['id']),aDict['user_id'])
    from time import sleep
    sleep(2)
  elif aDict['next-state'] == 'poweroff':
   with esxi:
    esxi.ssh_send("poweroff",aDict['user_id'])
 except Exception as err:
  ret['res'] = 'NOT_OK'
  ret['error'] = str(err)
 ret['state'] = esxi.get_vm_state(aDict['id'])
 ret['state_id'] = esxi.get_state_str(ret['state'])
 return ret
