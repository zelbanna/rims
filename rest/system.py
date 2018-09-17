"""SDCP generic REST module. Provides system and DB interaction for appication, settings and resources"""
__author__ = "Zacharias El Banna"
__version__ = "4.0GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)
__node__ = 'master'

from zdcp.core.common import DB

######################################### APPLICATION ############################################
#
#
def application(aDict):
 """Function docstring for application. Using 'portal' settings ('title', 'message' and resource 'id' of start page)

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
 """Function docstring for authenticate. Provide cookie with lifetime.

 Args:
  - id (required)

 Output:
 """
 from zdcp.core.genlib import random_string
 from datetime import datetime,timedelta
 ret = {}
 try:    tmp = int(aDict['id'])
 except: ret['authenticated'] = 'NOT_OK'
 else:
  ret['authenticated'] = 'OK'
  ret['token'] = random_string(16)
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
   ret.update({'node':True,'users':True})
   db.do("SELECT node FROM nodes WHERE system = 1")
   ret['logs'] = [x['node'] for x in db.get_rows()]
  else:
   ret['logs']  = [aDict['node']]

  if aDict.get('user_id'):
   db.do("SELECT alias FROM users WHERE id = %s"%aDict.get('user_id'))
   ret['navinfo'].append(db.get_val('alias'))

  db.do("SELECT parameter AS name, value AS service FROM settings WHERE section = 'services' AND node = '%s'"%aDict['node'])
  ret['services'] = db.get_rows()

  db.do("SELECT title, href FROM resources WHERE node = '%s' AND type = 'tool' AND view < 2 AND (user_id = %s OR private = 0) ORDER BY type,title"%(aDict['node'],aDict.get('user_id',1)))
  ret['tools'] = db.get_rows()

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
    ret['menu'] = [{'id':info['id'],'icon':'../images/icon-start.png', 'title':'Start', 'href':info['href'], 'view':info['view'] }]
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

#
#
def log(aDict):
 """ Function 'log' logs to default system log whatever is in parameter 'msg'

 Args:
  - msg

 Output:
 """
 ret = {'result':'OK'}
 from zdcp.core.common import log
 log(aDict['msg'])
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
  ret['count'] = db.do("SELECT * FROM settings WHERE node = '%s' %s ORDER BY section,parameter"%(ret['node'],filter))
  ret['data']  = db.get_dict(aDict.get('dict')) if aDict.get('dict') else db.get_rows()
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
  if op == 'update' and not (aDict['section'] == 'system' or aDict['section'] =='nodes'):
   if not id == 'new':
    ret['update'] = db.update_dict('settings',args,"id=%s"%id) 
   else:
    ret['update'] = db.insert_dict('settings',args)
    id = db.get_last_id() if ret['update'] > 0 else 'new'

  if not id == 'new':
   ret['found'] = (db.do("SELECT * FROM settings WHERE id = '%s'"%id) > 0)
   ret['data']  = db.get_row()
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
 """Function docstring for settings_comprehensive TBD

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
  ret['deleted'] = db.do("DELETE FROM settings WHERE id = %(id)s AND node = '%(node)s'"%aDict)
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
  db.do("SELECT 'nodes' AS section, node AS parameter, url AS value FROM nodes")
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
 from zdcp.core.common import rest_call
 ret = {'config_file':SC['system']['config_file']}
 try:
  SC.clear()
  with open(ret['config_file']) as sfile:
   temp = loads(sfile.read())
  for section,content in temp.iteritems():
   for key,params in content.iteritems():
    if not SC.get(section):
     SC[section] = {}
    SC[section][key] = params['value']
  SC['system']['config_file'] = ret['config_file']

  if SC['system']['id'] == 'master':
   with DB() as db:
    db.do("SELECT section,parameter,value FROM settings WHERE node = 'master'")
    data = db.get_rows()
    db.do("SELECT 'nodes' AS section, node AS parameter, url AS value FROM nodes")
    data.extend(db.get_rows())
   for setting in data:
    section = setting.pop('section')
    if not SC.get(section):
     SC[section] = {}
    SC[section][setting['parameter']] = setting['value']
  else:
   try: master = rest_call("%s/api/system_settings_fetch"%SC['system']['master'],{'node':SC['system']['id']})['data']
   except: pass
   else:
    for section,content in master.iteritems():
     if SC.get(section): SC[section].update(content)
     else: SC[section] = content

  container = ospath.abspath(ospath.join(ospath.dirname(__file__),'..','Settings.py'))
  with open(container,'w') as f:
   f.write("SC=%s\n"%dumps(SC))
  ret['result'] = 'OK'
 except Exception as e:
  ret['result'] = 'NOT_OK'
  ret['error'] = str(e)
 return ret

