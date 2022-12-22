"""Master node REST module. Provides system and DB interaction"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)
__node__ = 'master'

from crypt import crypt
from datetime import date
from time import localtime

####################################### SITE ######################################
#
#
def inventory(aRT, aArgs):
 """Function docstring for inventory. Provides inventory info for particular nodes

 Args:
  - node (required)
  - user_id (optional)

 Output:
 """
 ret = {'navinfo':[]}
 if aArgs['node'] == 'master':
  ret.update({'node':True,'users':True})
 with aRT.db as db:
  if 'user_id' in aArgs and (db.query("SELECT alias FROM users WHERE id = %s"%aArgs['user_id']) > 0):
   ret['navinfo'].append(db.get_val('alias'))
 return ret

####################################### NODE ######################################
#
#
def node_list(aRT, aArgs):
 """Function docstring for node_list TBD

 Args:

 Output:
 """
 ret = {}
 with aRT.db as db:
  ret['count'] = db.query("SELECT * FROM nodes")
  ret['data']  = db.get_rows()
 return ret

#
#
def node_info(aRT, aArgs):
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
 with aRT.db as db:
  if op == 'update':
   if id != 'new':
    ret['update'] = (db.update_dict('nodes',aArgs,'id=%s'%id) > 0)
   else:
    ret['update'] = (db.insert_dict('nodes',aArgs) > 0)
    id = db.get_last_id() if ret['update'] else 'new'
  if id != 'new':
   ret['found'] = (db.query("SELECT nodes.*, devices.hostname FROM nodes LEFT JOIN devices ON devices.id = nodes.device_id WHERE nodes.id = '%s'"%id) > 0)
   ret['data'] = db.get_row()
   if ret['found'] and op == 'update':
    node = ret['data']
    for k in list(aRT.nodes.keys()):
     if aRT.nodes[k]['id'] == node['id']:
      aRT.nodes.pop(k,None)
      break
    aRT.nodes[node['node']] = {'id':node['id'],'url':node['url']}
  else:
   ret['data'] = {'id':'new','node':'Unknown','url':'Unknown','device_id':None,'hostname':''}
 return ret

#
#
def node_delete(aRT, aArgs):
 """Function docstring for node_delete TBD

 Args:
  - id (required)

 Output:
  - deleted (bool)
 """
 ret = {}
 with aRT.db as db:
  if (aArgs['id'] != 'new') and db.query("SELECT node FROM nodes WHERE id = %s AND node <> 'master'"%aArgs['id']) > 0:
   aRT.nodes.pop(db.get_val('node'),None)
   ret['deleted'] = (db.execute("DELETE FROM nodes WHERE id = %s"%aArgs['id']) == 1)
  else:
   ret['deleted'] = False
 return ret

#
#
def node_to_api(aRT, aArgs):
 """ Function returns api for a specific node name

 Args:
  - node

 Output:
  - url
 """
 return {'url':aRT.nodes[aArgs['node']]['url']}

####################################### USERS ######################################
#
#
def user_list(aRT, aArgs):
 """Function docstring for user_list TBD

 Args:

 Output:
 """
 ret = {}
 with aRT.db as db:
  ret['count'] = db.query("SELECT id, alias, name, email FROM users ORDER by name")
  ret['data']  = db.get_rows()
 return ret

#
#
def user_encrypt(aRT, aArgs):
 """Function encrypts 'data' with password encryption techniques, providing entire encryption string (method,salt,code)

 Args:
  - data

 Output:
  - encrypted
 """
 ret = {}
 ret['data'] = crypt(aArgs['data'],"$1$%s$"%aRT.config['salt'])
 return ret

#
#
def user_info(aRT, aArgs):
 """Function docstring for user_info TBD

 Args:
  - id (required)
  - op (optional)
  - name (optional)
  - alias (optional)
  - class (optional)
  - email (optional)
  - password (optional)
  - theme (optional)

 Output:
 """
 ret = {}
 id = aArgs.pop('id','new')
 op = aArgs.pop('op',None)
 with aRT.db as db:
  if op == 'update':
   # Password at least 6 characters
   if len(aArgs.get('password','')) > 5:
    aArgs['password'] = crypt(aArgs['password'],'$1$%s$'%aRT.config['salt']).split('$')[3]
   else:
    ret['password_check'] = 'OK' if (aArgs.pop('password',None) is None) else 'NOT_OK'
   if id != 'new':
    ret['update'] = (db.update_dict('users',aArgs,"id=%s"%id) == 1)
   else:
    if 'password' not in aArgs:
     aArgs['password'] = crypt('changeme','$1$%s$'%aRT.config['salt']).split('$')[3]
    ret['update'] = (db.insert_dict('users',aArgs) == 1)
    id = db.get_last_id() if ret['update'] > 0 else 'new'

  if id != 'new':
   ret['found'] = (db.query("SELECT users.* FROM users WHERE id = '%s'"%id) > 0)
   ret['data'] = db.get_row()
   ret['data'].pop('password',None)
  else:
   ret['data'] = {'id':'new','name':'Unknown','alias':'Unknown','class':'user','email':'Unknown','external_id':None,'theme':'light'}
  ret['classes'] = ['user','operator','admin']
 return ret

#
#
def user_delete(aRT, aArgs):
 """Function docstring for user_delete TBD

 Args:
  - id (required)

 Output:
 """
 with aRT.db as db:
  res = (db.execute("DELETE FROM users WHERE id = '%s'"%aArgs['id']) == 1)
 return { 'deleted':res }

################################ SERVERS ##################################
#
#
def server_list(aRT, aArgs):
 """Function docstring for server_list TBD

 Args:
  - type (optional)

 Output:
 """
 ret = {}
 with aRT.db as db:
  db.query("SELECT servers.id, st.service, servers.node, st.type, servers.ui FROM servers LEFT JOIN service_types AS st ON servers.type_id = st.id WHERE %s ORDER BY servers.node"%("type = '%s'"%aArgs['type'] if 'type' in aArgs else "TRUE"))
  ret['data']= db.get_rows()
 return ret

#
#
def server_info(aRT, aArgs):
 """Function docstring for server_info TBD

 Args:
  - id (required)

 Output:
 """
 ret = {}
 id = aArgs.pop('id','new')
 op = aArgs.pop('op',None)
 with aRT.db as db:
  ret['nodes'] = list(aRT.nodes.keys())
  if op == 'update':
   if aArgs.get('ui') == 'None':
    aArgs['ui'] = 'NULL'
   if id != 'new':
    ret['update'] = db.update_dict('servers',aArgs,"id=%s"%id)
   else:
    ret['update'] = db.insert_dict('servers',aArgs)
    id = db.get_last_id() if ret['update'] > 0 else 'new'
  if id != 'new':
   ret['found'] = (db.query("SELECT * FROM servers WHERE id = '%s'"%id) > 0)
   ret['data'] = db.get_row()
   db.query("SELECT id, service, type FROM service_types WHERE type IN (SELECT st.type FROM service_types AS st JOIN servers ON st.id = servers.type_id WHERE servers.id = '%s')"%ret['data']['id'])
   ret['services'] = db.get_rows()
   if op == 'update':
    for x in ret['services']:
     if ret['data']['type_id'] == x['id']:
      aRT.services[int(id)] = {'node':ret['data']['node'],'service':x['service'],'type':x['type']}
      break
  else:
   ret['data'] = {'id':'new','node':None,'type_id':None,'ui':''}
   db.query("SELECT id, service, type FROM service_types WHERE %s"%("type = '%s'"%aArgs['type'] if 'type' in aArgs else "TRUE"))
   ret['services'] = db.get_rows()

 return ret

#
#
def server_delete(aRT, aArgs):
 """Function docstring for server_delete TBD

 Args:
  - id (required)

 Output:
 """
 ret = {}
 with aRT.db as db:
  ret['deleted'] = db.execute("DELETE FROM servers WHERE id = %s"%aArgs['id'])
  aRT.services.pop(int(aArgs['id']),None)
 return ret

#
#
def server_operation(aRT, aArgs):
 """Server status sends 'op' message to server @ node and convey result. What 'op' means is server dependend

 Args:
  - id (required)
  - op (required)

 Output:
 """
 infra = aRT.services[int(aArgs['id'])]
 try:
  ret = aRT.node_function(infra['node'],"services.%s"%infra['service'],aArgs['op'])(aArgs = {'id':aArgs['id']})
 except Exception as e:
  ret = {'status':'NOT_OK','info':str(e)}
 else:
  ret['status'] = ret.get('status','NOT_OK')
 return ret

####################################### ACTIVITIES #######################################
#
#
def activity_list(aRT, aArgs):
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
 with aRT.db as db:
  db.query("SELECT %s, activity_types.type AS type, activity_types.class AS class, DATE_FORMAT(date_time,'%%H:%%i') AS time, DATE_FORMAT(date_time, '%%Y-%%m-%%d') AS date, alias AS user FROM activities LEFT JOIN activity_types ON activities.type_id = activity_types.id LEFT JOIN users ON users.id = activities.user_id ORDER BY date_time DESC LIMIT %s, %s"%(select,ret['start'],ret['end']))
  ret['data'] = db.get_rows()
 return ret

#
#
def activity_daily(aRT, aArgs):
 """ Function docstring for activity_daily.

 Args:
  - date (optional). Default to current date
  - extras (optional). list: 'users'
 Output:
 """
 ret = {}

 if not aArgs.get('date'):
  dt = date.today()
  ret['date'] = "%i-%02i-%02i"%(dt.year,dt.month,dt.day)
 else:
  ret['date'] = aArgs['date']

 with aRT.db as db:
  if 'users' in aArgs.get('extras',[]):
   db.query("SELECT id,alias FROM users ORDER BY alias")
   ret['users'] = {x['id']:x for x in db.get_rows()}
  db.query("SELECT at.id, act.id AS act_id, act.user_id, at.type, act.event FROM activity_types AS at LEFT JOIN activities AS act ON at.id = act.type_id AND (act.type_id = NULL OR DATE(act.date_time) = '%s') WHERE at.class = 'daily'"%ret['date'])
  ret['data'] = db.get_rows()
 return ret

#
#
def activity_info(aRT, aArgs):
 """ Function docstring for activity_info. TBD

 Args:
  - id (required)
  - user_id (optional required)
  - type_id (optional required)
  - event
  - date
  - time

 Output:
 """
 ret = {}
 id = aArgs.pop('id','new')
 op = aArgs.pop('op',None)
 with aRT.db as db:
  extras = aArgs.get('extras',[])
  if 'types' in extras:
   db.query("SELECT * FROM activity_types ORDER BY type ASC")
   ret['types'] = db.get_rows()
  if 'users' in extras:
   db.query("SELECT id,alias FROM users ORDER BY alias")
   ret['users'] = db.get_rows()
  if op == 'update' and all(x in aArgs for x in ['user_id','type_id']):
   aArgs['date_time'] ="%s %s:00"%(aArgs.pop('date','1970-01-01'),aArgs.pop('time','00:01'))

   if id != 'new':
    ret['update'] = (db.update_dict('activities',aArgs,'id = %s'%id) > 0)
   else:
    ret['update'] = (db.insert_dict('activities',aArgs) > 0)
    id = db.get_last_id() if ret['update'] else 'new'

  if id != 'new':
   ret['found'] = (db.query("SELECT id,user_id,type_id, DATE_FORMAT(date_time,'%%H:%%i') AS time, DATE_FORMAT(date_time, '%%Y-%%m-%%d') AS date, event FROM activities WHERE id = %s"%id) > 0)
   ret['data'] = db.get_row()
  else:
   tm = localtime()
   dt = date.today()
   ret['data'] = {'id':'new','user_id':None,'type_id':None,'date':"%i-%02i-%02i"%(dt.year,dt.month,dt.day),'time':"%02i:%02i"%(tm.tm_hour,tm.tm_min),'event':'empty'}
 return ret

#
#
def activity_delete(aRT, aArgs):
 """ Function docstring for activity_delete. TBD

 Args:
  - id (required)

 Output:
 """
 ret = {}
 with aRT.db as db:
  ret['deleted'] = (db.execute("DELETE FROM activities WHERE id = '%s'"%aArgs['id']) == 1)
 return ret

#
#
def activity_type_list(aRT, aArgs):
 """ Function docstring for activity_type_list. TBD

 Args:

 Output:
 """
 ret = {}
 with aRT.db as db:
  db.query("SELECT * FROM activity_types ORDER BY type ASC")
  ret['data'] = db.get_rows()
 return ret

#
#
def activity_type_info(aRT, aArgs):
 """ Function docstring for activity_type_info. TBD

 Args:

 Output:
 """
 ret = {}
 id = aArgs.pop('id','new')
 op = aArgs.pop('op',None)
 with aRT.db as db:
  if op == 'update':
   if id != 'new':
    ret['update'] = db.update_dict('activity_types',aArgs,"id=%s"%id)
   else:
    ret['update'] = db.insert_dict('activity_types',aArgs)
    id = db.get_last_id() if ret['update'] > 0 else 'new'

  if id != 'new':
   ret['found'] = (db.query("SELECT * FROM activity_types WHERE id = '%s'"%id) > 0)
   ret['data'] = db.get_row()
  else:
   ret['data'] = {'id':'new','class':'transient','type':''}
 ret['classes'] = ['transient','daily']
 return ret

#
#
def activity_type_delete(aRT, aArgs):
 """ Function docstring for activity_type_delete. TBD

 Args:
  - id (required)

 Output:
 """
 ret = {}
 with aRT.db as db:
  ret['deleted'] = (db.execute("DELETE FROM activity_types WHERE id = '%s'"%aArgs['id']) == 1)
 return ret
