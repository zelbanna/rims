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
  - controller (required)
  - appformix (optional)
  - name (optional)
  - token (optional)
 Extra:
 """
 ret = {}
 ret['title']   = "%s 2 Cloud"%(aDict.get('name','iaas'))
 ret['message']= "Welcome to the '%s' Cloud Portal"%(aDict.get('name','iaas'))
 cookies = {'name':aDict.get('name','iaas'),'controller':aDict['controller'],'appformix':aDict.get('appformix')}
 try:
  if aDict.get('token'):
   controller = OpenstackRPC(cookies['controller'],aDict.get('token'))
  else:
   from .. import SettingsContainer as SC
   controller = OpenstackRPC(cookies['controller'],None)
   res = controller.auth({'project':SC.openstack['project'], 'username':SC.openstack['username'],'password':SC.openstack['password']})
  # Forget about main token for security resasons, just retrieve projects for the list
  # main_token = controller.get_token()
  auth = controller.call("5000","v3/projects")
  if auth['code'] == 200:
   projects = []
   for project in auth['data']['projects']:
    projects.append({'name':project['name'], 'id':"%s_%s"%(project['id'],project['name'])})
   ret['choices'] = [{'display':'Customer', 'id':'project', 'data':projects}]
 except Exception as e:
  ret['exception'] = str(e)
 ret['parameters'] = [{'display':'Username', 'id':'username', 'data':'text'},{'display':'Password', 'id':'password', 'data':'password'}]
 ret['cookie'] = ",".join(["%s=%s"%(k,v) for k,v in cookies.iteritems()])
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
   ret.update({'project_name':aDict['project_name'],'project_id':aDict['project_id'],'username':aDict['username'],'token':controller.get_token(),'lifetime':controller.get_lifetime()})
   db.do("INSERT INTO openstack_tokens(token,expiry,project_id,username,controller) VALUES('%s','%s','%s','%s',INET_ATON('%s'))"%(ret['token'],ret['lifetime'],aDict['project_id'],aDict['username'],aDict['host']))
   uuid = db.get_last_id()
   ret['db_token'] = uuid
   ret['services'] = "&".join(['heat','nova','neutron','glance'])
   for service in ['heat','nova','neutron','glance']:
    port,url,id = controller.get_service(service,'public')
    if len(url) > 0:
     url = url + '/'
    ret.update({'%s_port'%service:port,'%s_url'%service:url,'%s_id'%service:id})
    db.do("INSERT INTO openstack_services(uuid,service,service_port,service_url,service_id) VALUES('%s','%s','%s','%s','%s')"%(uuid,service,port,url,id))
   ret['services'] = "contrail&" + ret['services']
   ret.update({'contrail_port':'8082','contrail_url':'','contrail_id':''})
   db.do("INSERT INTO openstack_services(uuid,service,service_port,service_url,service_id) VALUES('%s','%s','%s','%s','%s')"%(uuid,"contrail",8082,'',''))
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
def fqname(aDict):
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
def rest(aDict):
 """Function docstring for rest TBD

 Args:
  - host (required)
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
  - host (required)
  - token (required)
  - port (required)
  - url (required)
  - arguments (optional)
  - method (optional)

 Extra:
 """
 controller = OpenstackRPC(aDict['host'],aDict['token'])
 try:
  ret = controller.call(aDict['port'], aDict['url'], aDict.get('arguments'), aDict.get('method'))
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
 controller = OpenstackRPC(aDict['host'],aDict['token'])
 try:
  ret = controller.href(aDict['href'], aDict.get('arguments'), aDict.get('method'))
  ret['result'] = 'OK' if not ret.get('result') else ret.get('result')
 except Exception as e: ret = e[0]
 return ret

#
#
def heat_templates(aDict):
 """Function docstring for heat_templates TBD

 Args:

 Extra:
 """
 ret = {'result':'OK','templates':[]}
 try:
  from os import listdir
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
  - host (required)
  - token (required)
  - port (required) - heat port
  - url (required) - heat base url
  - template (required)
  - name (required)
  - parameters (required)

 Extra:
 """
 from json import load,dump
 ret = {}
 data = {}
 try:
  with open("os_templates/%s.tmpl.json"%aDict['template']) as f:
   data = load(f)
  data['stack_name'] = aDict['name']
  for key,value in aDict['parameters'].iteritems():
   data['parameters'][key] = value
 except Exception as e:
  ret['info'] = str(e)
  ret['result'] = 'NOT_OK'
 else:
  try:
   controller = OpenstackRPC(aDict['host'],aDict['token'])
   ret = controller.call(aDict['port'], aDict['url'] + "stacks", data, 'POST')
   ret['result'] = 'OK'
  except Exception as e: ret = e[0]
 return ret

