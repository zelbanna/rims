"""Interface API module."""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

############################################### INTERFACES ################################################
#
#
def list(aCTX, aArgs):
 """List interfaces for a specific device

 Args:
  - device_id
  - sort (optional, default to 'snmp_index')
  - filter (optional), 'connected'
 Output:
 """
 ret = {}

 with aCTX.db as db:
  columns = ['di.interface_id', 'di.ipam_id', 'di.class', 'INET6_NTOA(ia.ip) AS ip', 'di.connection_id', 'LPAD(hex(di.mac),12,0) AS mac','di.state AS if_state', 'ia.state AS ip_state', 'di.snmp_index', 'di.name AS name', 'di.description']
  tables = ['ipam_addresses AS ia ON di.ipam_id = ia.id']
  if aArgs.get('device_id'):
   flter = [f"device_id = {aArgs['device_id']}"]
  else:
   flter = ['TRUE']
   columns.extend(['di.device_id','devices.hostname'])
   tables.append('devices ON di.device_id = devices.id')
  if 'filter' in aArgs:
   if 'connected' in aArgs['filter']:
    flter.append('di.connection_id IS NULL')
  ret['count'] = db.query(f"SELECT {','.join(columns)} FROM interfaces AS di LEFT JOIN {' LEFT JOIN '.join(tables)} WHERE {' AND '.join(flter)} ORDER BY {aArgs.get('sort','snmp_index')}")
  ret['data'] = db.get_rows()
  for row in ret['data']:
   row['mac'] = ':'.join(row['mac'][i:i+2] for i in [0,2,4,6,8,10])
 return ret

