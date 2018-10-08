"""Openstack REST module. Provides all REST functions to interwork with Contrail based Openstack. Keystone will provide service catalog


Node:
- node name in nodes, this will be the keystone URL, e.g. http://x.y.z.a:5000, to fetch service catalog

Settings:
- heat_directory: "Heat Templates Directory"
- contrail:       "Contrail URL"
- password:       "Keystone Password"
- project:        "Keystone Project"
- username:       "Keystone Username"

"""
__author__ = "Zacharias El Banna"
__version__ = "5.0GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

from zdcp.devices.openstack import Device
from datetime import datetime,timedelta

#
#
def application(aDict, aCTX):
 """Function docstring for application. Delivers the information for SDCP login to redirect to the openstack App.

 Args:
  - node (required)
  - appformix (optional)
  - name (optional)
  - token (optional)
 Output:
 """
 ret = {'title':"%s 2 Cloud"%(aDict.get('name','iaas')),'choices':[],'message':"Welcome to the '%s' Cloud Portal"%(aDict.get('name','iaas')),'portal':'openstack' }
 node = aDict['node']
 try:
  if aDict.get('token'):
   controller = Device(aCTX.settings['nodes'][node],aDict['token'])
  else:
   controller = Device(aCTX.settings['nodes'][node])
   res = controller.auth({'project':aCTX.settings[node]['project'], 'username':aCTX.settings[node]['username'],'password':aCTX.settings[node]['password']})
  ret['choices'] = [{'display':'Customer', 'id':'project', 'data':controller.projects()}]
  for proj in ret['choices'][0]['data']:
   proj['id'] = "%(id)s_%(name)s"%proj
 except Exception as e:
  ret['exception'] = str(e)
 ret['parameters'] = [{'display':'Username', 'id':'username', 'data':'text'},{'display':'Password', 'id':'password', 'data':'password'}]
 cookie = {'name':aDict.get('name','iaas'),'node':node,'portal':'openstack'}
 if aDict.get('appformix'):
  cookie['appformix'] = aDict.get('appformix')
 ret['cookie'] = ",".join("%s=%s"%i for i in cookie.items())
 ret['expires'] = (datetime.utcnow() + timedelta(hours=1)).strftime('%a, %d %b %Y %H:%M:%S GMT')
 return ret

#
#
def authenticate(aDict, aCTX):
 """Function docstring for authenticate TBD

 Args:
  - node (required)
  - username (required)
  - project_id (required)
  - password (required)
  - project_name (required)
  - interface (optional). openstack interface to use

 Output:
 """
 from zdcp.core.common import log
 ret = {}
 node = aDict['node']
 controller = Device(aCTX.settings['nodes'][node])
 res = controller.auth({'project':aDict['project_name'], 'username':aDict['username'],'password':aDict['password'] })
 ret = {'authenticated':res['auth']}
 if res['auth'] == 'OK':
  with aCTX.db as db:
   ret.update({'project_name':aDict['project_name'],'project_id':aDict['project_id'],'username':aDict['username'],'token':controller.get_token(),'expires':controller.get_cookie_expire()})
   db.do("INSERT INTO openstack_tokens(token,expires,project_id,username,node_name,node_url) VALUES('%s','%s','%s','%s','%s','%s')"%(controller.get_token(),controller.get_token_expire(),aDict['project_id'],aDict['username'],node,aCTX.settings['nodes'][node]))
   token_id = db.get_last_id()
   for service in ['heat','nova','neutron','glance']:
    svc = controller.get_service(service,aDict.get('interface','internal'))
    db.do("INSERT INTO openstack_services(id,service,service_url,service_id) VALUES('%s','%s','%s','%s')"%(token_id,service,svc['url'],svc['id']))
   db.do("INSERT INTO openstack_services(id,service,service_url,service_id) VALUES('%s','%s','%s','%s')"%(token_id,'contrail',aCTX.settings[node]['contrail'],''))
  log("openstack_authenticate - successful login and catalog init for %s@%s"%(aDict['username'],node))
 else:
  log("openstack_authenticate - error logging in for  %s@%s"%(aDict['username'],ctrl))
 return ret

#
#
def services(aDict, aCTX):
 """Function docstring for services. Produces a list of services attached to token, services can be filtered on project names as a string list

 Args:
  - token (required)
  - filter (optional)

 Output:
 """
 ret = {}
 with aCTX.db as db:
  db.do("SELECT id FROM openstack_tokens WHERE token = '%s'"%aDict['token'])
  id = db.get_val('id')
  ret['count']    = db.do("SELECT %s FROM openstack_services WHERE id = '%s'"%("*" if not aDict.get('filter') else aDict.get('filter'), id))
  ret['services'] = db.get_rows()
 return ret