#
#
def vm_networks(aDict):
 """Function docstring for vm_networks TBD

 Args:
  - host (required)
  - token (required)
  - port (required) - contrail port
  - url (required) - contrail base url
  - vm (required)

 Extra:
 """
 ret = {'result':'OK','vm':None,'interfaces':[]}
 controller = OpenstackRPC(aDict['host'],aDict['token'])
 vm = controller.call(aDict['port'],aDict['url'] + "virtual-machine/%s"%aDict['vm'])['data']['virtual-machine']
 ret['vm'] = vm['name']
 for vmir in vm['virtual_machine_interface_back_refs']:
  vmi = controller.href(vmir['href'])['data']['virtual-machine-interface']
  ip  = controller.href(vmi['instance_ip_back_refs'][0]['href'])['data']['instance-ip']
  network = vmi['virtual_network_refs'][0]['to']
  network.reverse()
  data = {'mac_address':vmi['virtual_machine_interface_mac_addresses']['mac_address'][0],'routing-instance':vmi['routing_instance_refs'][0]['to'][3],'network_uuid':vmi['virtual_network_refs'][0]['uuid'],'network_fqdn':".".join(network),'ip_address':ip['instance_ip_address']}
  if vmi.get('floating_ip_back_refs'):
   fip = controller.href(vmi['floating_ip_back_refs'][0]['href'])['data']['floating-ip']
   data.update({'floating_ip_address':fip['floating_ip_address'],'floating_ip_name':fip['fq_name'][2],'floating_ip_uuid':fip['uuid']})
  ret['interfaces'].append(data)
 return ret

#
#
def vm_console(aDict):
 """Function docstring for vm_console TBD

 Args:
  - host (required)
  - token (required)
  - port (required) - nova port
  - url (required) - nova base url
  - vm (required)

 Extra:
 """
 ret = {'result':'NOT_OK','vm':aDict['vm']}
 controller = OpenstackRPC(aDict['host'],aDict['token'])
 try:
  res = controller.call(aDict['port'], aDict['url'] + "servers/%s/remote-consoles"%(aDict['vm']), {'remote_console':{ "protocol": "vnc", "type": "novnc" }}, header={'X-OpenStack-Nova-API-Version':'2.8'})
  if res['code'] == 200:
   url = res['data']['remote_console']['url']
   # URL is not always proxy ... so force it through: remove http:// and replace IP (assume there is a port..) with controller IP
   ret['url'] = "http://%s:%s"%(aDict['host'],url[7:].partition(':')[2])
   ret['result'] = 'OK'
  elif res['code'] == 401 and res['data'] == 'Authentication required':
   ret.update({'info':'Authentication required'})
 except Exception,e: ret = e[0]
 return ret

#
#
def vm_new_infra(aDict):
 """Function docstring for vm_new_infra TBD

 Args:
  - host (required)
  - token (required)
  - nova_port (required) - port
  - nova_url (required) - base url
  - glance_port (required) - port
  - glance_url (required) - base url
  - neutron_port (required) - port
  - neutron_url (required) - base url

 Extra:
 """

