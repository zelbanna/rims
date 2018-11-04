"""Generic REST module. Provides system and DB interaction for application, settings and resources"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__node__ = 'master'


######################################### APPLICATION ############################################
#
#
def application(aDict, aCTX):
 """Function docstring for application. Using 'portal' settings ('title', 'message' and resource 'id' of start page)

 Args:

 Output:
 """
 from datetime import datetime,timedelta
 """ Default login information """
 ret  = {'message':"Welcome to the Management Portal",'title':'Portal'}
 aDict['node'] = aDict.get('node','master')
 with aCTX.db as db:
  db.do("SELECT parameter,value FROM settings WHERE section = 'portal' AND node = '%s'"%aDict['node'])
  for row in db.get_rows():
   ret[row['parameter']] = row['value']
  db.do("SELECT alias as id, name FROM users ORDER BY name")
  ret['usernames'] = db.get_rows()
 return ret

#
#
def inventory(aDict, aCTX):
 """Function docstring for inventory. Provides inventory info for paticular nodes

 Args:
  - node (required)
  - user_id (optional)

 Output:
 """
 ret = {'navinfo':[]}
 with aCTX.db as db:
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
def menu(aDict, aCTX):
 """Function docstring for menu TBD

 Args:
  - node (required)
  - id (required)

 Output:
 """
 id = int(aDict['id'])
 ret = {}
 with aCTX.db as db:
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
  title_exist = (db.do("SELECT value FROM settings WHERE section = 'portal' AND parameter = 'title' and node = '%s'"%aDict['node']) == 1)
  ret['title']= db.get_val('value') if title_exist else "Portal"
 return ret

#
#
def oui_fetch(aDict, aCTX):
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
   if aDict.get('clear') is True:
    db.do("TRUNCATE oui")
   for line in data.split('\n'):
    if len(line) > 0:
     parts = line.split()
     if len(parts) > 2 and parts[1] == '(hex)':
      oui = parts[0].replace('-',':').lower()
      company = (" ".join(parts[2:]).replace("'",''))[0:60]
      ret['count'] += db.do("INSERT INTO oui(oui,company) VALUES('%s','%s') ON DUPLICATE KEY UPDATE company = '%s'"%(oui,company,company))
   else:
    ret['status'] = 'OK'
 return ret

#
#
def oui_info(aDict, aCTX):
 """ Function retrieves OUI info from database

 Args:
  - oui (required). string, e.g. "AA-BB-00"

 Output:
 """
 ret = {}
 with aCTX.db as db:
  db.do("SELECT * FROM oui WHERE oui = '%s'"%aDict['oui'])
  ret['oui'] = db.get_row()
 return ret

############################################ SETTINGS ########################################
#
#
def settings_list(aDict, aCTX):
 """Function docstring for settings_list TBD

 Args:
  - node (optional)
  - dict (optional)
  - section (optional)
  - user_id (optional)

 Output:
 """
 ret = {'user_id':aDict.get('user_id',"1"),'node':aDict.get('node',aCTX.node) }
 if aDict.get('section'):
  filter = "AND section = '%s'"%aDict.get('section')
  ret['section'] = aDict.get('section')
 else:
  filter = ""
  ret['section'] = 'all'
 with aCTX.db as db:
  ret['count'] = db.do("SELECT * FROM settings WHERE node = '%s' %s ORDER BY section,parameter"%(ret['node'],filter))
  ret['data']  = db.get_dict(aDict.get('dict')) if aDict.get('dict') else db.get_rows()
 return ret

#
#
def settings_info(aDict, aCTX):
 """Function docstring for settings_info TBD

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
 id = aDict.pop('id','new')
 op = aDict.pop('op',None)

 with aCTX.db as db:
  if op == 'update' and not (aDict['section'] == 'system' or aDict['section'] =='nodes'):
   if not id == 'new':
    ret['update'] = db.update_dict('settings',aDict,"id=%s"%id)
   else:
    ret['update'] = db.insert_dict('settings',aDict)
    id = db.get_last_id() if ret['update'] > 0 else 'new'
   # Insert HERE into CTX, or node_call
   if aDict['node'] == 'master':
    section = aCTX.settings.get(aDict['section'],{})
    section[aDict['parameter']] = aDict['value']
    aCTX.settings[aDict['section']] = section
   else:
    aCTX.workers.add_function(aCTX.rest_call,"%s/system/sync/%s"%(aCTX.config['master'],aDict['node']))
  if not id == 'new':
   ret['found'] = (db.do("SELECT * FROM settings WHERE id = '%s'"%id) > 0)
   ret['data']  = db.get_row()
  else:
   ret['data'] = {'id':'new','value':'Unknown','section':aDict.get('section','Unknown'),'parameter':'Unknown'}

 return ret

