"""Master node REST module. Provides system and DB interaction"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__node__ = 'master'

####################################### SITE ######################################
#
#
def inventory(aCTX, aArgs = None):
 """Function docstring for inventory. Provides inventory info for particular nodes

 Args:
  - node (required)
  - user_id (optional)

 Output:
 """
 ret = {'navinfo':[]}
 if aArgs['node'] == 'master':
  ret.update({'node':True,'users':True})
  ret['logs'] = [k for k,v in aCTX.nodes.items()]
 else:
  ret['logs']  = [aArgs['node']]
 with aCTX.db as db:
  if 'user_id' in aArgs:
   db.do("SELECT alias FROM users WHERE id = %s"%aArgs['user_id'])
   ret['navinfo'].append(db.get_val('alias'))

 ret['services'] = aCTX.config.get('services',[])

 return ret

########################################## OUI ##########################################
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
 ret = {'new':0}
 try:
  req = Request(aCTX.config['oui']['location'])
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
      ret['new'] += db.do("INSERT INTO oui(oui,company) VALUES(%d,'%s') ON DUPLICATE KEY UPDATE company = '%s'"%(oui,company,company))
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

####################################### NODE ######################################
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
    aCTX.nodes[node['node']] = {'id':node['id'],'url':node['url']}
  else:
   ret['data'] = {'id':'new','node':'Unknown','url':'Unknown','device_id':None,'hostname':None}
 return ret

#
#
def node_delete(aCTX, aArgs = None):
 """Function docstring for node_delete TBD

 Args:
  - id (required)

 Output:
  - deleted (bool)
 """
 ret = {}
 with aCTX.db as db:
  if (aArgs['id'] != 'new') and db.do("SELECT node FROM nodes WHERE id = %s AND node <> 'master'"%aArgs['id']) > 0:
   aCTX.nodes.pop(db.get_val('node'),None)
   ret['deleted'] = (db.do("DELETE FROM nodes WHERE id = %s"%aArgs['id']) == 1)
  else:
   ret['deleted'] = False
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

####################################### USERS ######################################
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
  - alias (optional)
  - email (optional)
  - password (optional)
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
   if not id == 'new':
    ret['update'] = db.update_dict('users',aArgs,"id=%s"%id)
   else:
    if not 'password' in aArgs:
     aArgs['password'] = crypt('changeme','$1$%s$'%aCTX.config['salt']).split('$')[3]
    ret['update'] = db.insert_dict('users',aArgs)
    id = db.get_last_id() if ret['update'] > 0 else 'new'

  if not id == 'new':
   ret['found'] = (db.do("SELECT users.* FROM users WHERE id = '%s'"%id) > 0)
   ret['data'] = db.get_row()
   ret['data'].pop('password',None)
  else:
   ret['data'] = {'id':'new','name':'Unknown','alias':'Unknown','email':'Unknown','external_id':None,'theme':'blue'}
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
  res = (db.do("DELETE FROM users WHERE id = '%s'"%aArgs['id']) == 1)
 return { 'deleted':res }

#
#
def token_maintenance(aCTX, aArgs = None):
 """Function manage tokens

 Args:

 Output:
 """
 ret = {}
 with aCTX.db as db:
  ret['deleted'] = db.do("DELETE FROM user_tokens WHERE created + INTERVAL 5 DAY < NOW()")
 return ret

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
  db.do("SELECT servers.id, st.service, servers.node, st.type, servers.ui FROM servers LEFT JOIN service_types AS st ON servers.type_id = st.id WHERE %s ORDER BY servers.node"%("type = '%s'"%aArgs['type'] if 'type' in aArgs else "TRUE"))
  ret['data']= db.get_rows()
 return ret

#
#
def server_info(aCTX, aArgs = None):
 """Function docstring for server_info TBD

 Args:
  - id (required)

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
   else:
    ret['update'] = db.insert_dict('servers',aArgs)
    id = db.get_last_id() if ret['update'] > 0 else 'new'
  if not id == 'new':
   ret['found'] = (db.do("SELECT * FROM servers WHERE id = '%s'"%id) > 0)
   ret['data'] = db.get_row()
   db.do("SELECT id, service, type FROM service_types WHERE type IN (SELECT st.type FROM service_types AS st JOIN servers ON st.id = servers.type_id WHERE servers.id = '%s')"%ret['data']['id'])
   ret['services'] = db.get_rows()
   if op == 'update':
    for x in ret['services']:
     if ret['data']['type_id'] == x['id']:
      aCTX.services[int(id)] = {'node':ret['data']['node'],'service':x['service'],'type':x['type']}
      break
  else:
   ret['data'] = {'id':'new','node':None,'type_id':None,'ui':''}
   db.do("SELECT id, service, type FROM service_types WHERE %s"%("type = '%s'"%aArgs['type'] if 'type' in aArgs else "TRUE"))
   ret['services'] = db.get_rows()

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
  aCTX.services.pop(int(aArgs['id']),None)
 return ret