#
#
def rest(aDict, aCTX):
 """Function docstring for rest TBD

 Args:
  - token (required)
  - service (optional)
  - call (optional)
  - href (optional)
  - arguments (optional)
  - method (optional)

 Output:
 """
 try:
  if aDict.get('href'):
   url = aDict['href']
  else:
   with aCTX.db as db:
    db.do("SELECT service_url FROM openstack_services AS os LEFT JOIN openstack_tokens AS ot ON ot.id = os.id WHERE ot.token = '%s' AND service = '%s'"%(aDict['token'],aDict.get('service')))
    url = db.get_val('service_url')
  ret = aCTX.rest_call(url, aDict.get('arguments'), aDict.get('method','GET'), { 'X-Auth-Token':aDict['token'] })
  ret['result'] = 'OK' if not ret.get('result') else ret.get('result')
 except Exception as e: ret = e[0]
 return ret

#
#
def call(aDict, aCTX):
 """Function docstring for call. Basically creates a controller instance and send a (nested) rest call.

 Args:
  - node (required)
  - token (required)
  - service (required)
  - call (required)
  - arguments (optional)
  - method (optional)

 Output:
 """
 with aCTX.db as db:
  db.do("SELECT service_url FROM openstack_services AS os LEFT JOIN openstack_tokens AS ot ON ot.id = os.id WHERE ot.token = '%(token)s' AND service = '%(service)s'"%aDict)
  data = db.get_row()
 try:
  ret = aCTX.rest_call("%s/%s"%(data['service_url'],aDict.get('call',"")), aDict.get('arguments'), aDict.get('method','GET'), { 'X-Auth-Token':aDict['token'] })
  ret['result'] = 'OK' if not ret.get('result') else ret.get('result')
 except Exception as e: ret = e[0]
 return ret

def href(aDict, aCTX):
 """Sends a (nested) aCTX.rest_call

 Args:
  - href (required)
  - token (required)
  - arguments (optional)
  - method (optional)

 Output:
 """
 try: ret = aCTX.rest_call(aDict.get('href'), aDict.get('arguments'), aDict.get('method','GET'), { 'X-Auth-Token':aDict['token'] })
 except Exception as e: ret = e[0]
 return ret

#
#
def token_list(aDict, aCTX):
 """Function docstring for info. Returns a list of Internal to Openstack tokens for user X

 Args:
  - username (required)

 Output:
 """
 ret = {}
 with aCTX.db as db:
  ret['found'] = (db.do("SELECT id, token, node_name, node_url, CAST(FROM_UNIXTIME(expires) AS CHAR(50)) AS expires, (UNIX_TIMESTAMP() < expires) AS valid FROM openstack_tokens WHERE username = '%s'"%aDict['username']) > 0)
  ret['data'] = db.get_rows()
 return ret

#
#
def token_info(aDict, aCTX):
 """Function docstring for info. Returns detailed list of Openstack token given token

 Args:
  - token (required)

 Output:
 """
 ret = {}
 with aCTX.db as db:
  ret['found'] = (db.do("SELECT node_url, SELECT CAST(NOW() AS CHAR(50)) AS time, INET_NTOA(controller) AS controller, id, CAST(FROM_UNIXTIME(expires) AS CHAR(50)) AS expires FROM openstack_tokens WHERE token = '%s'"%aDict['token']) > 0)
  ret['data'] = db.get_row()
 return ret

################################################# HEAT ###########################################
#
#
def heat_templates(aDict, aCTX):
 """Function docstring for heat_templates TBD. PAssing the entire cookie would be simpler but require React.JS.

 Args:
  - token (required)

 Output:
 """
 from os import path as ospath, listdir
 ret = {'result':'OK','templates':[]}
 with aCTX.db as db:
  db.do("SELECT node_name FROM openstack_tokens WHERE token = '%s'"%aDict['token'])
  node = db.get_val('node_name')
 try:
  for file in listdir(ospath.abspath(aCTX.settings[node]['heat_directory'])):
   name,_,suffix = file.partition('.')
   if suffix == 'tmpl.json':
    ret['templates'].append(name)
 except Exception as e:
  ret['info'] = str(e)
  ret['result'] = 'NOT_OK'
 return ret