#
#
def settings_comprehensive(aDict, aCTX):
 """Function docstring for settings_comprehensive TBD

 Args:
  - node (required)
  - dict (optional)
  - section (optional)

 Output:
 """
 ret = {}
 with aCTX.db as db:
  if not aDict.get('section'):
   db.do("SELECT DISTINCT section FROM settings WHERE node='%s'"%aDict['node'])
   rows = db.get_rows()
   sections = [row['section'] for row in rows]
  else:
   sections = [aDict.get('section')]
  for section in sections:
   db.do("SELECT parameter,id,value FROM settings WHERE node = '%s' AND section = '%s'  ORDER BY parameter"%(aDict['node'],section))
   ret[section] = db.get_rows() if not aDict.get('dict') else db.get_dict(aDict.get('dict'))
 return ret

#
#
def settings_delete(aDict, aCTX):
 """Function docstring for settings_delete TBD

 Args:
  - node (required)
  - id (required)

 Output:
 """
 ret = {}
 with aCTX.db as db:
  db.do("SELECT section,parameter FROM settings WHERE id = %(id)s AND node = '%(node)s'"%aDict)
  data = db.get_row()
  ret['deleted'] = db.do("DELETE FROM settings WHERE id = %(id)s AND node = '%(node)s'"%aDict)
 if aDict['node'] == 'master':
  aCTX.settings.get(data['section'],{}).pop(data['parameter'],None)
 else:
  aCTX.workers.add_function(aCTX.rest_call,"%s/system/sync/%s"%(aCTX.config['master'],aDict['node']))
 return ret

################################################# NODE ##############################################
#
#
def node_list(aDict, aCTX):
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
def node_info(aDict, aCTX):
 """Function docstring for node_info TBD

 Args:
  - id (required)
  - op (optional)

 Output:
 """
 ret = {}
 id = aDict.pop('id','new')
 op = aDict.pop('op',None)
 aDict.pop('hostname',None)
 try:
  aDict['device_id'] = int(aDict.get('device_id'))
 except:
  aDict['device_id'] = 'NULL'
 with aCTX.db as db:
  if op == 'update':
   if not id == 'new':
    ret['update'] = db.update_dict('nodes',aDict,'id=%s'%id)
    aCTX.nodes[aDict['node']].update(aDict)
   else:
    ret['update'] = db.insert_dict('nodes',aDict)
    id = db.get_last_id() if ret['update'] > 0 else 'new'
    aCTX.nodes[aDict['node']] = {'id':id,'url':aDict['url']}
  if not id == 'new':
   ret['found'] = (db.do("SELECT nodes.*, devices.hostname FROM nodes LEFT JOIN devices ON devices.id = nodes.device_id WHERE nodes.id = '%s'"%id) > 0)
   ret['data'] = db.get_row()
  else:
   ret['data'] = {'id':'new','node':'Unknown','url':'Unknown','device_id':None,'hostname':None,'system':0}
 return ret

