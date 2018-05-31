"""Openstack REST module. Provides all REST functions to interwork with an Openstack controller for different services"""
__author__ = "Zacharias El Banna"
__version__ = "18.05.31GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

from sdcp.devices.openstack import Device
from sdcp.core.common import DB,SC,rest_call
#
#
def application(aDict):
 """Function docstring for application. Delivers the information for SDCP login to redirect to the openstack App.

 Args:
  - node (required)
  - appformix (optional)
  - name (optional)
  - token (optional)
 Output:
 """
 from datetime import datetime,timedelta
 ret = {'title':"%s 2 Cloud"%(aDict.get('name','iaas')),'choices':[],'message':"Welcome to the '%s' Cloud Portal"%(aDict.get('name','iaas')),'portal':'openstack' }
 try:
  if aDict.get('token'):
   controller = Device(SC['node'][aDict['node']],aDict.get('token'))
  else:
   controller = Device(SC['node'][aDict['node']],None)
   res = controller.auth({'project':SC['openstack']['project'], 'username':SC['openstack']['username'],'password':SC['openstack']['password']})
  auth = controller.call("5000","v3/projects")
  if auth['code'] == 200:
   projects = []
   for project in auth['data']['projects']:
    projects.append({'name':project['name'], 'id':"%s_%s"%(project['id'],project['name'])})
   ret['choices'] = [{'display':'Customer', 'id':'project', 'data':projects}]
 except Exception as e:
  ret['exception'] = str(e)
 ret['parameters'] = [{'display':'Username', 'id':'username', 'data':'text'},{'display':'Password', 'id':'password', 'data':'password'}]
 cookie = {'name':aDict.get('name','iaas'),'node':aDict['node'],'portal':'openstack'}
 if aDict.get('appformix'):
  cookie['appformix'] = aDict.get('appformix')
 ret['cookie'] = ",".join(["%s=%s"%(k,v) for k,v in cookie.iteritems()])
 ret['expires'] = (datetime.utcnow() + timedelta(hours=1)).strftime('%a, %d %b %Y %H:%M:%S GMT')
 return ret

#
#
def authenticate(aDict):
 """Function docstring for authenticate TBD

 Args:
  - node (required)
  - username (required)
  - project_id (required)
  - password (required)
  - project_name (required)

 Output:
 """
 from sdcp.core.logger import log
 ret = {}
 controller = Device(SC['node'][aDict['node']],None)
 res = controller.auth({'project':aDict['project_name'], 'username':aDict['username'],'password':aDict['password'] })
 ret = {'authenticated':res['auth']}
 if res['auth'] == 'OK':
  with DB() as db:
   ret.update({'project_name':aDict['project_name'],'project_id':aDict['project_id'],'username':aDict['username'],'token':controller.get_token(),'expires':controller.get_cookie_expire()})
   db.do("INSERT INTO openstack_tokens(token,expires,project_id,username,node) VALUES('%s','%s','%s','%s','%s')"%(controller.get_token(),controller.get_token_expire(),aDict['project_id'],aDict['username'],SC['node'][aDict['node']]))
   token_id = db.get_last_id()
   for service in ['heat','nova','neutron','glance']:
    svc = controller.get_service(service,'public')
    if len(svc['path']) > 0:
     svc['path'] = svc['path'] + '/'
    db.do("INSERT INTO openstack_services(id,service,service_port,service_url,service_id) VALUES('%s','%s','%s','%s','%s')"%(token_id,service,svc['port'],svc['path'],svc['id']))
   db.do("INSERT INTO openstack_services(id,service,service_port,service_url,service_id) VALUES('%s','%s','%s','%s','%s')"%(token_id,"contrail",8082,'',''))
  log("openstack_authenticate - successful login and catalog init for %s@%s"%(aDict['username'],aDict['node']))
 else:
  log("openstack_authenticate - error logging in for  %s@%s"%(aDict['username'],ctrl))
 return ret

#
#
def services(aDict):
 """Function docstring for services. Produces a list of services attached to token, services can be filtered on project names as a string list

 Args:
  - token (required)
  - filter (optional)

 Output:
 """
 ret = {}
 with DB() as db:
  db.do("SELECT id FROM openstack_tokens WHERE token = '%s'"%aDict['token'])
  id = db.get_val('id')
  ret['xist'] = db.do("SELECT %s FROM openstack_services WHERE id = '%s'"%("*" if not aDict.get('filter') else aDict.get('filter'), id))
  ret['services'] = db.get_rows()
 return ret

