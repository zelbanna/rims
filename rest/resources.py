"""Resources REST module. Provides functionality to manage menuitems, tools, bookmarks etc."""
__author__ = "Zacharias El Banna"
__version__ = "18.03.07GA"
__status__ = "Production"

from ..core.dbase import DB

#
#
def list(aDict):
 """Function docstring for list TBD

 Args:
  - user_id (required)
  - dict (required)
  - type (optional)
  - view_public (optional)
  - dict (optional)

 Output:
 """
 ret = {'user_id':aDict.get('user_id',"1"), 'type':aDict.get('type') }
 with DB() as db:
  if aDict.get('view_public') is None:
   db.do("SELECT view_public FROM users WHERE id = %s"%ret['user_id'])
   ret['view_public'] = (db.get_val('view_public') == 1)
  else:
   ret['view_public'] = aDict.get('view_public')
  select = "%s(user_id = %s %s)"%("type = '%s' AND "%ret['type'] if ret['type'] else "", ret['user_id'],"" if not ret['view_public'] else 'OR private = 0')
  ret['xist'] = db.do("SELECT id, icon, title, href, type, inline, user_id FROM resources WHERE %s ORDER BY type,title"%select)
  ret['data'] = db.get_dict(aDict.get('dict')) if aDict.get('dict') else db.get_rows()
 return ret

#
#
def info(aDict):
 """Function docstring for info TBD

 Args:
  - id (required)
  - op (optional)
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
    ret['update'] = db.do("INSERT INTO resources (title,href,icon,type,inline,private,user_id) VALUES ('{}','{}','{}','{}','{}','{}','{}')".format(args['title'],args['href'],args['icon'],args['type'],args['inline'],args['private'],args['user_id']))
    ret['id']   = db.get_last_id()
   else:
    ret['update'] = db.update_dict('resources',args,'id=%s'%id)
  else:
   db.do("SELECT id,title,href,icon,type,inline,private,user_id FROM resources WHERE id = '%s'"%id)
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