#
#
def node_delete(aDict, aCTX):
 """Function docstring for node_delete TBD

 Args:
  - id (required)

 Output:
 """
 ret = {}
 with aCTX.db as db:
  if db.do("SELECT node FROM nodes WHERE id = %s AND node <> 'master'"%aDict['id']) > 0:
   aCTX.nodes.pop(db.get_val('node'),None)
   ret['delete'] = (db.do("DELETE FROM nodes WHERE id = %s"%aDict['id']) == 1)
  else:
   ret['delete'] = False 
 return ret

#
#
def node_device_mapping(aDict, aCTX):
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
 with aCTX.db as db:
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

#
#
def node_to_api(aDict, aCTX):
 """ Function returns api for a specific node name

 Args:
  - node

 Output:
  - url
 """
 return {'url':aCTX.nodes[aDict['node']]['url']}

############################################# RESOURCES #############################################

#
#
def resources_list(aDict, aCTX):
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
 with aCTX.db as db:
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
def resources_info(aDict, aCTX):
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
 id = aDict.pop('id','new')
 op = aDict.pop('op',None)
 with aCTX.db as db:
  if op == 'update':
   if aDict['icon'] == 'None':
    aDict['icon'] = '../images/icon-na.png'
   if not id == 'new':
    ret['update'] = db.update_dict('resources',aDict,'id=%s'%id)
   else:
    ret['update'] = db.insert_dict('resources',aDict)
    id = db.get_last_id() if ret['update'] > 0 else 'new'

  if not id == 'new':
   db.do("SELECT * FROM resources WHERE id = '%s'"%id)
   ret['data'] = db.get_row()
  else:
   ret['data'] = {'id':'new','node':aDict['node'],'user_id':aDict['user_id'],'title':'Unknown','href':'Unknown','type':None,'icon':None,'private':0,'view':0}
 return ret

#
#
def resources_delete(aDict, aCTX):
 """Function docstring for resources_delete TBD

 Args:
  - id (required)

 Output:
 """
 with aCTX.db as db:
  deleted = db.do("DELETE FROM resources WHERE id = '%s'"%aDict['id'])
 return { 'deleted':deleted }

########################################## THEMES ############################################
#
def themes_list(aDict, aCTX):
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
def users_list(aDict, aCTX):
 """Function docstring for users_list TBD

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
def users_info(aDict, aCTX):
 """Function docstring for users_info TBD

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
 id = aDict.pop('id','new')
 op = aDict.pop('op',None)
 with aCTX.db as db:
  if op == 'update':
   """ Password at least 6 characters """
   if len(aDict.get('password','')) > 5:
    from hashlib import md5
    hash = md5()
    hash.update(aDict['password'].encode('utf-8'))
    aDict['password'] = hash.hexdigest()
   else:
    ret['password_check_failed'] = (not (aDict.pop('password',None) is None))
   if not id == 'new':
    ret['update'] = db.update_dict('users',aDict,"id=%s"%id)
   else:
    ret['update'] = db.insert_dict('users',aDict)
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
def users_delete(aDict, aCTX):
 """Function docstring for users_delete TBD

 Args:
  - id (required)

 Output:
 """
 with aCTX.db as db:
  res = db.do("DELETE FROM users WHERE id = '%s'"%aDict['id'])
 return { 'deleted':res }


################################ SERVERS ##################################
#
#
def server_list(aDict, aCTX):
 """Function docstring for server_list TBD

 Args:
  - type (optional)

 Output:
 """
 ret = {}
 
 with aCTX.db as db:
  db.do("SELECT id, server, node, type FROM servers WHERE %s"%("type = '%s'"%aDict['type'] if aDict.get('type') else "TRUE"))
  ret['servers']= db.get_rows()
 return ret