#
#
def rest(aDict):
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
   ret = rest_call(aDict.get('href'), aDict.get('arguments'), aDict.get('method','GET'), { 'X-Auth-Token':aDict['token'] })
  else:
   with DB() as db:
    db.do("SELECT node, service_port, service_url FROM openstack_tokens LEFT JOIN openstack_services ON openstack_tokens.id = openstack_services.id WHERE openstack_tokens.token = '%s' AND service = '%s'"%(aDict['token'],aDict.get('service')))
    data = db.get_row()
   controller = Device(data['node'],aDict['token'])
   ret = controller.call(data['service_port'], data['service_url'] + aDict['call'], aDict.get('arguments'), aDict.get('method','GET'))
  ret['result'] = 'OK' if not ret.get('result') else ret.get('result')
 except Exception as e: ret = e[0]
 return ret

#
#
def call(aDict):
 """Function docstring for call. Basically creates a controller instance and send a (nested) rest_call.

 Args:
  - node (required)
  - token (required)
  - service (required)
  - call (required)
  - arguments (optional)
  - method (optional)

 Output:
 """
 with DB() as db:
  db.do("SELECT node, service_port, service_url FROM openstack_tokens LEFT JOIN openstack_services ON openstack_tokens.id = openstack_services.id WHERE openstack_tokens.token = '%s' AND service = '%s'"%(aDict['token'], aDict['service']))
  data = db.get_row()
 controller = Device(data['node'],aDict['token'])
 try:
  ret = controller.call(data['service_port'], data['service_url'] + aDict.get('call',''), aDict.get('arguments'), aDict.get('method'))
  ret['result'] = 'OK' if not ret.get('result') else ret.get('result')
 except Exception as e: ret = e[0]
 return ret

def href(aDict):
 """Function docstring for call. Basically creates a controller instance and send a (nested) rest_call

 Args:
  - href (required)
  - token (required)
  - arguments (optional)
  - method (optional)

 Output:
 """
 try: ret = rest_call(aDict.get('href'), aDict.get('arguments'), aDict.get('method','GET'), { 'X-Auth-Token':aDict['token'] })
 except Exception as e: ret = e[0]
 return ret

#
#
def info(aDict):
 """Function docstring for info. Returns a list of Internal to Openstack tokens for user X

 Args:
  - username (required)

 Output:
 """
 from datetime import datetime
 ret = {}
 with DB() as db:
  ret['xist'] = db.do("SELECT id, token, node, CAST(FROM_UNIXTIME(expires) AS CHAR(50)) AS expires, (UNIX_TIMESTAMP() < expires) AS valid FROM openstack_tokens WHERE username = '%s'"%aDict['username'])
  ret['data'] = db.get_rows()
 return ret

#
#
def token_info(aDict):
 """Function docstring for info. Returns detailed list of Openstack token given token

 Args:
  - token (required)

 Output:
 """
 from datetime import datetime
 ret = {}
 with DB() as db:
  ret['xist'] = db.do("node, SELECT CAST(NOW() AS CHAR(50)) AS time, INET_NTOA(controller) AS controller, id, CAST(FROM_UNIXTIME(expires) AS CHAR(50)) AS expires FROM openstack_tokens WHERE token = '%s'"%aDict['token'])
  ret['data'] = db.get_row()
 return ret

################################################# HEAT ###########################################
#
#
def heat_templates(aDict):
 """Function docstring for heat_templates TBD

 Args:

 Output:
 """
 from os import listdir
 ret = {'result':'OK','templates':[]}
 try:
  for file in listdir(ospath.abspath(SC['openstack']['heat_directory'])):
   name,_,suffix = file.partition('.')
   if suffix == 'tmpl.json':
    ret['templates'].append(name)
 except Exception as e:
  ret['info'] = str(e)
  ret['result'] = 'NOT_OK'
 return ret

