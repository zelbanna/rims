"""Module docstring.

Resources REST module

"""
__author__ = "Zacharias El Banna"
__version__ = "18.02.09GA"
__status__ = "Production"

from ..core.dbase import DB

def list(aDict):
 ret = {'user_id':aDict.get('user_id',"1"), 'type':aDict.get('type') }
 with DB() as db:
  if aDict.get('view_public',None) is None:
   db.do("SELECT view_public FROM users WHERE id = %s"%ret['user_id'])
   ret['view_public'] = (db.get_val('view_public') == 1)
  else:
   ret['view_public'] = aDict['view_public']
  select = "%s(user_id = %s %s)"%("type = '%s' AND "%ret['type'] if ret['type'] else "", ret['user_id'],"" if not ret['view_public'] else 'OR private = 0')
  ret['xist'] = db.do("SELECT id, icon, title, href, type, inline, user_id FROM resources WHERE %s ORDER BY type,title"%select)
  ret['data'] = db.get_dict(aDict['dict']) if aDict.get('dict') else db.get_rows()
 return ret

#
#
def info(aDict):
 ret = {'id':aDict['id']}
 id = aDict['id']
 op = aDict.pop('op',None)
 with DB() as db:
  if op == 'update':
   if aDict['id'] == 'new':
    ret['xist'] = db.do("INSERT INTO resources (title,href,icon,type,inline,private,user_id) VALUES ('{}','{}','{}','{}','{}','{}','{}')".format(aDict['title'],aDict['href'],aDict['icon'],aDict['type'],aDict['inline'],aDict['private'],aDict['user_id']))
    ret['id']   = db.get_last_id()
   else:
    ret['xist'] = db.do("UPDATE resources SET title='{}',href='{}',icon='{}', type='{}', inline='{}', private='{}' WHERE id = '{}'".format(aDict['title'],aDict['href'],aDict['icon'],aDict['type'],aDict['inline'],aDict['private'],aDict['id']))
  else:
   db.do("SELECT id,title,href,icon,type,inline,private,user_id FROM resources WHERE id = '%s'"%id)
   ret['data'] = db.get_row()
 return ret

#
#
def delete(aDict):
 with DB() as db:
  res = db.do("DELETE FROM resources WHERE id = '%s'"%aDict['id'])
 return { 'deleted':res }
