"""AWX REST module."""
__author__ = "Zacharias El Banna"
__version__ = "5.0GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

from zdcp.devices.awx import Device

#
#
def inventory_list(aDict, aCTX):
 """Function main produces an inventory list for a device id

 Args:
  - id (optional required)
  - node (optional required)

 Output:
  - inventories
 """
 from zdcp.rest.system import node_device_mapping
 ret = node_device_mapping(aDict, aCTX)
 controller = Device(aCTX.settings['nodes'][ret['node']])
 controller.auth({'username':aCTX.settings['awx']['username'],'password':aCTX.settings['awx']['password'],'mode':'basic'})
 ret['inventories'] = controller.fetch_list("inventories/",('id','name','url'))
 return ret

#
#
def inventory_delete(aDict, aCTX):
 """Function deletes inventory with id x

 Args:
  - node (required)
  - id (required)

 Output:
 """
 controller = Device(aCTX.settings['nodes'][aDict['node']])
 controller.auth({'username':aCTX.settings['awx']['username'],'password':aCTX.settings['awx']['password'],'mode':'basic'})
 res = controller.call("inventories/%(id)s/"%aDict,None,"DELETE")
 ret = {'result':"deleted" if res['code'] == 204 else res['info']['x-code']}
 return ret

#
#
def inventory_info(aDict, aCTX):
 """Function produces inventory info for a specific inventory id

 Args:
  - node (required)
  - id (required)

 Output:
 """
 ret = {}
 controller = Device(aCTX.settings['nodes'][aDict['node']])
 controller.auth({'username':aCTX.settings['awx']['username'],'password':aCTX.settings['awx']['password'],'mode':'basic'})
 ret['groups'] = controller.fetch_dict("inventories/%(id)s/groups/"%aDict,('id','name','description','total_hosts'),'name')
 ret['hosts'] = []
 next = "inventories/%(id)s/hosts/"%aDict
 base = next
 while True:
  data = controller.call(next)['data']
  for row in data['results']:
   insert = {k:row.get(k) for k in ('id','instance_id','name','description')}
   insert['groups'] = row['summary_fields']['groups']['results']
   ret['hosts'].append(insert)
  try:
   _,_,page = data['next'].rpartition('?')
   next = "%s?%s"%(base,page)
  except: break
 return ret

#
#
def inventory_sync(aDict, aCTX):
 """Function retrieves and matches AWX hosts with devices - and add/updates missing info and groups. Either a list of device_xy id are supplied

 Args:
  - node (required)
  - id (required)
  - device_<xy> (optional required). Argument value must be <xy> as well (!)
  - search (optional required)
  - field (optional required)

 Output:
  - result (always) 'OK' / 'NOT_OK'
  - info (optional)
  - devices (always)
  - groups (always)
 """
 if aDict.get('search'):
  field = aDict['field']
  search= aDict['search']
 else:
  search = ",".join(v for k,v in aDict.items() if k[0:7] == 'device_')
  field  = 'id'
 from zdcp.rest.device import list as device_list
 devices = device_list({'search':search,'field':field,'extra':'type'}, aCTX)['data']
 ret = {'devices':devices,'result':'OK','groups':{}}
 if len(devices) == 0:
  return ret
 controller = Device(aCTX.settings['nodes'][aDict['node']])
 controller.auth({'username':aCTX.settings['awx']['username'],'password':aCTX.settings['awx']['password'],'mode':'basic'})
 ret['groups'] = controller.fetch_dict("inventories/%s/groups/"%aDict['id'],('id','name','description','total_hosts'),'name')
 try:
  hosts = {}
  next = "inventories/%(id)s/hosts/"%aDict
  base = next
  while True:
   data = controller.call(next)['data']
   for row in data['results']:
    insert = {k:row.get(k) for k in ('id','name','description','enabled')}
    insert['groups'] = row['summary_fields']['groups']['results']
    hosts[row['instance_id']] = insert
   try:
    _,_,page = data['next'].rpartition('?')
    next = "%s?%s"%(base,page)
   except: break
  for dev in devices:
   # Check device group
   group = ret['groups'].get(dev['type_name'],{'id':None})
   if not group['id']:
    group = {'name':dev['type_name'], 'description':"%s devices"%dev['type_name']}
    res = controller.call("inventories/%s/groups/"%(aDict['id']),group,"POST")
    if res['code'] == 201:
     group.update({'id':res['data']['id'],'info':'CREATED','total_hosts':0})
    else:
     group.update({'id':None,'error':res['code'],'info':'NOT_CREATED','total_hosts':0})
    ret['groups'][dev['type_name']] = group

   # Now the group 'exists', so patch host if exist and add to group if not exist
   # If available group, add host to it somehow
   if group['id']:
    host  = hosts.get(str(dev['id']))
    args = {"name": "%s.%s"%(dev['hostname'],dev['domain']),"description": "%(model)s (%(ip)s)"%dev,"enabled": True,"instance_id": str(dev['id']), "variables": "" }
    if host:
     res  = controller.call("hosts/%s/"%(host['id']),args,"PATCH")
     dev['awx'] = {'code':res['code'],'id':res['data']['id']}
     # Check if already in group otherwise add to group
     for hgrp in host['groups']:
      if hgrp['id'] == group['id']:
       dev['awx']['group'] = 'REMAIN_IN_GROUP'
       break
     else:
      res  = controller.call("groups/%s/hosts/"%(group['id']),{'id':host['id']},"POST")
      if res['code'] == 204:
       dev['awx']['group'] = 'ADDED_TO_GROUP'
       group['total_hosts'] += 1
      else:
       dev['awx']['group'] = 'ERROR:%i'%res['code']
    else:
     # No host, create directly to group (belonging to inventory) x :-)
     res  = controller.call("groups/%s/hosts/"%(group['id']),args,"POST")
     dev['awx'] = {'code':res['code'],'id':res['data']['id'],'group':'CREATED_TO_GROUP'}
     args['id'] = res['data']['id']
     hosts[str(dev['id'])] = args
     group['total_hosts'] += 1
   else:
    dev['awx'] = {'code':600,'group':'NO_GROUP_ID'}
 except Exception as e:
  ret['info'] = str(e)
  ret['result'] = 'NOT_OK'
 return ret

#
#
def inventory_delete_hosts(aDict, aCTX):
 """Deletes a list of hosts, represented as host_<xy>

 Args:
  - node (required)
  - id (required)
  - host_<xy> (required). argument value must be xy as well (!)

 Output:
 """
 ret = {'hosts':{}}
 node = aDict.pop('node',None)
 id   = aDict.pop('id',None)
 controller = Device(aCTX.settings['nodes'][node])
 controller.auth({'username':aCTX.settings['awx']['username'],'password':aCTX.settings['awx']['password'],'mode':'basic'})
 for host,host_id in aDict.items():
  if host[0:5] == 'host_':
   res = controller.call("hosts/%s/"%host_id,None,"DELETE")
   ret['hosts'][host_id] = "OK" if res['code'] == 204 else res['info']['x-code']
 return ret

########################################## Hosts ##########################################
#
#
def host_list(aDict, aCTX):
 """Function retrieves all hosts from AWX node

 Args:
  - node (required)

 Output:
 """
 controller = Device(aCTX.settings['nodes'][aDict['node']])
 controller.auth({'username':aCTX.settings['awx']['username'],'password':aCTX.settings['awx']['password'],'mode':'basic'})
 ret = {'hosts':controller.fetch_list("hosts/",('id','name','url','inventory','description','enabled','instance_id'))}
 return ret