#
#
def info(aCTX, aArgs):
 """Show or update a specific interface for a device

 Args:
  - interface_id (required) 'new'/<if-id>
  - device_id (required)
  - ipam_id (optional)
  - mac (optional)
  - connection_id
  - snmp_index (optional)
  - name (optional)
  - description (optional)
  - op (optional), 'update','ipam_primary', 'ipam_create', 'dns_sync'

  - extra (optional) list of extra data to pull, 'classes'/'ip'

  - record (optional). IPAM record to create for ipam_id

 Output:
 """
 ret = {'status':'OK'}
 iid = aArgs.pop('interface_id','new')
 extra = aArgs.pop('extra',[])
 op = aArgs.pop('op',None)
 with aCTX.db as db:
  if op == 'update':
   # IPAM_id has it's own ops
   aArgs.pop('ipam_id',None)
   if 'mac' in aArgs:
    try:
     aArgs['mac'] = int(aArgs['mac'].replace(':',""),16)
    except:
     aArgs['mac'] = 0
   if 'snmp_index' in aArgs:
    try:
     aArgs['snmp_index'] = int(aArgs['snmp_index'])
    except:
     aArgs['snmp_index'] = None
    else:
     if aArgs['snmp_index'] == 0:
      aArgs['snmp_index'] = None
   if 'connection_id' in aArgs:
    try:
     aArgs['connection_id'] = int(aArgs['connection_id'])
    except:
     aArgs['connection_id'] = None
   if iid != 'new':
    try:
     ret['update'] = (db.update_dict('interfaces',aArgs,"interface_id=%s"%iid) == 1)
    except Exception as e:
     ret['status'] = 'NOT_OK'
     ret['exception'] = repr(e)
     ret['info'] = "Could not update interface, check unique SNMP or IPAM id"
   else:
    aArgs['manual'] = 1
    try:
     ret['update'] = (db.insert_dict('interfaces',aArgs) > 0)
    except Exception as e:
     ret['status'] = 'NOT_OK'
     ret['exception'] = repr(e)
     ret['info'] = "Could not insert interface, check unique SNMP or IPAM id"
    else:
     iid = db.get_last_id() if ret['update'] > 0 else 'new'

  elif iid == 'new':
   pass

  elif op == 'dns_sync':
   if db.query("SELECT devices.hostname, di.name, devices.ipam_id AS system_ipam_id, devices.a_domain_id, di.ipam_id, domains.name AS domain FROM interfaces AS di LEFT JOIN devices ON di.device_id = devices.id LEFT JOIN domains ON domains.id = devices.a_domain_id WHERE interface_id = %s AND di.ipam_id IS NOT NULL"%iid):
    data = db.get_row()
    from rims.api.ipam import address_info, address_sanitize
    from rims.api.dns import record_info, record_delete
    data['hostname'] = address_sanitize(aCTX, {'hostname':data['hostname']})['sanitized']
    # Update IP hostname and DNS with 'device-interface' name
    res = address_info(aCTX, {'op':'update_only','id':data['ipam_id'],'hostname':'%s-%s'%(data['hostname'],data['name'])})
    # If this happens to be the management ip and device has a domain too, check what is the new interface IP hostname and update the CNAME
    if data['system_ipam_id'] == data['ipam_id'] and data['a_domain_id']:
     tp = 'A' if 'A' in res else 'AAAA'
     FWD = res[tp] if res['status'] == 'OK' else {'create':'NOT_OK'}
     args = {'domain_id':data['a_domain_id'], 'name':'%s.%s'%(data['hostname'],data['domain']),'type':tp}
     if FWD['create'] == 'OK':
      args.update({'op':'update', 'content':res['ip']})
      res = record_info(aCTX, args)
      ret[tp] = res['data']
     else:
      res = record_delete(aCTX, args)
    ret['status'] = res['status']
    ret['update'] = ret['status'] == 'OK'
   else:
    ret.update({'update':False,'status':'NOT_OK','info':'no interface/ip found'})

  elif op == 'ipam_primary':
   if db.query("SELECT ipam_id FROM interfaces WHERE interface_id = %s and ipam_id IS NOT NULL"%iid):
    ret['result'] = 'swap' if (db.execute("UPDATE interface_alternatives SET ipam_id = %s WHERE ipam_id = %s AND interface_id = %s"%(db.get_val('ipam_id'), aArgs['ipam_id'], iid)) > 0) else 'swap_failure'
   else:
    ret['result'] = 'change' if (db.execute("DELETE FROM interface_alternatives WHERE ipam_id = %s AND interface_id = %s"%(aArgs['ipam_id'], iid)) > 0) else 'change_failure'
   ret['status'] = 'OK' if db.execute("UPDATE interfaces SET ipam_id = %s WHERE interface_id = %s"%(aArgs['ipam_id'], iid)) else 'NOT_OK'

  elif op == 'ipam_create':
   args = aArgs['record']
   args.update({'op':'insert','id':'new'})
   if 'hostname' in args:
    args['hostname'] = args['hostname']
   elif db.query("SELECT CONCAT(devices.hostname,'-',di.name) AS hostname FROM interfaces AS di LEFT JOIN devices ON di.device_id = devices.id WHERE interface_id = '%s'"%iid):
    args['hostname'] = db.get_val('hostname')
   else:
    args['hostname'] = 'unknown'
   from rims.api.ipam import address_info
   ret['ipam'] = address_info(aCTX, args)
   ret['status'] = ret['ipam'].pop('status','NOT_OK')
   if ret['status'] == 'OK':
    db.execute("INSERT INTO interface_alternatives SET interface_id = %s, ipam_id = %s"%(iid,ret['ipam']['data']['id']))
   else:
    ret['info'] = ret['ipam'].pop('info','IPAM unknown error')

  if 'classes' in extra:
   db.query("SHOW COLUMNS FROM interfaces LIKE 'class'")
   parts = (db.get_val('Type')).split("'")
   ret['classes'] = [parts[i] for i in range(1,len(parts),2)]
  if iid != 'new' and (db.query("SELECT di.* FROM interfaces AS di WHERE di.interface_id = '%s'"%iid) > 0):
   ret['data'] = db.get_row()
   ret['data']['mac'] = ':'.join(("%s%s"%x).upper() for x in zip(*[iter("{:012x}".format(ret['data']['mac']))]*2))
   ret['data'].pop('manual',None)
   if 'ip' in extra or op[:4] == 'ipam':
    ret['alternatives'] = db.get_rows() if (db.query("SELECT id, INET6_NTOA(ia.ip) AS ip FROM ipam_addresses AS ia WHERE id IN (SELECT ipam_id FROM interface_alternatives WHERE interface_id = %s)"%iid) > 0) else []
    if ret['data']['ipam_id']:
     ret['primary'] = db.get_row() if db.query("SELECT ia.id, INET6_NTOA(ia.ip) AS ip FROM ipam_addresses AS ia WHERE ia.id = %s"%ret['data']['ipam_id']) > 0 else {}
   if ret['data']['connection_id'] and (db.query("SELECT interface_id,device_id FROM interfaces AS di WHERE connection_id = %(connection_id)s AND device_id <> %(device_id)s"%ret['data']) > 0):
    ret['peer'] = db.get_row()
  else:
   ret['data'] = {'interface_id':'new','device_id':int(aArgs['device_id']),'ipam_id':None,'connection_id':None,'mac':aArgs.get('mac','00:00:00:00:00:00'),'state':'unknown','snmp_index':None,'name':aArgs.get('name','Unknown'),'description':aArgs.get('description','Unknown'),'class':aArgs.get('class','wired')}
   ret['peer'] = None
   if 'ip' in extra:
    ret['alternatives'] = []
 return ret

