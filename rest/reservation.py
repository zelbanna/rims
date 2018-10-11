"""reservation REST module. Provides basic reservation functionality for devices"""
__author__ = "Zacharias El Banna"
__version__ = "5.2GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

#
# reservation(op, device_id, user_id)
#

def update(aDict, aCTX):
 """Function docstring for update TBD

 Args:
  - device_id (required)
  - user_id (required)
  - op (required)

 Output:
 """
 ret = {'op':aDict['op']}
 if aDict['op'] == 'reserve':
  sql = "INSERT INTO reservations (device_id,user_id) VALUES('%(device_id)s','%(user_id)s')"
 elif aDict['op'] == 'drop':
  sql = "DELETE FROM reservations WHERE device_id = '%(device_id)s' AND user_id = '%(user_id)s'"
 elif aDict['op'] == 'extend':
  sql = "UPDATE reservations SET time_start = NOW() WHERE device_id = '%(device_id)s' AND user_id = '%(user_id)s'"
 with aCTX.db as db:
  ret['update'] = db.do(sql%aDict)
  db.do("SELECT alias FROM users WHERE id = '%(user_id)s'"%aDict)
  ret['alias'] = db.get_val('alias')
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
  ret['count'] = db.do("SELECT user_id, device_id, DATE_FORMAT(time_start,'%Y-%m-%d %H:%i') as start, NOW() < ADDTIME(time_start, '14 0:0:0.0') AS valid, DATE_FORMAT(ADDTIME(time_start, '14 0:0:0.0'),'%Y-%m-%d %H:%i') as end, devices.hostname, users.alias {} FROM reservations INNER JOIN devices ON device_id = devices.id INNER JOIN users ON user_id = users.id ORDER by user_id".format('' if not aDict.get('extended') else ", loan, address"))
  ret['data'] = db.get_rows()
  if aDict.get('extended'):
   for res in ret['data']:
    res['loan'] = False if res['loan'] == 0 else True
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
 ret = {}
 with aCTX.db as db:
  db.do("SELECT hostname, vm, dt.name as type FROM devices LEFT JOIN device_types AS dt ON devices.type_id = dt.id LEFT JOIN ipam_addresses AS ia ON devices.ipam_id = ia.id WHERE ia.state != 1")
  ret['devices'] = db.get_rows()
 return ret