#
#
def heat_content(aDict, aCTX):
 """Function docstring for heat_content TBD

 Args:
  - token (required)
  - template (required)

 Output:
 """
 from os import path as ospath
 from json import loads
 ret = {'result':'OK','template':None}
 with aCTX.db as db:
  db.do("SELECT node_name FROM openstack_tokens WHERE token = '%s'"%aDict['token'])
  node = db.get_val('node_name')
 try:
  with open(ospath.abspath(ospath.join(aCTX.settings[node]['heat_directory'],"%s.tmpl.json"%aDict['template']))) as f:
   ret['template'] = loads(f.read())
 except Exception as e:
  ret['info'] = str(e)
  ret['result'] = 'NOT_OK'
 return ret

#
#
def heat_create_template(aDict, aCTX):
 return aDict

#
#
def heat_instantiate(aDict, aCTX):
 """Function docstring for heat_instantiate TBD

 Args:
  - token (required)
  - template (required)
  - name (required)
  - parameters (required)

 Output:
 """
 from json import loads
 from os import path as ospath
 ret = {}
 args = {}
 try:
  with aCTX.db as db:
   db.do("SELECT service_url, node_name FROM openstack_services AS os LEFT JOIN openstack_tokens AS ot ON ot.id = os.id WHERE ot.token = '%(token)s' AND service = 'heat'"%aDict)
   data = db.get_row()
   node = data['node_name']
  with open(ospath.abspath(ospath.join(aCTX.settings[node]['heat_directory'],"%s.tmpl.json"%aDict['template']))) as f:
   args = loads(f.read())
  args['stack_name'] = aDict['name']
  for key,value in aDict['parameters'].items():
   args['parameters'][key] = value
 except Exception as e:
  ret['info'] = str(e)
  ret['result'] = 'NOT_OK'
 else:
  try:
   controller = Device(aToken = aDict['token'])
   ret = controller.call("%s/stacks"%data['service_url'],args, 'POST')
   ret['result'] = 'OK'
  except Exception as e: ret = e[0]
 return ret

################################################# NOVA ###########################################
#
#
def vm_networks(aDict, aCTX):
 """Function docstring for vm_networks TBD

 Args:
  - token (required)
  - vm (required)

 Output:
 """
 ret = {'result':'OK','vm':None,'interfaces':[]}
 with aCTX.db as db:
  db.do("SELECT service_url FROM openstack_services AS os LEFT JOIN openstack_tokens AS ot ON ot.id = os.id WHERE ot.token = '%(token)s' AND service = 'contrail'"%aDict)
  svc_url = db.get_val('service_url')
 controller = Device(aToken = aDict['token'])
 vm = controller.call("%s/virtual-machine/%s"%(svc_url,aDict['vm']))['data']['virtual-machine']
 ret['vm'] = vm['name']
 for vmir in vm['virtual_machine_interface_back_refs']:
  vmi = controller.call(vmir['href'])['data']['virtual-machine-interface']
  ip  = controller.call(vmi['instance_ip_back_refs'][0]['href'])['data']['instance-ip']
  network = vmi['virtual_network_refs'][0]['to']
  network.reverse()
  record = {'mac_address':vmi['virtual_machine_interface_mac_addresses']['mac_address'][0],'routing-instance':vmi['routing_instance_refs'][0]['to'][3],'network_uuid':vmi['virtual_network_refs'][0]['uuid'],'network_fqdn':".".join(network),'ip_address':ip['instance_ip_address']}
  if vmi.get('floating_ip_back_refs'):
   fip = controller.call(vmi['floating_ip_back_refs'][0]['href'])['data']['floating-ip']
   record.update({'floating_ip_address':fip['floating_ip_address'],'floating_ip_name':fip['fq_name'][2],'floating_ip_uuid':fip['uuid']})
  ret['interfaces'].append(record)
 return ret

#
#
def vm_console(aDict, aCTX):
 """Function docstring for vm_console TBD

 Args:
  - token (required)
  - vm (required)

 Output:
 """
 ret = {'result':'NOT_OK','vm':aDict['vm']}
 with aCTX.db as db:
  db.do("SELECT service_url FROM openstack_services AS os LEFT JOIN openstack_tokens AS ot ON ot.id = os.id WHERE ot.token = '%(token)s' AND service = 'nova'"%aDict)
  svc_url = db.get_val('service_url')
 controller = Device(aToken = aDict['token'])
 try:
  res = controller.call("%s/servers/%s/remote-consoles"%(svc_url,aDict['vm']), {'remote_console':{ "protocol": "vnc", "type": "novnc" }}, header={'X-OpenStack-Nova-API-Version':'2.8'})
  if res['code'] == 200:
   url = res['data']['remote_console']['url']
   # URL is not always proxy ... so force it through: remove http:// and replace IP (assume there is a port..) with controller IP
   ret['url'] = "%s:%s"%(data['node_url'],url[7:].partition(':')[2])
   ret['result'] = 'OK'
  elif res['code'] == 401 and res['data'] == 'Authentication required':
   ret.update({'info':'Authentication required'})
 except Exception as e: ret = e[0]
 return ret

