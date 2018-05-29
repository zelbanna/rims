"""Visualize API module. This module provides data for vis.js networks"""
__author__ = "Zacharias El Banna"
__version__ = "18.04.07GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

from sdcp.core.common import DB

#
#
def network(aDict):
 """ Function produces a dictionary tree of edges and nodes.
  - For devices it builds a graph using center device and then add edge interfaces to leaf nodes (devices) and iterate this process for 'diameter' times
  - for id or name it will retrieve whatever info is there

 Args:
  - device_id (optional required)
  - device_ip (optional required)
  - diameter (optional) integer from 1-3, defaults to 2 to build graph

 Output:
  - name
  - edges
  - nodes
  - options
  
 """
 ret = {}
 with DB() as db:
  if aDict.get('device_ip'):
   db.do("SELECT id FROM devices WHERE ip = INET_ATON('%s')"%aDict['device_ip'])
   id = db.get_val('id')
  else:
   id = int(aDict['device_id'])
 
  devices = {id:{'processed':False,'interfaces':0,'multipoint':0,'distance':0}}
  interfaces = []
  ret['options'] = {'edges': {'length': 220, 'smooth':{'type': 'dynamic'}}, 'nodes': {'shadow': True, 'font':'14px verdana blue','shape':'image' }}

  # Connected and Multipoint
  sql_connected  = "SELECT CAST({0} AS UNSIGNED) AS a_device, dc.id AS a_interface, dc.name AS a_name, dc.snmp_index AS a_index, dc.peer_interface AS b_interface, peer.snmp_index AS b_index, peer.name AS b_name, peer.device_id AS b_device FROM device_interfaces AS dc LEFT JOIN device_interfaces AS peer ON dc.peer_interface = peer.id WHERE dc.peer_interface IS NOT NULL AND dc.device_id = {0}"
  sql_multipoint = "SELECT CAST({0} AS UNSIGNED) AS a_device, dc.id AS a_interface, dc.name AS a_name, dc.snmp_index AS a_index FROM device_interfaces AS dc WHERE dc.multipoint = 1 AND dc.device_id = {0}"
  sql_multi_peer = "SELECT dc.id AS b_interface, dc.snmp_index AS b_index, dc.device_id AS b_device, dc.name AS b_name FROM device_interfaces AS dc WHERE dc.peer_interface = {0}"
  for lvl in range(0,aDict.get('diameter',2)):
   new_dev = {}
   new_int = []
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
      # If not seen before:
      #  - Add device to process next round and save interface
      #  -- in case already found as new, it means there is already such a connection, find that one and make both interfaces 'dynamic'
      #  - Else, check if processed (then those interfaces are already added) if not add interface
      # 1) For straight interface we cover 'back' since the dev is processed
      # 2) For multipoint the other side will (ON SQL) see a straight interface so also covered by processed
      # 3) There is no multipoint to multipoint
      if not seen:
       new_dev[con['b_device']] = {'processed':False,'interfaces':0,'multipoint':0,'distance':lvl + 1}
       interfaces.append(con)
      elif not seen['processed']:
       # exist but interface has not been registered, this covers loops as we set processed last :-)
       interfaces.append(con)

     dev['processed'] = True
   # After all device leafs are processed we can add (net) new devices
   devices.update(new_dev)

  # Now update devices with hostname and type and model, rename fields to fitting info
  db.do("SELECT devices.id, hostname AS label, model, icon AS image FROM devices LEFT JOIN device_types ON devices.type_id = device_types.id WHERE devices.id IN (%s)"%(",".join(str(x) for x in devices.keys())))
  nodes = db.get_rows()
  for node in nodes:
   devices[node['id']]['hostname'] = node['label']

 # Finalize
 ret['nodes'] = nodes
 ret['name']  = devices[id]['hostname']
 ret['edges'] = [{'from':intf['a_device'],'to':intf['b_device'],'title':"%s:%s <-> %s:%s"%(devices[intf['a_device']]['hostname'],intf['a_name'],devices[intf['b_device']]['hostname'],intf['b_name'])} for intf in interfaces]
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
