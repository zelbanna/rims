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
 from ..core.dbase import DB
 """ Default login information """
 ret = {'message':"Welcome to the Management Portal",'parameters':[]}
 with DB() as db:
  existing = db.do("SELECT value FROM settings WHERE section = 'generic' AND parameter = 'title'")
  ret['title'] = db.get_val('value') if existing > 0 else 'New Installation'
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