#
#
def heat_content(aDict):
 """Function docstring for heat_content TBD

 Args:
  - template (required)
 Output:
 """
 ret = {'result':'OK','template':None}
 try:
  with open(ospath.abspath(ospath.join(SC['openstack']['heat_directory'],"%s.tmpl.json"%aDict['template']))) as f:
   ret['template'] = loads(f.read())
 except Exception as e:
  ret['info'] = str(e)
  ret['result'] = 'NOT_OK'
 return ret

#
#
def heat_create_template(aDict):
 return aDict

#
#
def heat_instantiate(aDict):
 """Function docstring for heat_instantiate TBD

 Args:
  - token (required)
  - template (required)
  - name (required)
  - parameters (required)

 Output:
 """
 ret = {}
 args = {}
 try:
  with open(ospath.abspath(ospath.join(SC['openstack']['heat_directory'],"%s.tmpl.json"%aDict['template']))) as f:
   args = loads(f.read())
  args['stack_name'] = aDict['name']
  for key,value in aDict['parameters'].iteritems():
   args['parameters'][key] = value
 except Exception as e:
  ret['info'] = str(e)
  ret['result'] = 'NOT_OK'
 else:
  with DB() as db:
   db.do("SELECT node, service_port, service_url FROM openstack_tokens LEFT JOIN openstack_services ON openstack_tokens.id = openstack_services.id WHERE openstack_tokens.token = '%s' AND service = 'heat'"%(aDict['token']))
   data = db.get_row()
  try:
   controller = Device(data['node'],aDict['token'])
   ret = controller.call(data['service_port'], data['service_url'] + "stacks", args, 'POST')
   ret['result'] = 'OK'
  except Exception as e: ret = e[0]
 return ret

################################################# NOVA ###########################################
#
#
def vm_networks(aDict):
 """Function docstring for vm_networks TBD

 Args:
  - token (required)
  - vm (required)

 Output:
 """
 ret = {'result':'OK','vm':None,'interfaces':[]}
 with DB() as db:
  db.do("node, service_port, service_url FROM openstack_tokens LEFT JOIN openstack_services ON openstack_tokens.id = openstack_services.id WHERE openstack_tokens.token = '%s' AND service = 'contrail'"%(aDict['token']))
  data = db.get_row()
 controller = Device(data['node'],aDict['token'])
 vm = controller.call(data['service_port'],data['service_url'] + "virtual-machine/%s"%aDict['vm'])['data']['virtual-machine']
 ret['vm'] = vm['name']
 for vmir in vm['virtual_machine_interface_back_refs']:
  vmi = controller.href(vmir['href'])['data']['virtual-machine-interface']
  ip  = controller.href(vmi['instance_ip_back_refs'][0]['href'])['data']['instance-ip']
  network = vmi['virtual_network_refs'][0]['to']
  network.reverse()
  record = {'mac_address':vmi['virtual_machine_interface_mac_addresses']['mac_address'][0],'routing-instance':vmi['routing_instance_refs'][0]['to'][3],'network_uuid':vmi['virtual_network_refs'][0]['uuid'],'network_fqdn':".".join(network),'ip_address':ip['instance_ip_address']}
  if vmi.get('floating_ip_back_refs'):
   fip = controller.href(vmi['floating_ip_back_refs'][0]['href'])['data']['floating-ip']
   record.update({'floating_ip_address':fip['floating_ip_address'],'floating_ip_name':fip['fq_name'][2],'floating_ip_uuid':fip['uuid']})
  ret['interfaces'].append(record)
 return ret

#
#
def vm_console(aDict):
 """Function docstring for vm_console TBD

 Args:
  - token (required)
  - vm (required)

 Output:
 """
 ret = {'result':'NOT_OK','vm':aDict['vm']}
 with DB() as db:
  db.do("SELECT node, service_port, service_url FROM openstack_tokens LEFT JOIN openstack_services ON openstack_tokens.id = openstack_services.id WHERE openstack_tokens.token = '%s' AND service = 'nova'"%(aDict['token']))
  data = db.get_row()
 controller = Device(data['node'],aDict['token'])
 try:
  res = controller.call(data['service_port'], data['service_url'] + "servers/%s/remote-consoles"%(aDict['vm']), {'remote_console':{ "protocol": "vnc", "type": "novnc" }}, header={'X-OpenStack-Nova-API-Version':'2.8'})
  if res['code'] == 200:
   url = res['data']['remote_console']['url']
   # URL is not always proxy ... so force it through: remove http:// and replace IP (assume there is a port..) with controller IP
   ret['url'] = "%s:%s"%(data['node'],url[7:].partition(':')[2])
   ret['result'] = 'OK'
  elif res['code'] == 401 and res['data'] == 'Authentication required':
   ret.update({'info':'Authentication required'})
 except Exception as e: ret = e[0]
 return ret

