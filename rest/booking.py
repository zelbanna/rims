"""Module docstring.

Booking REST module

"""
__author__ = "Zacharias El Banna"
__version__ = "18.02.09GA"
__status__ = "Production"

#
# booking(op, device_id, user_id)
#
from ..core.dbase import DB

def update(aDict):
 """Function docstring for update TBD

 Args:
  - device_id (required)
  - user_id (required)
  - op (required)

 Extra:
 """
 ret = {'op':aDict['op']}
 if aDict['op'] == 'book':
  sql = "INSERT INTO bookings (device_id,user_id) VALUES('{}','{}')"
 elif aDict['op'] == 'debook':
  sql = "DELETE FROM bookings WHERE device_id = '{}' AND user_id = '{}'"
 elif aDict['op'] == 'extend':
  sql = "UPDATE bookings SET time_start = NOW() WHERE device_id = '{}' AND user_id = '{}'"
 with DB() as db:
  ret['update'] = db.do(sql.format(aDict['device_id'],aDict['user_id']))
  db.do("SELECT alias FROM users WHERE id = '%s'"%aDict['user_id'])
  ret['alias'] = db.get_val('alias')
 return ret

#
#
def list(aDict):
 """Function docstring for list TBD

 Args:

 Extra:
 """
 ret = {}
 with DB() as db:
  ret['xist'] = db.do("SELECT user_id, device_id, DATE_FORMAT(time_start,'%Y-%m-%d %H:%i') as start, NOW() < ADDTIME(time_start, '30 0:0:0.0') AS valid, DATE_FORMAT(ADDTIME(time_start, '30 0:0:0.0'),'%Y-%m-%d %H:%i') as end, devices.hostname, users.alias FROM bookings INNER JOIN devices ON device_id = devices.id INNER JOIN users ON user_id = users.id ORDER by user_id")
  ret['list'] = db.get_rows()
 return ret
