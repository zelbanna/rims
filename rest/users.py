"""Users API module. Provides user interaction and management (create, delete, setting and fetching menuitems etc)"""
__author__ = "Zacharias El Banna"
__version__ = "18.03.16"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

from sdcp.core.common import DB

def list(aDict):
 """Function docstring for list TBD

 Args:

 Output:
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

 Output:
  - op (pop)
 """
 ret = {'id':aDict['id']}
 id = aDict.pop('id','new')
 op = aDict.pop('op',None)
 args = aDict
 with DB() as db:
  if op == 'update':
   if id == 'new':
    ret['update'] = db.insert_dict('users',args)
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

 Output:
 """
 with DB() as db:
  res = db.do("DELETE FROM users WHERE id = '%s'"%aDict['id'])
 return { 'deleted':res }

#
#
def menu(aDict):
 """Function docstring for menu TBD

 Args:
  - node (required)
  - id (required)

 Output:
 """
 ret = {}
 with DB() as db:
  start = db.do("SELECT id,view,href FROM resources WHERE id = (SELECT CAST(value AS UNSIGNED) FROM settings WHERE node = '%s' AND section = 'portal' AND parameter = 'start')"%aDict['node'])
  if start > 0:
   info = db.get_row()
   ret['start'] = True
   ret['menu'] = [{'id':info['id'],'icon':'images/icon-start.png', 'title':'Start', 'href':info['href'], 'view':info['view'] }]
  else:
   ret['start'] = False
   ret['menu'] = []
  if aDict['node'] == 'master':
   db.do("SELECT menulist FROM users WHERE id = '%s'"%aDict['id'])
   menulist = db.get_val('menulist')
   select = "type = 'menuitem'" if menulist == 'default' else "id IN (%s) ORDER BY FIELD(id,%s)"%(menulist,menulist)
  else:
   select = "type = 'menuitem'"
  db.do("SELECT id, icon, title, href, view FROM resources WHERE node = '%s' AND %s"%(aDict['node'],select))
  ret['menu'].extend(db.get_rows())
 return ret