#
#
def vm_resources(aDict):
 """Function docstring for vm_resources TBD

 Args:
  - token (required)

 Output:
 """
 ret = {}
 with DB() as db:
  db.do("SELECT node,id FROM openstack_tokens WHERE token = '%s'"%(aDict['token']))
  data = db.get_row()
  db.do("SELECT service,service_port,service_url FROM openstack_services WHERE id = '%s'"%(data['id']))
  services = db.get_dict('service')
 controller = Device(data['node'],aDict['token'])
 ret['flavors']  = controller.call(services['nova']['service_port'],services['nova']['service_url'] + "flavors/detail?sort_key=name")['data']['flavors']
 ret['images']   = controller.call(services['glance']['service_port'],services['glance']['service_url'] + "v2/images?sort=name:asc")['data']['images']
 ret['networks'] = controller.call(services['neutron']['service_port'],services['neutron']['service_url'] + "v2.0/networks?sort_key=name")['data']['networks']
 return ret

################################################# CONTRAIL ###########################################
#
#
def contrail_fqname(aDict):
 """Function docstring for fqname TBD

 Args:
  - token (required)
  - uuid (required)

 Output:
 """
 with DB() as db:
  db.do("SELECT node FROM openstack_tokens WHERE token = '%s'"%aDict['token'])
  data = db.get_row()
 controller = Device(data['node'],aDict['token'])
 try:
  ret = controller.call("8082","id-to-fqname",args={'uuid':aDict['uuid']},method='POST')
  ret['result'] = 'OK' if not ret.get('result') else ret.get('result')
 except Exception as e: ret = e[0]
 return ret

#
#
def contrail_uuid(aDict):
 """Function docstring for uuid_info TBD

 Args:
  - token (required)
  - uuid (required)

 Output:
 """
 with DB() as db:
  db.do("SELECT node FROM openstack_tokens WHERE token = '%s'"%aDict['token'])
  data = db.get_row()
 controller = Device(data['node'],aDict['token'])
 try:
  res = controller.call("8082","id-to-fqname",args={'uuid':aDict['uuid']},method='POST')
  if res.get('result','OK') == 'OK':
   ret = controller.call("8082","%s/%s"%(res['data']['type'],aDict['uuid']))['data']
 except Exception as e: ret = e[0]
 return ret

