"""SDCP generic REST module. The portal and authentication"""
__author__ = "Zacharias El Banna"
__version__ = "18.03.16"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

from sdcp.core.common import DB,SC

#
#
def application(aDict):
 """Function docstring for application TBD

 Args:

 Output:
 """
 from datetime import datetime,timedelta
 """ Default login information """
 ret  = {'message':"Welcome to the Management Portal",'parameters':[],'title':'Portal'}
 aDict['node'] = aDict.get('node','master')
 with DB() as db:
  db.do("SELECT parameter,value FROM settings WHERE section = 'portal' AND node = '%s'"%aDict['node'])
  for row in db.get_rows():
   ret[row['parameter']] = row['value']
  db.do("SELECT CONCAT(id,'_',name) as id, name FROM users ORDER BY name")
  rows = db.get_rows()
 ret['choices'] = [{'display':'Username', 'id':'system_login', 'data':rows}]
 cookie = aDict
 ret['cookie'] = ",".join(["%s=%s"%(k,v) for k,v in cookie.iteritems()])
 ret['expires'] = (datetime.utcnow() + timedelta(days=1)).strftime("%a, %d %b %Y %H:%M:%S GMT")
 return ret


#
#
def authenticate(aDict):
 """Function docstring for authenticate. Provide cookie with lifetime. TODO should set auth and ID here

 Args:

 Output:
 """
 from datetime import datetime,timedelta
 ret = {}
 ret['authenticated'] = 'OK'
 ret['expires'] = (datetime.utcnow() + timedelta(days=1)).strftime("%a, %d %b %Y %H:%M:%S GMT")
 return ret

#
#
def inventory(aDict):
 """Function docstring for inventory. Provides inventory info for paticular nodes

 Args:
  - node (required)
  - user_id (optional)

 Output:
 """
 ret = {'navinfo':[]}
 with DB() as db:
  if aDict['node'] == 'master':
   ret.update({'node':True,'extra':True,'users':True})
   db.do("SELECT node FROM nodes WHERE system = 1")
   ret['logs'] = [x['node'] for x in db.get_rows()]
   db.do("SELECT node FROM nodes WHERE www = 1")
   ret['www'] = [x['node'] for x in db.get_rows()]
  else:
   ret['logs']  = [aDict['node']]

  if aDict.get('user_id'):
   db.do("SELECT alias FROM users WHERE id = %s"%aDict.get('user_id'))
   ret['navinfo'].append(db.get_val('alias'))

  db.do("SELECT parameter AS name, value AS service FROM settings WHERE section = 'services' AND node = '%s'"%aDict['node'])
  ret['services'] = db.get_rows()

  db.do("SELECT title, href FROM resources WHERE node = '%s' AND type = 'tool' AND view < 2 AND (user_id = %s OR private = 0) ORDER BY type,title"%(aDict['node'],aDict.get('user_id',1)))
  ret['tools'] = db.get_rows()
  db.do("SELECT section,value FROM settings WHERE parameter = 'node' AND node = '%s'"%aDict['node'])
  for row in db.get_rows():
   ret[row['section']]= {'node':row['value'],'type':SC[row['section']].get('type') }

 return ret

####################################### Settings #####################################
#
#
def settings_list(aDict):
 """Function docstring for settings_list TBD

 Args:
  - node (optional)
  - dict (optional)
  - section (optional)
  - user_id (optional)

 Output:
 """
 ret = {'user_id':aDict.get('user_id',"1"),'node':aDict.get('node',SC['system']['id']) }
 if aDict.get('section'):
  filter = "AND section = '%s'"%aDict.get('section')
  ret['section'] = aDict.get('section')
 else:
  filter = ""
  ret['section'] = 'all'
 with DB() as db:
  ret['xist'] = db.do("SELECT * FROM settings WHERE node = '%s' %s ORDER BY section,parameter"%(ret['node'],filter))
  ret['data'] = db.get_dict(aDict.get('dict')) if aDict.get('dict') else db.get_rows()
 return ret

#
#
def settings_info(aDict):
 """Function docstring for settings_info TBD

 Args:
  - node (required)
  - id (required)
  - op (optional)
  - description (cond required)
  - section (cond required)
  - value (cond required)
  - parameter (cond required)

 Output:
 """
 ret = {}
 args = aDict
 id = args.pop('id',None)
 op = args.pop('op',None)
 with DB() as db:
  if op == 'update' and not (aDict['section'] == 'system' or aDict['section'] =='node'):
   if not id == 'new':
    ret['update'] = db.update_dict('settings',args,"id=%s"%id) 
   else:
    ret['update'] = db.insert_dict('settings',args)
    id = db.get_last_id()
  ret['xist'] = db.do("SELECT * FROM settings WHERE id = '%s'"%id)
  ret['data'] = db.get_row()
 return ret

#
#
def parameter(aDict):
 """Function docstring for parameter TBD

 Args:
  - section (required)
  - parameter (required)

 Output:
 """
 try: ret = {'value':SC[aDict['section']][aDict['parameter']]}
 except: ret = {'value':None }
 return ret

