"""Module docstring.

Settings REST module

"""
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"

from ..core.dbase import DB

def list(aDict):
 ret = {'user_id':aDict.get('user_id',"1"), 'type':aDict.get('type') }
 with DB() as db:
  ret['xist'] = db.do("SELECT id,type,parameter,description FROM settings ORDER BY type,parameter")
  ret['data'] = db.get_dict(aDict['dict']) if aDict.get('dict') else db.get_rows()
 return ret

#
#
def info(aDict):
 ret = {'id':aDict['id']}
 return ret

#
#
def remove(aDict):
 with DB() as db:
  res = db.do("DELETE FROM settings WHERE id = '%s'"%aDict['id'])
 return { 'deleted':res }
