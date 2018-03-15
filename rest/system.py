"""SDCP generic REST module. The portal and authentication"""
__author__ = "Zacharias El Banna"
__version__ = "18.03.14GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

#
#
def application(aDict):
 """Function docstring for application TBD

 Args:

 Output:
 """
 from datetime import datetime,timedelta
 from ..core.common import DB,SC
 """ Default login information """
 ret = {'message':"Welcome to the Management Portal",'parameters':[],'title':'Portal','portal':'system'}
 with DB() as db:
  db.do("SELECT parameter,value FROM settings WHERE section = 'portal' AND node = '%s'"%aDict.pop('node','master'))
  for row in db.get_rows():
   ret[row['parameter']] = row['value']
  db.do("SELECT CONCAT(id,'_',name) as id, name FROM users ORDER BY name")
  rows = db.get_rows()
 ret['choices'] = [{'display':'Username', 'id':'system_login', 'data':rows}]
 cookie = aDict
 cookie['portal'] = ret['portal']
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
 from ..core.common import DB,SC
 from resources import list as resource_list
 ret = {}
 with DB() as db:
  if aDict['node'] == 'master':
   db.do("SELECT node FROM nodes WHERE system = 1")
   ret['nodes'] = [x['node'] for x in db.get_rows()]
   db.do("SELECT id, icon, title, href, type, inline, user_id FROM resources WHERE type = 'monitor' AND (user_id = %s OR private = 0) ORDER BY type,title"%ret.get('user_id',1))
   ret['monitors'] = db.get_dict(aDict.get('dict')) if aDict.get('dict') else db.get_rows()
   db.do("SELECT section,value FROM settings WHERE parameter = 'node' AND node = '%s'"%aDict['node'])
   for row in db.get_rows():
    ret[row['section']]= {'node':row['value'],'type':SC[row['section']].get('type') }

 ret['id'] = SC['system']['id']
 return ret

#
#
def settings_fetch(aDict):
 """Function docstring for settings_fetch TBD

 Args:
  - node (required)
 
 Output:
 """
 from ..core.common import DB
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
 from os import path as ospath
 from ..core.common import DB,SC,rest_call
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
  settings['system']['config_file'] = ret['file']

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

 Output:
 """
 from ..core.common import DB
 ret = {}
 args = aDict
 with DB() as db:
  ret['update'] = db.insert_dict('nodes',args,'ON DUPLICATE KEY UPDATE node = node')
 return ret

#
#
def node_list(aDict):
 """Function docstring for node_list TBD

 Args:

 Output:
 """
 from ..core.common import DB
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
 from ..core.common import DB
 id = aDict.pop('id','new')
 op = aDict.pop('op',None)
 ret = {}
 args = aDict
 with DB() as db:
  if op == 'update':
   if not id == 'new':
    ret['update'] = db.update_dict('nodes',args,'id=%s AND system = 0'%id)
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
 from ..core.common import DB
 ret = {}   
 with DB() as db:
  ret['delete'] = db.do("DELETE FROM nodes WHERE id = %s AND system = 0"%aDict['id'])
 return ret
