"""AWX REST module."""
__author__ = "Zacharias El Banna"
__version__ = "1.0GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

from zdcp.devices.awx import Device
from zdcp.SettingsContainer import SC

#
#
def node_to_ui(aDict):
 """Function docstring for node_to_ui TBD

 Args:
  - node (required)

 Output:
 """
 node = SC['node'][aDict.get('node','awx')]
 parts = node.partition('//')
 host = "%s//%s/"%(parts[0],(parts[2].split('/')[0]).split(':')[0])
 return {'ui':host }

#
#
def inventory_list(aDict):
 """Function main produces an inventory list for a device id

 Args:
  - id (optional required)
  - node (optional required)

 Output:
  - inventories
 """
 from zdcp.rest.device import node_mapping
 ret = node_mapping(aDict)
 controller = Device(SC['node'][ret['node']])
 controller.auth({'username':SC['awx']['username'],'password':SC['awx']['password'],'mode':'basic'})
 ret['inventories'] = controller.fetch_list("inventories/",('id','name','url'))
 return ret

#
#
def inventory_delete(aDict):
 """Function deletes inventory with id x

 Args:
  - node (required)
  - id (required)

 Output:
 """
 controller = Device(SC['node'][aDict['node']])
 controller.auth({'username':SC['awx']['username'],'password':SC['awx']['password'],'mode':'basic'})
 res = controller.call("inventories/%(id)s/"%aDict,None,"DELETE")
 ret = {'result':"deleted" if res['code'] == 204 else res['info']['x-api-code']}
 return ret

#
#
def inventory_info(aDict):
 """Function produces inventory info for a specific inventory id

 Args:
  - node (required)
  - id (required)

 Output:
 """
 ret = {'hosts':[]}
 controller = Device(SC['node'][aDict['node']])
 controller.auth({'username':SC['awx']['username'],'password':SC['awx']['password'],'mode':'basic'})
 ret['hosts']  = controller.fetch_list("inventories/%(id)s/hosts/"%aDict,('id','instance_id','name','description'))
 ret['groups'] = controller.fetch_dict("inventories/%(id)s/groups/"%aDict,('id','name','description','total_hosts'),'name')
 return ret

#
#
def inventory_sync(aDict):
 """Function retrieves and matches AWX hosts with local ones and updates missing info

 Args:
  - node (required)
  - id (required)
  - search (required)
  - field (required)

 Output:
  - result (boolean)
  - info (optional)
 """
 from zdcp.rest.device import list as device_list
 hosts = {}
 devices = device_list({'search':aDict['search'],'field':aDict['field']})['data']
 ret = {'devices':devices,'result':'OK','extra':[]}
 controller = Device(SC['node'][aDict['node']])
 controller.auth({'username':SC['awx']['username'],'password':SC['awx']['password'],'mode':'basic'})
 controller.fetch_dict("inventories/%(id)s/groups/"%aDict,('id','name','description','total_hosts'),'name')
 try:
  controller.fetch_dict("inventories/%(id)s/hosts/"%aDict,('id','name','url','description','enabled','instance_id'),'instance_id')

  for dev in devices:
   args = {"name": "%s.%s"%(dev['hostname'],dev['domain']),"description": "%(model)s (%(ipasc)s)"%dev,"enabled": True,"instance_id": dev['id'], "variables": "" }
   host = hosts.get(str(dev['id']))
   res = controller.call("inventories/%(id)s/hosts/"%aDict,args,"POST") if not host else controller.call("inventories/%s/hosts/%s/"%(aDict['id'],host['id']),args,"PATCH")
   dev['sync'] = {'code':res['code'],'id':res['data']['id']}
 except Exception as e:
  ret['info'] = str(e)
  ret['result'] = 'NOT_OK'
 return ret

########################################## Hosts ##########################################
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
 ret = {'hosts':controller.fetch_list("hosts/",('id','name','url','inventory','description','enabled','instance_id'))}
 return ret

#
#
def inventory_delete_list(aDict):
 """Deletes a list of hosts, represented as host_xx, host_xy and so on (where xx and xy are awx id:s)

 Args:
  - node (required)
  - id (required)
  - host_xx (required)

 Output:
 """
 ret = {'hosts':{}}
 node = aDict.pop('node',None)
 id   = aDict.pop('id',None)
 controller = Device(SC['node'][node])
 controller.auth({'username':SC['awx']['username'],'password':SC['awx']['password'],'mode':'basic'})
 args = aDict
 for host in aDict.keys():
  if host[0:5] == 'host_':
   host_id = host[5:]
   res = controller.call("hosts/%s/"%host_id,None,"DELETE")
   ret['hosts'][host_id] = "OK" if res['code'] == 204 else res['info']['x-api-code']
 return ret

