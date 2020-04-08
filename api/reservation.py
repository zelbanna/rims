"""reservation REST module. Provides basic reservation functionality for devices


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
  - alias
 """
 ret = {'op':aArgs['op']}
 if aArgs['op'] == 'reserve':
  sql = "INSERT INTO reservations (device_id,user_id,time_end) VALUES('%(device_id)s','%(user_id)s',NOW() + INTERVAL %(days)s DAY)"
 elif aArgs['op'] == 'delete':
  sql = "DELETE FROM reservations WHERE device_id = '%(device_id)s' AND user_id = '%(user_id)s'"
 elif aArgs['op'] == 'extend':
  sql = "UPDATE reservations SET time_end = NOW() + INTERVAL %(days)s DAY WHERE device_id = '%(device_id)s' AND user_id = '%(user_id)s'"
 with aCTX.db as db:
  ret['result'] = (db.do(sql%aArgs) ==  0)
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
  ret['count'] = db.do("SELECT user_id, shutdown, device_id, DATE_FORMAT(time_start,'%Y-%m-%d %H:%i') AS start, DATE_FORMAT(time_end,'%Y-%m-%d %H:%i') AS end, NOW() < time_end AS valid, devices.hostname, users.alias {} FROM reservations INNER JOIN devices ON device_id = devices.id INNER JOIN users ON user_id = users.id ORDER by user_id".format('' if not aArgs.get('extended') else ", info"))
  ret['data'] = db.get_rows()
  for res in ret['data']:
   res['valid'] = (res['valid'] == 1)
 return ret

#
#
def info(aCTX, aArgs = None):
 """ Function provides reservation info and operation

 Args:
  - device_id (required)
  - op (optional)
  - info (optional)
  - shutdown (optional)

 Output:
  - found (bool)
 """
 ret = {}
 op = aArgs.pop('op',None)
 id = aArgs.pop('device_id',None)
 with aCTX.db as db:
  if op == 'update':
   aArgs.pop('alias',None)
   aArgs['shutdown'] = aArgs.get('shutdown',1)
   db.update_dict('reservations',aArgs,"device_id=%s"%id)
  ret['found'] = (db.do("SELECT device_id, user_id, shutdown, info, alias, DATE_FORMAT(time_end,'%Y-%m-%d %H:%i') AS time_end, DATE_FORMAT(time_start,'%Y-%m-%d %H:%i') AS time_start FROM reservations LEFT JOIN users ON users.id = reservations.user_id WHERE device_id = {0}".format(id)) == 1)
  ret['data'] = db.get_row()
 return ret

#
#
def status(aCTX, aArgs = None):
 """ Function provides reservation status for a device

 Args:
  - device_id (required)

 Output:

 """
 ret = {}
 with aCTX.db as db:
  ret['reservation'] = db.get_row() if (db.do("SELECT users.alias, reservations.user_id, NOW() < time_end AS valid FROM reservations LEFT JOIN users ON reservations.user_id = users.id WHERE device_id = %s"%aArgs['device_id']) > 0) else None
 return ret

#
#
def expiration_status(aCTX, aArgs = None):
 """ Function runs shutdown and kills power when no time left.

 Args:
  - threshold (optional) When to start nagging about defaults to 3600 (seconds)

 Output:
  - result
 """
 from rims.api.device import control as device_control
 ret = {}
 with aCTX.db as db:
  db.do("SELECT devices.id, vm, res.shutdown, hostname, res.user_id, users.alias, INET_NTOA(ia.ip) AS ip, (res.time_end - NOW()) AS remaining FROM devices LEFT JOIN ipam_addresses AS ia ON devices.ipam_id = ia.id LEFT JOIN reservations AS res ON res.device_id = devices.id LEFT JOIN users ON res.user_id = users.id WHERE (res.time_end - NOW()) < %s"%aArgs.get('threshold',3600))
  ret['hosts'] = db.get_rows()
  for host in ret['hosts']:
   if host['remaining'] < 0:
    if host['shutdown'] > 0:
     aCTX.workers.add_function(device_control, aCTX, {'id':host['id'], 'pem_op':'off','pem_id':'all','device_op':'shutdown' if host['shutdown'] == 1 else 'reset'})
    message = 'Host %(hostname)s reservation expired (reserved by %(alias)s)'%host
   else:
    message = 'Host %(hostname)s reservation about to expire - remaining time: %(remaining)s (reserved by %(alias)s)'%host
   db.do("INSERT INTO device_logs (device_id,message) VALUES (%s,'%s')"%(host['id'],message))

 return ret