#
#
def vm_resources(aDict, aCTX):
 """Function docstring for vm_resources TBD

 Args:
  - token (required)

 Output:
 """
 ret = {}
 with aCTX.db as db:
  db.do("SELECT service,service_url FROM openstack_services LEFT JOIN openstack_tokens AS ot ON ot.id = openstack_services.id WHERE ot.token = '%s'"%aDict['token'])
  services = db.get_dict('service')
 controller = Device(aToken = aDict['token'])
 ret['flavors']  = controller.call(services['nova']['service_url'] + "flavors/detail?sort_key=name")['data']['flavors']
 ret['images']   = controller.call(services['glance']['service_url'] + "v2/images?sort=name:asc")['data']['images']
 ret['networks'] = controller.call(services['neutron']['service_url'] + "v2.0/networks?sort_key=name")['data']['networks']
 return ret

################################################# CONTRAIL ###########################################
#
#
def contrail_fqname(aDict, aCTX):
 """Function docstring for fqname TBD

 Args:
  - token (required)
  - uuid (required)

 Output:
 """
 with aCTX.db as db:
  db.do("SELECT service_url FROM openstack_services AS os LEFT JOIN openstack_tokens AS ot ON ot.id = os.id WHERE ot.token = '%(token)s' AND service = 'contrail'"%aDict)
  svc_url = db.get_val('service_url')
 controller = Device(aToken = aDict['token'])
 try:
  ret = controller.call("%s/id-to-fqname"%svc_url,aArgs={'uuid':aDict['uuid']},aMethod='POST')
  ret['result'] = 'OK' if not ret.get('result') else ret.get('result')
 except Exception as e: ret = e[0]
 return ret

#
#
def contrail_uuid(aDict, aCTX):
 """Function docstring for uuid_info TBD

 Args:
  - token (required)
  - uuid (required)

 Output:
 """
 with aCTX.db as db:
  db.do("SELECT service_url FROM openstack_services AS os LEFT JOIN openstack_tokens AS ot ON ot.id = os.id WHERE ot.token = '%(token)s' AND service = 'contrail'"%aDict)
  svc_url = db.get_val('service_url')
 controller = Device(aToken = aDict['token'])
 try:
  res = controller.call("%s/id-to-fqname"%svc_url,aArgs={'uuid':aDict['uuid']},aMethod='POST')
  if res.get('result','OK') == 'OK':
   ret = controller.call("%s/%s/%s"%(svc_url,res['data']['type'],aDict['uuid']))['data']
 except Exception as e: ret = e[0]
 return ret

#
#
def contrail_interfaces(aDict, aCTX):
 """Function docstring for contrail_interfaces TBD

 Args:
  - token (required)
  - virtual_network (required)

 Output:
 """
 ret = {'virtual-network':aDict['virtual_network'],'ip_addresses':[]}
 with aCTX.db as db:
  db.do("SELECT service_url FROM openstack_services AS os LEFT JOIN openstack_tokens AS ot ON ot.id = os.id WHERE ot.token = '%(token)s' AND service = 'contrail'"%aDict)
  svc_url = db.get_val('service_url')
 controller = Device(aToken = aDict['token'])
 res = controller.call("%s/virtual-network/%s"%(svc_url,aDict['virtual_network']))
 vn = res['data']['virtual-network']
 fqdn = vn['fq_name']
 fqdn.reverse()
 ret['fqdn'] = ".".join(fqdn)
 ret['name'] = vn['name']
 for ip in vn.get('instance_ip_back_refs',[]):
  iip = controller.call(ip['href'])['data']['instance-ip']
  vmi = controller.call(iip['virtual_machine_interface_refs'][0]['href'])['data']['virtual-machine-interface']
  record = {'ip_address':iip['instance_ip_address'],'mac_address':vmi['virtual_machine_interface_mac_addresses']['mac_address'][0]}
  if vmi.get('virtual_machine_refs'):
   record['vm_uuid'] = vmi['virtual_machine_refs'][0]['uuid']
  if vmi.get('virtual_machine_interface_bindings'):
   host = vmi['virtual_machine_interface_bindings']['key_value_pair']
   for kvp in host:
    if kvp['key'] == 'host_id':
     record['vm_binding'] = kvp['value']
     break
  if vmi.get('logical_interface_back_refs'):
   li = vmi['logical_interface_back_refs'][0]
   record['logical_interface'] = li['to'][1] + "-" + li['to'][3]
   record['logical_interface_uuid'] = li['uuid']
  if vmi.get('virtual_machine_interface_device_owner'):
   record['vm_interface_owner'] = vmi['virtual_machine_interface_device_owner']
  ret['ip_addresses'].append(record)
 return ret

