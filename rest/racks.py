"""Module docstring.

Tools REST module

"""
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"

from ..core.dbase import DB


def list(aDict):
 ret = []
 sort = aDict.get('sort','id')
 with DB() as db:
  db.do("SELECT racks.* from racks ORDER BY %s"%sort)
  ret = db.get_rows()
 return ret


#
# info([id:<rackid>])
def info(aDict):
 ret = {'name': None, 'console':[], 'pdu':[] }
 with DB() as db:
  if aDict.get('id'):
   res = db.do("SELECT name, pdu_1, pdu_2, console FROM racks WHERE id = %s"%aDict['id'])
   select = db.get_row()
   ret['name'] = select.pop('name',"Noname")
   if select.get('console'):
    value = select.pop('console',None)
    db.do("SELECT devices.id, devices.hostname, INET_NTOA(ip) AS ipasc, devicetypes.name AS type FROM devices INNER JOIN devicetypes ON devices.type_id = devicetypes.id WHERE devices.id = %i"%value)
    ret['console'].append(db.get_row())

   if select.get('pdu_1') == select.get('pdu_2'):
    select.pop('pdu_2',None)
   for pdu_no,value in select.iteritems():
    if value:
     db.do("SELECT id, name AS hostname, INET_NTOA(ip) AS ipasc, 'pdu' AS type FROM pdus WHERE id = %i"%value)
     ret['pdu'].append(db.get_row())
  else:
   db.do("SELECT devices.id, devices.hostname, INET_NTOA(ip) AS ipasc, devicetypes.name AS type FROM devices INNER JOIN devicetypes ON devices.type_id = devicetypes.id WHERE devicetypes.base = 'console'")
   ret['console'] = db.get_rows()
   res = db.do("SELECT id, name AS hostname, INET_NTOA(ip) AS ipasc, 'pdu' AS type FROM pdus")
   ret['pdu'] = db.get_rows()

 return ret

#
#
def infra(aDict):
 ret =  {}
 with DB() as db:
  ret['typexist'] = db.do("SELECT id, name, base FROM devicetypes") 
  ret['types']    = db.get_rows()
  if aDict.get('id'):
   if aDict['id'] == 'new':
    ret['rackxist'] = 0
    ret['rack']     = { 'id':'new', 'name':'new-name', 'size':'48', 'pdu_1':None, 'pdu_2':None, 'console':None, 'image_url':None }
   else:
    ret['rackxist'] = db.do("SELECT racks.* FROM racks WHERE id = %s"%aDict['id'])
    ret['rack']     = db.get_row()   
  else:
   ret['rackxist'] = db.do("SELECT racks.* FROM racks")
   ret['racks']    = db.get_rows()
   ret['racks'].append({ 'id':'NULL', 'name':'Not used'})
  ret['consolexist'] = db.do("SELECT devices.id, devices.hostname AS name, ip, INET_NTOA(ip) AS ipasc, devicetypes.name AS type FROM devices INNER JOIN devicetypes ON devices.type_id = devicetypes.id WHERE devicetypes.base = 'console'") 
  ret['consoles']    = db.get_rows()
  ret['consoles'].append({ 'id':'NULL', 'name':'No Console', 'ip':2130706433, 'ipasc':'127.0.0.1' })
  ret['pduxist'] = db.do("SELECT pdus.*, INET_NTOA(ip) as ipasc FROM pdus")
  ret['pdus']    = db.get_rows()
  ret['pdus'].append({ 'id':'NULL', 'name':'No PDU', 'ip':'127.0.0.1', 'slots':0, '0_slot_id':0, '0_slot_name':'', '1_slot_id':0, '1_slot_name':'' })
  ret['dnscachexist'] = db.do("SELECT domains.* FROM domains")
  ret['dnscache']     = db.get_rows()
 return ret

#
#
def devices(aDict):
 ret = {'sort':aDict.get('sort','devices.id')}
 id = aDict['id']
 with DB() as db:
  db.do("SELECT name, size from racks where id = %s"%id)
  ret.update(db.get_row())
  ret['xist']    = db.do("SELECT devices.id, hostname, rackinfo.rack_unit, rackinfo.rack_size, bookings.user_id FROM devices LEFT JOIN bookings ON devices.id = bookings.device_id INNER JOIN rackinfo ON devices.id = rackinfo.device_id WHERE rackinfo.rack_id = %s ORDER BY %s"%(id,ret['sort']))
  ret['devices'] = db.get_rows()
 return ret

#
#
def update(aDict):
 ret = {'id':aDict['id']}
 with DB() as db:
  if aDict['id'] == 'new':
   ret['xist'] = db.do("INSERT into racks (name, size, pdu_1, pdu_2, console, image_url) VALUES ('%s',%s,%s,%s,%s,'%s')"%(aDict['name'],aDict['size'],aDict['pdu_1'],aDict['pdu_2'],aDict['console'],aDict['image_url']))
   ret['id']   = db.get_last_id() 
  else:
   ret['xist'] = db.do("UPDATE racks SET name = '%s', size = %s, pdu_1 = %s, pdu_2 = %s, console = %s, image_url='%s' WHERE id = '%s'"%(aDict['name'],aDict['size'],aDict['pdu_1'],aDict['pdu_2'],aDict['console'],aDict['image_url'],aDict['id']))
 return ret