#
#
def settings_container(aDict):
 """Function returns the settings container

 Args:

 Output:
 """
 return SC

################################################# NODE ##############################################
#
# A node represent a system entity that can run REST commands remote (or locally),
# - system indicates it was registered and should not be deletable
# - device_id: connected to a device in the device/IPAM DB:s
#


#
#
def node_register(aDict):
 """Function docstring for register TBD

 Args:
  - node (required)
  - url (required)
  - system (optional)

 Output:
 """
 ret = {}
 args = {'node':aDict['node'],'url':aDict['url'],'system':aDict.get('system','0')}
 with DB() as db:
  ret['update'] = db.insert_dict('nodes',args,"ON DUPLICATE KEY UPDATE system = %(system)s, url = '%(url)s'"%args)
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
  ret['count'] = db.do("SELECT * FROM nodes")
  ret['data']  = db.get_rows()
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
 args.pop('hostname',None)
 try:
  args['device_id'] = int(args.get('device_id'))
 except:
  args['device_id'] = 'NULL'
 with DB() as db:
  if op == 'update':
   if not id == 'new':
    ret['update'] = db.update_dict('nodes',args,'id=%s'%id)
   else:
    ret['update'] = db.insert_dict('nodes',args)
    id = db.get_last_id() if ret['update'] > 0 else 'new'
   SC['nodes'][args['node']] = args['url']
  if not id == 'new':
   ret['found'] = (db.do("SELECT nodes.*, devices.hostname FROM nodes LEFT JOIN devices ON devices.id = nodes.device_id WHERE nodes.id = '%s'"%id) > 0)
   ret['data'] = db.get_row()
  else:
   ret['data'] = {'id':'new','node':'Unknown','url':'Unknown','device_id':None,'hostname':None}
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
  if db.do("SELECT node FROM nodes WHERE id = %s AND node <> 'master'"%aDict['id']) > 0:
   SC['nodes'].pop(db.get_val('node'),None)
   ret['delete'] = (db.do("DELETE FROM nodes WHERE id = %s'"%aDict['id']) == 1)
  else:
   ret['delete'] = False 
 return ret

#
#
def node_module_reload(aDict):
 """Function attempts to reload a module @ a system node identified by id or node name

 Args:
  - id (optionally required)
  - node (optionally required)
  - module (required)

 Output:
  - result.
 """
 ret = {}
 from zdcp.core.common import rest_call
 if aDict.get('node'):
  ret['node'] = aDict['node']
 else:
  with DB() as db:
   db.do("SELECT node FROM nodes WHERE id = %s"%aDict['id'])
   ret['node'] = db.get_val('node')
 if ret['node'] == SC['system']['id']:
  ret['result'] = 'module reloaded'
 else:
  ret['result'] = rest_call("%s/api/system_node_module_reload"%(SC['nodes'][ret['node']]),{'module':aDict['module']})['data']['result']
 return ret

