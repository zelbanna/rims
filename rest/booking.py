"""Module docstring.

Booking REST module

"""
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"

#
# booking(op, device_id, user_id)
#
def booking(aDict):
 from sdcp.core.dbase import DB
 ret = {'res':'NOT_OK', 'op':aDict['op']}
 if aDict['op'] == 'book':
  sql = "INSERT INTO bookings (device_id,user_id) VALUES('{}','{}')"
 elif aDict['op'] == 'debook':
  sql = "DELETE FROM bookings WHERE device_id = '{}' AND user_id = '{}'"
 elif aDict['op'] == 'extend':
  sql = "UPDATE bookings SET time_start = NOW() WHERE device_id = '{}' AND user_id = '{}'"
 with DB() as db:
  ret['update'] = db.do(sql.format(aDict['device_id'],aDict['user_id']))
  ret['res']    = 'OK' if ret['update'] > 0 else 'NOT_OK'
 return ret
