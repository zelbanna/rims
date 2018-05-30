"""Visualize API module. This module provides data for vis.js networks"""
__author__ = "Zacharias El Banna"
__version__ = "18.04.07GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

from sdcp.core.common import DB

#
#
def list(aDict):
 """ Function produces a list of available maps/networks

 Args:

 Output:
  - maps: list of (id,name)
 """
 ret = {}
 with DB() as db:
  ret['xist'] = db.do("SELECT id,name FROM visualize")
  ret['maps'] = db.get_rows()
 return ret

#
#
def delete(aDict):
 """ Deletes a map

 Args:
  - id
 
 Output:
  - deleted
 """
 ret = {}
 with DB() as db:
  ret['deleted'] = db.do("DELETE FROM visualize WHERE id = %s"%aDict['id'])
 return ret

#
#
def save(aDict):
 """ Saves config for later visualizer retrieval and edit

 Args:
  - id (required)
  - type (required)
  - name (required)
  - options (required)
  - nodes (required)
  - edges (required)

 Output:
  - result
 """
 name    = aDict['name']
 options = dumps(aDict['options'])
 nodes   = dumps(aDict['nodes'])
 edges   = dumps(aDict['edges'])
 ret = {}
 with DB() as db:
  if aDict['type'] == 'network':
   ret['update'] = db.do("UPDATE visualize SET name='%s', options='%s', nodes='%s', edges='%s' WHERE id = %s"%(name,options,nodes,edges,aDict['id']))
   ret['id'] = aDict['id']
   ret['result'] = 'OK' if ret['update'] > 0 else 'NOT_OK'
  else:
   ret['insert'] = db.do("INSERT INTO visualize (name,options,nodes,edges) VALUES('%s','%s','%s','%s') ON DUPLICATE KEY UPDATE id = LAST_INSERT_ID(id), name=name"%(name,options,nodes,edges))
   ret['id'] = db.get_last_id()
   ret['result'] = 'OK' if ret['insert'] == 1 else 'EXISTED'
 return ret

#
#
def info(aDict):
 """ Info function to update information for specific id
 Args:
  - id (required)
  - name (required)
  - options (required)
  - nodes (required)
  - edges (required)

 Output:
  - result
 """
 id = aDict.pop('id',0)
 op = aDict.pop('op',None)
 ret = {'result':None}
 with DB() as db:
  if op == 'update':
   if id == 'new':
    ret['insert']= db.do("INSERT INTO visualize (name,options,nodes,edges) VALUES('%s','%s','%s','%s')"%(aDict['name'],aDict['options'],aDict['nodes'],aDict['edges']))
    id = db.get_last_id()
    ret['result']= 'insert (%s)'%(ret['insert'])
   else:
    ret['update']= db.do("UPDATE visualize SET options='%s',nodes='%s',edges='%s' WHERE id = %s"%(aDict['options'],aDict['nodes'],aDict['edges'],id))
    ret['result']= 'update (%s)'%(ret['update'] > 0)
  ret['xist'] = db.do("SELECT * FROM visualize WHERE id = %s"%id)
  data = db.get_row() if ret['xist'] > 0 else {}
  ret['name'] = data.get('name',"")
  for var in ['nodes','edges','options']:
   ret[var] = loads(data.get(var,'null'))
  ret['id'] = id
 return ret
 

#
#
def network(aDict):
 """ Function produces a dictionary tree of edges and nodes based on saved config

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
  ret['options']['physics'] = {'enabled':True, 'stabilization':{'onlyDynamicEdges':True}}
  ret['options']['nodes']['image'] = 'images/viz-generic.png'
  ret['result']  = 'OK' if ret['xist'] > 0 else 'NON_EXISTANT'
 return ret

#
#
def device(aDict):
 """ Function produces a dictionary tree of edges and nodes based on device id or ip

 Args:
  - id (optional required)
  - ip (optional required)
  - diameter (optional) integer from 1-3, defaults to 2 to build graph

 Output:
  - name
  - options
  - edges
  - nodes  
 """
 ret = {}
 with DB() as db:
  if aDict.get('ip'):
   db.do("SELECT id FROM devices WHERE ip = INET_ATON('%s')"%aDict['ip'])
   id = db.get_val('id')
  else:
   id = int(aDict['id'])
 
  devices = {id:{'processed':False,'interfaces':0,'multipoint':0,'distance':0,'uplink':0}}
  interfaces = []
  ret['options'] = {'edges': {'length': 120, 'smooth':{'type': 'dynamic'}}, 'nodes': {'shadow': True, 'font':'14px verdana blue','shape':'image' }}

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
       new = new_dev.get(con['b_device'],{'processed':False,'interfaces':0,'multipoint':0,'distance':lvl + 1,'uplink':0})
       new['uplink'] += 1
       new_dev[con['b_device']] = new
       new_int.append(con)
      elif not seen['processed']:
       # exist but interface has not been registered, this covers loops as we set processed last :-)
       new_int.append(con)

     dev['processed'] = True
   # After all device leafs are processed we can add (net) new devices
   devices.update(new_dev)
   interfaces.extend(new_int)

  # Now update devices with hostname and type and model, rename fields to fitting info
  db.do("SELECT devices.id, hostname AS label, model, icon AS image FROM devices LEFT JOIN device_types ON devices.type_id = device_types.id WHERE devices.id IN (%s)"%(",".join(str(x) for x in devices.keys())))
  nodes = db.get_rows()
  for node in nodes:
   devices[node['id']]['hostname'] = node['label']

 # Finalize
 ret['nodes'] = nodes
 ret['name']  = devices[id]['hostname']
 ret['edges'] = [{'from':intf['a_device'],'to':intf['b_device'],'title':"%s:%s <-> %s:%s"%(devices[intf['a_device']]['hostname'],intf['a_name'],devices[intf['b_device']]['hostname'],intf['b_name'])} for intf in interfaces]
 print dumps(devices,indent=4)
 return ret
