"""Visualize API module. This module provides data for vis.js networks"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

#
#
def list(aCTX, aArgs = None):
 """ Function produces a list of available maps/networks

 Args:

 Output:
  - maps: list of (id,name)
 """
 ret = {}
 with aCTX.db as db:
  ret['count'] = db.do("SELECT id,name FROM visualize")
  ret['maps']  = db.get_rows()
 return ret

#
#
def delete(aCTX, aArgs = None):
 """ Deletes a map

 Args:
  - id

 Output:
  - deleted
 """
 ret = {}
 with aCTX.db as db:
  ret['deleted'] = db.do("DELETE FROM visualize WHERE id = %(id)s"%aArgs)
 return ret

#
#
def show(aCTX, aArgs = None):
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
 from json import loads
 ret = {}
 with aCTX.db as db:
  search = "id = %(id)s"%aArgs if 'id' in aArgs else "name = '%(name)s'"%aArgs
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
def network(aCTX, aArgs = None):
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
 from builtins import list
 from json import dumps, loads
 args = dict(aArgs)
 op   = args.pop('op',None)
 ret = {'id':args.get('id',0),'type':args.pop('type','map')}
 with aCTX.db as db:
  if op == 'update':
   for type in ['options','nodes','edges']:
    args[type] = dumps(loads(args[type]))
   if ret['id'] == 'new' or ret['type'] == 'device':
    ret['insert']= db.do("INSERT INTO visualize (name,options,nodes,edges) VALUES('%(name)s','%(options)s','%(nodes)s','%(edges)s')"%args)
    ret['id']    = db.get_last_id()
    ret['type']  = 'map'
    ret['status']= 'insert (%s)'%(ret['insert'] > 0)
   else:
    ret['update']= db.do("UPDATE visualize SET name='%(name)s',options='%(options)s',nodes='%(nodes)s',edges='%(edges)s' WHERE id = %(id)s"%args)
    ret['status']= 'update (%s)'%(ret['update'] > 0)

  ret['id'] = int(ret['id'])
  if ret['type'] == 'map':
   ret['found'] = (db.do("SELECT * FROM visualize WHERE id = %s"%ret['id']) > 0)
   data = db.get_row() if ret['found'] else {}
   ret['name'] = data.get('name',"")
   for var in ['nodes','edges','options']:
    ret[var] = loads(data.get(var,'null'))
  else:
   if 'ip' in args:
    db.do("SELECT devices.id FROM devices LEFT JOIN device_interfaces AS di ON devices.id = di.device_id LEFT JOIN ipam_addresses AS ia ON ia.id = di.ipam_id WHERE ia.ip = INET_ATON('%(ip)s')"%args)
    ret['id'] = db.get_val('id')

   nodes = {ret['id']:{'processed':False,'distance':0,'connected':0}}
   edges = []
   ret['options'] = {'layout':{'randomSeed':2}, 'physics':{'enabled':True }, 'edges':{'length':180}, 'nodes': {'shadow': True, 'font':'14px verdana blue','shape':'image','image':'../images/viz-generic.png' }}

   sql_connected = "SELECT di.device_id AS a_device, di.interface_id AS a_if, di.name AS a_name, di.snmp_index AS a_index, peer.device_id AS b_device, peer.interface_id AS b_if, peer.snmp_index AS b_index, peer.name AS b_name FROM device_interfaces AS di RIGHT JOIN device_interfaces AS peer ON di.connection_id = peer.connection_id AND peer.device_id <> {0} LEFT JOIN device_connections AS dc ON di.connection_id = dc.id WHERE dc.map = 1 AND di.device_id = {0}"
   for lvl in range(0,args.get('diameter',2)):
    level_ids = list(nodes.keys())
    for current_id in level_ids:
     current_node = nodes[current_id]
     if not current_node['processed']:
      local_nodes = {}
      local_edges = []
      current_node['edges'] = db.do(sql_connected.format(current_id))
      # Deduce if interface is registered (the hard way, as no double dictionaries) by checking 'recursively' if node has been processed else process the connection
      for con in db.get_rows():
       to_id   = con['b_device']
       to_node = nodes.get(to_id,{'processed':False,'distance':lvl + 1,'connected':[]})
       # If not processed before add device to locally connected nodes and save interface
       if not to_node['processed']:
        # If first time seen, i.e. no connections. it's root connection is the current id and it should be added to nodes
        if len(to_node['connected']) == 0:
         nodes[to_id] = to_node
        to_node['connected'].append(current_id)
        local_nodes[to_id] = to_node
        local_edges.append(con)

      current_node['processed'] = True
      # Check if from <--> to  connection is multihomed, then make dynamic, else straight, local_nodes function as reduction of set of nodes to inspect
      multihomed = [k for k,v in local_nodes.items() if v['connected'].count(current_id) > 1]
      for con in local_edges:
       con['type'] = {'type':'dynamic'} if con['b_device'] in multihomed else False
      edges.extend(local_edges)

   # Now update nodes with hostname and type and model, rename fields to fitting info
   db.do("SELECT devices.id, hostname AS label, model, icon AS image FROM devices LEFT JOIN device_types ON devices.type_id = device_types.id WHERE devices.id IN (%s)"%(",".join(str(x) for x in nodes.keys())))
   ret['nodes'] = db.get_rows()
   for node in ret['nodes']:
    nodes[node['id']]['hostname'] = node['label']
   ret['name']  = nodes[ret['id']]['hostname']
   ret['edges'] = [{'id':"rims_%(a_if)i_%(b_if)i"%intf,'from':intf['a_device'],'to':intf['b_device'],'smooth':intf['type'],'title':"%s:%s <-> %s:%s"%(nodes[intf['a_device']]['hostname'],intf['a_name'],nodes[intf['b_device']]['hostname'],intf['b_name'])} for intf in edges]
 return ret
