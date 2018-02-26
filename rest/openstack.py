"""Module docstring.

Openstack Portal REST module

"""
__author__ = "Zacharias El Banna"
__version__ = "18.02.09GA"
__status__ = "Production"

from ..devices.openstack import OpenstackRPC
from ..core.dbase import DB
#
#
def application(aDict):
 """Function docstring for application. Delivers the information for SDCP login to redirect to the openstack App.

 Args:
  - host (required)
  - appformix (optional)
  - name (optional)
  - token (optional)
 Extra:
 """
 from datetime import datetime,timedelta
 ret = {}
 ret['title']   = "%s 2 Cloud"%(aDict.get('name','iaas'))
 ret['message']= "Welcome to the '%s' Cloud Portal"%(aDict.get('name','iaas'))
 try:
  if aDict.get('token'):
   controller = OpenstackRPC(aDict['host'],aDict.get('token'))
  else:
   from .. import SettingsContainer as SC
   controller = OpenstackRPC(aDict['host'],None)
   res = controller.auth({'project':SC.openstack['project'], 'username':SC.openstack['username'],'password':SC.openstack['password']})
  auth = controller.call("5000","v3/projects")
  if auth['code'] == 200:
   projects = []
   for project in auth['data']['projects']:
    projects.append({'name':project['name'], 'id':"%s_%s"%(project['id'],project['name'])})
   ret['choices'] = [{'display':'Customer', 'id':'project', 'data':projects}]
 except Exception as e:
  ret['exception'] = str(e)
 ret['parameters'] = [{'display':'Username', 'id':'username', 'data':'text'},{'display':'Password', 'id':'password', 'data':'password'}]
 cookie = {'name':aDict.get('name','iaas'),'host':aDict['host']}
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
  - host (required)
  - username (required)
  - project_id (required)
  - password (required)
  - project_name (required)

 Extra:
 """
 from ..core.logger import log
 ret = {}
 controller = OpenstackRPC(aDict['host'],None)
 res = controller.auth({'project':aDict['project_name'], 'username':aDict['username'],'password':aDict['password'] })
 ret['authenticated'] = res['auth']
 if ret['authenticated'] == 'OK':
  with DB() as db:
   ret.update({'project_name':aDict['project_name'],'project_id':aDict['project_id'],'username':aDict['username'],'os_token':controller.get_token()})
   db.do("INSERT INTO openstack_tokens(token,expires,project_id,username,controller) VALUES('%s','%s','%s','%s',INET_ATON('%s'))"%(controller.get_token(),controller.get_token_expire(),aDict['project_id'],aDict['username'],aDict['host']))
   ret['token'] = db.get_last_id()
   for service in ['heat','nova','neutron','glance']:
    port,url,id = controller.get_service(service,'public')
    if len(url) > 0:
     url = url + '/'
    db.do("INSERT INTO openstack_services(uuid,service,service_port,service_url,service_id) VALUES('%s','%s','%s','%s','%s')"%(ret['token'],service,port,url,id))
   db.do("INSERT INTO openstack_services(uuid,service,service_port,service_url,service_id) VALUES('%s','%s','%s','%s','%s')"%(ret['token'],"contrail",8082,'',''))
  ret['expires'] = controller.get_cookie_expire()
  log("openstack_authenticate - successful login and catalog init for %s@%s"%(aDict['username'],aDict['host']))
 else:
  log("openstack_authenticate - error logging in for  %s@%s"%(aDict['username'],ctrl))
 return ret

#
#
def services(aDict):
 ret = {}
 with DB() as db:
  ret['xist'] = db.do("SELECT %s FROM openstack_services WHERE uuid = '%s'"%("*" if not aDict.get('filter') else aDict.get('filter'), aDict['token']))
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

 Extra:
 """
 try:
  with DB() as db:
   db.do("SELECT INET_NTOA(controller) as ipasc, token FROM openstack_tokens WHERE openstack_tokens.uuid = '%s'"%(aDict['token']))
   data = db.get_row()
   if not aDict.get('href'):
    db.do("SELECT service_port,service_url FROM openstack_services WHERE uuid = '%s' AND service = '%s'"%(aDict['token'],aDict.get('service')))
    data.update(db.get_row())
  controller = OpenstackRPC(data['ipasc'],data['token'])
  if aDict.get('href'):
   ret = controller.href(aDict.get('href'), aDict.get('arguments'), aDict.get('method','GET'))
  else:
   ret = controller.call(data['service_port'], data['service_url'] + aDict['call'], aDict.get('arguments'), aDict.get('method','GET'))
  ret['result'] = 'OK' if not ret.get('result') else ret.get('result')
 except Exception as e: ret = e[0]
 return ret

