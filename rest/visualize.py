"""Visualize API module. This module provides data for vis.js networks"""
__author__ = "Zacharias El Banna"
__version__ = "18.05.31GA"
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
  search = "id = %s"%aDict['id'] if aDict.get('id') else "name = '%s'"%aDict['name']
  ret['xist'] = db.do("SELECT * FROM visualize WHERE %s"%search)
  if ret['xist'] > 0:
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
 ret = {'id':args.pop('id',0),'type':args.pop('type','map')}
 with DB() as db:
  if op == 'update':
   if ret['id'] == 'new' or ret['type'] == 'device':
    ret['insert']= db.do("INSERT INTO visualize (name,options,nodes,edges) VALUES('%s','%s','%s','%s')"%(args['name'],args['options'],args['nodes'],args['edges']))
    ret['id']    = db.get_last_id()
    ret['type']  = 'map'
    ret['result']= 'insert (%s)'%(ret['insert'])
   else:
    ret['update']= db.do("UPDATE visualize SET name='%s',options='%s',nodes='%s',edges='%s' WHERE id = %s"%(args['name'],args['options'],args['nodes'],args['edges'],ret['id']))
    ret['result']= 'update (%s)'%(ret['update'] > 0)

  ret['id'] = int(ret['id'])
  if ret['type'] == 'map':
   ret['xist'] = db.do("SELECT * FROM visualize WHERE id = %s"%ret['id'])
   data = db.get_row() if ret['xist'] > 0 else {}
   ret['name'] = data.get('name',"")
   for var in ['nodes','edges','options']:
    ret[var] = loads(data.get(var,'null'))
  else:
   if args.get('ip'):
    db.do("SELECT devices.id FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id WHERE ia.ip = INET_ATON('%s')"%args['ip'])
    ret['id'] = db.get_val('id')
 
   devices = {ret['id']:{'processed':False,'interfaces':0,'multipoint':0,'distance':0,'uplink':0}}
   interfaces = []
   ret['options'] = {'layout':{'randomSeed':2}, 'physics':{'enabled':True }, 'edges':{'length':180}, 'nodes': {'shadow': True, 'font':'14px verdana blue','shape':'image','image':'images/viz-generic.png' }}

   # Connected and Multipoint
   sql_connected  = "SELECT CAST({0} AS UNSIGNED) AS a_device, dc.id AS a_interface, dc.name AS a_name, dc.snmp_index AS a_index, dc.peer_interface AS b_interface, peer.snmp_index AS b_index, peer.name AS b_name, peer.device_id AS b_device FROM device_interfaces AS dc LEFT JOIN device_interfaces AS peer ON dc.peer_interface = peer.id WHERE dc.peer_interface IS NOT NULL AND dc.device_id = {0}"
   sql_multipoint = "SELECT CAST({0} AS UNSIGNED) AS a_device, dc.id AS a_interface, dc.name AS a_name, dc.snmp_index AS a_index FROM device_interfaces AS dc WHERE dc.multipoint = 1 AND dc.device_id = {0}"
   sql_multi_peer = "SELECT dc.id AS b_interface, dc.snmp_index AS b_index, dc.device_id AS b_device, dc.name AS b_name FROM device_interfaces AS dc WHERE dc.peer_interface = {0}"
   for lvl in range(0,args.get('diameter',2)):
    new_dev = {}
    new_int = []
    for from_id,from_dev in devices.iteritems():
     if not from_dev['processed']:
      # Find straight interfaces
      from_dev['interfaces'] += db.do(sql_connected.format(from_id))
      cons = db.get_rows()

      # Find local multipoint
      from_dev['multipoint'] += db.do(sql_multipoint.format(from_id))
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
       to = con['b_device']
       seen = devices.get(to)
       # If not seen before:
       #  - Add device to process next round and save interface
       #  -- in case already found as new, it means there is already such a connection, find that one and make both interfaces 'dynamic'
       #  - Else, check if processed (then those interfaces are already added) if not add interface
       # 1) For straight interface we cover 'back' since the dev is processed
       # 2) For multipoint the other side will (ON SQL) see a straight interface so also covered by processed
       # 3) There is no multipoint to multipoint
       if not seen:
        new = new_dev.get(to,{'processed':False,'interfaces':0,'multipoint':0,'distance':lvl + 1,'uplink':0})
        new['uplink'] += 1
        new_dev[to] = new
        new_int.append(con)
       elif not seen['processed']:
        # exist but interface has not been registered, this covers loops as we set processed last :-)
        new_int.append(con)

      from_dev['processed'] = True
    # After all device leafs are processed we can add (net) new devices
    devices.update(new_dev)
    # Check if a connection is multihomed, then make dynamic, else straight
    multihomed = [k for k,v in new_dev.iteritems() if v['uplink'] > 1]
    for con in new_int:
     con['type'] = {'type':'dynamic'} if con['b_device'] in multihomed else False
    interfaces.extend(new_int)

   # Now update devices with hostname and type and model, rename fields to fitting info
   db.do("SELECT devices.id, hostname AS label, model, icon AS image FROM devices LEFT JOIN device_types ON devices.type_id = device_types.id WHERE devices.id IN (%s)"%(",".join(str(x) for x in devices.keys())))
   ret['nodes'] = db.get_rows()
   for node in ret['nodes']:
    devices[node['id']]['hostname'] = node['label']
   ret['name']  = devices[ret['id']]['hostname']
   ret['edges'] = [{'from':intf['a_device'],'to':intf['b_device'],'smooth':intf['type'],'title':"%s:%s <-> %s:%s"%(devices[intf['a_device']]['hostname'],intf['a_name'],devices[intf['b_device']]['hostname'],intf['b_name'])} for intf in interfaces]
 return ret
