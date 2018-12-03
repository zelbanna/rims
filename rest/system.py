"""Generic REST module. Provides system and DB interaction for application, settings and resources"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__node__ = 'master'


######################################### APPLICATION ############################################
#
#
def application(aCTX, aArgs = None):
 """Function docstring for application. Using 'portal' settings ('title', 'message' and resource 'id' of start page)

 Args:

 Output:
 """
 from datetime import datetime,timedelta
 """ Default login information """
 ret  = {'message':"Welcome to the Management Portal",'title':'Portal'}
 aArgs['node'] = aArgs.get('node','master')
 with aCTX.db as db:
  db.do("SELECT parameter,value FROM settings WHERE section = 'portal' AND node = '%s'"%aArgs['node'])
  for row in db.get_rows():
   ret[row['parameter']] = row['value']
  db.do("SELECT alias as id, name FROM users ORDER BY name")
  ret['usernames'] = db.get_rows()
 return ret

#
#
def inventory(aCTX, aArgs = None):
 """Function docstring for inventory. Provides inventory info for paticular nodes

 Args:
  - node (required)
  - user_id (optional)

 Output:
 """
 ret = {'navinfo':[]}
 with aCTX.db as db:
  if aArgs['node'] == 'master':
   ret.update({'node':True,'users':True})
   ret['logs'] = [k for k,v in aCTX.nodes.items() if v['system'] == 1]
  else:
   ret['logs']  = [aArgs['node']]

  if aArgs.get('user_id'):
   db.do("SELECT alias FROM users WHERE id = %s"%aArgs.get('user_id'))
   ret['navinfo'].append(db.get_val('alias'))

  db.do("SELECT parameter AS name, value AS service FROM settings WHERE section = 'services' AND node = '%s'"%aArgs['node'])
  ret['services'] = db.get_rows()

  db.do("SELECT title, href FROM resources WHERE node = '%s' AND type = 'tool' AND view < 2 AND (user_id = %s OR private = 0) ORDER BY type,title"%(aArgs['node'],aArgs.get('user_id',1)))
  ret['tools'] = db.get_rows()

 return ret

#
#
def menu(aCTX, aArgs = None):
 """Function docstring for menu TBD

 Args:
  - node (required)
  - id (required)

 Output:
 """
 id = int(aArgs['id'])
 ret = {}
 with aCTX.db as db:
  start = db.do("SELECT id,view,href FROM resources WHERE id = (SELECT CAST(value AS UNSIGNED) FROM settings WHERE node = '%s' AND section = 'portal' AND parameter = 'start')"%aArgs['node'])
  if start > 0:
   info = db.get_row()
   ret['start'] = True
   ret['menu'] = [{'id':info['id'],'icon':'../images/icon-start.png', 'title':'Start', 'href':info['href'], 'view':info['view'] }]
  else:
   ret['start'] = False
   ret['menu'] = []
  if aArgs['node'] == 'master':
   db.do("SELECT menulist FROM users WHERE id = '%s'"%aArgs['id'])
   menulist = db.get_val('menulist')
   select = "type = 'menuitem'" if menulist == 'default' else "id IN (%s) ORDER BY FIELD(id,%s)"%(menulist,menulist)
  else:
   select = "type = 'menuitem'"
  db.do("SELECT id, icon, title, href, view FROM resources WHERE node = '%s' AND %s"%(aArgs['node'],select))
  ret['menu'].extend(db.get_rows())
  title_exist = (db.do("SELECT value FROM settings WHERE section = 'portal' AND parameter = 'title' and node = '%s'"%aArgs['node']) == 1)
  ret['title']= db.get_val('value') if title_exist else "Portal"
 return ret

#
#
def oui_fetch(aCTX, aArgs = None):
 """ Function fetch and populate OUI table

 Args:
  - clear (optional). Clear database before populating if true. Defaults to false
 
 Output:
 """
 from urllib.request import urlopen, Request
 from urllib.error import HTTPError
 ret = {'count':0}
 try:
  req = Request(aCTX.settings['oui']['location'])
  sock = urlopen(req, timeout = 120)
  data = sock.read().decode()
  sock.close()
 except HTTPError as h:
  ret.update({'status':'HTTPError', 'code':h.code, 'info':dict(h.info())})
 except Exception as e:
  ret.update({ 'status':type(e).__name__, 'code':590, 'error':repr(e)})
 else:
  with aCTX.db as db:
   if aArgs.get('clear') is True:
    db.do("TRUNCATE oui")
   for line in data.split('\n'):
    if len(line) > 0:
     parts = line.split()
     if len(parts) > 3 and parts[1] == '(base' and parts[2] == '16)':
      oui = int(parts[0].upper(),16)
      company = (" ".join(parts[3:]).replace("'",''))[0:60]
      ret['count'] += db.do("INSERT INTO oui(oui,company) VALUES(%d,'%s') ON DUPLICATE KEY UPDATE company = '%s'"%(oui,company,company))
   else:
    ret['status'] = 'OK'
 return ret

#
#
def oui_info(aCTX, aArgs = None):
 """ Function retrieves OUI info from database

 Args:
  - oui (required). string, e.g. "AABB00"

 Output:
 """
 try:
  oui = int(aArgs['oui'].translate(str.maketrans({':':'','-':''}))[:6],16)
  with aCTX.db as db:
   found = (db.do("SELECT LPAD(HEX(oui),6,0) AS oui, company FROM oui WHERE oui = %s"%oui) == 1)
   ret = db.get_row() if found else {'oui':'NOT_FOUND','company':'NOT_FOUND'}
   ret['status'] = 'OK' if ret['oui'] != 'NOT_FOUND' else 'NOT_FOUND'
 except Exception as e:
  ret = {'status':'NOT_OK','error':repr(e),'oui':None,'company':''}
 return ret

#
#
def oui_list(aCTX, aArgs = None):
 """ Function retrieves OUI list

 Args:

 Output:
 """
 ret = {}
 with aCTX.db as db:
  db.do("SELECT LPAD(HEX(oui),6,0) AS oui, company FROM oui")
  ret['data'] = db.get_rows()
 return ret

############################################ SETTINGS ########################################
#
#
def setting_list(aCTX, aArgs = None):
 """Function docstring for settings_list TBD

 Args:
  - node (optional)
  - dict (optional)
  - section (optional)
  - user_id (optional)

 Output:
 """
 ret = {'user_id':aArgs.get('user_id',"1"),'node':aArgs.get('node',aCTX.node) }
 if aArgs.get('section'):
  filter = "AND section = '%s'"%aArgs.get('section')
  ret['section'] = aArgs.get('section')
 else:
  filter = ""
  ret['section'] = 'all'
 with aCTX.db as db:
  ret['count'] = db.do("SELECT * FROM settings WHERE node = '%s' %s ORDER BY section,parameter"%(ret['node'],filter))
  ret['data']  = db.get_dict(aArgs.get('dict')) if aArgs.get('dict') else db.get_rows()
 return ret

#
#
def setting_info(aCTX, aArgs = None):
 """Function docstring for setting_info TBD

 Args:
  - node (required)
  - id (required)
  - op (optional)
  - section (cond required)
  - value (cond required)
  - parameter (cond required)

 Output:
 """
 ret = {}
 id = aArgs.pop('id','new')
 op = aArgs.pop('op',None)

 with aCTX.db as db:
  if op == 'update' and not (aArgs['section'] == 'system' or aArgs['section'] =='nodes'):
   if not id == 'new':
    ret['update'] = db.update_dict('settings',aArgs,"id=%s"%id)
   else:
    ret['update'] = db.insert_dict('settings',aArgs)
    id = db.get_last_id() if ret['update'] > 0 else 'new'
   if aArgs['node'] == 'master':
    section = aCTX.settings.get(aArgs['section'],{})
    section[aArgs['parameter']] = aArgs['value']
    aCTX.settings[aArgs['section']] = section
   else:
    aCTX.workers.add_function(aCTX.rest_call,"%s/system/sync/%s"%(aCTX.config['master'],aArgs['node']), aDataOnly = True)
  if not id == 'new':
   ret['found'] = (db.do("SELECT * FROM settings WHERE id = '%s'"%id) > 0)
   ret['data']  = db.get_row()
  else:
   ret['data'] = {'id':'new','value':'Unknown','section':aArgs.get('section','Unknown'),'parameter':'Unknown'}

 return ret

#
#
def setting_comprehensive(aCTX, aArgs = None):
 """Function docstring for setting_comprehensive TBD

 Args:
  - node (required)
  - dict (optional)
  - section (optional)

 Output:
 """
 ret = {}
 with aCTX.db as db:
  if not aArgs.get('section'):
   db.do("SELECT DISTINCT section FROM settings WHERE node='%s'"%aArgs['node'])
   rows = db.get_rows()
   sections = [row['section'] for row in rows]
  else:
   sections = [aArgs.get('section')]
  for section in sections:
   db.do("SELECT parameter,id,value FROM settings WHERE node = '%s' AND section = '%s'  ORDER BY parameter"%(aArgs['node'],section))
   ret[section] = db.get_rows() if not aArgs.get('dict') else db.get_dict(aArgs.get('dict'))
 return ret

#
#
def setting_delete(aCTX, aArgs = None):
 """Function docstring for setting_delete TBD

 Args:
  - node (required)
  - id (required)

 Output:
 """
 ret = {}
 with aCTX.db as db:
  db.do("SELECT section,parameter FROM settings WHERE id = %(id)s AND node = '%(node)s'"%aArgs)
  data = db.get_row()
  ret['deleted'] = db.do("DELETE FROM settings WHERE id = %(id)s AND node = '%(node)s'"%aArgs)
 if aArgs['node'] == 'master':
  aCTX.settings.get(data['section'],{}).pop(data['parameter'],None)
 else:
  aCTX.workers.add_function(aCTX.rest_call,"%s/system/sync/%s"%(aCTX.config['master'],aArgs['node']), aDataOnly = True)
 return ret

################################################# NODE ##############################################
#
#
def node_list(aCTX, aArgs = None):
 """Function docstring for node_list TBD

 Args:

 Output:
 """
 ret = {}
 with aCTX.db as db:
  ret['count'] = db.do("SELECT * FROM nodes")
  ret['data']  = db.get_rows()
 return ret

#
#
def node_info(aCTX, aArgs = None):
 """Function docstring for node_info TBD

 Args:
  - id (required)
  - op (optional)

 Output:
 """
 ret = {}
 id = aArgs.pop('id','new')
 op = aArgs.pop('op',None)
 aArgs.pop('hostname',None)
 try:
  aArgs['device_id'] = int(aArgs.get('device_id'))
 except:
  aArgs['device_id'] = 'NULL'
 with aCTX.db as db:
  if op == 'update':
   if not id == 'new':
    ret['update'] = db.update_dict('nodes',aArgs,'id=%s'%id)
   else:
    ret['update'] = db.insert_dict('nodes',aArgs)
    id = db.get_last_id() if ret['update'] > 0 else 'new'
  if not id == 'new':
   ret['found'] = (db.do("SELECT nodes.*, devices.hostname FROM nodes LEFT JOIN devices ON devices.id = nodes.device_id WHERE nodes.id = '%s'"%id) > 0)
   ret['data'] = db.get_row()
   if ret['found'] and op == 'update':
    node = ret['data']
    for k in list(aCTX.nodes.keys()):
     if aCTX.nodes[k]['id'] == node['id']:
      aCTX.nodes.pop(k,None)
      break
    aCTX.nodes[node['node']] = {'id':node['id'],'url':node['url'],'system':node['system']}
  else:
   ret['data'] = {'id':'new','node':'Unknown','url':'Unknown','device_id':None,'hostname':None,'system':0}
 return ret

#
#
def node_delete(aCTX, aArgs = None):
 """Function docstring for node_delete TBD

 Args:
  - id (required)

 Output:
 """
 ret = {}
 with aCTX.db as db:
  if (aArgs['id'] != 'new') and db.do("SELECT node FROM nodes WHERE id = %s AND node <> 'master'"%aArgs['id']) > 0:
   aCTX.nodes.pop(db.get_val('node'),None)
   ret['delete'] = (db.do("DELETE FROM nodes WHERE id = %s"%aArgs['id']) == 1)
  else:
   ret['delete'] = False 
 return ret

#
#
def node_to_api(aCTX, aArgs = None):
 """ Function returns api for a specific node name

 Args:
  - node

 Output:
  - url
 """
 return {'url':aCTX.nodes[aArgs['node']]['url']}

############################################# RESOURCES #############################################

#
#
def resource_list(aCTX, aArgs = None):
 """Function docstring for resource_list TBD

 Args:
  - node (required)
  - user_id (required)
  - dict (required)
  - type (optional)
  - view_public (optional)
  - dict (optional)

 Output:
 """
 ret = {'user_id':aArgs.get('user_id',"1"),'type':aArgs.get('type','all')}
 with aCTX.db as db:
  if aArgs.get('view_public') is None:
   db.do("SELECT view_public FROM users WHERE id = %s"%ret['user_id'])
   ret['view_public'] = (db.get_val('view_public') == 1)
  else:
   ret['view_public'] = aArgs.get('view_public')
  node = "node = '%s'"%aArgs['node'] if aArgs.get('node') else "true"
  type = "type = '%s'"%aArgs['type'] if aArgs.get('type') else "true"
  user = "(user_id = %s OR %s)"%(ret['user_id'],'false' if not ret['view_public'] else 'private = 0')
  select = "%s AND %s AND %s"%(node,type,user)
  ret['count'] = db.do("SELECT id, node, icon, title, href, type, view, user_id FROM resources WHERE %s ORDER BY type,title"%select)
  ret['data']  = db.get_dict(aArgs.get('dict')) if aArgs.get('dict') else db.get_rows()
 return ret

#
#
def resource_info(aCTX, aArgs = None):
 """Function docstring for resource_info TBD

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
 id = aArgs.pop('id','new')
 op = aArgs.pop('op',None)
 with aCTX.db as db:
  if op == 'update':
   if aArgs['icon'] == 'None':
    aArgs['icon'] = '../images/icon-na.png'
   if not id == 'new':
    ret['update'] = db.update_dict('resources',aArgs,'id=%s'%id)
   else:
    ret['update'] = db.insert_dict('resources',aArgs)
    id = db.get_last_id() if ret['update'] > 0 else 'new'

  if not id == 'new':
   db.do("SELECT * FROM resources WHERE id = '%s'"%id)
   ret['data'] = db.get_row()
  else:
   ret['data'] = {'id':'new','node':aArgs['node'],'user_id':aArgs['user_id'],'title':'Unknown','href':'Unknown','type':None,'icon':None,'private':0,'view':0}
 return ret

