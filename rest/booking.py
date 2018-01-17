"""Module docstring.

Booking REST module

"""
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"

#
# booking(op, device_id, user_id)
#
from ..core.dbase import DB

def modify(aDict):
 ret = {'result':'NOT_OK', 'op':aDict['op']}
 if aDict['op'] == 'book':
  sql = "INSERT INTO bookings (device_id,user_id) VALUES('{}','{}')"
 elif aDict['op'] == 'debook':
  sql = "DELETE FROM bookings WHERE device_id = '{}' AND user_id = '{}'"
 elif aDict['op'] == 'extend':
  sql = "UPDATE bookings SET time_start = NOW() WHERE device_id = '{}' AND user_id = '{}'"
 with DB() as db:
  ret['update'] = db.do(sql.format(aDict['device_id'],aDict['user_id']))
  ret['result'] = 'OK' if ret['update'] > 0 else 'NOT_OK'
 return ret

def list(aDict):
 ret = {}
 with DB() as db:
  ret['xist'] = db.do("SELECT user_id, device_id, DATE_FORMAT(time_start,'%Y-%m-%d %H:%i') as start, NOW() < ADDTIME(time_start, '30 0:0:0.0') AS valid, DATE_FORMAT(ADDTIME(time_start, '30 0:0:0.0'),'%Y-%m-%d %H:%i') as end, devices.hostname, users.alias FROM bookings INNER JOIN devices ON device_id = devices.id INNER JOIN users ON user_id = users.id ORDER by user_id")
  ret['list'] = db.get_rows()
 ret['result'] = 'OK' if ret['xist'] > 0 else 'NOT_OK'
 return ret
