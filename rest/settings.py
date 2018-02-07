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
   db.do("SELECT parameter,id,value,description,required FROM settings WHERE section = '%s' ORDER BY parameter"%(section['section']))
   ret[section['section']] = db.get_rows() if not aDict.get('dict') else db.get_dict(aDict['dict'])
 return ret

#
#
def save(aDict):
 from os import chmod, remove, listdir, path as ospath
 from json import dumps,dump
 ret = {'containers':'OK','config':'OK'}
 config = {}
 container = {}

 with DB() as db:
  db.do("SELECT value FROM settings WHERE section = 'generic' AND parameter = 'config_file'")
  config_file = db.get_val('value')
  db.do("SELECT DISTINCT section FROM settings")
  sections = db.get_rows()
  for section in sections:
   sect = section['section']
   config[sect] = {}
   container[sect] = {}
   db.do("SELECT parameter,value,description,required FROM settings WHERE section = '%s' ORDER BY parameter"%sect)
   params = db.get_rows()
   for param in params:
    key = param.pop('parameter',None)
    config[sect][key] = param
    container[sect][key] = param['value']
 try:
  with open(config_file,'w') as f:
   dump(config,f,indent=4,sort_keys=True)
 except Exception as e:
  print e
  ret['config'] = 'NOT_OK'
 try:
  for key,values in container.iteritems():
   file= ospath.abspath(ospath.join(ospath.dirname(__file__),'..','settings',"%s.py"%key))
   with open(file,'w') as f:
    f.write("data=%s"%dumps(values))
 except:
  ret['containers'] = 'NOT_OK'
 return ret

#
#
def delete(aDict):
 with DB() as db:
  res = db.do("DELETE FROM settings WHERE id = '%s' AND required ='0'"%aDict['id'])
 return { 'deleted':res }