#
#
def resource_delete(aCTX, aArgs = None):
 """Function docstring for resource_delete TBD

 Args:
  - id (required)

 Output:
 """
 with aCTX.db as db:
  deleted = db.do("DELETE FROM resources WHERE id = '%s'"%aArgs['id'])
 return { 'deleted':deleted }

########################################## THEMES ############################################
#
def theme_list(aCTX, aArgs = None):
 """ Function returns a list of available thems
 
 Args:

 Output:
  - list of theme names
 """
 from os import walk, path as ospath
 path = ospath.join(aCTX.path,'infra')
 _, _, filelist = next(walk(path), (None, None, []))
 return [x.split('.')[1] for x in filelist if x.startswith('theme.')]

########################################### USERS ############################################
#
#
def user_list(aCTX, aArgs = None):
 """Function docstring for user_list TBD

 Args:

 Output:
 """
 ret = {}
 with aCTX.db as db:
  ret['count'] = db.do("SELECT id, alias, name, email FROM users ORDER by name")
  ret['data']  = db.get_rows()
 return ret

#
#
def user_encrypt(aCTX, aArgs = None):
 """Function encrypts 'data' with password encryption techniques, providing entire encryption string (method,salt,code)

 Args:
  - data

 Output:
  - encrypted
 """
 from crypt import crypt
 ret = {}
 ret['encrypted'] = crypt(aArgs['data'],"$1$%s$"%aCTX.config['salt'])
 return ret

