"""Racks REST module. Rack infrastructure management, info, listing etc (of PDUs, console servers and devices)"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

#
#
def list(aRT, aArgs):
 """Function docstring for list TBD

 Args:
  - sort (optional)

 Output:
 """
 ret = {}
 sort = aArgs.get('sort','racks.id')
 with aRT.db as db:
  ret['count'] = db.query("SELECT racks.id, racks.name, racks.size, locations.name AS location, locations.id AS location_id FROM racks LEFT JOIN locations ON racks.location_id = locations.id ORDER BY %s"%sort)
  ret['data'] = db.get_rows()
 return ret

#
#
def info(aRT, aArgs):
 """Function docstring for info TBD

 Args:
  - id (required)
  - op (optional)

 Output:
 """
 ret =  {'status':'OK'}
 id = aArgs.pop('id','new')
 op = aArgs.pop('op',None)
 with aRT.db as db:
  if op == 'update':
   if id != 'new':
    ret['update'] = (db.update_dict('racks',aArgs,'id=%s'%id) > 0)
   else:
    ret['update'] = (db.insert_dict('racks',aArgs) == 1)
    id = db.get_last_id() if ret['update'] > 0 else 'new'
  if id != 'new':
   ret['found'] = (db.query("SELECT racks.* FROM racks WHERE id = %s"%id) > 0)
   ret['data'] = db.get_row()
  else:
   ret['data'] = { 'id':'new', 'name':'new-name','location_id':None, 'size':'48', 'pdu_1':None, 'pdu_2':None, 'console':None  }

  sqlbase = "SELECT devices.id, devices.hostname FROM devices INNER JOIN device_types ON devices.type_id = device_types.id WHERE device_types.base = '%s' ORDER BY devices.hostname"
  db.query(sqlbase%('console'))
  ret['consoles'] = db.get_rows()
  ret['consoles'].append({ 'id':'NULL', 'hostname':'No Console'})
  db.query(sqlbase%('pdu'))
  ret['pdus'] = db.get_rows()
  ret['pdus'].append({ 'id':'NULL', 'hostname':'No PDU'})
  db.query("SELECT id, name FROM locations")
  ret['locations'] = db.get_rows()
  ret['locations'].append({'id':'NULL', 'name':'No Location'})
 return ret

#
#
def inventory(aRT, aArgs):
 """Function docstring for inventory TBD

 Args:
  - id (optional)

 Output:
 """
 ret = {'name': None, 'console':[], 'pdu':[] }
 sqlbase = "SELECT devices.id, devices.hostname, dt.name AS type, dt.base AS base FROM devices INNER JOIN device_types AS dt ON devices.type_id = dt.id WHERE %s ORDER BY devices.hostname"

 with aRT.db as db:
  if 'id' in aArgs:
   db.query("SELECT name, pdu_1, pdu_2, console FROM racks WHERE id = '%s'"%aArgs['id'])
   select = db.get_row()
   ret['name'] = select.pop('name',"Noname")
   ids = [str(x) for x in [ select['pdu_1'],select['pdu_2'],select['console']] if x]
   if ids:
    db.query(sqlbase%f"devices.id IN({','.join(ids)})")
    for item in db.get_rows():
     ret[item['base']].append(item)
  else:
   for tp in ['console','pdu']:
    db.query(sqlbase%f"dt.base = '{tp}'")
    ret[tp] = db.get_rows()

 return ret

#
#
def devices(aRT, aArgs):
 """Devices finds device information for rack such that we can build a rack "layout"

 Args:
  - id (required)
  - sort (optional)

 Output:
 """
 ret = {'sort':aArgs.get('sort','devices.id')}
 id = aArgs['id']
 with aRT.db as db:
  db.query("SELECT name, size FROM racks where id = %s"%id)
  ret.update(db.get_row())
  db.query("SELECT devices.id, devices.hostname, ri.rack_unit, ri.rack_size FROM devices INNER JOIN rack_info AS ri ON devices.id = ri.device_id WHERE ri.rack_id = %s ORDER BY %s"%(id,ret['sort']))
  devices = db.get_rows()
  ret['front'] = [dev for dev in devices if dev['rack_unit'] > 0]
  ret['back'] = [dev for dev in devices if dev['rack_unit'] < 0]
 return ret

#
#
def delete(aRT, aArgs):
 """Function docstring for delete TBD

 Args:
  - id (required)

 Output:
 """
 with aRT.db as db:
  deleted = (db.execute("DELETE FROM racks WHERE id = %s"%aArgs['id']) == 1)
 return {'deleted':deleted}
