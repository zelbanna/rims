"""Racks REST module. Rack infrastructure management, info, listing etc (of PDUs, console servers and devices)"""
__author__ = "Zacharias El Banna"
__version__ = "18.03.16"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

from sdcp.core.common import DB,SC

#
#
def list(aDict):
 """Function docstring for list TBD

 Args:
  - sort (optional)

 Output:
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
  - id (required)
  - op (optional)

 Output:
 """
 ret =  {}
 args = aDict
 id = args.pop('id','new')
 op = args.pop('op',None)
 with DB() as db:
  if op == 'update':
   if not id == 'new':
    ret['update'] = db.update_dict('racks',args,'id=%s'%id)
   else:
    ret['update'] = db.insert_dict('racks',args)
    id = db.get_last_id() if ret['update'] > 0 else 'new'
  if not id == 'new':
   ret['rackxist'] = db.do("SELECT racks.* FROM racks WHERE id = %s"%id)
   ret['rack']     = db.get_row()
  else:
   ret['rack']     = { 'id':'new', 'name':'new-name', 'size':'48', 'pdu_1':None, 'pdu_2':None, 'console':None, 'image_url':None }

  ret['consolexist'] = db.do("SELECT devices.id, devices.hostname, ip, INET_NTOA(ip) AS ipasc, devicetypes.name AS type FROM devices INNER JOIN devicetypes ON devices.type_id = devicetypes.id WHERE devicetypes.base = 'console'")
  ret['consoles']    = db.get_rows()
  ret['consoles'].append({ 'id':'NULL', 'hostname':'No Console', 'ip':2130706433, 'ipasc':'127.0.0.1', 'type':'NULL' })
  ret['pduxist'] = db.do("SELECT devices.id, devices.hostname, ip, INET_NTOA(ip) AS ipasc, devicetypes.name AS type FROM devices INNER JOIN devicetypes ON devices.type_id = devicetypes.id WHERE devicetypes.base = 'pdu' ORDER BY devices.hostname")
  ret['pdus']    = db.get_rows()
  ret['pdus'].append({ 'id':'NULL', 'hostname':'No PDU', 'ip':2130706433, 'ipasc':'127.0.0.1', 'type':'NULL'})
  db.do("SELECT pduinfo.* FROM pduinfo")
  ret['pduinfo'] = db.get_dict('device_id')
  ret['pduinfo']['NULL'] = {'slots':1, '0_slot_id':0, '0_slot_name':'', '1_slot_id':0, '1_slot_name':''}

 from os import listdir, path
 directory = listdir(path.join(SC['generic']['docroot'],"images")) if not SC['generic'].get('rack_image_directory') else SC['generic']['rack_image_directory']
 ret['images'] = [f for f in listdir(directory) if (f[-3:] == "png" or f[-3:] == "jpg") and not (f[:4] == 'btn-' or f[:5] == 'icon-')]
 return ret


#
#
def inventory(aDict):
 """Function docstring for inventory TBD

 Args:
  - id (optional)

 Output:
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
     db.do("SELECT devices.id, devices.hostname, INET_NTOA(ip) AS ipasc, devicetypes.name AS type FROM devices INNER JOIN devicetypes ON devices.type_id = devicetypes.id WHERE devices.id = '%s' ORDER BY devices.hostname"%value)
     main,_,_ = type.partition('_')
     ret[main].append(db.get_row())
  else:
   sql = "SELECT devices.id, devices.hostname, INET_NTOA(ip) AS ipasc, devicetypes.name AS type FROM devices INNER JOIN devicetypes ON devices.type_id = devicetypes.id WHERE devicetypes.base = '%s' ORDER BY devices.hostname"
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

 Output:
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
def delete(aDict):
 """Function docstring for delete TBD

 Args:
  - id (required)

 Output:
 """
 with DB() as db:
  deleted = db.do("DELETE FROM racks WHERE id = %s"%aDict['id'])
 return {'deleted':deleted}
