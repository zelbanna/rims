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
  db.do("SELECT parameter,value FROM settings WHERE section = 'portal' AND 'node' = '%s'"%aDict.get('node','master'))
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

####################################### Node Management #####################################
#
#
def register(aDict):
 """Function docstring for register TBD

 Args:
  - node (required)
  - url (required)
  - system (optional)

 Output:
 """
 from ..core.common import DB
 ret = {}
 args = aDict
 with DB() as db:
  ret['update'] = db.insert_dict('nodes',args,'ON DUPLICATE KEY UPDATE node = node')
 return ret

#
#
def node_list(aDict):
 """Function docstring for node_list TBD

 Args:

 Output:
 """
 from ..core.common import DB
 ret = {}
 args = aDict
 with DB() as db:
  ret['xist'] = db.do("SELECT * FROM nodes")
  ret['data'] = db.get_rows()
 return ret

#
#
def node_info(aDict):
 """Function docstring for node_info TBD

 Args:
  - id (required)
  - op (optional)

 Output:
 """
 from ..core.common import DB
 id = aDict.pop('id','new')
 op = aDict.pop('op',None)
 ret = {}
 args = aDict
 with DB() as db:
  if op == 'update':
   if not id == 'new':
    ret['update'] = db.update_dict('nodes',args,'id=%s AND system = 0'%id)
   else:
    ret['update'] = db.insert_dict('nodes',args)
    id = db.get_last_id()
  ret['xist'] = db.do("SELECT * FROM nodes WHERE id = '%s'"%id)
  ret['data'] = db.get_row()
 return ret

#
#
def node_delete(aDict):
 """Function docstring for node_delete TBD

 Args:
  - id (required)

 Output:
 """
 from ..core.common import DB
 ret = {}   
 with DB() as db:
  ret['delete'] = db.do("DELETE FROM nodes WHERE id = %s AND system = 0"%aDict['id'])
 return ret