#
#
def contrail_interfaces(aDict):
 """Function docstring for contrail_interfaces TBD

 Args:
  - token (required)
  - virtual_network (required)

 Output:
 """
 ret = {'virtual-network':aDict['virtual_network'],'ip_addresses':[]}
 with DB() as db:
  db.do("SELECT node, service_port, service_url FROM openstack_tokens LEFT JOIN openstack_services ON openstack_tokens.id = openstack_services.id WHERE openstack_tokens.token = '%s' AND service = 'contrail'"%(aDict['token']))
  data = db.get_row()
 controller = Device(data['node'],aDict['token'])
 res = controller.call(data['service_port'],data['service_url'] + "virtual-network/%s"%aDict['virtual_network'])
 vn = res['data']['virtual-network']
 fqdn = vn['fq_name']
 fqdn.reverse()
 ret['fqdn'] = ".".join(fqdn)
 ret['name'] = vn['name']
 for ip in vn.get('instance_ip_back_refs',[]):
  iip = controller.href(ip['href'])['data']['instance-ip']
  vmi = controller.href(iip['virtual_machine_interface_refs'][0]['href'])['data']['virtual-machine-interface']
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
def contrail_floating_ips(aDict):
 """Function docstring for contrail_floating_ips TBD

 Args:
  - token (required)
  - virtual_network (required)

 Output:
 """
 ret = {'virtual-network':aDict['virtual_network'],'ip_addresses':[]}
 with DB() as db:
  db.do("SELECT node, service_port, service_url FROM openstack_tokens LEFT JOIN openstack_services ON openstack_tokens.id = openstack_services.id WHERE openstack_tokens.token = '%s' AND service = 'contrail'"%(aDict['token']))
  data = db.get_row()
 controller = Device(data['node'],aDict['token'])
 vn = controller.call(data['service_port'],data['service_url'] + "virtual-network/%s"%aDict['virtual_network'])['data']['virtual-network']
 for fipool in vn.get('floating_ip_pools',[]):
  pool = controller.call(data['service_port'],data['service_url'] +"floating-ip-pool/%s"%(fipool['uuid']) )['data']['floating-ip-pool']
  for fips in pool['floating_ips']:
   fip = controller.call(data['service_port'],data['service_url'] + "floating-ip/%s"%(fips['uuid']))['data']['floating-ip']
   record = {'pool_uuid':pool['uuid'],'pool_name':pool['name'],'ip_address':fip['floating_ip_address'],'uuid':fip['uuid'],'vm_ip_address':fip.get('floating_ip_fixed_ip_address')}
   if fip.get('floating_ip_fixed_ip_address'):
    vmi = controller.href(fip['virtual_machine_interface_refs'][0]['href'])['data']['virtual-machine-interface']
    record.update({'vm_interface':vmi['virtual_machine_refs'][0]['to'][0],'vm_network_uuid':vmi['virtual_network_refs'][0]['uuid'],'vm_network_name':vmi['virtual_network_refs'][0]['to'][2]})
   ret['ip_addresses'].append(record)
 return ret

#
#
def contrail_vm_interfaces(aDict):
 """Function docstring for contrail_vm_interfaces TBD

 Args:
  - token (required)
  - vm (required)

 Output:
 """
 ret = {'vm':aDict['vm'],'interfaces':[]}
 with DB() as db:
  db.do("SELECT node, service_port, service_url FROM openstack_tokens LEFT JOIN openstack_services ON openstack_tokens.id = openstack_services.id WHERE openstack_tokens.token = '%s' AND service = 'contrail'"%(aDict['token']))
  data = db.get_row()
 controller = Device(data['node'],aDict['token'])
 vmis = controller.call(data['service_port'],data['service_url'] + "virtual-machine/%s"%aDict['vm'])['data']['virtual-machine']['virtual_machine_interface_back_refs']
 for vmi in vmis:
  vmi = controller.href(vmi['href'])['data']['virtual-machine-interface']
  iip = controller.href(vmi['instance_ip_back_refs'][0]['href'])['data']['instance-ip']
  ret['interfaces'].append({'uuid':vmi['uuid'],'ip_address':iip['instance_ip_address'],'virtual_network':iip['virtual_network_refs'][0]['to'][2]})
 return ret

#
#
def contrail_vm_associate_fip(aDict):
 """Function docstring for contrail_vm_interfaces TBD

 Args:
  - token (required)
  - vm_interface (required)
  - vm_ip_address (required)
  - floating_ip (required)
 Output:
 """
 ret = {}
 with DB() as db:
  db.do("SELECT node, service_port, service_url FROM openstack_tokens LEFT JOIN openstack_services ON openstack_tokens.id = openstack_services.id WHERE openstack_tokens.token = '%s' AND service = 'contrail'"%(aDict['token']))
  data = db.get_row()
 controller = Device(data['node'],aDict['token'])
 try:
  vmi = controller.call(data['service_port'],data['service_url'] + "virtual-machine-interface/%s"%aDict['vm_interface'])['data']['virtual-machine-interface']
  fip = { 'floating-ip':{ 'floating_ip_fixed_ip_address':aDict['vm_ip_address'], 'virtual_machine_interface_refs':[ {'href':vmi['href'],'attr':None,'uuid':vmi['uuid'],'to':vmi['fq_name'] } ] } }
  res = controller.call(data['service_port'],data['service_url'] +"floating-ip/%s"%aDict['floating_ip'],args=fip,method='PUT')
  ret['result'] = "OK" if res['code'] == 200 else "NOT_OK"
 except Exception as e:
  ret['result'] ='ERROR'
  ret['info'] = str(e)
 return ret
