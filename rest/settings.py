"""Module docstring.

Settings REST module

"""
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"

from ..core.dbase import DB

def list(aDict):
 ret = {'user_id':aDict.get('user_id',"1") }
 if aDict.get('section'):
  filter = "WHERE section = '%s'"%aDict['section']
  ret['section'] = aDict['section']
 else:
  filter = ""
  ret['section'] = 'all'
 with DB() as db:
  ret['xist'] = db.do("SELECT * FROM settings %s ORDER BY section,parameter"%(filter))
  ret['data'] = db.get_dict(aDict['dict']) if aDict.get('dict') else db.get_rows()
 return ret

#
#
def info(aDict):
 ret = {}
 id = aDict['id']
 op = aDict.pop('op',None)
 with DB() as db:
  if op == 'update':
   if id == 'new':
    ret['result'] = db.do("INSERT INTO settings (section,parameter,required,value,description) VALUES ('{}','{}','{}','{}','{}')".format(aDict['section'],aDict['parameter'],aDict.get('required',0),aDict['value'],aDict['description']))
    id = db.get_last_id()
   else:
    if aDict['required'] == '0':
     ret['result'] = db.do("UPDATE settings SET section='{}',parameter='{}',value='{}',description='{}' WHERE id = '{}'".format(aDict['section'],aDict['parameter'],aDict['value'],aDict['description'],id))
    else:
     ret['result'] = db.do("UPDATE settings SET value='{}' WHERE id = '{}'".format(aDict['value'],id))
  ret['xist'] = db.do("SELECT * FROM settings WHERE id = '%s'"%id)
  ret['data'] = db.get_row()
 return ret

#
#
def parameter(aDict):
 ret = {}
 with DB() as db:
  ret['xist'] = db.do("SELECT * FROM settings WHERE section='%s' AND parameter='%s'"%(aDict['section'],aDict['parameter']))
  ret['data'] = db.get_row()
 return ret

#
#
def section(aDict):
 ret = {}
 with DB() as db:
  ret['xist'] = db.do("SELECT id,parameter,value,description FROM settings WHERE section = '%s' ORDER BY parameter"%(aDict['section']))
  ret['data'] = db.get_dict('parameter')
 return ret

#
#
def all(aDict):
 ret = {}
 with DB() as db:
  if not aDict.get('section'):
   db.do("SELECT DISTINCT section FROM settings")
   sections = db.get_rows()
  else:
   sections = [{'section':aDict['section']}]
  for section in sections:
   db.do("SELECT parameter,id,value,description,required FROM settings WHERE section = '%s'"%(section['section']))
   ret[section['section']] = db.get_rows()
 return ret

#
#
def delete(aDict):
 with DB() as db:
  res = db.do("DELETE FROM settings WHERE id = '%s' AND required ='0'"%aDict['id'])
 return { 'deleted':res }
