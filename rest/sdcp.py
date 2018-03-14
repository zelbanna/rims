"""SDCP generic REST module. The portal and authentication"""
__author__ = "Zacharias El Banna"
__version__ = "18.03.07GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

#
#
def application(aDict):
 """Function docstring for application TBD

 Args:

 Output:
 """
 from datetime import datetime,timedelta
 from ..core.common import DB,SC
 """ Default login information """
 ret = {'message':"Welcome to the Management Portal",'parameters':[],'title':'Portal','application':'sdcp'}
 with DB() as db:
  db.do("SELECT parameter,value FROM settings WHERE section = 'portal' AND 'node' = '%s'"%SC.system['id'])
  for row in db.get_rows():
   ret[row['parameter']] = row['value']
  db.do("SELECT CONCAT(id,'_',name) as id, name FROM users ORDER BY name")
  rows = db.get_rows()
 ret['choices'] = [{'display':'Username', 'id':'sdcp_login', 'data':rows}]
 cookie = aDict
 ret['cookie'] = ",".join(["%s=%s"%(k,v) for k,v in cookie.iteritems()])
 ret['expires'] = (datetime.utcnow() + timedelta(days=1)).strftime("%a, %d %b %Y %H:%M:%S GMT")
 return ret


#
#
def authenticate(aDict):
 """Function docstring for authenticate. Provide cookie with lifetime. TODO should set auth and ID here

 Args:

 Output:
 """
 from datetime import datetime,timedelta
 ret = {}
 ret['authenticated'] = 'OK'
 ret['expires'] = (datetime.utcnow() + timedelta(days=1)).strftime("%a, %d %b %Y %H:%M:%S GMT")
 return ret

#
#
def register(aDict):
 """Function docstring for register TBD

 Args:
  - (node)
  - (url)

 Output:
 """
 from ..core.common import DB,SC
 ret = {}
 args = aDict
 with DB() as db:
  ret['update'] = db.insert_dict('nodes',args,'ON DUPLICATE KEY UPDATE node = node')
 return ret

