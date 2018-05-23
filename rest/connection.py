"""Connection API module. This is the main device connection module for handling connections and network functions"""
__author__ = "Zacharias El Banna"
__version__ = "18.04.07GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

from sdcp.core.common import DB

#
#
def list(aDict):
 """List connections for a specific device

 Args:
  - device_id (required)
  - sort (optional, default to 'snmp_index')
 Output:
 """
 ret = {}
 id = aDict['device_id']
 with DB() as db:
  sort = aDict.get('sort','snmp_index')
  ret['xist'] = db.do("SELECT id,name,description,snmp_index,peer_connection,multipoint FROM device_connections WHERE device_id = %s ORDER BY %s"%(id,sort))
  ret['data'] = db.get_rows()
  db.do("SELECT hostname FROM devices WHERE id = %s"%id)
  ret['hostname'] = db.get_val('hostname')
 return ret

#
#
def info(aDict):
 """Show or update a specific connection for a device

 Args:
  - id (required)
  - device_id (required)
  - name
  - description
  - snmp_index
  - peer_connection
  - multipoint (0/1)

 Output:
 """
 ret = {}
 args = aDict
 id = args.pop('id','new')
 op = args.pop('op',None)
 with DB() as db:
  if op == 'update':
   # If multipoint there should not be any single peer connection
   args['multipoint'] = aDict.get('multipoint',0)
   if int(args['multipoint']) == 1:
    args['peer_connection'] = None
   if not id == 'new':
    ret['update'] = db.update_dict('device_connections',args,"id=%s"%id)
   else:
    args['manual'] = 1
    ret['insert'] = db.insert_dict('device_connections',args)
    id = db.get_last_id() if ret['insert'] > 0 else 'new'

  if not id == 'new':
   ret['xist'] = db.do("SELECT dc.*, peer.device_id AS peer_device FROM device_connections AS dc LEFT JOIN device_connections AS peer ON dc.peer_connection = peer.id WHERE dc.id = '%s'"%id)
   ret['data'] = db.get_row()
   ret['data'].pop('manual',None)
  else:
   ret['data'] = {'id':'new','device_id':int(aDict['device_id']),'name':'Unknown','description':'Unknown','snmp_index':None,'peer_connection':None,'peer_device':None,'multipoint':0}
 return ret

#
#
def delete(aDict):
 """Function docstring for connection_delete TBD. Delete a certain connection

 Args:
  - id (required)
  - device_id (required)

 Output:
 """
 ret = {}
 id = aDict['id']
 with DB() as db:
  ret['cleared'] = db.do("UPDATE device_connections SET peer_connection = NULL WHERE peer_connection = %s"%id)
  ret['deleted'] = db.do("DELETE FROM device_connections WHERE id = %s"%id)
 return ret

#
#
def link(aDict):
 """Function docstring for connection_link. Link two device interfaces simultaneously to each other, remove old connections before (unless multipoint)

 Args:
  - a_id (required)
  - b_id (required)

 Output:
 """
 ret = {'a':{},'b':{}}
 with DB() as db:
  sql_clear = "UPDATE device_connections SET peer_connection = NULL WHERE peer_connection = %s AND multipoint = 0"
  sql_set   = "UPDATE device_connections SET peer_connection = %s WHERE id = %s AND multipoint = 0"
  ret['a']['clear'] = db.do(sql_clear%(aDict['a_id']))
  ret['b']['clear'] = db.do(sql_clear%(aDict['b_id']))
  ret['a']['set']   = (db.do(sql_set%(aDict['b_id'],aDict['a_id'])) == 1)
  ret['b']['set']   = (db.do(sql_set%(aDict['a_id'],aDict['b_id'])) == 1)
 return ret

#
#
def link_advanced(aDict):
 """Function docstring for connection_link_advanced. Link two IP and SNMP index:s (i.e. physical or logical interfaces) to each other simultaneously

 Args:
  - a_ip (required)
  - a_index (required)
  - b_ip (required)
  - b_index (required)

 Output:
 """
 ret = {'error':None,'a':{},'b':{}}
 with DB() as db:
  sql_dev  ="SELECT id FROM devices WHERE ip = INET_ATON('%s')"
  sql_indx = "SELECT id FROM device_connections WHERE device_id = '%s' AND snmp_index = '%s'"
  for peer in ['a','b']:
   xist = db.do(sql_dev%aDict['%s_ip'%peer])
   if xist > 0:
    ret[peer]['device'] = db.get_val('id')
    xist = db.do(sql_indx%(ret[peer]['device'],aDict['%s_index'%peer]))
    if xist > 0:
     ret[peer]['index'] = db.get_val('id')
    else:
     db.insert_dict('device_connections',{'device_id':ret[peer]['device'],'name':'Unknown','description':'Unknown','snmp_index':aDict['%s_index'%peer]})
     ret[peer]['index'] = db.get_last_id()
   else:
    ret['error'] = "IP not found (%s)"%aDict['%s_ip'%peer]
  if not ret['error']:
   sql_clear = "UPDATE device_connections SET peer_connection = NULL WHERE peer_connection = %s AND multipoint = 0"
   sql_set   = "UPDATE device_connections SET peer_connection = %s WHERE id = %s AND multipoint = 0"
   ret['a']['clear'] = db.do(sql_clear%(aDict['a_id']))
   ret['b']['clear'] = db.do(sql_clear%(aDict['b_id']))
   ret['a']['set']   = (db.do(sql_set%(aDict['b_id'],aDict['a_id'])) == 1)
   ret['b']['set']   = (db.do(sql_set%(aDict['a_id'],aDict['b_id'])) == 1)

 return ret

