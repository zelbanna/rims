e"""AWX REST module."""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__type__ = 'PROVISIONING'

####################################### Device #######################################
#
#
class Device(object):

 def __init__(self, aCTX, aNode, aToken = None):
  self._ctx = aCTX
  self._node = aNode
  self._token = aToken

 def __str__(self):
  return "AWX(node=%s, token=%s)".format(self._node, self._token)

 #
 # { 'username','password','mode' }
 # mode: 'basic'/'full' auth process
 #
 def auth(self, aAuth):
  from base64 import b64encode
  self._token = 'Basic %s'%(b64encode(("%s:%s"%(aAuth['username'],aAuth['password'])).encode('utf-8')).decode())
  try:
   if aAuth.get('mode','full') == 'full':
    ret = self._ctx.rest_call("%s/me"%self._ctx.nodes[self._node]['url'], aHeader = {'Authorization':self._token}, aDataOnly = False)
    ret.pop('data',None)
    ret.pop('node',None)
   else:
    ret = {}
  except Exception as e:
   ret['error'] = e[0]
   ret['auth'] = 'NOT_OK'
  else:
   ret['auth'] = 'OK'
  return ret

 def get_token(self):
  return self._token

 # call and href
 # Input:
 # - url  = service url
 # - args = dict with arguments for post operation, empty dict or nothing means no arguments (!)
 # - method = used to send other things than GET and POST (i.e. 'DELETE')
 # - header = send additional headers as dictionary
 #
 def call(self, query, **kwargs):
  try:    kwargs['aHeader'].update({'Authorization':self._token})
  except: kwargs['aHeader'] = {'Authorization':self._token}
  kwargs['aDataOnly'] = False
  return self._ctx.rest_call("%s/%s"%(self._ctx.nodes[self._node]['url'], query), **kwargs)

 def fetch_list(self,aBase,aSet):
  ret  = []
  next = aBase
  while True:
   data = self.call(next)['data']
   for row in data['results']:
    ret.append({k:row.get(k) for k in aSet})
   try:
    _,_,page = data['next'].rpartition('?')
    next = "%s?%s"%(base,page)
   except: break
  return ret

 def fetch_list(self,aBase,aSet):
  ret  = []
  next = aBase
  while True:
   data = self.call(next)['data']
   for row in data['results']:
    ret.append({k:row.get(k) for k in aSet})
   try:
    _,_,page = data['next'].rpartition('?')
    next = "%s?%s"%(base,page)
   except: break
  return ret

 def fetch_dict(self,aBase,aSet,aKey):
  ret  = {}
  next = aBase
  while True:
   data = self.call(next)['data']
   for row in data['results']:
    ret[row[aKey]] ={k:row.get(k) for k in aSet if row.get(aKey) and row[aKey] != ""}
   try:
    _,_,page = data['next'].rpartition('?')
    next = "%s?%s"%(base,page)
   except: break
  return ret

####################################### AWX #######################################

#
#
def inventory_list(aCTX, aArgs):
 """Function main produces an inventory list for a node

 Args:
  - node (required)

 Output:
  - inventories
 """
 ret = {}
 try:
  controller = Device(aCTX,aArgs['node'])
  controller.auth({'username':aCTX.config['awx']['username'],'password':aCTX.config['awx']['password'],'mode':'basic'})
  ret['inventories'] = controller.fetch_list("inventories/",('id','name','url'))
 except Exception as e:
  ret = {'status':'NOT_OK','info':str(e)}
 return ret

#
#
def inventory_delete(aCTX, aArgs):
 """Function deletes inventory with id x

 Args:
  - node (required)
  - id (required)

 Output:
 """
 controller = Device(aCTX,aArgs['node'])
 controller.auth({'username':aCTX.config['awx']['username'],'password':aCTX.config['awx']['password'],'mode':'basic'})
 res = controller.call("inventories/%(id)s/"%aArgs,aMethod = "DELETE")
 ret = {'deleted': True if res['code'] == 204 else res['info']['x-code']}
 return ret

