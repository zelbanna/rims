"""Module docstring.

SDCP generic REST module
- Hardcoded for the moment

"""
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"

def portal_info(aDict):
 """
 - portal: 'sdcp', 'openstack'
 """

 from ..core.dbase import DB
 ret = {'result':'NOT_OK'}

 if aDict.get('portal') == 'sdcp':
  ret['call'] = 'sdcp_portal'
  ret['name'] = 'El Banna Portal'
  with DB() as db:
   db.do("SELECT name, CONCAT(id,'_',name,'_',view_public) as value FROM users ORDER BY name")
   rows = db.get_rows()
  ret['choises'] = [{'sdcp_login':rows}]
  ret['parameters'] = []
  ret['result'] = 'OK'
 return ret
