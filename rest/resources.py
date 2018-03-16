"""Resources REST module. Provides functionality to manage menuitems, tools, bookmarks etc."""
__author__ = "Zacharias El Banna"
__version__ = "18.03.16"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

from sdcp.core.common import DB

#
#
def list(aDict):
 """Function docstring for list TBD

 Args:
  - node (required)
  - user_id (required)
  - dict (required)
  - type (optional)
  - view_public (optional)
  - dict (optional)

 Output:
 """
 ret = {'user_id':aDict.get('user_id',"1"),'type':aDict.get('type','all')}
 with DB() as db:
  if aDict.get('view_public') is None:
   db.do("SELECT view_public FROM users WHERE id = %s"%ret['user_id'])
   ret['view_public'] = (db.get_val('view_public') == 1)
  else:
   ret['view_public'] = aDict.get('view_public')
  node = "node = '%s'"%aDict['node'] if aDict.get('node') else "true"
  type = "type = '%s'"%aDict['type'] if aDict.get('type') else "true"
  user = "(user_id = %s OR %s)"%(ret['user_id'],'false' if not ret['view_public'] else 'private = 0')
  select = "%s AND %s AND %s"%(node,type,user)
  ret['xist'] = db.do("SELECT id, node, icon, title, href, type, inline, user_id FROM resources WHERE %s ORDER BY type,title"%select)
  ret['data'] = db.get_dict(aDict.get('dict')) if aDict.get('dict') else db.get_rows()
 return ret

#
#
def info(aDict):
 """Function docstring for info TBD

 Args:
  - id (required)
  - op (optional)
  - node (optional)
  - user_id (required conditionally)
  - title (required conditionally)
  - private (required conditionally)
  - href (required conditionally)
  - inline (required conditionally)
  - type (required conditionally)
  - icon (required conditionally)

 Output:
 """
 id = aDict.pop('id',None)
 op = aDict.pop('op',None)
 ret = {'id':id}
 args = aDict
 with DB() as db:
  if op == 'update':
   if id == 'new':
    ret['update'] = db.insert_dict('resources',args)
    ret['id']   = db.get_last_id()
   else:
    ret['update'] = db.update_dict('resources',args,'id=%s'%id)
  else:
   db.do("SELECT * FROM resources WHERE id = '%s'"%id)
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
  deleted = db.do("DELETE FROM resources WHERE id = '%s'"%aDict['id'])
 return { 'deleted':deleted }
