"""Module docstring.

Openstack Portal REST module

"""
__author__ = "Zacharias El Banna"
__version__ = "18.02.09GA"
__status__ = "Production"

def application(aDict):
 from .. import SettingsContainer as SC
 from ..core.dbase import DB
 from ..devices.openstack import OpenstackRPC
 ret = {}
 ret['title']   = "%s 2 Cloud"%(aDict.get('name','iaas'))
 ret['message']= "Welcome to the '%s' Cloud Portal"%(aDict.get('name','iaas'))
 cookies = {'name':aDict.get('name','iaas'),'controller':aDict['controller'],'appformix':aDict.get('appformix',None)}
 try:
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
 from ..devices.openstack import OpenstackRPC
 from ..core.logger import log
 ret = {}
 openstack = OpenstackRPC(ctrl,None)
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
   ret.update({'%s_port'%service:port,'%s_url'%service:url,'%s_id'%service:id})
  log("openstack_authenticate - successful login and catalog init for %s@%s"%(aDict['username'],ctrl))
 else:
  log("openstack_authenticate - error logging in for  %s@%s"%(aDict['username'],ctrl))
 return ret
