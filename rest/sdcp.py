"""Module docstring.

SDCP generic REST module

"""
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"

from ..core.dbase import DB

#
#
def application(aDict):
 """ Default login information """
 from .. import PackageContainer as PC
 ret = {'title':PC.generic['name'],'portal':"sdcp_portal",'message':"Welcome to the management Portal",'parameters':[]}
 with DB() as db:
  db.do("SELECT CONCAT(id,'_',name,'_',view_public) as id, name FROM users ORDER BY name")
  rows = db.get_rows()
 ret['choices'] = [{'display':'Username', 'id':'sdcp_login', 'data':rows}]
 ret['cookie'] = ",".join(["%s=%s"%(k,v) for k,v in aDict.iteritems()])
 return ret