#
#
def call(aDict):
 """Function docstring for call. Basically creates a controller instance and send a (nested) rest_call

 Args:
  - token (required)
  - service (required)
  - call (optional)
  - arguments (optional)
  - method (optional)

 Extra:
 """
 with DB() as db:
  db.do("SELECT INET_NTOA(controller) as ipasc, token, service_port, service_url FROM openstack_tokens LEFT JOIN openstack_services ON openstack_tokens.uuid = openstack_services.uuid WHERE openstack_tokens.uuid = '%s' AND service = '%s'"%(aDict['token'], aDict['service']))
  data = db.get_row()
 controller = OpenstackRPC(data['ipasc'],data['token'])
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

 Extra:
 """
 with DB() as db:
  db.do("SELECT INET_NTOA(controller) as ipasc, token FROM openstack_tokens WHERE openstack_tokens.uuid = '%s'"%(aDict['token']))
  data = db.get_row()
 controller = OpenstackRPC(data['ipasc'],data['token'])
 try:
  ret = controller.href(aDict['href'], aDict.get('arguments'), aDict.get('method'))
  ret['result'] = 'OK' if not ret.get('result') else ret.get('result')
 except Exception as e: ret = e[0]
 return ret

#
#
def info(aDict):
 from datetime import datetime
 ret = {}
 with DB() as db:
  ret['xist'] = db.do("SELECT INET_NTOA(controller) AS controller, uuid AS internal_token, token AS openstack_token, CAST(FROM_UNIXTIME(expires) AS CHAR(50)) AS expires, (UNIX_TIMESTAMP() < expires) AS valid FROM openstack_tokens WHERE username = '%s'"%aDict['username'])
  ret['data'] = db.get_rows()
 return ret

#
#
def token_info(aDict):
 from datetime import datetime
 ret = {}
 with DB() as db:
  ret['xist'] = db.do("SELECT CAST(NOW() AS CHAR(50)) AS time, INET_NTOA(controller) AS controller, token AS openstack_token, CAST(FROM_UNIXTIME(expires) AS CHAR(50)) AS expires FROM openstack_tokens WHERE uuid = '%s'"%aDict['token'])
  ret['data'] = db.get_row()
 return ret

################################################# HEAT ###########################################
#
#
def heat_templates(aDict):
 """Function docstring for heat_templates TBD

 Args:

 Extra:
 """
 from os import listdir
 ret = {'result':'OK','templates':[]}
 try:
  for file in listdir("os_templates/"):
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
 Extra:
 """
 from json import load
 ret = {'result':'OK','template':None}
 try:
  with open("os_templates/%s.tmpl.json"%aDict['template']) as f:
   ret['template'] = load(f)
 except Exception as e:
  ret['info'] = str(e)
  ret['result'] = 'NOT_OK'
 return ret

#
#
def heat_instantiate(aDict):
 """Function docstring for heat_instantiate TBD

 Args:
  - token (required)
  - template (required)
  - name (required)
  - parameters (required)

 Extra:
 """
 from json import load
 ret = {}
 args = {}
 try:
  with open("os_templates/%s.tmpl.json"%aDict['template']) as f:
   args = load(f)
  args['stack_name'] = aDict['name']
  for key,value in aDict['parameters'].iteritems():
   args['parameters'][key] = value
 except Exception as e:
  ret['info'] = str(e)
  ret['result'] = 'NOT_OK'
 else:
  with DB() as db:
   db.do("SELECT INET_NTOA(controller) as ipasc, token, service_port, service_url FROM openstack_tokens LEFT JOIN openstack_services ON openstack_tokens.uuid = openstack_services.uuid WHERE openstack_tokens.uuid = '%s' AND service = 'heat'"%(aDict['token']))
   data = db.get_row()
  try:
   controller = OpenstackRPC(data['ipasc'],data['token'])
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

 Extra:
 """
 ret = {'result':'OK','vm':None,'interfaces':[]}
 with DB() as db:
  db.do("SELECT INET_NTOA(controller) as ipasc, token, service_port, service_url FROM openstack_tokens LEFT JOIN openstack_services ON openstack_tokens.uuid = openstack_services.uuid WHERE openstack_tokens.uuid = '%s' AND service = 'contrail'"%(aDict['token']))
  data = db.get_row()
 controller = OpenstackRPC(data['ipasc'],data['token'])
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

 Extra:
 """
 ret = {'result':'NOT_OK','vm':aDict['vm']}
 with DB() as db:
  db.do("SELECT INET_NTOA(controller) as ipasc, token, service_port, service_url FROM openstack_tokens LEFT JOIN openstack_services ON openstack_tokens.uuid = openstack_services.uuid WHERE openstack_tokens.uuid = '%s' AND service = 'nova'"%(aDict['token']))
  data = db.get_row()
 controller = OpenstackRPC(data['ipasc'],data['token'])
 try:
  res = controller.call(data['service_port'], data['service_url'] + "servers/%s/remote-consoles"%(aDict['vm']), {'remote_console':{ "protocol": "vnc", "type": "novnc" }}, header={'X-OpenStack-Nova-API-Version':'2.8'})
  if res['code'] == 200:
   url = res['data']['remote_console']['url']
   # URL is not always proxy ... so force it through: remove http:// and replace IP (assume there is a port..) with controller IP
   ret['url'] = "http://%s:%s"%(data['ipasc'],url[7:].partition(':')[2])
   ret['result'] = 'OK'
  elif res['code'] == 401 and res['data'] == 'Authentication required':
   ret.update({'info':'Authentication required'})
 except Exception,e: ret = e[0]
 return ret

