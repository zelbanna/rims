"""AWX REST module."""
__author__ = "Zacharias El Banna"
__version__ = "18.05.31GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

from sdcp.devices.awx import Device
from sdcp.SettingsContainer import SC

#
#
def inventories_list(aDict):
 """Function docstring for inventory_list TBD

 Args:
  - node (required)

 Output:
 """
 controller = Device(SC['node'][aDict['node']])
 controller.auth({'username':SC['awx']['username'],'password':SC['awx']['password'],'mode':'basic'})
 return controller.inventories()

#
#
def hosts_list(aDict):
 """Function retrieves all hosts from AWX node

 Args:
  - node (required)

 Output:
 """
 controller = Device(SC['node'][aDict['node']])
 controller.auth({'username':SC['awx']['username'],'password':SC['awx']['password'],'mode':'basic'})
 return controller.hosts()
 
#
#
def hosts_sync(aDict):
 """Function retrieves and matches AWX hosts with local ones and updates missing

 Args:
  - node (required)
  - inventory_id (required)
  - device_search (required)
  - device_field (required)

 Output:
  - result (boolean)
  - info (optional)
 """
 from sdcp.rest.device import list as device_list
 hosts = {}
 devices = device_list({'search':aDict['device_search'],'field':aDict['device_field']})['data']
 ret = {'devices':devices,'result':'OK','extra':[]}
 controller = Device(SC['node'][aDict['node']])
 controller.auth({'username':SC['awx']['username'],'password':SC['awx']['password'],'mode':'basic'})
 try:
  next = "hosts"
  while next:
   data = controller.call(next)['data']
   for row in data['results']:
    info = {k:row.get(k) for k in ('id','name','url','inventory','description','enabled','instance_id')}
    if row['instance_id'] == "":
     ret['extra'].append({k:row.get(k) for k in ('id','name')})
    else:
     hosts[row['instance_id']] = {k:row.get(k) for k in ('id','name','url','inventory','description','enabled','instance_id')}
   next = data['next']
  for dev in devices:
   args = {"name": dev['fqdn'],"description": "%s (%s)"%(dev['model'],dev['ipasc']),"inventory": aDict['inventory_id'],"enabled": True,"instance_id": dev['id'], "variables": "" }
   host = hosts.get(str(dev['id']))
   res = controller.call("hosts/",args,"POST") if not host else controller.call("hosts/%s/"%host['id'],args,"PATCH")
   dev['sync'] = {'code':res['code'],'id':res['data']['id']}
 except Exception as e:
  ret['info'] = str(e)
  ret['result'] = 'NOT_OK'
 return ret
