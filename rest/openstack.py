"""Module docstring.

Openstack Portal REST module

"""
__author__ = "Zacharias El Banna"
__version__ = "18.02.09GA"
__status__ = "Production"

from ..devices.openstack import OpenstackRPC

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
 openstack = OpenstackRPC(aDict['host'],None)
 res = openstack.auth({'project':aDict['project_name'], 'username':aDict['username'],'password':aDict['password'] })
 ret['authenticated'] = res['auth']
 if ret['authenticated'] == 'OK':
  ret['project_name'] = aDict['project_name']
  ret['project_id'] = aDict['project_id']
  ret['username']   = aDict['username']
  ret['user_token'] = openstack.get_token()
  ret['services']   = "&".join(['heat','nova','neutron','glance'])
  for service in ['heat','nova','neutron','glance']:
   port,url,id = openstack.get_service(service,'public')
   if len(url) > 0:
    url = url + '/'
   ret.update({'%s_port'%service:port,'%s_url'%service:url,'%s_id'%service:id})
  log("openstack_authenticate - successful login and catalog init for %s@%s"%(aDict['username'],aDict['host']))
 else:
  log("openstack_authenticate - error logging in for  %s@%s"%(aDict['username'],ctrl))
 return ret


#
#
def fqname(aDict):
 """Function docstring for fqname TBD

 Args:
  - host (required)
  - token (required)
  - uuid (required)

 Extra:
 """
 controller = OpenstackRPC(aDict['host'],aDict['token'])
 try:
  ret = controller.call("8082","id-to-fqname",args={'uuid':aDict['uuid']},method='POST')
  ret['result'] = 'OK'
 except Exception as e:
  ret = e[0]
 return ret

#
#
def rest(aDict):
 """Function docstring for rest TBD

 Args:
  - host (required)
  - token (required)
  - port (optional)
  - url (optional)
  - href (optional)
  - arguments (optional)
  - method (optional)

 Extra:
 """
 controller = OpenstackRPC(aDict['host'],aDict['token'])
 try:
  if aDict.get('href'):
   ret = controller.href(aDict.get('href'), aDict.get('arguments'), aDict.get('method','GET'))
  else:
   ret = controller.call(aDict.get('port'), aDict.get('url'), aDict.get('arguments'), aDict.get('method','GET'))
  ret['result'] = 'OK'
 except Exception as e:
  ret = e[0]
 return ret