#
#
def delete(aCTX, aArgs):
 """Delete device interfaces using either id of interface or device (the latter where interfaces are not up or bound to ip addresses)

 Args:
  - interface_id (optional required)
  - interfaces (optional required). List of ids

 Output:
  - cleared. Number of cleared connections
  - deleted. Number of deleted interfaces
 """
 ret = {'deleted':0,'cleared':0}
 with aCTX.db as db:
  from rims.api.ipam import address_delete
  interfaces = [aArgs['interface_id']] if 'interface_id' in aArgs else aArgs['interfaces']
  for id in interfaces:
   if db.query("SELECT ipam_id FROM interfaces AS di WHERE di.interface_id = %s AND di.ipam_id IS NOT NULL"%id):
    address_delete(aCTX, {'id':db.get_val('ipam_id')})
   if db.query("SELECT ipam_id FROM interface_alternatives AS iia WHERE interface_id = %s"%id):
    for ipam in db.get_rows():
     address_delete(aCTX, {'id':ipam['ipam_id']})
   ret['cleared'] += db.execute("DELETE FROM connections WHERE id IN (SELECT DISTINCT connection_id FROM interfaces WHERE interface_id = %s)"%id)
   ret['deleted'] += db.execute("DELETE FROM interfaces WHERE interface_id = %s"%id)
 return ret

#
#
def cleanup(aCTX, aArgs):
 """Cleanup interfaces using id of device. Interfaces which doesn't have any associations

 Args:
  - device_id (required)

 Output:
  - delete. Number of deleted interfaces
 """
 ret = {}
 with aCTX.db as db:
  ret['delete'] = db.execute("DELETE FROM interfaces WHERE device_id = %(device_id)s AND manual = 0 AND state != 'up' AND ipam_id IS NULL AND connection_id IS NULL AND NOT EXISTS (SELECT 1 FROM interface_alternatives AS iia WHERE iia.interface_id = interfaces.interface_id)"%aArgs)
 return ret

#
#
def addresses(aCTX, aArgs):
 """Function returns all addresses associated with interface

 Args:
  - interface_id

 Output:
  - addresses
  - primary

 """
 ret = {}
 with aCTX.db as db:
  ret['primary'] = db.get_row() if db.query("SELECT ia.id, INET6_NTOA(ia.ip) AS ip FROM ipam_addresses AS ia LEFT JOIN interfaces AS di ON di.ipam_id = ia.id WHERE di.interface_id = %s"%aArgs['interface_id']) > 0 else {}
  ret['alternatives'] = db.get_rows() if db.query("SELECT ia.id, INET6_NTOA(ia.ip) AS ip FROM ipam_addresses AS ia LEFT JOIN interface_alternatives AS iia ON iia.ipam_id = ia.id WHERE iia.interface_id = %s"%aArgs['interface_id']) > 0 else []
 return ret

#
#
def connect(aCTX, aArgs):
 """Function connects two device interfaces simultaneously to each other, removes old interfaces before

 Args:
  - a_id (required). A interface side
  - b_id (required)  B interface side
  - disconnect (optional). Bool indicate unlinking instead. Defaults to False
  - map (optional). Bool indicate whether to visualize or not this connection. Defaults to True

 Output:
 """
 ret = {}
 with aCTX.db as db:
  ret['clear'] = db.execute("DELETE FROM connections WHERE id IN (SELECT DISTINCT connection_id FROM interfaces WHERE interface_id IN (%(a_id)s,%(b_id)s))"%aArgs)
  if not aArgs.get('disconnect',False):
   db.execute("INSERT INTO connections SET map = '%s'"%('true' if aArgs.get('map',True) else 'false'))
   id = db.get_last_id()
   ret['update'] = (db.execute("UPDATE interfaces SET connection_id = %s WHERE interface_id IN (%s,%s) AND class NOT IN ('logical','virtual')"%(id,aArgs['a_id'],aArgs['b_id'])) == 2)
   if not ret['update']:
    ret['rollback'] = bool(db.execute("DELETE FROM connections WHERE id = %s"%id))
 return ret

