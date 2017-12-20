"""Module docstring.

Resources REST module

"""
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"

def list(aDict):
 from sdcp.core.dbase import DB
 ret = {'result':'OK'}
 ret['user_id'] = aDict.get('user_id',"1")
 ret['view'] = aDict.get('view',"1")
 ret['type'] = aDict.get('type')
 select = "%s(user_id = %s %s)"%("type = '%s' AND "%ret['type'] if ret['type'] else "", ret['user_id'],"" if ret['view'] == '0' else 'OR private = 0')
 with DB() as db:
  ret['xist'] = db.do("SELECT id, icon, title, href, type, inline, user_id FROM resources WHERE %s ORDER BY type,title"%select)
  ret['data'] = db.get_dict(aDict['dict']) if aDict.get('dict') else db.get_rows()
 return ret
