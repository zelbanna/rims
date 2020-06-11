"""Visualize API module. This module provides data for vis.js networking"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

#
#
def list(aCTX, aArgs):
 """ Function produces a list of available map/network entries

 Args:

 Output:
  - maps: list of (id,name)
 """
 ret = {}
 with aCTX.db as db:
  ret['count'] = db.query("SELECT id,name FROM visualize")
  ret['data']  = db.get_rows()
 return ret

#
#
def delete(aCTX, aArgs):
 """ Deletes a map

 Args:
  - id

 Output:
  - deleted
 """
 ret = {}
 with aCTX.db as db:
  ret['deleted'] = db.execute("DELETE FROM visualize WHERE id = %(id)s"%aArgs)
 return ret

#
#
def show(aCTX, aArgs):
 """ Get map data from name or id

 Args:
  - id (optional required)

 Output:
  - name
  - options
  - edges
  - nodes
 """
 ret = {}
 with aCTX.db as db:
  ret['found'] = (db.query("SELECT * FROM visualize WHERE id = %(id)s"%aArgs) > 0)
  if ret['found']:
   from json import loads
   data = db.get_row()
   ret['data'] = {'id':data['id'],'name':data['name']}
   for var in ['nodes','edges','options']:
    try:    ret['data'][var] = loads(data[var])
    except: ret['data'][var] = data[var]
 return ret

#
#
def network(aCTX, aArgs):
 """ Function to view or update information for specific network map id or generate a network map for device id/ip

 Args:
  - id (optional required)
  - op (optional)
  - type (required) 'map/device'
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
 op = args.pop('op',None)
 id = int(args.get('id',0))
 type = args.pop('type','map')
 ret = {}
 with aCTX.db as db:
  if op == 'update':
   for tp in ['options','nodes','edges']:
    args[tp] = dumps(args[tp])
   if id == 'new' or type == 'device':
    ret['insert']= (db.execute("INSERT INTO visualize (name,options,nodes,edges) VALUES('%(name)s','%(options)s','%(nodes)s','%(edges)s')"%args) > 0)
    id = db.get_last_id()
    type  = 'map'
    ret['status']= 'OK'
   else:
    ret['update']= (db.execute("UPDATE visualize SET name='%(name)s',options='%(options)s',nodes='%(nodes)s',edges='%(edges)s' WHERE id = %(id)s"%args) > 0)
    ret['status']= 'OK'

  if type == 'map':
   ret['found'] = (db.query("SELECT * FROM visualize WHERE id = %s"%id) == 1)
   if ret['found']:
    data = db.get_row()
    ret['data'] = {'id':id,'name':data.get('name',"N/A"),'type':'map'}
    try:
     ret['data']['nodes'] = loads(data.get('nodes','[]'))
     ret['data']['edges'] = loads(data.get('edges','[]'))
     ret['data']['options'] = loads(data.get('options','{}'))
    except Exception as e:
     ret['status'] = 'NOT_OK'
     ret['info'] = str(e)
     ret['data']['nodes'] = data.get('nodes','[]')
     ret['data']['edges'] = data.get('edges','[]')
     ret['data']['options'] = data.get('options','{}')

  else:
   nodes = {id:{'processed':False,'distance':0,'connected':0}}
   edges = []
   ret['data'] = {'id':id,'type':'device','options':{'layout':{'randomSeed':2}, 'physics':{'enabled':True }, 'edges':{'length':180}, 'nodes': {'shadow': True, 'font':'14px verdana blue','shape':'image','image':'images/viz-generic.png' }}}
   sql_connected = "SELECT di.device_id AS a_device, di.interface_id AS a_if, di.name AS a_name, di.snmp_index AS a_index, peer.device_id AS b_device, peer.interface_id AS b_if, peer.snmp_index AS b_index, peer.name AS b_name FROM interfaces AS di RIGHT JOIN interfaces AS peer ON di.connection_id = peer.connection_id AND peer.device_id <> {0} LEFT JOIN connections AS dc ON di.connection_id = dc.id WHERE dc.map = 'true' AND di.device_id = {0}"
   for lvl in range(0,args.get('diameter',2)):
    level_ids = list(nodes.keys())
    for current_id in level_ids:
     current_node = nodes[current_id]
     if not current_node['processed']:
      local_nodes = {}
      local_edges = []
      current_node['edges'] = db.query(sql_connected.format(current_id))
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
   db.query("SELECT devices.id, hostname AS label, model, icon AS image FROM devices LEFT JOIN device_types ON devices.type_id = device_types.id WHERE devices.id IN (%s)"%(",".join(str(x) for x in nodes.keys())))
   ret['data']['nodes'] = db.get_rows()
   for node in ret['data']['nodes']:
    nodes[node['id']]['hostname'] = node['label']
   ret['data']['name']  = nodes[id]['hostname']
   ret['data']['edges'] = [{'id':"rims_%(a_if)i_%(b_if)i"%intf,'from':intf['a_device'],'to':intf['b_device'],'smooth':intf['type'],'title':"%s:%s <-> %s:%s"%(nodes[intf['a_device']]['hostname'],intf['a_name'],nodes[intf['b_device']]['hostname'],intf['b_name'])} for intf in edges]
 return ret