#
#
def disconnect(aCTX, aArgs):
 """Function disconnects a connection

 Args:
  - connection_id (required)

 Output:
 """
 ret = {}
 with aCTX.db as db:
  ret['clear'] = db.execute("DELETE FROM connections WHERE id = '%s'"%aArgs['connection_id'])
 return ret


#
#
def snmp(aCTX, aArgs):
 """ SNMP Discovery function for interfaces. Either provide info for a single interface or trying to detect new interfaces.

 Args:
  - device_id (required)
  - index (optional)

 Output:
 """
 from importlib import import_module

 ret = {}
 with aCTX.db as db:
  db.query("SELECT INET6_NTOA(ia.ip) AS ip, device_types.name AS type FROM devices LEFT JOIN ipam_addresses AS ia ON devices.ipam_id = ia.id LEFT JOIN device_types ON type_id = device_types.id  WHERE devices.id = %s"%aArgs['device_id'])
  info = db.get_row()
  try:
   module  = import_module("rims.devices.%s"%(info['type']))
   dev = getattr(module,'Device',lambda x,y: None)(aCTX, aArgs['device_id'], info['ip'])
   if aArgs.get('index'):
    data = dev.interface(aArgs['index'])
   else:
    data = dev.interfaces()
  except Exception as err:
   ret['status'] = 'NOT_OK'
   ret['info'] = str(err)
  else:
   ret['status'] = 'OK'
   if aArgs.get('index'):
    ret['data'] = data
   else:
    ret.update({'insert':0,'update':0,'skip':0})
    def mac2int(aMAC):
     try:
      return int(aMAC.replace(':',""),16)
     except:
      return 0
    db.query("SELECT interface_id, snmp_index, name, description, mac FROM interfaces WHERE device_id = %s"%aArgs['device_id'])
    for con in db.get_rows():
     entry = data.pop(con['snmp_index'],None)
     if entry:
      mac = mac2int(entry.get('mac','0'))
      if not ((entry['name'] == con['name']) and (entry['description'] == con['description']) and (mac == con['mac'])):
       ret['update'] += db.execute("UPDATE interfaces SET name = '%s', description = '%s', mac = %s WHERE interface_id = %s"%(entry['name'][:24],entry['description'][:24],mac,con['interface_id']))
    for key, entry in data.items():
     if entry['state'] == 'up':
      ret['insert'] += db.execute("INSERT INTO interfaces (device_id,name,description,snmp_index,mac) VALUES (%s,'%s','%s',%s,%s)"%(aArgs['device_id'],entry['name'][:24],entry['description'][:24],key,mac2int(entry['mac'])))
     else:
      ret['skip'] += 1
 return ret

#
#
def stats(aCTX, aArgs):
 """ Function fetches interface stats for a particular device interface(s)

 Args:
  - device_id (required)
  - ip (optional)

 Output:
 """
 ret = {'status':'NOT_OK'}
 from rims.devices.generic import Device
 with aCTX.db as db:
  if db.query("SELECT snmp_index,interface_id FROM interfaces WHERE device_id = %s AND snmp_index > 0"%aArgs['device_id']):
   interfaces = db.get_rows()
   device = Device(aCTX, aArgs['device_id'], aArgs.get('ip'))
   res = device.data_points([],interfaces)
   ret.update(res)
 return ret


#
#
def connection_info(aCTX, aArgs):
 """Function to find out connection info

 Args:
  - connection_id (required)
  - op (optional)
  - map (optional required)

 Output:
  - data object
 """
 ret = {}
 id = aArgs.get('connection_id')
 op = aArgs.get('op')
 with aCTX.db as db:
  if op == 'update':
   ret['status'] = 'OK' if (db.execute("UPDATE connections SET map = '%s' WHERE id = '%s'"%('true' if aArgs.get('map',False) else 'false',id)) > 0) else 'NOT_OK'
  ret['found'] = bool(db.query("SELECT map FROM connections WHERE id = '%s'"%id))
  if ret['found']:
   ret['data'] = {'map':db.get_val('map') == 'true','connection_id':id}
   db.query("SELECT di.interface_id, di.name AS interface_name, di.device_id, devices.hostname AS device_name FROM interfaces AS di LEFT JOIN devices ON di.device_id = devices.id WHERE connection_id = '%s'"%id)
   ret['interfaces'] = db.get_rows()
 return ret

