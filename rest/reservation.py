"""reservation REST module. Provides basic reservation functionality for devices

Module uses notifier setting to deduce where to 'notify':
-  notifier{node,server} => node_call for server to send data

"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

#
#
def update(aDict, aCTX):
 """Function docstring for update TBD

 Args:
  - device_id (required)
  - user_id (required)
  - days (required)
  - op (required)

 Output:
 """
 ret = {'op':aDict['op']}
 if aDict['op'] == 'reserve':
  sql = "INSERT INTO reservations (device_id,user_id,time_end) VALUES('%(device_id)s','%(user_id)s',ADDTIME(NOW(), '%(days)s 0:0:0.0'))"
 elif aDict['op'] == 'drop':
  sql = "DELETE FROM reservations WHERE device_id = '%(device_id)s' AND user_id = '%(user_id)s'"
 elif aDict['op'] == 'extend':
  sql = "UPDATE reservations SET time_end = ADDTIME(NOW(), '%(days)s 0:0:0.0') WHERE device_id = '%(device_id)s' AND user_id = '%(user_id)s'"
 with aCTX.db as db:
  ret['update'] = db.do(sql%aDict)
  db.do("SELECT alias FROM users WHERE id = '%(user_id)s'"%aDict)
  ret['alias']  = db.get_val('alias')
 return ret

#
#
def list(aDict, aCTX):
 """Function docstring for list TBD

 Args:
  - extended (optional). boolean

 Output:
 """
 ret = {}
 with aCTX.db as db:
  ret['count'] = db.do("SELECT user_id, device_id, DATE_FORMAT(time_start,'%Y-%m-%d %H:%i') AS start, DATE_FORMAT(time_end,'%Y-%m-%d %H:%i') AS end, NOW() < time_end AS valid, devices.hostname, users.alias {} FROM reservations INNER JOIN devices ON device_id = devices.id INNER JOIN users ON user_id = users.id ORDER by user_id".format('' if not aDict.get('extended') else ", loan, address"))
  ret['data'] = db.get_rows()
  for res in ret['data']:
   res['valid'] = (res['valid'] == 1)
   if aDict.get('extended'):
    res['loan'] = (res['loan'] == 1)
 return ret

#
#
def expiration_check(aDict, aCTX):
 """ Function notifies users (using notification service@node) about reservation time left. If NOW() - time_end < threashold => service@node.notify('user':user,'message':'Device X reservation will expire in XX seconds')
  Ideally run as a periodic task.

 Args:
  - service
  - node
  - threshold (in seconds)

 Output:
  - result
 """
 ret = {}
 with aCTX.db as db:
  db.do("SELECT hostname, INET_NTOA(ia.ip) AS ip, NOW() - res.time_end AS remaining FROM devices LEFT JOIN ipam_addresses AS ia ON devices.ipam_id = ia.id LEFT JOIN reservations AS res ON res.device_id = devices.id WHERE NOW() - res.time_end < %s"%aDict['threshold'])
  ret['hosts'] = db.get_rows()
 notifier = aCTX.settings.get('notifier')
 if notifier:
  for res in ret['hosts']:
   res = aCTX.node_call(notifier['node'],notifier['server'],"notify", aArgs = {'message':'Host %s expiration'%res['hostname']}, aHeader = {'X-Log':'true'})
   print(res)
 return ret

#
#
def shutdown(aDict, aCTX):
 """ Function retrieves devices and VMs and shut them down if it can, add a delay and then shutdown power (type 1)
  - For devices not in state up we will do PEM shutdown only (type 2)
  - For VMs there will not be much done ATM as there is no hypervisor correlation yet (type 3)

  Args:

  Output:
 """
 from importlib import import_module
 ret = {}
 modules = {}

 def __shutdown(aInfo,aDevice):
  print("Device shutdown:%s"%aDevice.shutdown())
  return True

 with aCTX.db as db:
  db.do("SELECT hostname, INET_NTOA(ia.ip) AS ip, vm, dt.name as type FROM devices LEFT JOIN device_types AS dt ON devices.type_id = dt.id LEFT JOIN ipam_addresses AS ia ON devices.ipam_id = ia.id LEFT JOIN reservations ON reservations.device_id = devices.id WHERE devices.shutdown > 0 AND reservations.time_end IS NULL OR reservations.time_end < NOW()")
  ret['devices'] = db.get_rows()
 for info in ret['devices']:
  try:
   module = modules.get(info['type'])
   if not module:
    module = import_module("rims.devices.%s"%info['type'])
    modules[info['type']] = module
   device = getattr(module,'Device',lambda x: None)(info['ip'],aCTX)
   __shutdown(info,device)
  except Exception as e:
   info['error'] = str(e)
 return ret