#
#
def user_info(aCTX, aArgs = None):
 """Function docstring for user_info TBD

 Args:
  - id (required)
  - op (optional)
  - name (optional)
  - view_public (optional)
  - menulist (optional)
  - alias (optional)
  - email (optional)
  - password (optional)
  - slack (optional)
  - theme (optional)

 Output:
 """
 ret = {}
 id = aArgs.pop('id','new')
 op = aArgs.pop('op',None)
 with aCTX.db as db:
  if op == 'update':
   from crypt import crypt
   """ Password at least 6 characters """
   if len(aArgs.get('password','')) > 5:
    aArgs['password'] = crypt(aArgs['password'],'$1$%s$'%aCTX.config['salt']).split('$')[3]
   else:
    ret['password_check_failed'] = (not (aArgs.pop('password',None) is None))
   if aArgs.get('slack') == 'None':
    aArgs['slack'] = 'NULL'
   if not id == 'new':
    ret['update'] = db.update_dict('users',aArgs,"id=%s"%id)
   else:
    if not aArgs.get('password'):
     aArgs['password'] = crypt('changeme','$1$%s$'%aCTX.config['salt']).split('$')[3]
    ret['update'] = db.insert_dict('users',aArgs)
    id = db.get_last_id() if ret['update'] > 0 else 'new'

  if not id == 'new':
   ret['found'] = (db.do("SELECT users.* FROM users WHERE id = '%s'"%id) > 0)
   ret['data'] = db.get_row()
   ret['data'].pop('password',None)
  else:
   ret['data'] = {'id':'new','name':'Unknown','alias':'Unknown','email':'Unknown','view_public':'0','menulist':'default','external_id':None,'slack':'Unknown','theme':'blue'}
 return ret

