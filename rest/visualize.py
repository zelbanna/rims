"""Visualize API module. This module provides data for vis.js networks"""
__author__ = "Zacharias El Banna"
__version__ = "1.0GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

from zdcp.core.common import DB

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
  ret['count'] = db.do("SELECT id,name FROM visualize")
  ret['maps']  = db.get_rows()
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
  ret['deleted'] = db.do("DELETE FROM visualize WHERE id = %(id)s"%aDict)
 return ret

#
#
def show(aDict):
 """ Get map data from name or id

 Args:
  - id (optional required)
  - name (optional required)

 Output:
  - name
  - options
  - edges
  - nodes
 """
 ret = {}
 with DB() as db:
  search = "id = %(id)s"%aDict if aDict.get('id') else "name = '%(name)s'"%aDict
  ret['found'] = (db.do("SELECT * FROM visualize WHERE %s"%search) > 0)
  if ret['found']:
   data = db.get_row() 
   ret['id']   = data['id']
   ret['name'] = data['name']
   for var in ['nodes','edges','options']:
    ret[var] = loads(data[var])
 return ret

#
#
def network(aDict):
 """ Function to view or update information for specific network map id or generate a network map for device id/ip

 Args:
  - id (optional required)
  - op (optional)
  - type (required) 'map/device'
  - ip (optional required). IP of device, valid only for type 'device'
  - diameter (optional) integer from 1-3, defaults to 2 to build graph for type 'device'
  - name (optional)
  - options (optional)
  - nodes (optional)
  - edges (optional)

 Output:
  - id
  - result
  - type
  - name
  - options
  - nodes
  - edges
 """
 args = dict(aDict)
 op   = args.pop('op',None)
 ret = {'id':args.get('id',0),'type':args.pop('type','map')}
 with DB() as db:
  if op == 'update':
   for type in ['options','nodes','edges']:
    args[type] = dumps(loads(args[type]))
   if ret['id'] == 'new' or ret['type'] == 'device':
    ret['insert']= db.do("INSERT INTO visualize (name,options,nodes,edges) VALUES('%(name)s','%(options)s','%(nodes)s','%(edges)s')"%args)
    ret['id']    = db.get_last_id()
    ret['type']  = 'map'
    ret['result']= 'insert (%s)'%(ret['insert'] > 0)
   else:
    ret['update']= db.do("UPDATE visualize SET name='%(name)s',options='%(options)s',nodes='%(nodes)s',edges='%(edges)s' WHERE id = %(id)s"%args)
    ret['result']= 'update (%s)'%(ret['update'] > 0)

  ret['id'] = int(ret['id'])
  if ret['type'] == 'map':
   ret['found'] = (db.do("SELECT * FROM visualize WHERE id = %s"%ret['id']) > 0)
   data = db.get_row() if ret['found'] else {}
   ret['name'] = data.get('name',"")
   for var in ['nodes','edges','options']:
    ret[var] = loads(data.get(var,'null'))
  else:
   if args.get('ip'):
    db.do("SELECT devices.id FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id WHERE ia.ip = INET_ATON('%(ip)s')"%args)
    ret['id'] = db.get_val('id')

   nodes = {ret['id']:{'processed':False,'edges':0,'multipoint':0,'distance':0,'connected':0}}
   edges = []
   ret['options'] = {'layout':{'randomSeed':2}, 'physics':{'enabled':True }, 'edges':{'length':180}, 'nodes': {'shadow': True, 'font':'14px verdana blue','shape':'image','image':'images/viz-generic.png' }}

   # Connected and Multipoint
   sql_connected  = "SELECT CAST({0} AS UNSIGNED) AS a_device, dc.id AS a_interface, dc.name AS a_name, dc.snmp_index AS a_index, dc.peer_interface AS b_interface, peer.snmp_index AS b_index, peer.name AS b_name, peer.device AS b_device FROM device_interfaces AS dc LEFT JOIN device_interfaces AS peer ON dc.peer_interface = peer.id WHERE dc.peer_interface IS NOT NULL AND dc.device = {0}"
   sql_multipoint = "SELECT CAST({0} AS UNSIGNED) AS a_device, dc.id AS a_interface, dc.name AS a_name, dc.snmp_index AS a_index FROM device_interfaces AS dc WHERE dc.multipoint = 1 AND dc.device = {0}"
   sql_multi_peer = "SELECT dc.id AS b_interface, dc.snmp_index AS b_index, dc.device AS b_device, dc.name AS b_name FROM device_interfaces AS dc WHERE dc.peer_interface = {0}"
   for lvl in range(0,args.get('diameter',2)):
    level_ids = nodes.keys()
    # We cannot iterate as the current data format required that we add each new device found, for each id - otherwise multihomed get's screwed
    for current_id in level_ids:
     current_node = nodes[current_id]
     if not current_node['processed']:
      local_nodes = {}
      local_edges = []
      # Find straight edges
      current_node['edges'] += db.do(sql_connected.format(current_id))
      cons = db.get_rows()
      # Find local multipoint
      current_node['multipoint'] += db.do(sql_multipoint.format(current_id))
      multipoints = db.get_rows()
      # Check 'other side' and find peer interfaces, add local interface info to new 'peer' interfaces and insert into local's list
      for edge in multipoints:
       db.do(sql_multi_peer.format(edge['a_interface']))
       peers = db.get_rows()
       for peer in peers:
        peer.update(edge)
       cons.extend(peers)

      # Deduce if interface is registered (the hard way, as no double dictionaries) by checking 'recursively' if node has been processed else process the connection
      for con in cons:
       to_id   = con['b_device']
       to_node = nodes.get(to_id,{'processed':False,'edges':0,'multipoint':0,'distance':lvl + 1,'connected':[]})
       # If not processed before add device to locally connected nodes and save interface, even if some other node seen this we append our id to make sure we understand if node is multihomed
       # 1) For straight interface we cover 'back' since the dev is/will be processed
       # 2) For multipoint the other side will (through SQL) see the same interface so also covered by processed
       # 3) There is no multipoint to multipoint (!)
       if not to_node['processed']:
        # If first time seen, it's root will become the current id and it should be added to nodes
        if len(to_node['connected']) == 0:
         nodes[to_id] = to_node
        to_node['connected'].append(current_id)
        local_nodes[to_id] = to_node
        local_edges.append(con)

      current_node['processed'] = True
      # Check if from <--> to  connection is multihomed, then make dynamic, else straight, local_nodes function as reduction of set of nodes to inspect
      multihomed = [k for k,v in local_nodes.iteritems() if v['connected'].count(current_id) > 1]
      for con in local_edges:
       con['type'] = {'type':'dynamic'} if con['b_device'] in multihomed else False
      edges.extend(local_edges)

   # Now update nodes with hostname and type and model, rename fields to fitting info
   db.do("SELECT devices.id, hostname AS label, model, icon AS image FROM devices LEFT JOIN device_types ON devices.type_id = device_types.id WHERE devices.id IN (%s)"%(",".join(str(x) for x in nodes.keys())))
   ret['nodes'] = db.get_rows()
   for node in ret['nodes']:
    nodes[node['id']]['hostname'] = node['label']
   ret['name']  = nodes[ret['id']]['hostname']
   ret['edges'] = [{'from':intf['a_device'],'to':intf['b_device'],'smooth':intf['type'],'title':"%s:%s <-> %s:%s"%(nodes[intf['a_device']]['hostname'],intf['a_name'],nodes[intf['b_device']]['hostname'],intf['b_name'])} for intf in edges]
 return ret