#
#
def lldp(aCTX, aArgs):
 """Function to find out lldp information

 Args:
  - device_id (required)
  - ip (optional)

 Output:
  - LLDP info
 """
 from rims.devices.generic import Device
 device = Device(aCTX, aArgs['device_id'], aArgs.get('ip'))
 return device.lldp()

#
#
def lldp_mapping(aCTX, aArgs):
 """Function discovers connections using lldp info

 Args:
  - device_id (required)

 Output:
 """
 def mac2int(aMAC):
  try:
   return int(aMAC.replace(':',""),16)
  except:
   return 0

 with aCTX.db as db:
  if db.query("SELECT dt.name AS type, INET6_NTOA(ia.ip) AS ip FROM devices LEFT JOIN ipam_addresses AS ia ON devices.ipam_id = ia.id LEFT JOIN device_types AS dt ON devices.type_id = dt.id WHERE devices.id = '%(device_id)s'"%aArgs):
   dev = db.get_row()
   from importlib import import_module
   try:
    module = import_module("rims.devices.%s"%dev['type'])
    info   = getattr(module,'Device',None)(aCTX, aArgs['device_id'],dev['ip']).lldp()
   except Exception as e:
    return {'status':'NOT_OK','info':'Could not load device lldp process','error':repr(e)}
   else:
    # First find local interfaces
    sql_intf = "SELECT interface_id, snmp_index, name, connection_id FROM interfaces WHERE device_id = %(device_id)s AND snmp_index > 0"
    if not db.query(sql_intf%aArgs):
     # INTERNAL from rims.api.interface import snmp
     snmp(aCTX, aArgs)
     db.query(sql_intf%aArgs)
    interfaces = db.get_dict('snmp_index')
    for k,v in info.items():
     args = {}
     if not interfaces.get(int(k)):
      aCTX.log(f"DEVICE_LOG({aArgs['device_id']}): LLDP local interface index not in database: {k}")
      v['status'] = 'no_local_interface'
      v['connection_id'] = None
      continue
     tables = ['interfaces AS di']
     if   v['chassis_type'] == 4:
      args['id'] = "devices.mac = %s"%mac2int(v['chassis_id'])
      tables.append('devices ON devices.id = di.device_id')
     elif v['chassis_type'] == 5:
      args['id'] = "ia.ip = INET6_ATON('%s')"%v['chassis_id']
      tables.append('ipam_addresses AS ia ON di.ipam_id = ia.id')
     else:
      v['status'] = "chassis_mapping_impossible_no_id"
      continue
     if   v['port_type'] == 3:
      args['port'] = "di.mac = %s"%mac2int(v['port_id'])
     elif v['port_type'] == 5:
      args['port'] = "di.name = '%s'"%v['port_id']
     elif v['port_type'] == 7:
      # Locally defined... should really look into remote device and see what it configures.. complex, so simplify and guess
      args['port'] = "di.name = '%s' OR di.name = '%s'"%(v['port_id'],v['port_desc'])
     else:
      v['status'] = "chassis_mapping_impossible_no_port"
      continue
     args['desc'] = "di.description COLLATE UTF8_GENERAL_CI LIKE '%s'"%v['port_desc'] if v['port_desc'] else "FALSE"
     if db.query("SELECT di.name, di.connection_id, di.mac, di.interface_id, di.description FROM %s WHERE %s AND (%s OR %s)"%(' LEFT JOIN '.join(tables),args['id'],args['port'],args['desc'])):
      local = interfaces[int(k)]
      remote = db.get_row()
      if local['connection_id'] == remote['connection_id']:
       if remote['connection_id']:
        v['status'] = 'existing_connection'
        v['connection_id'] = remote['connection_id']
       else:
        db.execute("INSERT INTO connections SET map = 'true'")
        cid = db.get_last_id()
        db.execute("UPDATE interfaces SET connection_id = %s WHERE interface_id IN (%s,%s)"%(cid,local['interface_id'],remote['interface_id']))
        v['status'] = 'new connection'
        v['connection_id'] = cid
      else:
       v['status'] = 'other_mapping(%s<=>%s)'%(local['connection_id'],remote['connection_id'])
       v['connection_id'] = remote['connection_id']
     else:
      v['status'] = 'chassis_mapping_impossible'
      v['connection_id'] = None

 return {'status':'OK','data':info}