#
#
def user_delete(aCTX, aArgs = None):
 """Function docstring for user_delete TBD

 Args:
  - id (required)

 Output:
 """
 with aCTX.db as db:
  res = db.do("DELETE FROM users WHERE id = '%s'"%aArgs['id'])
 return { 'deleted':res }


################################ SERVERS ##################################
#
#
def server_list(aCTX, aArgs = None):
 """Function docstring for server_list TBD

 Args:
  - type (optional)

 Output:
 """
 ret = {}
 
 with aCTX.db as db:
  db.do("SELECT servers.id, servers.service, servers.node, servers.type, servers.ui, nodes.system FROM servers LEFT JOIN nodes ON servers.node = nodes.node WHERE %s ORDER BY servers.node"%("type = '%s'"%aArgs['type'] if aArgs.get('type') else "TRUE"))
  ret['servers']= db.get_rows()
 return ret

#
#
def server_info(aCTX, aArgs = None):
 """Function docstring for server_info TBD

 Args:

 Output:
 """
 ret = {}
 id = aArgs.pop('id','new')
 op = aArgs.pop('op',None)
 with aCTX.db as db:
  ret['nodes'] = list(aCTX.nodes.keys())
  if op == 'update':
   if aArgs.get('ui') == 'None':
    aArgs['ui'] = 'NULL'
   if not id == 'new':
    ret['update'] = db.update_dict('servers',aArgs,"id=%s"%id)
    aCTX.servers[int(id)].update(aArgs)
   else:
    ret['update'] = db.insert_dict('servers',aArgs)
    id = db.get_last_id() if ret['update'] > 0 else 'new'
    aCTX.servers[int(id)] = aArgs
  if not id == 'new':
   ret['found'] = (db.do("SELECT * FROM servers WHERE id = '%s'"%id) > 0)
   ret['data'] = db.get_row()
   db.do("SELECT name AS service, base AS type FROM service_types WHERE base = '%s'"%ret['data']['type'])
  else:
   type = aArgs.get('type',None)
   ret['data'] = {'id':'new','node':None,'service':'Unknown','type':type,'ui':None}
   if type:
    ret['types'] = [type]
    db.do("SELECT name AS service, base AS type FROM service_types WHERE base = '%s'"%type) 
   else:
    db.do("SELECT DISTINCT base AS type FROM service_types")
    ret['types'] = [x['type'] for x in db.get_rows()]
    db.do("SELECT name AS service, base AS type FROM service_types") 
  ret['servers'] = db.get_rows()

 return ret

