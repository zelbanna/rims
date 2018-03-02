"""Module docstring.

SDCP generic REST module

"""
__author__ = "Zacharias El Banna"
__version__ = "18.02.09GA"
__status__ = "Production"

#
#
def application(aDict):
 """Function docstring for application TBD

 Args:

 Extra:
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
 """Function docstring for authenticate. Provide cookie with lifetime

 Args:

 Extra:
 """
 from datetime import datetime,timedelta
 ret = {}
 ret['authenticated'] = 'OK'
 ret['expires'] = (datetime.utcnow() + timedelta(days=1)).strftime("%a, %d %b %Y %H:%M:%S GMT")
 return ret
