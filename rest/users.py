"""Module docstring.

Users REST module

"""
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"

from ..core.dbase import DB

def list(aDict):
 ret = {'result':'OK'}
 with DB() as db:
  ret['xist'] = db.do("SELECT id, alias, name, email FROM users ORDER by name")
  ret['data'] = db.get_rows()
 return ret

#
#
def info(aDict):
 ret = {'result':'OK','id':aDict['id']}
 id = aDict['id']
 op = aDict.pop('op',None)
 with DB() as db:
  if op == 'update':
   if aDict['id'] == 'new':
    ret['xist'] = db.do("INSERT INTO users (alias,name,email,menulist,view_public) VALUES ('{}','{}','{}','{}',{})".format(aDict['alias'],aDict['name'],aDict['email'],aDict['menulist'],aDict['view_public']))
    ret['id']   = db.get_last_id()
   else:
    ret['xist'] = db.do("UPDATE users SET alias='{}',name='{}',email='{}',view_public='{}',menulist='{}' WHERE id = '{}'".format(aDict['alias'],aDict['name'],aDict['email'],aDict['view_public'],aDict['menulist'],aDict['id']))
  else:
   ret['xist'] = db.do("SELECT users.* FROM users WHERE id = '%s'"%id)
   ret['data'] = db.get_row()
 return ret

#
#
def remove(aDict):
 with DB() as db:
  res = db.do("DELETE FROM users WHERE id = '%s'"%aDict['id'])
 return { 'result':"OK" if res == 1 else "NOT_OK" }

