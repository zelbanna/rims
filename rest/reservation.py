"""reservation REST module. Provides basic reservation functionality for devices

Module uses notifier setting to deduce where to 'notify':
-  notifier{node,service} => node_function for service to send data

"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

#
#
def update(aCTX, aArgs = None):
 """Function docstring for update TBD

 Args:
  - device_id (required)
  - user_id (required)
  - days (required)
  - op (required)

 Output:
 """
 ret = {'op':aArgs['op']}
 if aArgs['op'] == 'reserve':
  sql = "INSERT INTO reservations (device_id,user_id,time_end) VALUES('%(device_id)s','%(user_id)s',ADDTIME(NOW(), '%(days)s 0:0:0.0'))"
 elif aArgs['op'] == 'drop':
  sql = "DELETE FROM reservations WHERE device_id = '%(device_id)s' AND user_id = '%(user_id)s'"
 elif aArgs['op'] == 'extend':
  sql = "UPDATE reservations SET time_end = ADDTIME(NOW(), '%(days)s 0:0:0.0') WHERE device_id = '%(device_id)s' AND user_id = '%(user_id)s'"
 with aCTX.db as db:
  ret['update'] = db.do(sql%aArgs)
  db.do("SELECT alias FROM users WHERE id = '%(user_id)s'"%aArgs)
  ret['alias']  = db.get_val('alias')
 return ret

#
#
def list(aCTX, aArgs = None):
 """Function docstring for list TBD

 Args:
  - extended (optional). boolean

 Output:
 """
 ret = {}
 with aCTX.db as db:
  ret['count'] = db.do("SELECT user_id, shutdown, device_id, DATE_FORMAT(time_start,'%Y-%m-%d %H:%i') AS start, DATE_FORMAT(time_end,'%Y-%m-%d %H:%i') AS end, NOW() < time_end AS valid, devices.hostname, users.alias {} FROM reservations INNER JOIN devices ON device_id = devices.id INNER JOIN users ON user_id = users.id ORDER by user_id".format('' if not aArgs.get('extended') else ", loan, address"))
  ret['data'] = db.get_rows()
  for res in ret['data']:
   res['valid'] = (res['valid'] == 1)
   if aArgs.get('extended'):
    res['loan'] = (res['loan'] == 1)
 return ret

#
#
def info(aCTX, aArgs = None):
 """ Function provides reservation info and operation

 Args:
  - device_id (required)
  - op (optional)
  - address (optional)
  - loan (optional)

 Output:

 """
 ret = {}
 op = aArgs.pop('op',None)
 id = aArgs.pop('device_id',None)
 with aCTX.db as db:
  if op == 'update':
   aArgs['loan'] = 0 if not aArgs.get('loan') else 1
   aArgs['shutdown'] = aArgs.get('shutdown',1)
   db.update_dict('reservations',aArgs,"device_id=%s"%id)
  db.do("SELECT device_id, user_id, loan, shutdown, address, alias, DATE_FORMAT(time_end,'%Y-%m-%d %H:%i') AS end, DATE_FORMAT(time_start,'%Y-%m-%d %H:%i') AS start FROM reservations LEFT JOIN users ON users.id = reservations.user_id WHERE device_id = {0}".format(id))
  ret['data'] = db.get_row()
  ret['data']['loan'] = (ret['data']['loan'] == 1)
 return ret

#
#
def expiration_status(aCTX, aArgs = None):
 """ Function notifies users (using notification service@node) about reservation time left. If NOW() - time_end < threashold => service@node.notify('user':user,'message':'Device X reservation will expire in XX seconds')
  Ideally run as a periodic task.

 Args:
  - threshold (optional) defaults to 3600 (seconds)

 Output:
  - result
 """
 from rims.rest.device import control as device_control
 ret = {}
 with aCTX.db as db:
  db.do("SELECT devices.id, vm, res.shutdown, notify, hostname, res.user_id, users.alias, INET_NTOA(ia.ip) AS ip, (res.time_end - NOW()) AS remaining FROM devices LEFT JOIN ipam_addresses AS ia ON devices.ipam_id = ia.id LEFT JOIN reservations AS res ON res.device_id = devices.id LEFT JOIN users ON res.user_id = users.id WHERE (res.time_end - NOW()) < %s"%aArgs.get('threshold',3600))
  ret['hosts'] = db.get_rows()

 notifications = aCTX.settings.get('notifier')
 if notifications:
  notify_node = notifications['node']
  notify_fun  = aCTX.node_function(notifications.get('proxy','master'),notifications['service'],"notify",aHeader = {'X-Log':'true'})

 for host in ret['hosts']:
  if host['remaining'] < 0:
   if host['shutdown'] > 0:
    aCTX.workers.add_function(device_control, aCTX, {'id':host['id'], 'pem_op':'off','pem_id':'all','dev_op':'shutdown' if host['shutdown'] == 1 else 'reset'})
   message = 'Host %(hostname)s reservation expired (reserved by %(alias)s)'
  else:
   message = 'Host %(hostname)s reservation about to expire - remaining time: %(remaining)s (reserved by %(alias)s)'
  if notifications:
   host['notify'] = notify_fun(aArgs = {'message':message%host,'node':notify_node,'user_id':host['user_id']})
 return ret