#
#
def node_device_mapping(aDict):
 """Node/Device mapping translates between nodes and devices and provide the same info, it depends on the device existing or node having mapped a device (else 'found' is false)

 Args:
  - id (optional required)
  - node (optional required)

 Output:
  - found. boolean
  - id. device id
  - node. node name
  - hostname. device hostname
  - ip. device ip
  - domain. Device domain name
  - url
 """
 with DB() as db:
  if aDict.get('id'):
   found = (db.do("SELECT hostname, INET_NTOA(ia.ip) as ip, domains.name AS domain, url FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id LEFT JOIN domains ON domains.id = devices.a_dom_id WHERE devices.id = %s"%aDict['id']) > 0)
   ret = db.get_row() if found else {}
   ret['found'] = (db.do("SELECT node FROM nodes WHERE device_id = %s"%aDict['id']) > 0)
   ret['node']  = db.get_val('node') if ret['found'] else None
   ret['id']    = int(aDict['id'])
  else:
   found = (db.do("SELECT device_id FROM nodes WHERE node = '%s'"%aDict['node']) > 0)
   ret = {'id':db.get_val('device_id') if found else None, 'node':aDict['node'], 'found':False}
   if ret['id']:
    ret['found'] = (db.do("SELECT hostname, INET_NTOA(ia.ip) as ip, domains.name AS domain, url FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id LEFT JOIN domains ON domains.id = devices.a_dom_id WHERE devices.id = %s"%ret['id']) > 0)
    ret.update(db.get_row())
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
  ret['count'] = db.do("SELECT id, node, icon, title, href, type, view, user_id FROM resources WHERE %s ORDER BY type,title"%select)
  ret['data']  = db.get_dict(aDict.get('dict')) if aDict.get('dict') else db.get_rows()
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
  ret['count'] = db.do("SELECT id, alias, name, email FROM users ORDER by name")
  ret['data']  = db.get_rows()
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
   ret['found'] = (db.do("SELECT users.* FROM users WHERE id = '%s'"%id) > 0)
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


################################ SERVERS ##################################
#
#
def server_list(aDict):
 """Function docstring for server_list TBD

 Args:
  - type (optional)

 Output:
 """
 ret = {}
 if aDict.get('type'):
  sql = "SELECT id, server, node, type FROM servers WHERE type = '%s'"%aDict['type']
 else:
  sql = "SELECT id, server, node, type FROM servers"
 with DB() as db:
  db.do(sql)
  ret['servers']= db.get_rows()
 return ret

#
#
def server_info(aDict):
 """Function docstring for server_info TBD

 Args:

 Output:
 """
 ret = {}
 args = aDict
 id = args.pop('id','new')
 op = args.pop('op',None)
 with DB() as db:
  db.do("SELECT node FROM nodes")
  ret['nodes'] = db.get_rows()
  if op == 'update':
   if not id == 'new':
    ret['update'] = db.update_dict('servers',args,"id=%s"%id)
   else:
    ret['update'] = db.insert_dict('servers',args)
    id = db.get_last_id() if ret['update'] > 0 else 'new'

  if not id == 'new':
   ret['found'] = (db.do("SELECT * FROM servers WHERE id = '%s'"%id) > 0)
   ret['data'] = db.get_row()
  else:
   ret['data'] = {'id':'new','node':None,'server':'Unknown','type':aDict.get('type')}
  if   ret['data']['type'] == 'DNS':
   ret['servers'] = [{'server':'nodns','type':'DNS'},{'server':'powerdns','type':'DNS'},{'server':'infoblox','type':'DNS'}]
  elif ret['data']['type'] == 'DHCP':
   ret['servers'] = [{'server':'nodhcp','type':'DHCP'},{'server':'iscdhcp','type':'DHCP'}]

 return ret

#
#
def server_delete(aDict):
 """Function docstring for server_delete TBD

 Args:
  - id (required)

 Output:
 """
 ret = {}
 with DB() as db:
  ret['deleted'] = db.do("DELETE FROM servers WHERE id = %s"%aDict['id'])
 return ret

#
#
def server_sync(aDict):
 """Server sync sends sync message to server @ node and convey result. What sync means is server dependent

 Args:
  - id (required):

 Output:
 """
 ret = {}
 with DB() as db:
  ret['found'] = (db.do("SELECT node,server FROM servers WHERE id = %s"%aDict['id']) == 1)
  if ret['found']:
   from zdcp.core.common import node_call
   data = db.get_row()
   ret['result'] = node_call(data['node'],data['server'],'sync',{'id':aDict['id']})
 return ret

#
#
def server_restart(aDict):
 """Server restart attempt to restart a server @ node.

 Args:
  - id (required))

 Output:
  - result.
 """
 ret = {}
 with DB() as db:
  ret['found'] = (db.do("SELECT node,server FROM servers WHERE id = %s"%aDict['id']) == 1)
  if ret['found']:
   from zdcp.core.common import node_call
   data = db.get_row()
   ret['result'] = node_call(data['node'],data['server'],'restart',{'id':aDict['id']})
 return ret