#
#
def inventory_info(aCTX, aArgs):
 """Function produces inventory info for a specific inventory id

 Args:
  - node (required)
  - id (required)

 Output:
 """
 ret = {}
 controller = Device(aCTX,aArgs['node'])
 controller.auth({'username':aCTX.config['awx']['username'],'password':aCTX.config['awx']['password'],'mode':'basic'})
 ret['groups'] = controller.fetch_dict("inventories/%(id)s/groups/"%aArgs,('id','name','description','total_hosts'),'name')
 ret['hosts'] = []
 next = "inventories/%(id)s/hosts/"%aArgs
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
def inventory_sync(aCTX, aArgs):
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
 if aArgs.get('search'):
  field = aArgs['field']
  search= aArgs['search']
 else:
  search = ",".join(v for k,v in aArgs.items() if k[0:7] == 'device_')
  field  = 'id'
 from rims.api.device import list as device_list
 devices = device_list(aCTX, {'search':search,'field':field,'extra':['type','domain']})['data']
 ret = {'devices':devices,'status':'OK','groups':{}}
 if len(devices) == 0:
  return ret
 controller = Device(aCTX,aArgs['node'])
 controller.auth({'username':aCTX.config['awx']['username'],'password':aCTX.config['awx']['password'],'mode':'basic'})
 ret['groups'] = controller.fetch_dict("inventories/%s/groups/"%aArgs['id'],('id','name','description','total_hosts'),'name')
 try:
  hosts = {}
  next = "inventories/%(id)s/hosts/"%aArgs
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
    res = controller.call("inventories/%s/groups/"%(aArgs['id']), aArgs = group, aMethod = "POST")
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
     res  = controller.call("hosts/%s/"%(host['id']), aArgs = args, aMethod = "PATCH")
     dev['awx'] = {'code':res['code'],'id':res['data']['id']}
     # Check if already in group otherwise add to group
     for hgrp in host['groups']:
      if hgrp['id'] == group['id']:
       dev['awx']['group'] = 'REMAIN_IN_GROUP'
       break
     else:
      res  = controller.call("groups/%s/hosts/"%(group['id']), aArgs = {'id':host['id']}, aMethod = "POST")
      if res['code'] == 204:
       dev['awx']['group'] = 'ADDED_TO_GROUP'
       group['total_hosts'] += 1
      else:
       dev['awx']['group'] = 'ERROR:%i'%res['code']
    else:
     # No host, create directly to group (belonging to inventory) x :-)
     res  = controller.call("groups/%s/hosts/"%(group['id']),aArgs = args,aMethod = "POST")
     dev['awx'] = {'code':res['code'],'id':res['data']['id'],'group':'CREATED_TO_GROUP'}
     args['id'] = res['data']['id']
     hosts[str(dev['id'])] = args
     group['total_hosts'] += 1
   else:
    dev['awx'] = {'code':600,'group':'NO_GROUP_ID'}
 except Exception as e:
  ret['info'] = str(e)
  ret['status'] = 'NOT_OK'
 return ret

#
#
def inventory_delete_hosts(aCTX, aArgs):
 """Deletes a list of hosts, represented as host_<xy>

 Args:
  - node (required)
  - id (required)
  - host_<xy> (required). argument value must be xy as well (!)

 Output:
 """
 ret = {'hosts':{}}
 node = aArgs.pop('node',None)
 id   = aArgs.pop('id',None)
 controller = Device(aCTX,node)
 controller.auth({'username':aCTX.config['awx']['username'],'password':aCTX.config['awx']['password'],'mode':'basic'})
 for host,host_id in aArgs.items():
  if host[0:5] == 'host_':
   res = controller.call("hosts/%s/"%host_id, aMethod = "DELETE")
   ret['hosts'][host_id] = "OK" if res['code'] == 204 else res['info']['x-code']
 return ret

########################################## Hosts ##########################################
#
#
def host_list(aCTX, aArgs):
 """Function retrieves all hosts from AWX node

 Args:
  - node (required)

 Output:
 """
 controller = Device(aCTX,aArgs['node'])
 controller.auth({'username':aCTX.config['awx']['username'],'password':aCTX.config['awx']['password'],'mode':'basic'})
 ret = {'hosts':controller.fetch_list("hosts/",('id','name','url','inventory','description','enabled','instance_id'))}
 return ret

#
#
def parameters(aCTX, aArgs):
 """ Function provides parameter mapping of anticipated config vs actual

 Args:

 Output:
  - status
  - parameters
 """
 settings = aCTX.config.get('awx',{})
 params = ['username','password']
 return {'status':'OK' if all(p in settings for p in params) else 'NOT_OK','parameters':{p:settings.get(p) for p in params}}
