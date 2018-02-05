"""Module docstring.

Settings REST module

"""
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"

from ..core.dbase import DB

def list(aDict):
 ret = {'user_id':aDict.get('user_id',"1") }
 if aDict.get('type'):
  filter = "WHERE type = '%s'"%aDict['type']
  ret['type'] = aDict['type']
 else:
  filter = ""
  ret['type'] = 'all'
 with DB() as db:
  ret['xist'] = db.do("SELECT id,type,parameter,value,description FROM settings %s ORDER BY type,parameter"%(filter))
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
    ret['xist'] = db.do("INSERT INTO settings (type,parameter,value,description) VALUES ('{}','{}','{}','{}')".format(aDict['type'],aDict['parameter'],aDict['value'],aDict['description']))
    ret['id']   = db.get_last_id()
   else:
    ret['xist'] = db.do("UPDATE settings SET type='{}',parameter='{}',value='{}',description='{}' WHERE id = '{}'".format(aDict['type'],aDict['parameter'],aDict['value'],aDict['description'],aDict['id']))
  else:
   db.do("SELECT id,type,parameter,value,description FROM settings WHERE id = '%s'"%id)
   ret['data'] = db.get_row()
 return ret

#
#
def parameter(aDict):
 ret = {}
 with DB() as db:
  ret['xist'] = db.do("SELECT id,type,parameter,value,description FROM settings WHERE type='%s' AND parameter='%s'"%(aDict['type'],aDict['parameter']))
  ret['data'] = db.get_row()
 return ret

#
#
def type(aDict):
 ret = {}
 with DB() as db:
  ret['xist'] = db.do("SELECT id,parameter,value,description FROM settings WHERE type = '%s' ORDER BY parameter"%(aDict['type']))
  ret['data'] = db.get_dict('parameter')
 return ret

#
#
def all(aDict):
 ret = {}
 with DB() as db:
  if not aDict.get('type'):
   db.do("SELECT DISTINCT type FROM settings")
   types = db.get_rows()
  else:
   types = [{'type':aDict['type']}]
  for tp in types:
   type = tp['type']
   db.do("SELECT parameter,id,value,description FROM settings WHERE type = '%s'"%(type))
   ret[type] = db.get_dict('parameter')   
 return ret

#
#
def remove(aDict):
 with DB() as db:
  res = db.do("DELETE FROM settings WHERE id = '%s'"%aDict['id'])
 return { 'deleted':res }