#
#
def server_delete(aCTX, aArgs = None):
 """Function docstring for server_delete TBD

 Args:
  - id (required)

 Output:
 """
 ret = {}
 with aCTX.db as db:
  ret['deleted'] = db.do("DELETE FROM servers WHERE id = %s"%aArgs['id'])
  aCTX.servers.pop(int(aArgs['id']),None)
 return ret

#
#
def server_sync(aCTX, aArgs = None):
 """Server sync sends sync message to server @ node and convey result. What sync means is server dependent

 Args:
  - id (required):

 Output:
 """
 server = aCTX.servers[int(aArgs['id'])]
 return aCTX.node_function(server['node'],server['service'],'sync')(aArgs = {'id':aArgs['id']})

#
#
def server_status(aCTX, aArgs = None):
 """Server status sends status message to server @ node and convey result. What status means is server dependent

 Args:
  - id (required):

 Output:
 """
 server = aCTX.servers[int(aArgs['id'])]
 return aCTX.node_function(server['node'],server['service'],'status')(aArgs = {'id':aArgs['id']})

#
#
def server_restart(aCTX, aArgs = None):
 """Server restart attempt to restart a server @ node.

 Args:
  - id (required))

 Output:
  - result.
 """
 server = aCTX.servers[int(aArgs['id'])]
 return {'status':aCTX.node_function(server['node'],server['service'],'restart')(aArgs = {'id':aArgs['id']})}

