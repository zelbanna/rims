"""Module docstring.

SDCP generic REST module
- Hardcoded for the moment

"""
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"

def application(aDict):
 """
 - app: 'sdcp', 'openstack'
 """
 from .. import PackageContainer as PC
 from ..core.dbase import DB
 ret = {'result':'NOT_OK'}
 if aDict.get('app') == 'sdcp':
  ret['title']  = PC.sdcp['name']
  ret['portal'] = "sdcp_portal"
  ret['message']= "Welcome to the management Portal"
  with DB() as db:
   db.do("SELECT CONCAT(id,'_',name,'_',view_public) as id, name FROM users ORDER BY name")
   rows = db.get_rows()
  ret['choices'] = [{'display':'Username', 'id':'sdcp_login', 'data':rows}]
  ret['parameters'] = []
  ret['cookie'] = "" if not aDict.get('args') else ",".join(["%s=%s"%(k,v) for k,v in aDict['args'].iteritems()])
  ret['result'] = 'OK'
 elif aDict.get('app') == 'openstack':
  from ..devices.openstack import OpenstackRPC
  from ..core.logger import log
  args = aDict.get('args',{})
  ret['title']   = "%s 2 Cloud"%(args.get('name','iaas'))
  ret['portal'] = "openstack_portal"
  ret['message']= "Welcome to the '%s' Cloud Portal"%(args.get('name','iaas'))
  cookies = {'name':args.get('name','iaas'),'controller':args.get('controller','127.0.0.1'),'appformix':args.get('appformix','127.0.0.1'),'main_token':args.get('main_token',None)}
  if cookies['main_token'] is None:
   controller = OpenstackRPC(cookies['controller'],None)
   res = controller.auth({'project':PC.openstack['project'], 'username':PC.openstack['username'],'password':PC.openstack['password']})
   cookies['main_token'] = controller.get_token()
   log("openstack_controller - login result: {}".format(str(res['result'])))
  else:
   log("openstack_controller - reusing token: {}".format(mtok))
   controller = OpenstackRPC(cookies['controller'],cookies['main_token'])
  auth = controller.call("5000","v3/projects")
  if auth['code'] == 200:
   projects = []
   for project in auth['data']['projects']:
    projects.append({'name':project['name'], 'id':"%s_%s"%(project['id'],project['name'])})
   ret['choices'] = [{'display':'Customer', 'id':'project', 'data':projects}]
  ret['parameters'] = [{'display':'Username', 'id':'username', 'data':'text'},{'display':'Password', 'id':'password', 'data':'password'}]
  ret['cookie'] = "" if not aDict.get('args') else ",".join(["%s=%s"%(k,v) for k,v in cookies.iteritems()])
  ret['result'] = 'OK'
 return ret