#
#
def server_info(aDict, aCTX):
 """Function docstring for server_info TBD

 Args:

 Output:
 """
 ret = {}
 id = aDict.pop('id','new')
 op = aDict.pop('op',None)
 with aCTX.db as db:
  db.do("SELECT node FROM nodes")
  ret['nodes'] = [x['node'] for x in db.get_rows()]
  if op == 'update':
   if not id == 'new':
    ret['update'] = db.update_dict('servers',aDict,"id=%s"%id)
    aCTX.servers[id].update(aDict)
   else:
    ret['update'] = db.insert_dict('servers',aDict)
    id = db.get_last_id() if ret['update'] > 0 else 'new'
    aCTX.servers[id] = aDict
  if not id == 'new':
   ret['found'] = (db.do("SELECT * FROM servers WHERE id = '%s'"%id) > 0)
   ret['data'] = db.get_row()
   db.do("SELECT name AS server, base AS type FROM server_types WHERE base = '%s'"%ret['data']['type'])
  else:
   ret['data'] = {'id':'new','node':None,'server':'Unknown','type':None}
   db.do("SELECT DISTINCT base AS type FROM server_types")
   ret['types'] = [x['type'] for x in db.get_rows()]
   db.do("SELECT name AS server, base AS type FROM server_types") 
  ret['servers'] = db.get_rows()

 return ret

#
#
def server_delete(aDict, aCTX):
 """Function docstring for server_delete TBD

 Args:
  - id (required)

 Output:
 """
 ret = {}
 with aCTX.db as db:
  ret['deleted'] = db.do("DELETE FROM servers WHERE id = %s"%aDict['id'])
 return ret

#
#
def server_sync(aDict, aCTX):
 """Server sync sends sync message to server @ node and convey result. What sync means is server dependent

 Args:
  - id (required):

 Output:
 """
 ret = {}
 with aCTX.db as db:
  ret['found'] = (db.do("SELECT node,server FROM servers WHERE id = %s"%aDict['id']) == 1)
  if ret['found']:
   data = db.get_row()
   ret['status'] = aCTX.node_call(data['node'],data['server'],'sync',{'id':aDict['id']})
 return ret

#
#
def server_status(aDict, aCTX):
 """Server status sends status message to server @ node and convey result. What status means is server dependent

 Args:
  - id (required):

 Output:
 """
 ret = {}
 with aCTX.db as db:
  ret['found'] = (db.do("SELECT node,server FROM servers WHERE id = %s"%aDict['id']) == 1)
  if ret['found']:
   data = db.get_row()
   ret['status'] = aCTX.node_call(data['node'],data['server'],'status',{'id':aDict['id']})
 return ret

#
#
def server_restart(aDict, aCTX):
 """Server restart attempt to restart a server @ node.

 Args:
  - id (required))

 Output:
  - result.
 """
 ret = {}
 with aCTX.db as db:
  ret['found'] = (db.do("SELECT node,server FROM servers WHERE id = %s"%aDict['id']) == 1)
  if ret['found']:
   data = db.get_row()
   ret['status'] = aCTX.node_call(data['node'],data['server'],'restart',{'id':aDict['id']})
 return ret

######################################### ACTIVITIES ###########################################
#
#
def activities_list(aDict, aCTX):
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
 with aCTX.db as db:
  db.do("SELECT %s, activity_types.type AS type, DATE_FORMAT(date_time,'%%H:%%i') AS time, DATE_FORMAT(date_time, '%%Y-%%m-%%d') AS date, alias AS user FROM activities LEFT JOIN activity_types ON activities.type_id = activity_types.id LEFT JOIN users ON users.id = activities.user_id ORDER BY date_time DESC LIMIT %s, %s"%(select,ret['start'],ret['end']))
  ret['data'] = db.get_rows()
 return ret

