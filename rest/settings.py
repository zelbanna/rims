"""Settings REST module. Manages settings for nodes, offers nested settings management for other nodes pinpointed from the node section"""
__author__ = "Zacharias El Banna"
__version__ = "18.03.07GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

from ..core.dbase import DB

def list(aDict):
 """Function docstring for list TBD

 Args:
  - node (optional)
  - dict (optional)
  - section (optional)
  - user_id (optional)

 Output:
 """
 if not aDict.get('node','master') == 'master':
  from ..core.rest import call as rest_call
  node = aDict.pop('node',None)
  with DB() as db:
   db.do("SELECT value FROM settings WHERE section = 'node' and parameter = '%s'"%node)
   url = db.get_val('value')
  ret = rest_call("%s?settings_list"%url,aDict)['data']
  if not ret:
   ret = {'xist':0,'data':{}}
 else:
  ret = {'user_id':aDict.get('user_id',"1") }
  if aDict.get('section'):
   filter = "WHERE section = '%s'"%aDict.get('section')
   ret['section'] = aDict.get('section')
  else:
   filter = ""
   ret['section'] = 'all'
  with DB() as db:
   ret['xist'] = db.do("SELECT * FROM settings %s ORDER BY section,parameter"%(filter))
   ret['data'] = db.get_dict(aDict.get('dict')) if aDict.get('dict') else db.get_rows()
 return ret

#
#
def info(aDict):
 """Function docstring for info TBD

 Args:
  - node (optional)
  - id (required)
  - op (optional)
  - description (cond required)
  - section (cond required)
  - value (cond required)
  - parameter (cond required)
  - required (conditionally required)

 Output:
 """
 node = aDict.pop('node','master')
 if not node == 'master':
  from ..core.rest import call as rest_call
  with DB() as db:
   db.do("SELECT value FROM settings WHERE section = 'node' and parameter = '%s'"%node)
   url = db.get_val('value')
  ret = rest_call("%s?settings_info"%url,aDict)['data']
 else:
  ret = {}
  args = aDict
  id = args.pop('id',None)
  op = args.pop('op',None)
  with DB() as db:
   if op == 'update':
    if not id == 'new':
     if args.pop('required','0') == '0':
      ret['update'] = db.update_dict('settings',args,"id=%s"%id) 
     else:
      ret['update'] = db.update_dict('settings',{'value':args['value']},"id=%s"%id) 
    else:
     ret['update'] = db.do("INSERT INTO settings (section,parameter,required,value,description) VALUES ('{}','{}','{}','{}','{}')".format(aDict['section'],aDict['parameter'],aDict.get('required',0),aDict['value'],aDict['description']))
     id = db.get_last_id()
   ret['xist'] = db.do("SELECT * FROM settings WHERE id = '%s'"%id)
   ret['data'] = db.get_row()
 return ret

#
#
def parameter(aDict):
 """Function docstring for parameter TBD

 Args:
  - node (optional)
  - section (required)
  - parameter (required)

 Output:
 """
 if not aDict.get('node','master') == 'master':
  from ..core.rest import call as rest_call
  node = aDict.pop('node',None)
  with DB() as db:
   db.do("SELECT value FROM settings WHERE section = 'node' and parameter = '%s'"%node)
   url = db.get_val('value')
  ret = rest_call("%s?settings_parameter"%url,aDict)['data']
 else:
  ret = {}
  with DB() as db:
   ret['xist'] = db.do("SELECT * FROM settings WHERE section='%s' AND parameter='%s'"%(aDict['section'],aDict['parameter']))
   ret['data'] = db.get_row()
 return ret

#
#
def section(aDict):
 """Function docstring for section TBD

 Args:
  - node (optional)
  - section (required)

 Output:
 """
 if not aDict.get('node','master') == 'master':
  from ..core.rest import call as rest_call
  node = aDict.pop('node',None)
  with DB() as db:
   db.do("SELECT value FROM settings WHERE section = 'node' and parameter = '%s'"%node)
   url = db.get_val('value')
  ret = rest_call("%s?settings_section"%url,aDict)['data']
 else:
  ret = {}
  with DB() as db:
   ret['xist'] = db.do("SELECT id,parameter,value,description FROM settings WHERE section = '%s' ORDER BY parameter"%(aDict['section']))
   ret['data'] = db.get_dict('parameter')
 return ret

#
#
def all(aDict):
 """Function docstring for all TBD

 Args:
  - node (optional)
  - dict (optional)
  - section (optional)

 Output:
 """
 if not aDict.get('node','master') == 'master':
  from ..core.rest import call as rest_call
  node = aDict.pop('node',None)
  with DB() as db:
   db.do("SELECT value FROM settings WHERE section = 'node' and parameter = '%s'"%node)
   url = db.get_val('value')
  ret = rest_call("%s?settings_all"%url,aDict)['data']
 else:
  ret = {}
  with DB() as db:
   if not aDict.get('section'):
    db.do("SELECT DISTINCT section FROM settings")
    rows = db.get_rows()
    sections = [row['section'] for row in rows]
   else:
    sections = [aDict.get('section')]
   for section in sections:
    db.do("SELECT parameter,id,value,description,required FROM settings WHERE section = '%s' ORDER BY parameter"%(section))
    ret[section] = db.get_rows() if not aDict.get('dict') else db.get_dict(aDict.get('dict'))
 return ret

#
#
def save(aDict):
 """Function docstring for save TBD

 Args:
  - node (optional)

 Output:
 """
 if not aDict.get('node','master') == 'master':
  from ..core.rest import call as rest_call
  node = aDict.pop('node',None)
  with DB() as db:
   db.do("SELECT value FROM settings WHERE section = 'node' and parameter = '%s'"%node)
   url = db.get_val('value')
  ret = rest_call("%s?settings_save"%url,aDict)['data']
 else:
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
   ret['config'] = 'NOT_OK'
  try:
   file=ospath.abspath(ospath.join(ospath.dirname(__file__),'..','SettingsContainer.py'))
   with open(file,'w') as f:
    for key,values in container.iteritems():
     f.write("%s=%s\n"%(key,dumps(values)))
  except:
   ret['containers'] = 'NOT_OK'
 return ret

#
#
def delete(aDict):
 """Function docstring for delete TBD

 Args:
  - node (optional)
  - id (required)

 Output:
 """
 if not aDict.get('node','master') == 'master':
  from ..core.rest import call as rest_call
  node = aDict.pop('node',None)
  with DB() as db:
   db.do("SELECT value FROM settings WHERE section = 'node' and parameter = '%s'"%node)
   url = db.get_val('value')
  ret = rest_call("%s?settings_delete"%url,aDict)['data']
 else:
  ret = {} 
  with DB() as db:
   ret['deleted'] = db.do("DELETE FROM settings WHERE id = '%s' AND required ='0'"%aDict['id'])
 return ret
