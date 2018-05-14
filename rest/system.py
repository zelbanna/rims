"""SDCP generic REST module. Provides system and DB interaction for appication, settings and resources"""
__author__ = "Zacharias El Banna"
__version__ = "18.04.07GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)
__node__ = 'master'

from sdcp.core.common import DB,SC

######################################### APPLICATION ############################################
#
#
def application(aDict):
 """Function docstring for application. Pick up 'portal' section from settings ('title', 'message' and resource 'id' of start page)

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
  - id (required)

 Output:
 """
 from datetime import datetime,timedelta
 ret = {}
 try:    tmp = int(aDict['id'])
 except: ret['authenticated'] = 'NOT_OK'
 else:   ret['authenticated'] = 'OK'
 ret['expires'] = (datetime.utcnow() + timedelta(days=30)).strftime("%a, %d %b %Y %H:%M:%S GMT")
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

#
#
def menu(aDict):
 """Function docstring for menu TBD

 Args:
  - node (required)
  - id (required)

 Output:
 """
 try:
  id = int(aDict['id'])
 except:
  ret = {'authenticated':'NOT_OK'}
 else:
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


############################################ SETTINGS ########################################
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
 id = args.pop('id','new')
 op = args.pop('op',None)
 with DB() as db:
  if op == 'update' and not (aDict['section'] == 'system' or aDict['section'] =='node'):
   if not id == 'new':
    ret['update'] = db.update_dict('settings',args,"id=%s"%id) 
   else:
    ret['update'] = db.insert_dict('settings',args)
    id = db.get_last_id() if ret['update'] > 0 else 'new'

  if not id == 'new':
   ret['xist'] = db.do("SELECT * FROM settings WHERE id = '%s'"%id)
   ret['data'] = db.get_row()
  else:
   ret['data'] = {'id':'new','value':'Unknown','section':aDict.get('section','Unknown'),'parameter':'Unknown','description':'Unknown'}
 return ret

#
#
def settings_parameter(aDict):
 """Function docstring for settings_parameter TBD

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
def settings_comprehensive(aDict):
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
  with open(ret['config_file']) as sfile:
   temp = loads(sfile.read())
  for section,content in temp.iteritems():
   for key,params in content.iteritems():
    if not settings.get(section):
     settings[section] = {}
    settings[section][key] = params['value'] 
  settings['system']['config_file'] = ret['config_file']

  if settings['system']['id'] == 'master':
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

#
#
def settings_container(aDict):
 """Function docstring for register TBD

 Args:

 Output:
 """
 return SC

################################################# NODE ##############################################
#
#
def node_register(aDict):
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
 ret = {}
 args = aDict
 id = args.pop('id','new')
 op = args.pop('op',None)
 with DB() as db:
  if op == 'update':
   if not id == 'new':
    ret['update'] = db.update_dict('nodes',args,'id=%s AND (system = 0 OR www = 0)'%id)
   else:
    ret['update'] = db.insert_dict('nodes',args)
    id = db.get_last_id() if ret['update'] > 0 else 'new'

  if not id == 'new':
   ret['xist'] = db.do("SELECT * FROM nodes WHERE id = '%s'"%id)
   ret['data'] = db.get_row()
  else:
   ret['data'] = {'id':'new','node':'Unknown','url':'Unknown'}
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


############################################# RESOURCES #############################################

#
#
def resources_list(aDict):
 """Function docstring for resources_list TBD

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
  ret['xist'] = db.do("SELECT id, node, icon, title, href, type, view, user_id FROM resources WHERE %s ORDER BY type,title"%select)
  ret['data'] = db.get_dict(aDict.get('dict')) if aDict.get('dict') else db.get_rows()
 return ret

#
#
def resources_info(aDict):
 """Function docstring for resources_info TBD

 Args:
  - id (required)
  - op (optional)
  - node (required conditionally)
  - user_id (required conditionally)
  - title (required conditionally)
  - private (required conditionally)
  - href (required conditionally)
  - view (required conditionally)
  - type (required conditionally)
  - icon (required conditionally)

 Output:
 """
 ret = {}
 args = aDict
 id = args.pop('id','new')
 op = args.pop('op',None)
 with DB() as db:
  if op == 'update':
   if not id == 'new':
    ret['update'] = db.update_dict('resources',args,'id=%s'%id)
   else:
    ret['update'] = db.insert_dict('resources',args)
    id = db.get_last_id() if ret['update'] > 0 else 'new'

  if not id == 'new':
   db.do("SELECT * FROM resources WHERE id = '%s'"%id)
   ret['data'] = db.get_row()
  else:
   ret['data'] = {'id':'new','node':aDict['node'],'user_id':aDict['user_id'],'title':'Unknown','href':'Unknown','type':None,'icon':None,'private':0,'view':0}
 return ret

#
#
def resources_delete(aDict):
 """Function docstring for resources_delete TBD

 Args:
  - id (required)

 Output:
 """
 with DB() as db:
  deleted = db.do("DELETE FROM resources WHERE id = '%s'"%aDict['id'])
 return { 'deleted':deleted }