#
#
def activities_info(aDict, aCTX):
 """ Function docstring for activities_info. TBD

 Args:
  - id (required)
  - start (optional)

 Output:
 """
 ret = {}
 id = aDict.pop('id','new')
 op = aDict.pop('op',None)
 with aCTX.db as db:
  db.do("SELECT * FROM activity_types")
  ret['types'] = db.get_rows()
  db.do("SELECT id,alias FROM users ORDER BY alias")
  ret['users'] = db.get_rows()
  if op == 'update':
   aDict['date_time'] ="%s %s:00"%(aDict.pop('date','1970-01-01'),aDict.pop('time','00:01'))

   if not id == 'new':
    ret['update'] = db.update_dict('activities',aDict,'id = %s'%id)
   else:
    ret['update'] = db.insert_dict('activities',aDict)
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
def activities_delete(aDict, aCTX):
 """ Function docstring for activities_delete. TBD

 Args:
  - id (required)

 Output:
 """
 ret = {}
 with aCTX.db as db:
  ret['delete'] = db.do("DELETE FROM activities WHERE id = '%s'"%aDict['id'])
 return ret

#
#
def activities_type_list(aDict, aCTX):
 """ Function docstring for activities_type_list. TBD

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
def activities_type_info(aDict, aCTX):
 """ Function docstring for activities_type_info. TBD

 Args:

 Output:
 """
 ret = {}
 id = aDict.pop('id','new')
 op = aDict.pop('op',None)
 with aCTX.db as db:
  if op == 'update':
   if not id == 'new':
    ret['update'] = db.update_dict('activity_types',aDict,"id=%s"%id)
   else:
    ret['update'] = db.insert_dict('activity_types',aDict)
    id = db.get_last_id() if ret['update'] > 0 else 'new'

  if not id == 'new':
   ret['found'] = (db.do("SELECT * FROM activity_types WHERE id = '%s'"%id) > 0)
   ret['data'] = db.get_row()
  else:
   ret['data'] = {'id':'new','type':'Unknown'}
 return ret

#
#
def activities_type_delete(aDict, aCTX):
 """ Function docstring for activity_type_delete. TBD

 Args:
  - id (required)

 Output:
 """
 ret = {}
 with aCTX.db as db:
  ret['delete'] = db.do("DELETE FROM activity_types WHERE id = '%s'"%aDict['id'])
 return ret

########################################## TASKs ##########################################
#
# The worker task can be carried out anywhere
#
def task_worker(aDict, aCTX):
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
 frequency = aDict.pop('frequency',None)
 if frequency:
  aCTX.workers.add_periodic(frequency,aDict)
 else:
  aCTX.workers.add_transient(aDict)
 return {'res':'TASK_ADDED'}

#
#
def task_add(aDict, aCTX):
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
 node = aDict.pop('node',None)
 aDict = aDict
 if aDict.get('periodic'):
  with aCTX.db as db:
   db.do("INSERT INTO tasks (node_id, module, func, args, frequency,output) VALUES((SELECT id FROM nodes WHERE node = '%s'),'%s','%s','%s',%i,%i)"%(node,aDict['module'],aDict['func'],dumps(aDict['args']),aDict.get('frequency',300),0 if not aDict.get('output') else 1))
   aDict['id'] = 'P%s'%db.get_last_id()
 if node == 'master':
  frequency = aDict.pop('frequency',None)
  if frequency:
   aCTX.workers.add_periodic(frequency,aDict)
  else:
   aCTX.workers.add_transient(aDict)
  ret['status'] = 'ADDED'
 else:
  ret.update(aCTX.rest_call("%s/api/system/task_worker"%aCTX.nodes[node]['url'],aDict)['data'])
 return ret

#
#
def task_list(aDict, aCTX):
 """ List tasks

 Args:
  - node (required)

 Output:
 """
 ret = {}
 with aCTX.db as db:
  ret['count'] = db.do("SELECT tasks.*, nodes.node FROM tasks LEFT JOIN nodes ON nodes.id = tasks.node_id WHERE node_id IN (SELECT id FROM nodes WHERE node LIKE '%%%s%%')"%aDict.get('node',''))
  ret['tasks'] = db.get_rows()
  for task in ret['tasks']:
   task['output'] = (task['output']== 1)
 return ret
