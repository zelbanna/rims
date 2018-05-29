"""Visualize API module. This module provides data for vis.js networks"""
__author__ = "Zacharias El Banna"
__version__ = "18.04.07GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

from sdcp.core.common import DB

#
#
def device(aDict):
 """ Function produces a dictionary tree of interfaces and devices. Build a graph using center device and then add edge interfaces to leaf nodes (devices) and iterate this process for 'diameter' times

 Args:
  - id (optional required)
  - ip (optional required)
  - diameter (optional) integer from 1-3, defaults to 2 to build graph

 Output:
  - interfaces. Local and peer interfaces and interface properties]
  - devices. Encompassed devices, with name, id and interface information
 """
 ret = {'options':{'edges': {'length': 220, 'smooth':{'type': 'dynamic'}}, 'nodes': {'shadow': True, 'font':'14px verdana blue','shape':'image' }}}

 with DB() as db:
  if aDict.get('ip'):
   db.do("SELECT id FROM devices WHERE ip = INET_ATON('%s')"%aDict['ip'])
   id = db.get_val('id')
  else:
   id = int(aDict['id'])
 
  devices = {id:{'processed':False,'interfaces':0,'multipoint':0,'distance':0}}
  interfaces = []

  # Connected and Multipoint
  sql_connected  = "SELECT CAST({0} AS UNSIGNED) AS a_device, dc.id AS a_interface, dc.name AS a_name, dc.snmp_index AS a_index, dc.peer_interface AS b_interface, peer.snmp_index AS b_index, peer.name AS b_name, peer.device_id AS b_device FROM device_interfaces AS dc LEFT JOIN device_interfaces AS peer ON dc.peer_interface = peer.id WHERE dc.peer_interface IS NOT NULL AND dc.device_id = {0}"
  sql_multipoint = "SELECT CAST({0} AS UNSIGNED) AS a_device, dc.id AS a_interface, dc.name AS a_name, dc.snmp_index AS a_index FROM device_interfaces AS dc WHERE dc.multipoint = 1 AND dc.device_id = {0}"
  sql_multi_peer = "SELECT dc.id AS b_interface, dc.snmp_index AS b_index, dc.device_id AS b_device, dc.name AS b_name FROM device_interfaces AS dc WHERE dc.peer_interface = {0}"
  for lvl in range(0,aDict.get('diameter',2)):
   new = {}
   for key,dev in devices.iteritems():
    if not dev['processed']:
     # Find straight interfaces
     dev['interfaces'] += db.do(sql_connected.format(key))
     cons = db.get_rows()

     # Find local multipoint
     dev['multipoint'] += db.do(sql_multipoint.format(key))
     multipoints = db.get_rows()
     # Check 'other side' and add that interface
     for interface in multipoints:
      db.do(sql_multi_peer.format(interface['a_interface']))
      peers = db.get_rows()
      for peer in peers:
       peer.update(interface)
      cons.extend(peers)

     # Deduce if interface is registered (the hard way, as no double dictionary)
     for con in cons:
      seen = devices.get(con['b_device'])
      # If not seen before, add device to process next round (in case already found as new, just overwrite) and save interface. Else, check if processed (then those interfaces are made) if not add interface
      # 1) For straight interface we cover 'back' since the dev is processed
      # 2) For multipoint the other side will (ON SQL) see a straight interface so also covered by processed
      # 3) There is no multipoint to multipoint
      if not seen:
       new[con['b_device']] = {'processed':False,'interfaces':0,'multipoint':0,'distance':lvl + 1}
       interfaces.append(con)
      elif not seen['processed']:
       # exist but interface has not been registered, this covers loops as we set processed last :-)
       interfaces.append(con)

     dev['processed'] = True
   # After all device leafs are processed we can add (net) new devices
   devices.update(new)

  # Now update devices with hostname and type and model, rename fields to fitting info
  db.do("SELECT devices.id, hostname AS label, model, icon AS image FROM devices LEFT JOIN device_types ON devices.type_id = device_types.id WHERE devices.id IN (%s)"%(",".join(str(x) for x in devices.keys())))
  ret['nodes'] = db.get_rows()
 
 for node in ret['nodes']:
  if node['id'] == id:
   ret['name'] = node['label']
   break
 ret['edges']= interfaces

 return ret

#
#
def save(aDict):
 """ Saves config for later visualizer retrieval and edit

 Args:
  - name (required)
  - options (required)
  - nodes (required)
  - edges (required)

 Output:
  - result
 """
 from sdcp.core.logger import log
 name    = aDict['name']
 options = dumps(aDict['options'])
 nodes   = dumps(aDict['nodes'])
 edges   = dumps(aDict['edges'])
 log("args%s"%aDict)
 ret = {}
 try:
  with DB() as db:
   ret['insert'] = db.do("INSERT INTO visualize (name,options,nodes,edges) VALUES('%s','%s','%s','%s') ON DUPLICATE KEY UPDATE id = LAST_INSERT_ID()"%(name,options,nodes,edges))
   ret['id'] = db.get_last_id()
   ret['result'] = 'OK' if ret['insert'] > 0 else 'EXISTED'
 except Exception as err:
  ret['result'] = "ERROR"
  ret['error'] = str(err)
 return ret

#
#
def load(aDict):
 """ Retrieve network config

 Args:
  - id
 
 Output:
  - name
  - options
  - nodes
  - edges
 """
 ret = {}
 with DB() as db:
  ret['xist'] = db.do("SELECT * FROM visualize WHERE id = %s"%aDict['id'])
  data = db.get_row()
  ret['name'] = data.get('name',"")
  for var in ['nodes','edges','options']:
   ret[var] = loads(data.get(var,""))
  ret['result']  = 'OK' if ret['xist'] > 0 else 'NON_EXISTANT'
 return ret
