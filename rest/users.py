"""Module docstring.

Users REST module

"""
__author__ = "Zacharias El Banna"
__version__ = "18.02.09GA"
__status__ = "Production"

from ..core.dbase import DB

def list(aDict):
 """Function docstring for list TBD

 Args:

 Extra:
 """
 ret = {}
 with DB() as db:
  ret['xist'] = db.do("SELECT id, alias, name, email FROM users ORDER by name")
  ret['data'] = db.get_rows()
 return ret

#
#
def info(aDict):
 """Function docstring for info TBD

 Args:
  - id (required) -  <x|'new'>
  - name (optional)
  - view_public (optional)
  - menulist (optional)
  - alias (optional)
  - email (optional)

 Extra:
  - op (pop)
 """
 ret = {'id':aDict['id']}
 id = aDict.pop('id','new')
 op = aDict.pop('op',None)
 args = aDict
 with DB() as db:
  if op == 'update':
   if id == 'new':
    ret['update'] = db.do("INSERT INTO users (alias,name,email,menulist,view_public) VALUES ('{}','{}','{}','{}',{})".format(aDict['alias'],aDict['name'],aDict['email'],aDict['menulist'],aDict['view_public']))
    ret['id'] = db.get_last_id()
   else:
    ret['update'] = db.update_dict('users',args,"id=%s"%id)
  else:
   ret['xist'] = db.do("SELECT users.* FROM users WHERE id = '%s'"%id)
   ret['data'] = db.get_row()
 return ret

#
#
def delete(aDict):
 """Function docstring for delete TBD

 Args:
  - id (required)

 Extra:
 """
 with DB() as db:
  res = db.do("DELETE FROM users WHERE id = '%s'"%aDict['id'])
 return { 'deleted':res }

#
#
def menu(aDict):
 """Function docstring for menu TBD

 Args:
  - id (required)
  - dict (optional)

 Extra:
 """
 ret = []
 with DB() as db:
  db.do("SELECT menulist FROM users WHERE id = '%s'"%aDict['id'])
  menulist = db.get_val('menulist')
  select = "type = 'menuitem'" if menulist == 'default' else "id IN (%s) ORDER BY FIELD(id,%s)"%(menulist,menulist)
  db.do("SELECT icon, title, href, inline FROM resources WHERE %s"%select)
  ret = db.get_rows() if not aDict.get('dict') else db.get_dict(aDict.get('dict'))
 return ret