#
#
def vm_resources(aDict):
 """Function docstring for vm_resources TBD

 Args:
  - token (required)

 Extra:
 """
 ret = {}
 with DB() as db:
  db.do("SELECT INET_NTOA(controller) as ipasc, token FROM openstack_tokens WHERE openstack_tokens.uuid = '%s'"%(aDict['token']))
  data = db.get_row()
  db.do("SELECT service,service_port,service_url FROM openstack_services WHERE uuid = '%s'"%(aDict['token']))
  services = db.get_dict('service')
 controller = OpenstackRPC(data['ipasc'],data['token'])
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

 Extra:
 """
 with DB() as db:
  db.do("SELECT INET_NTOA(controller) as ipasc, token FROM openstack_tokens WHERE uuid = '%s'"%aDict['token'])
  data = db.get_row()
 controller = OpenstackRPC(data['ipasc'],data['token'])
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

 Extra:
 """
 with DB() as db:
  db.do("SELECT INET_NTOA(controller) as ipasc, token FROM openstack_tokens WHERE uuid = '%s'"%aDict['token'])
  data = db.get_row()
 controller = OpenstackRPC(data['ipasc'],data['token'])
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

 Extra:
 """
 ret = {'virtual-network':aDict['virtual_network'],'ip_addresses':[]}
 with DB() as db:
  db.do("SELECT INET_NTOA(controller) as ipasc, token, service_port, service_url FROM openstack_tokens LEFT JOIN openstack_services ON openstack_tokens.uuid = openstack_services.uuid WHERE openstack_tokens.uuid = '%s' AND service = 'contrail'"%(aDict['token']))
  data = db.get_row()
 controller = OpenstackRPC(data['ipasc'],data['token'])
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

 Extra:
 """
 ret = {'virtual-network':aDict['virtual_network'],'ip_addresses':[]}
 with DB() as db:
  db.do("SELECT INET_NTOA(controller) as ipasc, token, service_port, service_url FROM openstack_tokens LEFT JOIN openstack_services ON openstack_tokens.uuid = openstack_services.uuid WHERE openstack_tokens.uuid = '%s' AND service = 'contrail'"%(aDict['token']))
  data = db.get_row()
 controller = OpenstackRPC(data['ipasc'],data['token'])
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

 Extra:
 """
 ret = {'vm':aDict['vm'],'interfaces':[]}
 with DB() as db:
  db.do("SELECT INET_NTOA(controller) as ipasc, token, service_port, service_url FROM openstack_tokens LEFT JOIN openstack_services ON openstack_tokens.uuid = openstack_services.uuid WHERE openstack_tokens.uuid = '%s' AND service = 'contrail'"%(aDict['token']))
  data = db.get_row()
 controller = OpenstackRPC(data['ipasc'],data['token'])
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
 Extra:
 """
 ret = {}
 with DB() as db:
  db.do("SELECT INET_NTOA(controller) as ipasc, token, service_port, service_url FROM openstack_tokens LEFT JOIN openstack_services ON openstack_tokens.uuid = openstack_services.uuid WHERE openstack_tokens.uuid = '%s' AND service = 'contrail'"%(aDict['token']))
  data = db.get_row()
 controller = OpenstackRPC(data['ipasc'],data['token'])
 try:
  vmi = controller.call(data['service_port'],data['service_url'] + "virtual-machine-interface/%s"%aDict['vm_interface'])['data']['virtual-machine-interface']
  fip = { 'floating-ip':{ 'floating_ip_fixed_ip_address':aDict['vm_ip_address'], 'virtual_machine_interface_refs':[ {'href':vmi['href'],'attr':None,'uuid':vmi['uuid'],'to':vmi['fq_name'] } ] } }
  res = controller.call(data['service_port'],data['service_url'] +"floating-ip/%s"%aDict['floating_ip'],args=fip,method='PUT')
  ret['result'] = "OK" if res['code'] == 200 else "NOT_OK"
 except Exception as e:
  ret['result'] ='ERROR'
  ret['info'] = str(e)
 return ret