#
#
def server_sync(aCTX, aArgs = None):
 """Server sync sends sync message to server @ node and convey result. What sync means is server dependent

 Args:
  - id (required):

 Output:
 """
 server = aCTX.services[int(aArgs['id'])]
 try:
  ret = aCTX.node_function(server['node'],server['service'],'sync')(aArgs = {'id':aArgs['id']})
  ret['status'] = ret.get('status','NOT_OK')
 except Exception as e:
  ret = {'status':'NOT_OK','info':str(e)}
 return ret

#
#
def server_status(aCTX, aArgs = None):
 """Server status sends status message to server @ node and convey result. What status means is server dependent

 Args:
  - id (required):

 Output:
 """
 server = aCTX.services[int(aArgs['id'])]
 try:
  ret = aCTX.node_function(server['node'],server['service'],'status')(aArgs = {'id':aArgs['id']})
  ret['status'] = ret.get('status','NOT_OK')
 except Exception as e:
  ret = {'status':'NOT_OK','info':str(e)}
 return ret

#
#
def server_restart(aCTX, aArgs = None):
 """Server restart attempt to restart a server @ node.

 Args:
  - id (required))

 Output:
  - result.
 """
 server = aCTX.services[int(aArgs['id'])]
 try:
  ret = aCTX.node_function(server['node'],server['service'],'restart')(aArgs = {'id':aArgs['id']})
  ret['status'] = ret.get('status','NOT_OK')
 except Exception as e:
  ret = {'status':'NOT_OK','info':str(e)}
 return ret

####################################### ACTIVITIES #######################################
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
  - user_id (optional required)
  - type_id (optional required)

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
  ret['deleted'] = (db.do("DELETE FROM activities WHERE id = '%s'"%aArgs['id']) == 1)
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
  ret['deleted'] = (db.do("DELETE FROM activity_types WHERE id = '%s'"%aArgs['id']) == 1)
 return ret

###################################### TASKs ######################################
#
#
def task_add(aCTX, aArgs = None):
 """ Adds a task

 Args:
  - node (required)
  - module (required)
  - function (required)
  - args (required)
  - frequency (optional required, > 0 seconds for periodic tasks)
  - output (optional)
  - on_boot (optional). For transients, indicate if this should be run every boot

 Output:
  - status.
 """
 from json import dumps
 ret = {}
 node = aArgs.pop('node',None)
 freq = aArgs.get('frequency',0)
 if freq > 0 or aArgs.get('on_boot'):
  with aCTX.db as db:
   db.do("INSERT INTO tasks (node_id, module, function, args, frequency, output) VALUES(%s,'%s','%s','%s',%i,'%s')"%(aCTX.nodes[node]['id'],aArgs['module'],aArgs['function'],dumps(aArgs['args']),freq,'true' if aArgs.get('output',False) else 'false'))
 # activate
 if node == 'master':
  aCTX.workers.add_task(aArgs['module'],aArgs['function'],freq, output = aArgs.get('output',False), args = aArgs.get('args',{}))
  ret['status'] = 'OK'
 else:
  try:   ret.update(aCTX.rest_call("%s/api/system/worker?node=%s"%(aCTX.nodes[node]['url'],node), aArgs = aArgs, aDataOnly = True))
  except Exception as e:
   ret['status'] = 'NOT_OK'
   ret['info'] = str(e)
  else:  ret['status'] = 'OK'
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
  ret['data'] = db.get_rows()
  for task in ret['data']:
   task['output'] = (task['output']== 'true')
 return ret

#
#
def task_delete(aCTX, aArgs = None):
 """ Delete a task

 Args:
  - id (required). List of id to delete

 Output:
 """
 ret = {}
 with aCTX.db as db:
  ret['deleted'] = db.do("DELETE FROM tasks WHERE id IN (%s)"%",".join(aArgs['id']))
 return ret