########################################### USERS ############################################
#
#
def users_list(aDict):
 """Function docstring for users_list TBD

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
def users_info(aDict):
 """Function docstring for users_info TBD

 Args:
  - id (required)
  - op (optional)
  - name (optional)
  - view_public (optional)
  - menulist (optional)
  - alias (optional)
  - email (optional)

 Output:
 """
 ret = {}
 args = aDict
 id = args.pop('id','new')
 op = args.pop('op',None)
 with DB() as db:
  if op == 'update':
   if not id == 'new':
    ret['update'] = db.update_dict('users',args,"id=%s"%id)
   else:
    ret['update'] = db.insert_dict('users',args)
    id = db.get_last_id() if ret['update'] > 0 else 'new'
  
  if not id == 'new':
   ret['xist'] = db.do("SELECT users.* FROM users WHERE id = '%s'"%id)
   ret['data'] = db.get_row()
  else:
   ret['data'] = {'id':'new','name':'Unknown','alias':'Unknown','email':'Unknown','view_public':'0','menulist':'default'}
 return ret

#
#
def users_delete(aDict):
 """Function docstring for users_delete TBD

 Args:
  - id (required)

 Output:
 """
 with DB() as db:
  res = db.do("DELETE FROM users WHERE id = '%s'"%aDict['id'])
 return { 'deleted':res }

######################################### ACTIVITIES ###########################################
#
#
def activities_list(aDict):
 """ Function docstring for activities_list. TBD

 Args:
  - start (optional)

 Output:
 """
 ret = {'start':aDict.get('start','0')}
 ret['end'] = int(ret['start']) + 50
 with DB() as db:
  db.utf8()
  db.do("SELECT activities.id, activity_types.type AS type, CONCAT(hour,':',minute) AS time, CONCAT(year,'-',month,'-',day) AS date FROM activities LEFT JOIN activity_types ON activities.type_id = activity_types.id ORDER BY year,month,day DESC LIMIT %s, %s"%(ret['start'],ret['end']))
  ret['data'] = db.get_rows()
 return ret

#
#
def activities_info(aDict):
 """ Function docstring for activities_info. TBD

 Args:
  - id (required)
  - start (optional)

 Output:
 """
 ret = {}
 args = aDict
 id = args.pop('id','new')
 op = args.pop('op',None)
 with DB() as db:
  db.utf8()
  db.do("SELECT * FROM activity_types")
  ret['types'] = db.get_rows()
  db.do("SELECT id,alias FROM users ORDER BY alias")
  ret['users'] = db.get_rows()
  if op == 'update':
   hour,minute    = args.pop('time','00:00').split(':')
   year,month,day = args.pop('date','1970-01-01').split('-')
   args.update({'year':year,'month':month,'day':day,'hour':hour,'minute':minute})

   if not id == 'new':
    ret['update'] = db.update_dict('activities',args,'id = %s'%id)
   else:
    ret['update'] = db.insert_dict('activities',args)
    id = db.get_last_id() if ret['update'] > 0 else 'new'

  if not id == 'new':
   ret['xist'] = db.do("SELECT * FROM activities WHERE id = %s"%id)
   act = db.get_row()
   ret['data'] = {'id':id,'user_id':act['user_id'],'type_id':act['type_id'],'date':"%i-%02i-%02i"%(act['year'],act['month'],act['day']),'time':"%02i:%02i"%(act['hour'],act['minute']),'event':act['event']}
  else:
   from time import localtime
   from datetime import date
   tm = localtime()
   dt = date.today()
   ret['data'] = {'id':'new','user_id':None,'type_id':None,'date':"%i-%02i-%02i"%(dt.year,dt.month,dt.day),'time':"%02i:%02i"%(tm.tm_hour,tm.tm_min),'event':'empty'}
 return ret

#
#
def activities_delete(aDict):
 """ Function docstring for activities_delete. TBD

 Args:
  - id (required)

 Output:
 """
 ret = {}
 with DB() as db:
  ret['delete'] = db.do("DELETE FROM activities WHERE id = '%s'"%aDict['id'])
 return ret

#
#
def activities_type_list(aDict):
 """ Function docstring for activities_type_list. TBD

 Args:                

 Output:
 """    
 ret = {}
 with DB() as db:
  db.utf8()
  db.do("SELECT * FROM activity_types")
  ret['data'] = db.get_rows()
 return ret

#
#
def activities_type_info(aDict):
 """ Function docstring for activities_type_info. TBD

 Args:

 Output:
 """
 ret = {}
 args = aDict
 id = args.pop('id','new')
 op = args.pop('op',None)
 with DB() as db:
  if op == 'update':
   if not id == 'new':
    ret['update'] = db.update_dict('activity_types',args,"id=%s"%id) 
   else:
    ret['update'] = db.insert_dict('activity_types',args)
    id = db.get_last_id() if ret['update'] > 0 else 'new'

  db.utf8()
  if not id == 'new':
   ret['xist'] = db.do("SELECT * FROM activity_types WHERE id = '%s'"%id)
   ret['data'] = db.get_row()
  else:
   ret['data'] = {'id':'new','type':'Unknown'}
 return ret
 
#
#
def activities_type_delete(aDict):
 """ Function docstring for activity_type_delete. TBD

 Args:
  - id (required)

 Output:
 """
 ret = {}
 with DB() as db:
  ret['delete'] = db.do("DELETE FROM activity_types WHERE id = '%s'"%aDict['id'])
 return ret