#
#
def settings_all(aDict):
 """Function docstring for settings_all TBD

 Args:
  - node (required)
  - dict (optional)
  - section (optional)

 Output:
 """
 ret = {}
 with DB() as db:
  if not aDict.get('section'):
   db.do("SELECT DISTINCT section FROM settings WHERE node='%s'"%aDict['node'])
   rows = db.get_rows()
   sections = [row['section'] for row in rows]
  else:
   sections = [aDict.get('section')]
  for section in sections:
   db.do("SELECT parameter,id,value,description FROM settings WHERE node = '%s' AND section = '%s'  ORDER BY parameter"%(aDict['node'],section))
   ret[section] = db.get_rows() if not aDict.get('dict') else db.get_dict(aDict.get('dict'))
 return ret

#
#
def settings_delete(aDict):
 """Function docstring for settings_delete TBD

 Args:
  - node (required)
  - id (required)

 Output:
 """
 ret = {} 
 with DB() as db:
  ret['deleted'] = db.do("DELETE FROM settings WHERE id = '%s' AND node = '%s'"%(aDict['id'],aDict['node']))
 return ret

#
#
def settings_fetch(aDict):
 """Function docstring for settings_fetch TBD

 Args:
  - node (required)
 
 Output:
 """
 ret = {}
 with DB() as db:
  db.do("SELECT section,parameter,value FROM settings WHERE node = '%s'"%aDict['node'])
  data = db.get_rows()
  db.do("SELECT 'node' AS section, node AS parameter, url AS value FROM nodes")
  data.extend(db.get_rows())
 for setting in data:
  section = setting.pop('section')
  if not ret.get(section):
   ret[section] = {}
  ret[section][setting['parameter']] = setting['value']
 return ret

#
#     
def settings_save(aDict):
 """Function docstring for settings_save TBD

 Args:
 
 Output:
 """
 from sdcp.core.common import rest_call
 ret = {'config_file':SC['system']['config_file']}
 try:
  settings = {}
  with open(SC['system']['config_file']) as sfile:         
   temp = loads(sfile.read())
  for section,content in temp.iteritems():
   for key,params in content.iteritems():
    if not settings.get(section):
     settings[section] = {}
    settings[section][key] = params['value'] 
  settings['system']['config_file'] = ret['config_file']

  if SC['system']['id'] == 'master':
   with DB() as db:
    db.do("SELECT section,parameter,value FROM settings WHERE node = 'master'")
    data = db.get_rows()
    db.do("SELECT 'node' AS section, node AS parameter, url AS value FROM nodes")
    data.extend(db.get_rows())
   for setting in data:
    section = setting.pop('section') 
    if not settings.get(section): 
     settings[section] = {} 
    settings[section][setting['parameter']] = setting['value']
  else:
   try: master = rest_call("%s?system_settings_fetch"%settings['system']['master'],{'node':settings['system']['id']})['data']
   except: pass
   else:
    for section,content in master.iteritems():
     if settings.get(section): settings[section].update(content)
     else: settings[section] = content

  container = ospath.abspath(ospath.join(ospath.dirname(__file__),'..','SettingsContainer.py'))
  with open(container,'w') as f:
   f.write("SC=%s\n"%dumps(settings))
  ret['result'] = 'OK'
 except Exception,e:
  ret['result'] = 'NOT_OK'
  ret['error'] = str(e)
 return ret

####################################### Node Management #####################################
#
#
def register(aDict):
 """Function docstring for register TBD

 Args:
  - node (required)
  - url (required)
  - system (optional)
  - www (optional)

 Output:
 """
 ret = {}
 args = {'node':aDict['node'],'url':aDict['url'],'system':aDict.get('system','0'),'www':aDict.get('www','0')}
 with DB() as db:
  ret['update'] = db.insert_dict('nodes',args,"ON DUPLICATE KEY UPDATE system = %s, www = %s, url = '%s'"%(args['system'],args['www'],args['url']))
 return ret

#
#
def node_list(aDict):
 """Function docstring for node_list TBD

 Args:

 Output:
 """
 ret = {}
 args = aDict
 with DB() as db:
  ret['xist'] = db.do("SELECT * FROM nodes")
  ret['data'] = db.get_rows()
 return ret

#
#
def node_info(aDict):
 """Function docstring for node_info TBD

 Args:
  - id (required)
  - op (optional)

 Output:
 """
 id = aDict.pop('id','new')
 op = aDict.pop('op',None)
 ret = {}
 args = aDict
 with DB() as db:
  if op == 'update':
   if not id == 'new':
    ret['update'] = db.update_dict('nodes',args,'id=%s AND (system = 0 OR www = 0)'%id)
   else:
    ret['update'] = db.insert_dict('nodes',args)
    id = db.get_last_id()
  ret['xist'] = db.do("SELECT * FROM nodes WHERE id = '%s'"%id)
  ret['data'] = db.get_row()
 return ret

#
#
def node_delete(aDict):
 """Function docstring for node_delete TBD

 Args:
  - id (required)

 Output:
 """
 ret = {}   
 with DB() as db:
  ret['delete'] = db.do("DELETE FROM nodes WHERE id = %s"%aDict['id'])
 return ret