######################################### ACTIVITYS ###########################################
#
#
def activity_list(aCTX, aArgs = None):
 """ Function docstring for activity_list. TBD

 Args:
  - start (optional)
  - mode (optional), 'basic' (default)/'full'

 Output:
 """
 ret = {'start':aArgs.get('start',0)}
 ret['end'] = int(ret['start']) + 50
 ret['mode']= aArgs.get('mode','basic')
 if ret['mode'] == 'full':
  select = "activities.id, activities.event"
 else:
  select = "activities.id"
 with aCTX.db as db:
  db.do("SELECT %s, activity_types.type AS type, DATE_FORMAT(date_time,'%%H:%%i') AS time, DATE_FORMAT(date_time, '%%Y-%%m-%%d') AS date, alias AS user FROM activities LEFT JOIN activity_types ON activities.type_id = activity_types.id LEFT JOIN users ON users.id = activities.user_id ORDER BY date_time DESC LIMIT %s, %s"%(select,ret['start'],ret['end']))
  ret['data'] = db.get_rows()
 return ret

#
#
def activity_info(aCTX, aArgs = None):
 """ Function docstring for activity_info. TBD

 Args:
  - id (required)
  - start (optional)

 Output:
 """
 ret = {}
 id = aArgs.pop('id','new')
 op = aArgs.pop('op',None)
 with aCTX.db as db:
  db.do("SELECT * FROM activity_types")
  ret['types'] = db.get_rows()
  db.do("SELECT id,alias FROM users ORDER BY alias")
  ret['users'] = db.get_rows()
  if op == 'update':
   aArgs['date_time'] ="%s %s:00"%(aArgs.pop('date','1970-01-01'),aArgs.pop('time','00:01'))

   if not id == 'new':
    ret['update'] = db.update_dict('activities',aArgs,'id = %s'%id)
   else:
    ret['update'] = db.insert_dict('activities',aArgs)
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
def activity_delete(aCTX, aArgs = None):
 """ Function docstring for activity_delete. TBD

 Args:
  - id (required)

 Output:
 """
 ret = {}
 with aCTX.db as db:
  ret['delete'] = db.do("DELETE FROM activities WHERE id = '%s'"%aArgs['id'])
 return ret