######################################### ACTIVITIES ###########################################
#
#
def activities_list(aDict):
 """ Function docstring for activities_list. TBD

 Args:
  - start (optional)
  - mode (optional), 'basic' (default)/'full'

 Output:
 """
 ret = {'start':aDict.get('start',0)}
 ret['end'] = int(ret['start']) + 50
 ret['mode']= aDict.get('mode','basic')
 if ret['mode'] == 'full':
  select = "activities.id, activities.event"
 else:
  select = "activities.id"
 with DB() as db:
  db.do("SELECT %s, activity_types.type AS type, DATE_FORMAT(date_time,'%%H:%%i') AS time, DATE_FORMAT(date_time, '%%Y-%%m-%%d') AS date, alias AS user FROM activities LEFT JOIN activity_types ON activities.type_id = activity_types.id LEFT JOIN users ON users.id = activities.user_id ORDER BY date_time DESC LIMIT %s, %s"%(select,ret['start'],ret['end']))
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
  db.do("SELECT * FROM activity_types")
  ret['types'] = db.get_rows()
  db.do("SELECT id,alias FROM users ORDER BY alias")
  ret['users'] = db.get_rows()
  if op == 'update':
   args['date_time'] ="%s %s:00"%(args.pop('date','1970-01-01'),args.pop('time','00:01'))

   if not id == 'new':
    ret['update'] = db.update_dict('activities',args,'id = %s'%id)
   else:
    ret['update'] = db.insert_dict('activities',args)
    id = db.get_last_id() if ret['update'] > 0 else 'new'

  if not id == 'new':
   ret['found'] = (db.do("SELECT id,user_id,type_id, DATE_FORMAT(date_time,'%%H:%%i') AS time, DATE_FORMAT(date_time, '%%Y-%%m-%%d') AS date, event FROM activities WHERE id = %s"%id) > 0)
   ret['data'] = db.get_row()
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

  if not id == 'new':
   ret['found'] = (db.do("SELECT * FROM activity_types WHERE id = '%s'"%id) > 0)
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

##################################### TASKs ###############################

#
#
def task_add(aDict):
 """ Adds a task

 Args:
  - node (required)
  - module (required)
  - func (required)
  - args (required)
  - state (optional). Boolean
  - type (optional) (0: transient, 1: periodic, defaults: 0)
  - frequency (optional required, seconds for periodic tasks, defaults: 300 seconds)

 Output:
  - result. Boolean
 """
 ret = {}
 with DB() as db:
  db.do("SELECT id FROM nodes WHERE node = '%s'"%aDict['node'])
  node = db.get_val('id')
  ret['add'] = (db.do("INSERT INTO system_tasks (node_id, module, func, args, state, type, frequency) VALUES(%i,'%s','%s','%s',%i,%i,%i)"%(node,aDict['module'],aDict['func'],dumps(aDict['args']), 1 if aDict.get('state') else 0,aDict.get('type',0),aDict.get('frequency',300))) == 1)
 return ret

#
#
def task_delete(aDict):
 """ Delete a task

 Args:
  - id (required)

 Output:
 """
 ret = {}
 with DB() as db:
  ret['delete'] = db.do("DELETE FROM system_tasks WHERE id = '%s'"%aDict['id'])
 return ret

#
#
def task_list(aDict):
 """ List tasks

 Args:
  - node (required)

 Output:
 """
 ret = {}
 with DB() as db:
  db.do("SELECT id FROM nodes WHERE node = '%s'"%aDict['node'])
  node = db.get_val('id')
  ret['count'] = db.do("SELECT * FROM system_tasks WHERE node_id = %s"%node)
  ret['tasks'] = db.get_rows()
 return ret

#
#
def task_state(aDict):
 """ Alter tasks state

 Args:
  - id (required)
  - state (optional: boolean, true for active and false for disabled, nothing meanse just read state)

 Output:
  - state (boolean)
 """
 ret = {}
 with DB() as db:
  if aDict.get('state'):
   ret['updated'] = (db.do("UPDATE system_types SET active = %i WHERE id = %i"%(1 if aDict['state'] else 0, int(aDict['id']))) == 1)
   ret['state']= aDict['state'] if ret['updated'] else None
  else:
   db.do("SELECT active FROM system_tasks WHERE id = %i")
   ret['state'] = (db.get_val('active') == 1)
 return ret