#################################### Monitor #################################
#
#
def clear(aCTX, aArgs):
 """ Clear all interface statistics

 Args:
  - device_id (optional)

 """
 ret = {'status':'OK'}
 with aCTX.db as db:
  ret['count'] = db.execute("UPDATE interfaces SET state = 'unknown' WHERE %s"%('TRUE' if not aArgs.get('device_id') else 'device_id = %s'%aArgs['device_id']))
 return ret

#
#
def check(aCTX, aArgs):
 """ Initiate a status check for devices' interfaces.

 Args:
  - networks (optional). List of subnet_ids to check
  - repeat (optional). In-memory repetition of state check

 """
 devices = []

 with aCTX.db as db:
  if db.query("SELECT id FROM ipam_networks" if 'networks' not in aArgs else "SELECT id FROM ipam_networks WHERE ipam_networks.id IN (%s)"%(','.join(str(x) for x in aArgs['networks']))) and db.query("SELECT devices.id AS device_id, INET6_NTOA(ia.ip) AS ip FROM devices LEFT JOIN ipam_addresses AS ia ON devices.ipam_id = ia.id WHERE ia.network_id IN (%s) ORDER BY ip"%(','.join(str(x['id']) for x in db.get_rows()))):
   for dev in db.get_rows():
    if db.query("SELECT snmp_index,interface_id,state FROM interfaces WHERE device_id = %s AND snmp_index > 0"%dev['device_id']):
     dev['interfaces'] = db.get_rows()
     devices.append(dev)

 if devices:
  if 'repeat' in aArgs:
   # INTERNAL from rims.api.interface import process
   aCTX.schedule_api_periodic(process,'interface_process',int(aArgs['repeat']),args = {'devices':devices}, output = aCTX.debug)
   return {'status':'OK','info':'INTERFACE_MONITOR_CONTINUOUS_INITIATED_F%s'%aArgs['repeat']}
  else:
   # INTERNAL from rims.api.interface import process
   return process(aCTX,{'devices':devices})
 else:
  return {'status':'OK','info':'no interfaces'}

#
#
def process(aCTX, aArgs):
 """ Function processes a list of devices and their interfaces

 Args:
  - devices (required)

 Output:
 """
 from rims.devices.generic import Device
 report = aCTX.node_function(aCTX.node if aCTX.db else 'master','interface','report', aHeader= {'X-Log':'false'})
 ret = {'status':'OK','function':'interface_process','changed':0}

 def __check_IF(aDev):
  if aDev['interfaces']:
   try:
    device = Device(aCTX, aDev['device_id'], aDev['ip'])
    probe  = device.interfaces_state()
   except Exception as e:
    aCTX.log("interface_process issue for device %s: %s"%(aDev['device_id'],str(e)))
   else:
    for intf in aDev['interfaces']:
     intf['old'] = intf['state']
     intf['state'] = probe.get(intf['snmp_index'],'unknown')
    changed = [intf for intf in aDev['interfaces'] if intf['state'] != intf['old']]
    if changed:
     ret['changed'] += len(changed)
     # from rims.api.interface import report
     report(aArgs = {'device_id':aDev['device_id'],'up':[x['interface_id'] for x in changed if x['state'] == 'up'], 'down':[x['interface_id'] for x in changed if x['state'] == 'down']})

 aCTX.queue_block(__check_IF,aArgs['devices'])
 return ret

#
#
def report(aCTX, aArgs):
 """Function updates interface status

 Args:
  - device_id (required)
  - up (optional).   List of id that changed to up
  - down (optional). List of id that changed to down

 Output:
 """
 ret = {'status':'OK','function':'interface_report'}
 with aCTX.db as db:
  for chg in ['up','down']:
   if aArgs.get(chg):
    ret[chg] = db.execute("UPDATE interfaces SET state = '%s' WHERE interface_id IN (%s)"%(chg,",".join(str(x) for x in aArgs[chg])))
 return ret
