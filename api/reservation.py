"""reservation REST module. Provides basic reservation functionality for devices"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

#
#
def list(aRT, aArgs):
 """Function docstring for list TBD

 Args:
  - extended (optional). boolean

 Output:
 """
 ret = {}
 with aRT.db as db:
  ret['count'] = db.query("SELECT user_id, shutdown, device_id, DATE_FORMAT(time_start,'%Y-%m-%d %H:%i') AS start, DATE_FORMAT(time_end,'%Y-%m-%d %H:%i') AS end, NOW() < time_end AS valid, devices.hostname, users.alias {} FROM reservations INNER JOIN devices ON device_id = devices.id INNER JOIN users ON user_id = users.id ORDER by user_id".format('' if not aArgs.get('extended') else ", info"))
  ret['data'] = db.get_rows()
  for res in ret['data']:
   res['valid'] = (res['valid'] == 1)
 return ret

#
#
def new(aRT, aArgs):
 """ Function creates a new reservation

 Args:
 - device_id (required)
 - info (optional)
 - shutdown (optional)
 - days (optional)

 Output:
 - status
 """
 ret = {}
 with aRT.db as db:
  aArgs['shutdown'] = aArgs.get('shutdown','no')
  try: db.insert_dict('reservations',aArgs)
  except: ret = 'NOT_OK'
  else:
   ret['status'] = 'OK' if (db.execute("UPDATE reservations SET time_end = NOW() + INTERVAL %i DAY WHERE device_id = %i"%(aArgs.get('days',14),aArgs['device_id'])) > 0) else 'NOT_OK'
 return ret

#
#
def delete(aRT, aArgs):
 """ Function creates a new reservation

 Args:
 - device_id (required)
 - user_id (required)

 Output:
 - status
 """
 ret = {}
 with aRT.db as db:
  ret['deleted'] = (db.execute("DELETE FROM reservations WHERE device_id = %s"%aArgs['device_id']) > 0)
 return ret

#
#
def info(aRT, aArgs):
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
 with aRT.db as db:
  if op == 'update':
   aArgs.pop('alias',None)
   aArgs['shutdown'] = aArgs.get('shutdown','no')
   db.update_dict('reservations',aArgs,"device_id=%s"%id)
  ret['found'] = (db.query("SELECT device_id, user_id, shutdown, info, alias, DATE_FORMAT(time_end,'%Y-%m-%d %H:%i') AS time_end, DATE_FORMAT(time_start,'%Y-%m-%d %H:%i') AS time_start FROM reservations LEFT JOIN users ON users.id = reservations.user_id WHERE device_id = {0}".format(id)) == 1)
  ret['data'] = db.get_row()
 return ret

#
#
def extend(aRT, aArgs):
 """ Function extends reservation for device

 Args:
 - device_id (required)
 - days (optional)
 Output:
 - status
 """
 ret = {}
 aArgs['days'] = aArgs.get('days',5)
 with aRT.db as db:
  ret['status'] = 'OK' if (db.execute("UPDATE reservations SET time_end = NOW() + INTERVAL %(days)s DAY WHERE device_id = %(device_id)s"%aArgs) == 1) else 'NOT_OK'
 return ret
#
#
def expiration_status(aRT, aArgs):
 """ Function runs shutdown and kills power when no time left.

 Args:
  - threshold (optional) When to start nagging about defaults to 3600 (seconds)

 Output:
  - result
 """
 from rims.api.device import control as device_control
 ret = {}
 with aRT.db as db:
  db.query("SELECT devices.id, res.shutdown, devices.hostname, res.user_id, users.alias, (res.time_end - NOW()) AS remaining FROM devices LEFT JOIN reservations AS res ON res.device_id = devices.id LEFT JOIN users ON res.user_id = users.id WHERE (res.time_end - NOW()) < %s"%aArgs.get('threshold',3600))
  ret['hosts'] = db.get_rows()
  for host in ret['hosts']:
   if host['remaining'] < 0:
    if host['shutdown'] > 0:
     aRT.queue_function(device_control, aRT, {'id':host['id'], 'pem_op':'off','pem_id':'all','device_op':'shutdown' if host['shutdown'] == 1 else 'reset'})
    message = 'Host %(hostname)s reservation expired (reserved by %(alias)s)'%host
   else:
    message = 'Host %(hostname)s reservation about to expire - remaining time: %(remaining)s (reserved by %(alias)s)'%host
   aRT.log(message)

 return ret
