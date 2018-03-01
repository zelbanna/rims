"""Module docstring.

Tools REST module

"""
__author__ = "Zacharias El Banna"
__version__ = "18.02.09GA"
__status__ = "Production"

from ..core.dbase import DB

#
#
def list(aDict):
 """Function docstring for list TBD

 Args:
  - sort (optional)

 Extra:
 """
 ret = []
 sort = aDict.get('sort','id')
 with DB() as db:
  db.do("SELECT racks.* FROM racks ORDER BY %s"%sort)
  ret = db.get_rows()
 return ret

#
#
def info(aDict):
 """Function docstring for info TBD

 Args:
  - id (optional)

 Extra:
 """
 ret = {'name': None, 'console':[], 'pdu':[] }
 with DB() as db:
  if aDict.get('id'):
   res = db.do("SELECT name, pdu_1, pdu_2, console FROM racks WHERE id = '%s'"%aDict.get('id'))
   select = db.get_row()
   ret['name'] = select.pop('name',"Noname")
   if select.get('pdu_1') == select.get('pdu_2'):
    select.pop('pdu_2',None)
   for type in ['console','pdu_1','pdu_2']:
    if select.get(type):
     value = select.pop(type,None)
     db.do("SELECT devices.id, devices.hostname, INET_NTOA(ip) AS ipasc, devicetypes.name AS type FROM devices INNER JOIN devicetypes ON devices.type_id = devicetypes.id WHERE devices.id = '%s'"%value)
     main,_,_ = type.partition('_')
     ret[main].append(db.get_row())
  else:
   sql = "SELECT devices.id, devices.hostname, INET_NTOA(ip) AS ipasc, devicetypes.name AS type FROM devices INNER JOIN devicetypes ON devices.type_id = devicetypes.id WHERE devicetypes.base = '%s'"
   for type in ['console','pdu']:
    db.do(sql%(type))
    ret[type] = db.get_rows()
 return ret

#
#
def devices(aDict):
 """Function docstring for devices TBD

 Args:
  - id (required)
  - sort (optional)

 Extra:
 """
 ret = {'sort':aDict.get('sort','devices.id')}
 id = aDict['id']
 with DB() as db:
  db.do("SELECT name, size FROM racks where id = %s"%id)
  ret.update(db.get_row())
  ret['xist']    = db.do("SELECT devices.id, hostname, rackinfo.rack_unit, rackinfo.rack_size, bookings.user_id FROM devices LEFT JOIN bookings ON devices.id = bookings.device_id INNER JOIN rackinfo ON devices.id = rackinfo.device_id WHERE rackinfo.rack_id = %s ORDER BY %s"%(id,ret['sort']))
  ret['devices'] = db.get_rows()
 return ret

#
#
def update(aDict):
 """Function docstring for update TBD

 Args:
  - console (required)
  - name (required)
  - image_url (required)
  - pdu_1 (required)
  - pdu_2 (required)
  - id (required)
  - size (required)

 Extra:
 """
 ret = {'id':aDict['id']}
 with DB() as db:
  if aDict['id'] == 'new':
   ret['xist'] = db.do("INSERT into racks (name, size, pdu_1, pdu_2, console, image_url) VALUES ('%s',%s,%s,%s,%s,'%s')"%(aDict['name'],aDict['size'],aDict['pdu_1'],aDict['pdu_2'],aDict['console'],aDict['image_url']))
   ret['id']   = db.get_last_id() 
  else:
   ret['xist'] = db.do("UPDATE racks SET name = '%s', size = %s, pdu_1 = %s, pdu_2 = %s, console = %s, image_url='%s' WHERE id = '%s'"%(aDict['name'],aDict['size'],aDict['pdu_1'],aDict['pdu_2'],aDict['console'],aDict['image_url'],aDict['id']))
 return ret

#
#
def delete(aDict):
 """Function docstring for delete TBD

 Args:
  - id (required)

 Extra:
 """
 with DB() as db:
  deleted = db.do("DELETE FROM racks WHERE id = %s"%aDict['id'])
 return deleted