#
#
def activity_type_list(aCTX, aArgs = None):
 """ Function docstring for activity_type_list. TBD

 Args:

 Output:
 """
 ret = {}
 with aCTX.db as db:
  db.do("SELECT * FROM activity_types")
  ret['data'] = db.get_rows()
 return ret

#
#
def activity_type_info(aCTX, aArgs = None):
 """ Function docstring for activity_type_info. TBD

 Args:

 Output:
 """
 ret = {}
 id = aArgs.pop('id','new')
 op = aArgs.pop('op',None)
 with aCTX.db as db:
  if op == 'update':
   if not id == 'new':
    ret['update'] = db.update_dict('activity_types',aArgs,"id=%s"%id)
   else:
    ret['update'] = db.insert_dict('activity_types',aArgs)
    id = db.get_last_id() if ret['update'] > 0 else 'new'

  if not id == 'new':
   ret['found'] = (db.do("SELECT * FROM activity_types WHERE id = '%s'"%id) > 0)
   ret['data'] = db.get_row()
  else:
   ret['data'] = {'id':'new','type':'Unknown'}
 return ret

#
#
def activity_type_delete(aCTX, aArgs = None):
 """ Function docstring for activity_type_delete. TBD

 Args:
  - id (required)

 Output:
 """
 ret = {}
 with aCTX.db as db:
  ret['delete'] = db.do("DELETE FROM activity_types WHERE id = '%s'"%aArgs['id'])
 return ret

########################################## TASKs ##########################################
#
# The worker task can be carried out anywhere
#
def task_worker(aCTX, aArgs = None):
 """Function instantiate a worker thread with arguments and bind to global worker dictionary

 Args:
  - id (optional)
  - module (required)
  - func (required)
  - args (required)
  - periodic (optional)
  - frequency (optional required)
  - output (optional)

 Output:
  - result
 """
 frequency = aArgs.pop('frequency',None)
 if frequency:
  aCTX.workers.add_periodic(frequency,aArgs)
 else:
  aCTX.workers.add_transient(aArgs)
 return {'res':'TASK_ADDED'}

#
#
def task_add(aCTX, aArgs = None):
 """ Adds a task

 Args:
  - node (required)
  - module (required)
  - func (required)
  - args (required)
  - periodic  (optional) (False: transient, True: periodic, defaults: False)
  - frequency (optional required, seconds for periodic tasks)
  - output (optional)

 Output:
  - result. Boolean
 """
 from json import dumps
 ret = {}
 node = aArgs.pop('node',None)
 aArgs = aArgs
 if aArgs.get('periodic'):
  with aCTX.db as db:
   db.do("INSERT INTO tasks (node_id, module, func, args, frequency,output) VALUES(%s,'%s','%s','%s',%i,%i)"%(aCTX.nodes[node]['id'],aArgs['module'],aArgs['func'],dumps(aArgs['args']),aArgs.get('frequency',300),0 if not aArgs.get('output') else 1))
   aArgs['id'] = 'P%s'%db.get_last_id()
 if node == 'master':
  frequency = aArgs.pop('frequency',None)
  if frequency:
   aCTX.workers.add_periodic(frequency,aArgs)
  else:
   aCTX.workers.add_transient(aArgs)
  ret['status'] = 'ADDED'
 else:
  ret.update(aCTX.rest_call("%s/api/system/task_worker"%aCTX.nodes[node]['url'], aArgs = aArgs, aDataOnly = True))
 return ret

#
#
def task_list(aCTX, aArgs = None):
 """ List tasks

 Args:
  - node (required)

 Output:
 """
 ret = {}
 with aCTX.db as db:
  ret['count'] = db.do("SELECT tasks.*, nodes.node FROM tasks LEFT JOIN nodes ON nodes.id = tasks.node_id WHERE node_id IN (SELECT id FROM nodes WHERE node LIKE '%%%s%%')"%aArgs.get('node',''))
  ret['tasks'] = db.get_rows()
  for task in ret['tasks']:
   task['output'] = (task['output']== 1)
 return ret
