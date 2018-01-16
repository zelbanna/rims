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
  ret['name'] = PC.sdcp['name']
  ret['portal'] = "sdcp_portal"
  ret['message']= "Welcome to the management Portal"
  with DB() as db:
   db.do("SELECT name, CONCAT(id,'_',name,'_',view_public) as value FROM users ORDER BY name")
   rows = db.get_rows()
  ret['choices'] = [{'display':'Username', 'id':'sdcp_login', 'data':rows}]
  ret['cookie'] = "" if not aDict.get('args') else ",".join(["%s=%s"%(k,v) for k,v in aDict['args'].iteritems()])
  ret['parameters'] = []
  ret['result'] = 'OK'
 elif aDict.get('app') == 'openstack':
  demo = aDict.get('name','iaas')
  ctrl = aDict.get('controller',"127.0.0.1")
  appf = aDict.get('appformix',"127.0.0.1")
 return ret