#
#
def discover(aDict):
 """ Discovery function for detecting interfaces. Will try SNMP to detect all interfaces first.
  Later stage is to do LLDP or similar to populate neighbor information

 Args:
  - device_id (required)
  - delete_nonexisting (optional, boolean)
  - neighbor_discovery (optional, boolean)

 Output:
 """
 ret = {'insert':0,'update':0,'delete':0}
 with DB() as db:
  db.do("SELECT INET_NTOA(ip) AS ipasc, hostname, device_types.name AS type FROM devices LEFT JOIN device_types ON type_id = device_types.id  WHERE devices.id = %s"%aDict['device_id'])
  info = db.get_row()
  db.do("SELECT id, snmp_index, name, description FROM device_connections WHERE device_id = %s"%aDict['device_id'])
  existing = db.get_rows()
  try:
   module  = import_module("sdcp.devices.%s"%(info['type']))
   dev = getattr(module,'Device',lambda x: None)(info['ipasc'])
   interfaces = dev.interfaces()
  except Exception as err:
   ret['error'] = str(err)
  else:
   for con in existing:
    entry = interfaces.pop(con['snmp_index'],None)
    if entry:
     if not ((entry['name'] == con['name']) and (entry['description'] == con['description'])):
      ret['update'] += db.do("UPDATE device_connections SET name = '%s', description = '%s' WHERE id = %s"%(entry['name'][0:24],entry['description'],con['id']))
    elif aDict.get('delete_nonexisting',False) == True:
     ret['delete'] += db.do("DELETE FROM device_connections WHERE id = %s AND manual = 0"%(con['id']))
   for key, entry in interfaces.iteritems():
    args = {'device_id':int(aDict['device_id']),'name':entry['name'][0:24],'description':entry['description'],'snmp_index':key}
    ret['insert'] += db.insert_dict('device_connections',args)
 return ret


def network(aDict):
 """ Function produces a dictionary tree of connections and devices. Build a graph using center device and then add edge connections to leaf nodes (devices) and iterate this process for 'diameter' times

 Args:
  - device_id (required)
  - diameter (optional) integer from 1-3, defaults to 2 to build graph

 Output:
  - connections. Local and peer interfaces and interface properties]
  - devices. Encompassed devices, with name, id and connection information
 """
 devices = {int(aDict['device_id']):{'processed':False,'connections':0,'multipoint':0,'distance':0}}
 connections = []
 with DB() as db:
  # Connected and Multipoint
  sql_connected  = "SELECT CAST({0} AS UNSIGNED) AS local_device, dc.id AS local_interface, dc.name AS local_name, dc.snmp_index AS local_index, dc.peer_connection AS peer_interface, peer.snmp_index AS peer_index, peer.name AS peer_name, peer.device_id AS peer_device FROM device_connections AS dc LEFT JOIN device_connections AS peer ON dc.peer_connection = peer.id WHERE dc.peer_connection IS NOT NULL AND dc.device_id = {0}"
  sql_multipoint = "SELECT CAST({0} AS UNSIGNED) AS local_device, dc.id AS local_interface, dc.name AS local_name, dc.snmp_index AS local_index FROM device_connections AS dc WHERE dc.multipoint = 1 AND dc.device_id = {0}"
  sql_multi_peer = "SELECT dc.id AS peer_interface, dc.snmp_index AS peer_index, dc.device_id AS peer_device, dc.name AS peer_name FROM device_connections AS dc WHERE dc.peer_connection = {0}"
  for lvl in range(0,aDict.get('diameter',2)):
   new = {}
   for key,dev in devices.iteritems():
    if not dev['processed']:
     # Find straight connections
     dev['connections'] += db.do(sql_connected.format(key))
     cons = db.get_rows()

     # Find local multipoint
     dev['multipoint'] += db.do(sql_multipoint.format(key))
     multipoints = db.get_rows()
     # Check 'other side' and add that connection
     for interface in multipoints:
      db.do(sql_multi_peer.format(interface['local_interface']))
      peers = db.get_rows()
      for peer in peers:
       peer.update(interface)
      cons.extend(peers)

     # Deduce if connection is registered (the hard way, as no double dictionary)
     for con in cons:
      seen = devices.get(con['peer_device'])
      # If not seen before, add device to process next round (in case already found as new, just overwrite) and save connection. Else, check if processed (then those connections are made) if not add connection
      # 1) For straight connection we cover 'back' since the dev is processed
      # 2) For multipoint the other side will (ON SQL) see a straight connection so also covered by processed
      # 3) There is no multipoint to multipoint
      if not seen:
       new[con['peer_device']] = {'processed':False,'connections':0,'multipoint':0,'distance':lvl + 1}
       connections.append(con)
      elif not seen['processed']:
       # exist but connection has not been registered, this covers loops as we set processed last :-)
       connections.append(con)

     dev['processed'] = True
   # After all device leafs are processed we can add (net) new devices
   devices.update(new)

  # Now update devices with hostname and type and model
  db.do("SELECT id, hostname FROM devices WHERE id IN (%s)"%(",".join(str(x) for x in devices.keys())))
  names = db.get_rows()
  for name in names:
   devices[name['id']]['hostname'] = name['hostname']

 return {'devices':devices, 'connections':connections}
