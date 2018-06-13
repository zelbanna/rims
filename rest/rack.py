"""Racks REST module. Rack infrastructure management, info, listing etc (of PDUs, console servers and devices)"""
__author__ = "Zacharias El Banna"
__version__ = "1.0GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

from zdcp.core.common import DB

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
   ret['xist'] = db.do("SELECT racks.* FROM racks WHERE id = %s"%id)
   ret['data'] = db.get_row()
  else:
   ret['data'] = { 'id':'new', 'name':'new-name', 'size':'48', 'pdu_1':None, 'pdu_2':None, 'console':None, 'image_url':None }

  sqlbase = "SELECT devices.id, devices.hostname FROM devices INNER JOIN device_types ON devices.type_id = device_types.id WHERE device_types.base = '%s' ORDER BY devices.hostname"
  db.do(sqlbase%('console'))
  ret['consoles'] = db.get_rows()
  ret['consoles'].append({ 'id':'NULL', 'hostname':'No Console'})
  db.do(sqlbase%('pdu'))
  ret['pdus'] = db.get_rows()
  ret['pdus'].append({ 'id':'NULL', 'hostname':'No PDU'})
 
  try:
   from os import listdir, path
   db.do("SELECT parameter,value FROM settings WHERE section = 'generic' AND node = 'master'")
   settings = db.get_dict('parameter')
   directory = listdir(path.join(settings['docroot']['value'],"images")) if not settings.get('rack_image_directory') else settings['rack_image_directory']['value']
   ret['images'] = [f for f in listdir(directory) if (f[-3:] == "png" or f[-3:] == "jpg") and not (f[:4] == 'btn-' or f[:5] == 'icon-')]
  except Exception as err:
   ret['error'] = "Error loading generic -> rack_image_directory: %s"%str(err)
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
 sqlbase = "SELECT devices.id, devices.hostname, INET_NTOA(ia.ip) AS ipasc, device_types.name AS type, device_types.base AS base FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id INNER JOIN device_types ON devices.type_id = device_types.id WHERE %s ORDER BY devices.hostname"

 with DB() as db:
  if aDict.get('id'):
   res = db.do("SELECT name, pdu_1, pdu_2, console FROM racks WHERE id = '%s'"%aDict.get('id'))
   select = db.get_row()
   ret['name'] = select.pop('name',"Noname")
   ids = ",".join([str(x) for x in [ select['pdu_1'],select['pdu_2'],select['console']] if x])
   if len(ids) > 0:
    db.do(sqlbase%("devices.id IN(%s)"%ids))
    for item in db.get_rows():
     ret[item['base']].append(item)
  else:
   for type in ['console','pdu']:
    db.do(sqlbase%("device_types.base = '%s'"%type))
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