#
#
def contrail_floating_ips(aDict, aCTX):
 """Function docstring for contrail_floating_ips TBD

 Args:
  - token (required)
  - virtual_network (required)

 Output:
 """
 ret = {'virtual-network':aDict['virtual_network'],'ip_addresses':[]}
 with aCTX.db as db:
  db.do("SELECT service_url FROM openstack_services AS os LEFT JOIN openstack_tokens AS ot ON ot.id = os.id WHERE ot.token = '%(token)s' AND service = 'contrail'"%aDict)
  svc_url = db.get_val('service_url')
 controller = Device(aToken = aDict['token'])
 vn = controller.call("%s/virtual-network/%s"%(svc_url,aDict['virtual_network']))['data']['virtual-network']
 for fipool in vn.get('floating_ip_pools',[]):
  pool = controller.call("%s/floating-ip-pool/%s"%(svc_url,fipool['uuid']) )['data']['floating-ip-pool']
  # print pool
  for fips in pool.get('floating_ips',[]):
   fip = controller.call("%s/floating-ip/%s"%(svc_url,fips['uuid']))['data']['floating-ip']
   record = {'pool_uuid':pool['uuid'],'pool_name':pool['name'],'ip_address':fip['floating_ip_address'],'uuid':fip['uuid'],'vm_ip_address':fip.get('floating_ip_fixed_ip_address')}
   if fip.get('floating_ip_fixed_ip_address'):
    vmi = controller.call(fip['virtual_machine_interface_refs'][0]['href'])['data']['virtual-machine-interface']
    record.update({'vm_interface':vmi['virtual_machine_refs'][0]['to'][0],'vm_network_uuid':vmi['virtual_network_refs'][0]['uuid'],'vm_network_name':vmi['virtual_network_refs'][0]['to'][2]})
   ret['ip_addresses'].append(record)
 return ret

#
#
def contrail_vm_interfaces(aDict, aCTX):
 """Function docstring for contrail_vm_interfaces TBD

 Args:
  - token (required)
  - vm (required)

 Output:
 """
 ret = {'vm':aDict['vm'],'interfaces':[]}
 with aCTX.db as db:
  db.do("SELECT service_url FROM openstack_services AS os LEFT JOIN openstack_tokens AS ot ON ot.id = os.id WHERE ot.token = '%(token)s' AND service = 'contrail'"%aDict)
  svc_url = db.get_val('service_url')
 controller = Device(aToken = aDict['token'])
 vmis = controller.call("%s/virtual-machine/%s"%(svc_url,aDict['vm']))['data']['virtual-machine']['virtual_machine_interface_back_refs']
 for vmi in vmis:
  vmi = controller.call(vmi['href'])['data']['virtual-machine-interface']
  iip = controller.call(vmi['instance_ip_back_refs'][0]['href'])['data']['instance-ip']
  ret['interfaces'].append({'uuid':vmi['uuid'],'ip_address':iip['instance_ip_address'],'virtual_network':iip['virtual_network_refs'][0]['to'][2]})
 return ret

#
#
def contrail_vm_associate_fip(aDict, aCTX):
 """Function docstring for contrail_vm_interfaces TBD

 Args:
  - token (required)
  - vm_interface (required)
  - vm_ip_address (required)
  - floating_ip (required)
 Output:
 """
 ret = {}
 with aCTX.db as db:
  db.do("SELECT service_url FROM openstack_services AS os LEFT JOIN openstack_tokens AS ot ON ot.id = os.id WHERE ot.token = '%(token)s' AND service = 'contrail'"%aDict)
  svc_url = db.get_val('service_url')
 controller = Device(aToken = aDict['token'])
 try:
  vmi = controller.call("%s/virtual-machine-interface/%s"%(svc_url,aDict['vm_interface']))['data']['virtual-machine-interface']
  fip = { 'floating-ip':{ 'floating_ip_fixed_ip_address':aDict['vm_ip_address'], 'virtual_machine_interface_refs':[ {'href':vmi['href'],'attr':None,'uuid':vmi['uuid'],'to':vmi['fq_name'] } ] } }
  res = controller.call("%s/floating-ip/%s"%(svc_url,aDict['floating_ip']),aArgs=fip,aMethod='PUT')
  ret['result'] = "OK" if res['code'] == 200 else "NOT_OK"
 except Exception as e:
  ret['result'] ='ERROR'
  ret['info'] = str(e)
 return ret
