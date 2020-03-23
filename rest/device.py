"""Device API module. This is the main device interaction module for device info, update, listing,discovery etc"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

# Internal stuff
def __is_ip(aIP):
 from ipaddress import ip_address
 try: ip_address(aIP)
 except: return False
 else: return True

############################################ Device Basics ###########################################
#
#
def list(aCTX, aArgs = None):
 """Function docstring for list TBD

 Args:
  - field (optional) 'id/ip/mac/hostname/type/base/vm/ipam_id' as search fields
  - search (optional) content to match on field, special case for mac where non-correct MAC will match all that are not '00:00:00:00:00:00'
  - extra (optional) list of extra info to add, None/'type'/'url'/'system'
  - rack_id (optional), id of rack to filter devices from
  - sort (optional) (sort on id or hostname or...)
  - dict (optional) (output as dictionary instead of list)

 Output:
 """
 ret = {}
 sort = 'ORDER BY ia.ip' if aArgs.get('sort','ip') == 'ip' else 'ORDER BY devices.hostname'
 fields = ['devices.id', 'devices.hostname', 'INET_NTOA(ia.ip) AS ip', 'devices.model','ia.state']
 tables = ['device_interfaces AS di ON devices.management_id = di.interface_id LEFT JOIN ipam_addresses AS ia ON ia.id = di.ipam_id']
 filter = ['TRUE']
 if aArgs.get('rack_id'):
  tables.append("rack_info AS ri ON ri.device_id = devices.id")
  filter.append("ri.rack_id = %(rack_id)s"%aArgs)
 if 'search' in aArgs:
  if   aArgs['field'] == 'hostname':
   filter.append("devices.hostname LIKE '%%%(search)s%%'"%aArgs)
  elif aArgs['field'] == 'ip':
   filter.append("ia.ip = INET_ATON('%(search)s')"%aArgs)
  elif aArgs['field'] == 'type':
   tables.append("device_types AS dt ON dt.id = devices.type_id")
   filter.append("dt.name = '%(search)s'"%aArgs)
  elif aArgs['field'] == 'base':
   tables.append("device_types AS dt ON dt.id = devices.type_id")
   filter.append("dt.base = '%(search)s'"%aArgs)
  elif aArgs['field'] == 'mac':
   try:    filter.append("di.mac = %i"%int(aArgs['search'].replace(':',""),16))
   except: filter.append("di.mac <> 0")
  else:
   filter.append("devices.%(field)s IN (%(search)s)"%aArgs)

 extras = aArgs.get('extra')
 if  extras:
  if 'domain' in extras:
   fields.append('domains.name AS domain')
   tables.append('domains ON domains.id = ia.a_domain_id')
  if 'type' in extras or 'functions' in extras:
   if 'functions' in extras:
    fields.append('dt.functions AS type_functions')
   if 'type' in extras:
    fields.append('dt.name AS type_name, dt.base AS type_base')
   if not (aArgs.get('field') in ['type','base']):
    tables.append("device_types AS dt ON dt.id = devices.type_id")
  if 'url' in extras:
   fields.append('devices.url')
  if 'mac' in extras or 'oui' in extras:
   fields.append('LPAD(hex(di.mac),12,0) AS mac')
   if 'oui' in extras:
    fields.append('oui.company AS oui')
    tables.append("oui ON oui.oui = (di.mac >> 24) and di.mac != 0")
  if 'system' in extras:
   fields.extend(['devices.serial','devices.version','ia.state','devices.oid'])
  if 'class' in extras:
   fields.append('devices.class')

 with aCTX.db as db:
  sql = "SELECT %s FROM devices LEFT JOIN %s WHERE %s %s"%(', '.join(fields),' LEFT JOIN '.join(tables),' AND '.join(filter),sort)
  ret['count'] = db.do(sql)
  ret['data'] = db.get_rows() if not 'dict' in aArgs else db.get_dict(aArgs['dict'])
  if extras and 'mac' in extras:
   for row in ret['data']:
    row['mac'] = ':'.join(row['mac'][i:i+2] for i in [0,2,4,6,8,10]) if row['mac'] else "00:00:00:00:00:00"
 return ret

#
#
def management(aCTX, aArgs = None):
 """Retrieves basic management information (IP, URL, hostname and username). Used internally and by site and visualize JScript

 Args:
  - id (required)

 Output:
  - ip
  - hostname
  - url
  - username
 """
 ret = {}
 with aCTX.db as db:
  ret['status'] = 'OK' if (db.do("SELECT INET_NTOA(ia.ip) AS ip, devices.hostname, devices.url FROM devices LEFT JOIN device_interfaces AS di ON devices.management_id = di.interface_id LEFT JOIN ipam_addresses AS ia ON di.ipam_id = ia.id WHERE devices.id = %s"%aArgs['id']) == 1) else 'NOT_OK'
  ret['data'] = db.get_row()
  ret['data']['username'] = aCTX.config['netconf']['username']
 return ret

#
#
def info(aCTX, aArgs = None):
 """Function docstring for info. Retrieves and updates device info (excluding rack info which is only fetched)

 TODO: remove ret['id'] when REACT

 Args:
  - id (required)
  - op (optional), None/'update'/'lookup'
  - extra (optional) list of extra info, 'types'/'classes'

 Output:
 """
 if not 'id' in aArgs:
  return {'found':False,'status':'NOT_OK','info':'device info requires id'}

 id = int(aArgs.pop('id',None))
 ret = {'id':id}

 op = aArgs.pop('op',None)
 with aCTX.db as db:
  extra = aArgs.pop('extra',[])
  if 'types' in extra or op == 'lookup':
   db.do("SELECT id, name FROM device_types ORDER BY name")
   ret['types'] = db.get_rows()
  if 'classes' in extra:
   db.do("SHOW COLUMNS FROM devices LIKE 'class'")
   parts = (db.get_val('Type')).split("'")
   ret['classes'] = [parts[i] for i in range(1,len(parts),2)]
  if op == 'lookup':
   db.do("SELECT INET_NTOA(ia.ip) AS ip FROM ipam_addresses AS ia LEFT JOIN device_interfaces AS di ON di.ipam_id = ia.id LEFT JOIN devices ON devices.management_id = di.interface_id WHERE devices.id = '%s'"%id)
   res = detect_hardware(aCTX,{'ip':db.get_val('ip')})
   ret['status'] = res['status']
   if res['status'] == 'OK':
    args = res['data']
    type_name = args.pop('type',None)
    for type in ret['types']:
     if type['name'] == type_name:
      args['type_id'] = type['id']
      break
    if not 'types' in extra:
     ret.pop('types',None)
    ret['update'] = (db.update_dict('devices',args,"id=%s"%id) == 1)

  elif op == 'update':
   aArgs.pop('management_id',None)
   if 'mac' in aArgs:
    # This is the system MAC, used by LLDP
    try:   aArgs['mac'] = int(aArgs.get('mac','0').replace(':',""),16)
    except:aArgs['mac'] = 0
   if aArgs.get('class') == 'vm':
    db.do("UPDATE device_interfaces SET class = 'virtual' WHERE device_id = %i"%id)
   ret['update'] = (db.update_dict('devices',aArgs,"id=%s"%id) == 1)

  ret['found'] = (db.do("SELECT * FROM devices WHERE id = %s"%id) == 1)
  if ret['found']:
   ret['data'] = db.get_row()
   db.do("SELECT ia.state AS ip_state, di.state AS if_state, di.interface_id, dt.base AS type_base, dt.name as type_name, dt.functions, LPAD(hex(di.mac),12,0) AS interface_mac, INET_NTOA(ia.ip) as interface_ip FROM devices LEFT JOIN device_interfaces AS di ON devices.management_id = di.interface_id LEFT JOIN ipam_addresses AS ia ON ia.id = di.ipam_id LEFT JOIN device_types AS dt ON dt.id = devices.type_id WHERE devices.id = %s"%id)
   ret['extra'] = db.get_row()
   # Pick login name from netconf
   ret['extra']['username'] = aCTX.config['netconf']['username']
   ret['data']['mac'] = ':'.join(("%s%s"%x).upper() for x in zip(*[iter("{:012x}".format(ret['data']['mac']))]*2))
   ret['extra']['interface_mac'] = ':'.join(ret['extra']['interface_mac'][i:i+2] for i in [0,2,4,6,8,10]) if ret['extra'].get('interface_mac') else '00:00:00:00:00:00'
   if not ret['extra']['functions']:
    ret['extra']['functions'] = ""
   # Rack infrastructure ?
   if ret['data']['class'] == 'vm' and (db.do("SELECT dvu.vm AS name, dvu.device_uuid, dvu.server_uuid, dvu.config, devices.hostname AS host FROM device_vm_uuid AS dvu LEFT JOIN devices ON devices.id = dvu.host_id WHERE dvu.device_id = %(id)s"%ret) == 1):
    ret['vm'] = db.get_row()
   elif (db.do("SELECT rack_unit,rack_size, console_id, console_port, rack_id, racks.name AS rack_name FROM rack_info LEFT JOIN racks ON racks.id = rack_info.rack_id WHERE rack_info.device_id = %i"%id) == 1):
    rack = db.get_row()
    ret['rack'] = rack
    infra_ids = [str(rack['console_id'])] if rack['console_id'] else []
    db.do("SELECT id,name,pdu_id,pdu_slot,pdu_unit FROM device_pems WHERE device_id = %(id)s"%ret)
    ret['pems'] = db.get_rows()
    pdu_ids = [str(x['pdu_id']) for x in ret['pems'] if x['pdu_id']]
    infra_ids.extend(pdu_ids)
    if infra_ids:
     db.do("SELECT devices.id, INET_NTOA(ia.ip) AS ip, devices.hostname FROM devices LEFT JOIN device_interfaces AS di ON devices.management_id = di.interface_id LEFT JOIN ipam_addresses AS ia ON ia.id = di.ipam_id WHERE devices.id IN (%s)"%','.join(infra_ids))
     devices = db.get_dict('id')
    else:
     devices = {}
    if pdu_ids:
     db.do("SELECT * FROM pdu_info WHERE device_id IN (%s)"%','.join(pdu_ids))
     pdus = db.get_dict('device_id')
    else:
     pdus = {}
    console = devices.get(rack['console_id'],{'hostname':None,'ip':None})
    rack.update({'console_name':console['hostname'],'console_ip':console['ip']})
    for pem in ret['pems']:
     pdu = pdus.get(pem['pdu_id'])
     pem['pdu_name'] = "%s:%s"%(devices[pem['pdu_id']]['hostname'],pdu['%s_slot_name'%pem['pdu_slot']]) if pdu else None
     pem['pdu_ip'] = devices[pem['pdu_id']]['ip'] if pdu else None
 return ret

#
#
def extended(aCTX, aArgs = None):
 """Function extended updates 'extended' device info (RACK info etc)

 Args:
  - id (required)
  - op (optional), 'update'
  - hostname (optional required). if updating this is required
  - management_id (optional required). if updating this is required
  - rack_info_<key>
  - pems_<id>_<key>
  - ddp_<id>_<key>
  - a_domain_id (optional)


 Output:
  - extended device info
 """
 ret = {'id':aArgs.pop('id',None)}

 with aCTX.db as db:
  operation = aArgs.pop('op',None)
  result = {}

  if operation and ret['id']:
   if   operation == 'add_pem':
    result['add_pem'] = (db.do("INSERT INTO device_pems(device_id) VALUES(%s)"%ret['id']) > 0)
   elif operation == 'remove_pem':
    result['remove_pem'] = (db.do("DELETE FROM device_pems WHERE device_id = %s AND id = %s "%(ret['id'],aArgs['pem_id'])) > 0)
   elif operation == 'add_ddp':
    result['add_pem'] = (db.do("INSERT INTO device_data_points(device_id) VALUES(%s)"%ret['id']) > 0)
   elif operation == 'remove_ddp':
    result['remove_pem'] = (db.do("DELETE FROM device_data_points WHERE device_id = %s AND id = %s "%(ret['id'],aArgs['ddp_id'])) > 0)
   elif operation == 'lookup_ddp':
    result['ddp'] = {'insert':0}
    from importlib import import_module
    try:
     db.do("SELECT INET_NTOA(ia.ip) AS ip, dt.name AS type FROM devices LEFT JOIN device_types AS dt ON devices.type_id = dt.id LEFT JOIN device_interfaces AS di ON di.interface_id = devices.management_id LEFT JOIN ipam_addresses AS ia ON ia.id = di.ipam_id WHERE devices.id = %s"%ret['id'])
     info = db.get_row()
     module = import_module("rims.devices.%s"%info['type'])
     device = getattr(module,'Device',None)(aCTX, ret['id'], info['ip'])
     for ddp in device.get_data_points():
      result['ddp']['insert'] += db.do("INSERT INTO device_data_points (device_id,measurement,tags,name,oid) VALUES(%i,'%s','%s','%s','%s') ON DUPLICATE KEY UPDATE id = id"%(int(ret['id']),ddp[0],ddp[1],ddp[2],ddp[3]))
    except Exception as e:
     result['ddp']['status'] = 'NOT_OK'
     result['ddp']['info'] = str(e)
    else:
     result['status'] = 'OK'

   if operation == 'update':
    if aArgs.get('a_domain_id') and not aArgs['management_id'] in ['NULL',None] and (db.do("SELECT ia.id, ia.hostname, ia.a_domain_id FROM ipam_addresses AS ia LEFT JOIN device_interfaces AS di ON di.ipam_id = ia.id WHERE di.interface_id = %s"%aArgs['management_id']) > 0):
     ipam = db.get_row()
     if (ipam['hostname'] != aArgs['hostname']) or (int(aArgs['a_domain_id']) != ipam['a_domain_id']):
      from rims.rest.ipam import address_info
      result['ipam'] = address_info(aCTX,{'id':ipam['id'],'hostname':aArgs['hostname'],'a_domain_id':aArgs['a_domain_id'],'op':'update_only'})['status']
    if aArgs.get('rack_info_rack_id') in ['NULL',None]:
     db.do("DELETE FROM rack_info WHERE device_id = %s"%ret['id'])
    else:
     db.do("INSERT INTO rack_info SET device_id = %s,rack_id=%s ON DUPLICATE KEY UPDATE rack_id = rack_id"%(ret['id'],aArgs.get('rack_info_rack_id')))
    # PEMs
    for id in [k.split('_')[1] for k,_ in aArgs.items() if k.startswith('pems_') and 'name' in k]:
     pdu_slot = aArgs.pop('pems_%s_pdu_slot'%id,"0.0").split('.')
     pem = {'name':aArgs.pop('pems_%s_name'%id,None),'pdu_unit':aArgs.pop('pems_%s_pdu_unit'%id,0),'pdu_id':pdu_slot[0],'pdu_slot':pdu_slot[1]}
     result["PEM_%s"%id] = db.update_dict('device_pems',pem,'id=%s'%id)
    # DDPs
    for id in [k.split('_')[1] for k,_ in aArgs.items() if k.startswith('ddp_') and 'measurement' in k]:
     ddp = {'measurement':aArgs.pop('ddp_%s_measurement'%id,'default'), 'tags':aArgs.pop('ddp_%s_tags'%id,""), 'name':aArgs.pop('ddp_%s_name'%id,'value'), 'oid':aArgs.pop('ddp_%s_oid'%id,None)}
     result["DDP_%s"%id] = db.update_dict('device_data_points',ddp,'id=%s'%id)

    rack_args = {k[10:]:v for k,v in aArgs.items() if k[0:10] == 'rack_info_'}
    result['rack_info'] = (db.update_dict('rack_info',rack_args,"device_id='%s'"%ret['id']) == 1) if rack_args else "NO_RACK_INFO"
    result['device'] = (db.do("UPDATE devices SET hostname = '%s', management_id = %s WHERE id = %s"%(aArgs['hostname'],aArgs['management_id'],ret['id'])) == 1)

  # Now fetch info
  ret['found'] = (db.do("SELECT management_id, devices.class, devices.oid, devices.hostname, dt.base AS type_base, oui.company AS oui FROM devices LEFT JOIN oui ON oui.oui = (devices.mac >> 24) AND devices.mac != 0 LEFT JOIN device_types AS dt ON dt.id = devices.type_id WHERE devices.id = %s"%ret['id']) == 1)
  if ret['found']:
   ret['extra'] = db.get_row()
   ret['data'] = {'hostname':ret['extra'].pop('hostname','unknown'),'management_id':ret['extra'].pop('management_id',None)}
   db.do("SELECT di.interface_id, di.name, INET_NTOA(ia.ip) AS ip, CONCAT(ia.hostname,'.',domains.name) AS fqdn, ia.a_domain_id FROM device_interfaces AS di LEFT JOIN ipam_addresses AS ia ON di.ipam_id = ia.id LEFT JOIN domains on ia.a_domain_id = domains.id WHERE di.device_id = %s"%ret['id'])
   ret['interfaces'] = db.get_rows()
   ret['interfaces'].append({'interface_id':'NULL', 'name':'N/A','ip':None,'fqdn':'N/A','a_domain_id':None})
   for intf in ret['interfaces']:
    if ret['data']['management_id'] == intf['interface_id']:
     ret['extra']['management_domain'] = intf['a_domain_id']
     break
   else:
    ret['extra']['management_domain'] = None
   db.do("SELECT * FROM device_data_points WHERE device_id = %s"%ret['id'])
   ret['data_points'] = db.get_rows()
   # Rack infrastructure
   ret['infra'] = {'racks':[{'id':'NULL', 'name':'Not used'}]}
   if ret['extra']['class'] != 'vm':
    db.do("SELECT id, name FROM racks")
    ret['infra']['racks'].extend(db.get_rows())
    if (db.do("SELECT rack_info.* FROM rack_info WHERE rack_info.device_id = %(id)s"%ret) == 1):
     ret['rack'] = db.get_row()
     ret['rack'].pop('device_id',None)
     sqlbase = "SELECT devices.id, devices.hostname FROM devices INNER JOIN device_types ON devices.type_id = device_types.id WHERE device_types.base = '%s' ORDER BY devices.hostname"
     db.do(sqlbase%('console'))
     ret['infra']['consoles'] = db.get_rows()
     ret['infra']['consoles'].append({ 'id':'NULL', 'hostname':'No Console' })
     db.do(sqlbase%('pdu'))
     ret['infra']['pdus'] = db.get_rows()
     ret['infra']['pdus'].append({ 'id':'NULL', 'hostname':'No PDU' })
     db.do("SELECT pdu_info.* FROM pdu_info")
     ret['infra']['pdu_info'] = db.get_dict('device_id')
     ret['infra']['pdu_info']['NULL'] = {'slots':1, '0_slot_id':0, '0_slot_name':'', '1_slot_id':0, '1_slot_name':''}
     db.do("SELECT id,name,pdu_id,pdu_slot,pdu_unit FROM device_pems WHERE device_id = %(id)s"%ret)
     ret['pems'] = db.get_rows()

  # Update PDU with hostname and PEM info on the right pdu slot and unit
  if operation == 'update' and 'rack' in ret:
   from importlib import import_module
   for pem in ret['pems']:
    if pem['pdu_id']:
     db.do("SELECT INET_NTOA(ia.ip) AS ip, devices.hostname, dt.name AS type FROM devices LEFT JOIN device_types AS dt ON devices.type_id = dt.id LEFT JOIN device_interfaces AS di ON devices.management_id = di.interface_id LEFT JOIN ipam_addresses AS ia ON di.ipam_id = ia.id WHERE devices.id = %i"%(pem['pdu_id']))
     pdu_info = db.get_row()
     try:
      module = import_module("rims.devices.%s"%pdu_info['type'])
      pdu = getattr(module,'Device',None)(aCTX, pem['pdu_id'],pdu_info['ip'])
      # Slot id is actually local slot ID, so we need to look up infra -> pdu_info -> pdu and then pdu[x_slot_id] to get the right ID
      pdu_res = pdu.set_name( int(ret['infra']['pdu_info'][pem['pdu_id']]['%s_slot_id'%pem['pdu_slot']] ), int(pem['pdu_unit']) , "%s-%s"%(ret['data']['hostname'],pem['name']) )
      result["PDU_(%s)"%pem['id']] = "RES:%s.%s"%(pdu_info['hostname'],pdu_res)
     except Exception as err:
      result["PDU_(%s)"%pem['id']] = "ERROR: %s"%repr(err)
 ret['result'] = result if len(result) > 0 else None
 ret['status'] = 'OK'
 return ret

#
#
def control(aCTX, aArgs = None):
 """ Function provides an operational interface towards device, either using ID or IP

 Args:
  - id (optional required)
  - ip (optional required)
  - user_id (required)
  - pem_op (optional required). Apply op (on|off|reboot) to pdu connected to pem
  - pem_id (optional required). Select which pem (or 'all') to apply op to
  - dev_op (optional required). Apply op (shutdown|reboot) to device

 Output:
  - pems. list of pems
 """
 from importlib import import_module
 ret = {}
 if   aArgs.get('id'):
  srch = "devices.id = %s"%aArgs['id']
 elif aArgs.get('ip'):
  srch = "ia.ip = INET_ATON('%s')"%aArgs['ip']
 else:
  return {'help':'requires device id or ip'}
 with aCTX.db as db:
  if (db.do("SELECT devices.id, INET_NTOA(ia.ip) AS ip, devices.class, dt.name AS type FROM devices LEFT JOIN device_interfaces AS di ON devices.management_id = di.interface_id LEFT JOIN device_types AS dt ON dt.id = devices.type_id LEFT JOIN ipam_addresses AS ia ON di.ipam_id = ia.id WHERE %s"%srch) == 1):
   ret.update(db.get_row())
   if ret['class'] != 'vm' and (db.do("SELECT dp.id, dp.device_id, dp.name, dp.pdu_id, dp.pdu_slot, dp.pdu_unit, pi.0_slot_id, pi.1_slot_id, dt.name AS pdu_type,INET_NTOA(ia.ip) AS pdu_ip FROM device_pems AS dp LEFT JOIN pdu_info AS pi ON pi.device_id = dp.pdu_id LEFT JOIN devices ON devices.id = dp.pdu_id LEFT JOIN device_types AS dt ON devices.type_id = dt.id LEFT JOIN device_interfaces AS di ON devices.management_id = di.interface_id LEFT JOIN ipam_addresses AS ia ON di.ipam_id = ia.id WHERE dp.device_id = %s AND dp.pdu_id IS NOT NULL"%ret['id']) > 0):
    ret['pems'] = db.get_rows()
   elif ret['class'] == 'vm' and (db.do("SELECT snmp_id, device_uuid, INET_NTOA(ia.ip) AS ip, dt.name AS type FROM device_vm_uuid AS dvu LEFT JOIN devices ON dvu.host_id = devices.id LEFT JOIN device_interfaces AS di ON devices.management_id = di.interface_id LEFT JOIN ipam_addresses AS ia ON ia.id = di.ipam_id LEFT JOIN device_types AS dt ON dt.id = devices.type_id WHERE dvu.device_id = %s"%ret['id']) == 1):
    ret['mapping'] = db.get_row()

 if aArgs.get('dev_op') and ret.get('id'):
  if ret['class'] != 'vm':
   module = import_module("rims.devices.%s"%ret['type'])
   with getattr(module,'Device',None)(aCTX,ret['id'],ret['ip']) as dev:
    ret['dev_op'] = dev.operation(aArgs['dev_op'])
  elif ret.get('mapping'):
   module = import_module("rims.devices.%s"%ret['mapping']['type'])
   with getattr(module,'Device',None)(aCTX,ret['id'],ret['mapping']['ip']) as dev:
    ret['dev_op'] = dev.vm_operation(aArgs['dev_op'],ret['mapping']['snmp_id'], aUUID = ret['mapping']['device_uuid'])
 if ret.get('pems'):
  for pem in ret['pems']:
   if not pem['pdu_id']:
    continue
   op_id = str(aArgs.get('pem_id','NULL'))
   module = import_module("rims.devices.%s"%pem['pdu_type'])
   pdu = getattr(module,'Device',None)(aCTX, pem['device_id'],pem['pdu_ip'])
   if op_id == 'all' or op_id == str(pem['id']):
    pem['op'] = pdu.set_state(pem['%s_slot_id'%pem['pdu_slot']],pem['pdu_unit'],aArgs['pem_op'])
   pem['state'] = pdu.get_state(pem['%s_slot_id'%pem['pdu_slot']],pem['pdu_unit']).get('state','unknown')
 return ret

#
#
def search(aCTX, aArgs = None):
 """ Functions returns device id for device matching name conditions

 Args:
  - hostname (optional required)
  - node (optional required)

 Output:
  - found (boolean)
  - device (object with id,hostname and domain of device or None)
 """
 ret = {}
 with aCTX.db as db:
  if aArgs.get('node'):
   url = aCTX.nodes[aArgs['node']]['url']
   arg = url.split(':')[1][2:].split('/')[0]
   if __is_ip(arg):
    search = "ia.ip = INET_ATON('%s')"%arg
   else:
    search = "ia.hostname LIKE '%{0}%' OR CONCAT(ia.hostname,'.',domains.name) LIKE '%{0}%'".format(arg)
  else:
   search = "ia.hostname LIKE '%{0}%' OR CONCAT(ia.hostname,'.',domains.name) LIKE '%{0}%'".format(aArgs['hostname'])
  ret['found'] = (db.do("SELECT devices.id, devices.hostname, domains.name AS domain FROM devices LEFT JOIN device_interfaces AS di ON di.device_id = devices.id LEFT JOIN ipam_addresses AS ia ON ia.id = di.ipam_id LEFT JOIN domains ON domains.id = ia.a_domain_id WHERE %s"%search) > 0)
  ret['device']= db.get_row()
 return ret

#
#
def new(aCTX, aArgs = None):
 """Function docstring for new TBD

 Args:
  - hostname (required)
  - class (optional)
  - mac (optional) NOTE - THIS IS THE MGMT INTERFACE MAC (!). For quicker deployment of new devices
  - ipam_network_id (optional)
  - ip (optional)
  - a_domain_id (optional)

 Output:
 """
 ret = {'status':'NOT_OK','id':None}
 intf = {}

 with aCTX.db as db:
  if aArgs.get('ipam_network_id') and __is_ip(aArgs.get('ip')):
   from rims.rest.ipam import address_info, address_sanitize
   res = address_info(aCTX, {'op':'insert','ip':aArgs['ip'],'network_id':aArgs['ipam_network_id'],'hostname':aArgs['hostname'],'a_domain_id':aArgs.get('a_domain_id')})
   if not res['status'] == 'OK':
    ret['info'] = res['info']
    return ret
   else:
    ret['ipam'] = 'OK'
    ipam = res['data']['id']
  else:
   ipam = None
  try:    mac = int(aArgs['mac'].replace(':',""),16)
  except: mac = 0

  db.do("INSERT INTO devices (hostname,class,type_id) SELECT '%s' AS hostname, '%s' AS class, id AS type_id FROM device_types WHERE name = 'generic'"%(aArgs['hostname'],aArgs.get('class','device')))
  ret['id'] = db.get_last_id()
  if mac > 0 or ipam is not None:
   ret['interface']  = db.do("INSERT INTO device_interfaces (device_id,mac,ipam_id,name,description) VALUES(%s,%s,%s,'management-%s','auto_created')"%(ret['id'], mac, ipam,ret['id']))
   ret['management'] = db.get_last_id()
   db.do("UPDATE devices SET management_id = %s WHERE id = %s"%(ret['management'],ret['id']))
 ret['status'] = 'OK'
 return ret

#
#
def delete(aCTX, aArgs = None):
 """Function docstring for delete TBD

 Args:
  - id (required)

 Output:
 """
 ret = {'status':'OK'}
 with aCTX.db as db:
  if (db.do("SELECT interface_id FROM device_interfaces WHERE device_id = %s"%aArgs['id']) > 0):
   from rims.rest.interface import delete as interface_delete
   ret['interfaces'] = interface_delete(aCTX, {'interfaces':[x['interface_id'] for x in db.get_rows()]})
  if (db.do("SELECT dt.base FROM devices LEFT JOIN device_types AS dt ON devices.type_id = dt.id WHERE devices.id = %s"%aArgs['id']) > 0) and (db.get_val('base') == 'pdu'):
   ret['pems'] = db.do("UPDATE device_pems SET pdu_id = NULL WHERE pdu_id = %s"%aArgs['id'])
  ret['deleted'] = (db.do("DELETE FROM devices WHERE id = %s"%aArgs['id']) > 0)

 return ret

#
#
def discover(aCTX, aArgs = None):
 """Function docstring for discover TBD

 Args:
  - network_id (required)
  - a_domain_id (optional). Passed on DNS subsystem
  - debug (optional). Bool, defaults to false

 Output:
 """
 from time import time
 from rims.rest.ipam import network_discover, address_info, address_delete
 from struct import unpack
 from socket import inet_aton

 def ip2int(addr):
  return unpack("!I", inet_aton(addr))[0]

 start_time = int(time())
 ipam = network_discover(aCTX, {'id':aArgs['network_id']})
 if ipam['status'] != 'OK':
  return {'time':int(time()) - start_time,'status':ipam['status'],'info':ipam.get('info')}

 ret = {'start':ipam['start'], 'end':ipam['end'],'addresses':len(ipam['addresses']) if not aArgs.get('debug',False) else ipam['addresses']}
 ip_addresses = {}

 def __detect_thread(aIP, aDB, aCTX):
  res = detect_hardware(aCTX,{'ip':aIP})
  aDB[aIP] = res['data'] if res['status'] == 'OK' else {}
  return (res['status'] == 'OK')

 sema = aCTX.workers.semaphore(20)
 for ip in ipam['addresses']:
  aCTX.workers.add_semaphore(__detect_thread, sema, ip, ip_addresses, aCTX)
 aCTX.workers.block(sema,20)

 # We can now do inserts only (no update) as we skip existing :-)
 if len(ip_addresses) > 0:
  with aCTX.db as db:
   db.do("SELECT id,name FROM device_types")
   devtypes = db.get_dict('name')
   for ip,entry in ip_addresses.items():
    ipam = address_info(aCTX, {'op':'insert','ip':ip,'network_id':aArgs['network_id'],'a_domain_id':aArgs.get('a_domain_id'),'hostname':'unknown-%s'%ip2int(ip)})
    if ipam['status'] == 'OK':
     entry['type_id'] = devtypes[entry.pop('type','generic')]['id'] if entry else devtypes['generic']['id']
     entry['hostname'] = 'unknown-%s'%ip2int(ip)
     if (db.insert_dict('devices',entry) == 1):
      dev_id = db.get_last_id()
      if (db.do("INSERT INTO device_interfaces (device_id,ipam_id,name,description) VALUES(%s,%s,'management-%s','auto_created')"%(dev_id, ipam['data']['id'],dev_id)) > 0):
       db.do("UPDATE devices SET management_id = %s WHERE id = %s"%(db.get_last_id(), dev_id))
     else:
      address_delete(aCTX,{'id':ipam['data']['id']})
 ret['time'] = int(time()) - start_time
 ret['found']= len(ip_addresses)
 return ret

#
#
def oids(aCTX, aArgs = None):
 """ Function returns unique oids found

  Args:

  Output:
   oids. List of unique enterprise oids
 """
 ret = {}
 with aCTX.db as db:
  for type in ['devices','device_types']:
   db.do("SELECT DISTINCT oid FROM %s"%type)
   oids = db.get_rows()
   ret[type] = [x['oid'] for x in oids]
 ret['unhandled'] = [x for x in ret['devices'] if x not in ret['device_types']]
 return ret

############################################## Specials ###############################################
#
#
def function(aCTX, aArgs = None):
 """Function docstring for function TBD

 Args:
  - id (required)
  - op (required)
  - type (required)

 Output:
 """
 from importlib import import_module
 ret = {}
 try:
  module = import_module("rims.devices.%s"%(aArgs['type']))
  dev = getattr(module,'Device',lambda x,y: None)(aCTX, aArgs['id'])
  with dev:
   ret['data'] = getattr(dev,aArgs['op'],None)()
  ret['status'] = 'OK'
 except Exception as err:
  ret = {'status':'NOT_OK','info':repr(err)}
 return ret

#
#
def configuration_template(aCTX, aArgs = None):
 """Function docstring for configuration_template TBD

 Args:
  - id (required)

 Output:
 """
 from importlib import import_module
 ret = {}
 with aCTX.db as db:
  db.do("SELECT ine.mask,INET_NTOA(ine.gateway) AS gateway,INET_NTOA(ine.network) AS network, INET_NTOA(ia.ip) AS ip, devices.hostname, device_types.name AS type, domains.name AS domain FROM devices LEFT JOIN device_interfaces AS di ON devices.management_id = di.interface_id LEFT JOIN ipam_addresses AS ia ON ia.id = di.ipam_id LEFT JOIN ipam_networks AS ine ON ine.id = ia.network_id LEFT JOIN domains ON domains.id = ia.a_domain_id LEFT JOIN device_types ON device_types.id = devices.type_id WHERE devices.id = '%s'"%aArgs['id'])
  data = db.get_row()
 ip = data['ip']
 try:
  module = import_module("rims.devices.%s"%data['type'])
  dev = getattr(module,'Device',lambda x,y: None)(aCTX, aArgs['id'], ip)
  ret['data'] = dev.configuration(data)
 except Exception as err:
  ret['info'] = "Error loading configuration template, make sure configuration is ok (netconf -> encrypted, ntpsrv, dnssrv, anonftp): %s"%repr(err)
  ret['status'] = 'NOT_OK'
 else:
  ret['status'] = 'OK'
 return ret

#
#
def network_info_discover(aCTX, aArgs = None):
 """Function discovers system macs and enterprise oid for devices (on a network segment)

 Args:
  - network_id (optional)
  - lookup (optional). Bool, default False

 Output:
 """
 def __detect_thread(aCTX, aDev, aInfo):
  res = detect_hardware(aCTX,{'ip':aDev['ip'],'basic':aInfo})
  if res['status'] == 'OK':
   aDev.update(res['data'])
  return True

 ret = {'updated':0,'empty':0}
 with aCTX.db as db:
  network = "TRUE" if not aArgs.get('network_id') else "ia.network_id = %s"%aArgs['network_id']
  if aArgs.get('lookup'):
   lookup = "TRUE"
   db.do("SELECT id, name FROM device_types")
   types = {x['name']:x['id'] for x in db.get_rows()}
  else:
   lookup = "(devices.mac = 0 OR devices.oid = 0)"

  if db.do("SELECT devices.id, INET_NTOA(ia.ip) AS ip FROM devices LEFT JOIN device_interfaces AS di ON devices.management_id = di.interface_id LEFT JOIN ipam_addresses AS ia ON ia.id = di.ipam_id WHERE ia.state = 'up' AND %s AND %s"%(network,lookup)) > 0:
   devices = db.get_rows()
   sema = aCTX.workers.semaphore(20)
   for dev in devices:
    aCTX.workers.add_semaphore(__detect_thread, sema, aCTX, dev, lookup != 'TRUE')
   aCTX.workers.block(sema,20)
   for dev in devices:
    id = dev.pop('id',None)
    ip = dev.pop('ip',None)
    if dev.get('type'):
     dev['type_id'] = types[dev.pop('type',None)]
    if len(dev) > 0:
     ret['updated'] += db.update_dict('devices',dev,'id = %s'%id)
    else:
     ret['empty'] += 1
  if aArgs.get('lookup'):
   old = db.ignore_warnings(True)
   ret['sync'] = "OK" if (db.do("INSERT IGNORE INTO device_models (name, type_id) SELECT DISTINCT model AS name ,type_id FROM devices") > 0) else "NO_NEW_MODELS"
   db.ignore_warnings(old)
 return ret

################################################## TYPES ##################################################
#
#
def type_list(aCTX, aArgs = None):
 """Function lists currenct device types

 Args:
  - sort (optional), type/name

 Output:
 """
 ret = {}
 sort = 'name' if aArgs.get('sort','name') == 'name' else 'base'
 with aCTX.db as db:
  ret['count'] = db.do("SELECT * FROM device_types ORDER BY %s"%sort)
  ret['data'] = db.get_rows()
 return ret

################################################## MODELS #################################################
#
# Models can be used to provision DHCP and PXE stuff

#
#
def model_list(aCTX, aArgs = None):
 """ Function returns the current models inventory.
  Models are cumulative, whenever synced newly found ones are added to the system

 Args:
  - op (optional). 'sync' triggers a resync before listing

 Output:
  - data
 """
 ret = {'status':'OK'}
 op = aArgs.pop('op',None)
 with aCTX.db as db:
  if op == 'sync':
   old = db.ignore_warnings(True)
   ret['result'] = "UPDATED" if (db.do("INSERT IGNORE INTO device_models (name, type_id) SELECT DISTINCT model AS name ,type_id FROM devices WHERE model NOT IN ('None','NULL')") > 0) else "NO_NEW_MODELS"
   db.ignore_warnings(old)
  ret['count'] = db.do("SELECT dm.id, dm.name, dt.name AS type FROM device_models AS dm LEFT JOIN device_types AS dt ON dt.id = dm.type_id ORDER BY dm.name, dt.name")
  ret['data'] = db.get_rows()
 return ret

#
#
def model_sync(aCTX, aArgs = None):
 """ Function syncs device models table with devices tables' models.

 Args:

 Output:
 """
 ret = {}
 op = aArgs.pop('op',None)
 with aCTX.db as db:
  old = db.ignore_warnings(True)
  ret['status'] = "OK" if (db.do("INSERT IGNORE INTO device_models (name, type_id) SELECT DISTINCT model AS name ,type_id FROM devices") > 0) else "NO_NEW_MODELS"
  db.ignore_warnings(old)
 return ret

#
#
def model_info(aCTX, aArgs = None):
 """ Function provides model info. Note that name and id can only be sync:ed to the system (there is no 'new' id as new models should be detected instead ATM)

 Args:
  - id (required)
  - op (optional). 'update' updates entries for model with id
  - defaults_file
  - image_file
  - parameters

 Output:
  - found
  - data
 """

 ret = {}
 id = aArgs.pop('id',None)
 op = aArgs.pop('op',None)
 with aCTX.db as db:
  if op == 'update':
   if aArgs.get('defaults_file') == 'None' :
    aArgs['defaults_file'] = None
   if aArgs.get('image_file') == 'None' :
    aArgs['image_file'] = None
   db.update_dict('device_models',aArgs,'id=%s'%id)

  ret['found'] = (db.do("SELECT dm.*, dt.name AS type FROM device_models AS dm LEFT JOIN device_types AS dt ON dt.id = dm.type_id WHERE dm.id = %s"%id) == 1)
  ret['data'] = db.get_row()
  ret['extra'] = {'type':ret['data'].pop('type',None)}
 return ret

#
#
def model_delete(aCTX, aArgs = None):
 """ Delete a specific model

 Args:
  - id

 Output:
  - deleted
 """
 ret = {}
 with aCTX.db as db:
  ret['deleted'] = (db.do("DELETE FROM device_models WHERE id = %s"%aArgs['id']) > 0)
 return ret

################################################### VM ###################################################
#
#
def vm_mapping(aCTX, aArgs = None):
 """ Function maps VMs on existing hypervisors using device management (!) interface MAC

 TODO:
 1) modify so if no hit on management interfaces for an inventory VM then run a (costly) check for each non-matched VM's other interfaces against the entire DB's mac table (where interface class = virtual)
 2) Save non-management interfaces and (maybe for a sync function or flag) verify that those are also in the database for each VM.

 Args:
  - clear (optional). Default false

 Output:
 """
 from importlib import import_module
 ret = {'inventory':[],'database':None,'discovered':[],'existing':[],'update':{}}
 vms = {}
 with aCTX.db as db:
  if aArgs.get('clear'):
   db.do("TRUNCATE device_vm_uuid")
  db.do("SELECT device_id, vm, device_uuid FROM device_vm_uuid")
  existing = {row.pop('device_uuid',None):row for row in db.get_rows()}
  db.do("SELECT di.device_id, di.interface_id, LPAD(hex(di.mac),12,0) AS mac FROM devices LEFT JOIN device_interfaces AS di ON devices.management_id = di.interface_id LEFT JOIN ipam_addresses AS ia ON ia.id = di.ipam_id WHERE devices.class = 'vm' and di.mac > 0")
  vms = {row.pop('mac',None):row for row in db.get_rows()}
  db.do("SELECT devices.id, INET_NTOA(ia.ip) AS ip, dt.name AS type FROM devices LEFT JOIN device_interfaces AS di ON devices.management_id = di.interface_id LEFT JOIN ipam_addresses AS ia ON ia.id = di.ipam_id LEFT JOIN device_types AS dt ON dt.id = devices.type_id WHERE dt.base = 'hypervisor' AND ia.state = 'up'")
  for row in db.get_rows():
   try:
    module    = import_module("rims.devices.%s"%row['type'])
    inventory = getattr(module,'Device',None)(aCTX,row['id'],row['ip']).get_inventory()
   except: pass
   else:
    for id,vm in inventory.items():
     vm.update({'host_id':row['id'],'snmp_id':id})
     for intf in vm.pop('interfaces',{}).values():
      db_vm = vms.pop(intf['mac'],None)
      if db_vm:
       vm['device_id'] = db_vm['device_id']
       existed = existing.pop(vm['device_uuid'],None)
       if existed:
        ret['existing'].append(vm)
       else:
        ret['discovered'].append(vm)
       break
     else:
      ret['inventory'].append(vm)

  for vm in ret['discovered']:
   ret['update']['discovered'] = db.do("INSERT INTO device_vm_uuid (device_id,host_id,snmp_id,device_uuid,config,vm) VALUES(%(device_id)s,%(host_id)s,%(snmp_id)s,'%(device_uuid)s','%(config)s','%(vm)s') ON DUPLICATE KEY UPDATE host_id = %(host_id)s, snmp_id = %(snmp_id)s, config = '%(config)s', vm = '%(vm)s'"%vm)
  for vm in ret['existing']:
   ret['update']['existing'] = db.do("UPDATE device_vm_uuid SET device_id = %(device_id)s, host_id = %(host_id)s, snmp_id = %(snmp_id)s, config = '%(config)s', vm = '%(vm)s' WHERE device_uuid = '%(device_uuid)s'"%vm)
  for vm in ret['inventory']:
   ret['update']['inventory'] = db.do("INSERT INTO device_vm_uuid (device_id,host_id,snmp_id,device_uuid,config,vm) VALUES(NULL,%(host_id)s,%(snmp_id)s,'%(device_uuid)s','%(config)s','%(vm)s') ON DUPLICATE KEY UPDATE device_id = NULL, host_id = %(host_id)s, snmp_id = %(snmp_id)s, config = '%(config)s', vm = '%(vm)s'"%vm)
 ret['database'] = [{'device_id':x['device_id'],'host_id':'-','device_uuid':'-','vm':'-','config':'-'} for x in vms.values()]
 return ret

################################################### Classes ###################################################
#
#
def class_list(aCTX, aArgs = None):
 """ Function list available device classes

 Args:
  - type (optional), 'device'/'interface'

 Output:
 """
 ret = {}
 with aCTX.db as db:
  if aArgs.get('type','device') == 'device':
   db.do("SHOW COLUMNS FROM devices LIKE 'class'")
  else:
   db.do("SHOW COLUMNS FROM device_interfaces LIKE 'class'")
  parts = (db.get_val('Type')).split("'")
  ret['data'] = [parts[i] for i in range(1,len(parts),2)]
 return ret

##################################################### Logs #####################################################
#
#
def log_put(aCTX, aArgs = None):
 """Function docstring for log_put. Insert device log

 Args:
  - id (required)
  - message (required)

 Output:
  - status
 """
 ret = {}
 with aCTX.db as db:
  ret['status'] = "OK" if (db.do("INSERT INTO device_logs (device_id,message) VALUES (%(id)s,'%(message)s')"%aArgs) == 1) else "NOT_OK"
 return ret

#
#
def log_get(aCTX, aArgs = None):
 """Function retrieves device logs

 Args:
  - id (optional)
  - count (optional)

 Output:
  - logs
 """
 ret = {}
 with aCTX.db as db:
  db.do("SELECT DATE_FORMAT(time,'%%Y-%%m-%%d %%H:%%i:%%s') AS time, message FROM device_logs WHERE %s ORDER BY id DESC LIMIT %s"%("device_id = %s"%aArgs['id'] if aArgs.get('id') else "TRUE", aArgs.get('count',30)))
  ret['logs'] = db.get_rows() # ["%(time)s: %(message)s"%(x) for x in db.get_rows()]
 return ret

#
#
def log_clear(aCTX, aArgs = None):
 """Function clear device logs.

 Args:
  - id (optional)

 Output:
  - deleted
 """
 ret = {}
 with aCTX.db as db:
  ret['deleted'] = db.do("DELETE FROM device_logs WHERE %s"%("device_id = %s"%aArgs['id'] if aArgs.get('id') else "TRUE"))
 return ret


################################################### Hardware ###################################################
#
#
def detect_hardware(aCTX, aArgs = None):
 """ Function does device detection and mapping

 Args:
  - ip (required)
  - basic (optional). Boolean, only fetch basic system info. Defaults to false
  - decode (optional). Boolean, decode MAC address. Defaults to false

 Output:
  - status
  - info (dependent)
  - data (dependent)
 """
 from rims.core.common import VarList, Session
 ret = {}
 try:
  session = Session(Version = 2, DestHost = aArgs['ip'], Community = aCTX.config['snmp']['read'], UseNumeric = 1, Timeout = int(aCTX.config['snmp'].get('timeout',100000)), Retries = 2)
  sysoid = VarList('.1.0.8802.1.1.2.1.3.2.0','.1.3.6.1.2.1.1.2.0')
  session.get(sysoid)
  if (session.ErrorInd != 0):
   raise Exception("SNMP_ERROR_%s"%session.ErrorInd)
  if not aArgs.get('basic',False):
   # Device info, Device name, Enterprise OID
   devoid = VarList('.1.3.6.1.2.1.1.1.0','.1.3.6.1.2.1.1.5.0','.1.3.6.1.2.1.1.2.0')
   session.get(devoid)
   if (session.ErrorInd != 0):
    raise Exception("SNMP_ERROR_%s"%session.ErrorInd)
 except Exception as err:
  ret['status'] = 'NOT_OK'
  ret['info'] = str(err)
 else:
  ret['status'] = 'OK'
  ret['data'] = info = {}
  if sysoid[0].val:
   try: info['mac'] = int(sysoid[0].val.hex(),16) if not aArgs.get('decode') else ':'.join("%s%s"%x for x in zip(*[iter(sysoid[0].val.hex())]*2)).upper()
   except: pass
  if sysoid[1].val:
   try:    info['oid'] = int(sysoid[1].val.decode().split('.')[7])
   except: pass
  if not aArgs.get('basic',False):
   info.update({'model':'unknown', 'snmp':'unknown','version':None,'serial':None,'mac':info.get('mac',0 if not aArgs.get('decode') else '00:00:00:00:00:00'),'oid':info.get('oid',0)})
   if devoid[1].val.decode():
    info['snmp'] = devoid[1].val.decode().lower()
   if devoid[2].val.decode():
    try:    enterprise = devoid[2].val.decode().split('.')[7]
    except: enterprise = 0
    infolist = devoid[0].val.decode().split()
    info['oid'] = enterprise
    if enterprise == '2636':
     # Juniper
     try:
      extobj = VarList('.1.3.6.1.4.1.2636.3.1.2.0','.1.3.6.1.4.1.2636.3.1.3.0')
      session.get(extobj)
      info['serial'] = extobj[1].val.decode()
      model_list = extobj[0].val.decode().lower().split()
      try: info['model'] = model_list[model_list.index('juniper') + 1]
      except: info['model'] = 'unknown'
      if (info['model']) in ['switch','internet','unknown','virtual']:
       info['model'] = ("%s" if not info['model'] == 'virtual' else "%s (VC)")%infolist[3].lower()
     except: pass
     else:
      for tp in [ 'ex', 'srx', 'qfx', 'mx' ]:
       if tp in info['model']:
        info['type'] = tp
        break
     try:    info['version'] = infolist[infolist.index('JUNOS') + 1][:-1].lower()
     except: pass
    elif enterprise == '14525':
     info['type'] = 'wlc'
     try:
      extobj = VarList('.1.3.6.1.4.1.14525.4.2.1.1.0','.1.3.6.1.4.1.14525.4.2.1.4.0')
      session.get(extobj)
      info['serial'] = extobj[0].val.decode()
      info['version'] = extobj[1].val.decode()
     except: pass
     info['model'] = " ".join(infolist[0:4])
    elif enterprise == '4526':
     # Netgear
     info['type'] = 'netgear'
     try:
      extobj = VarList('.1.3.6.1.4.1.4526.11.1.1.1.3.0','.1.3.6.1.4.1.4526.11.1.1.1.4.0','.1.3.6.1.4.1.4526.11.1.1.1.13.0')
      session.get(extobj)
      info['model']  = extobj[0].val.decode()
      info['serial'] = extobj[1].val.decode()
      info['version'] = extobj[2].val.decode()
     except: pass
    elif enterprise == '6876':
     # VMware
     info['type'] = "esxi"
     try:
      extobj = VarList('.1.3.6.1.4.1.6876.1.1.0','.1.3.6.1.4.1.6876.1.2.0','.1.3.6.1.4.1.6876.1.4.0')
      session.get(extobj)
      info['model']  = extobj[0].val.decode()
      info['version'] = "%s-%s"%(extobj[1].val.decode(),extobj[2].val.decode())
     except: pass
    elif enterprise == '24681':
     info['type'] = "qnap"
     try:
      extobj = VarList('.1.3.6.1.4.1.24681.1.4.1.1.1.1.1.2.1.3.1','.1.3.6.1.4.1.24681.1.4.1.1.1.1.1.2.1.4.1')
      session.get(extobj)
      info['model']  = extobj[0].val.decode()
      info['serial'] = extobj[1].val.decode()
     except: pass
    elif enterprise == '8072':
     info['model'] = ' '.join(infolist[0:4])
     if info['snmp'] == 'ubnt' and info['model'][0:5] == 'Linux':
      info['type'] = 'unifi_switch'
      # Fucked up MAC, saved as string instead of hex
      info['mac'] = sysoid[0].val.decode().replace('-',':') if aArgs.get('decode') else int(sysoid[0].val.decode().replace('-',""),16)
     elif info['model'][0:3] == 'UAP':
      info['type'] = 'unifi_ap'
      try:
       extobj = VarList('.1.3.6.1.4.1.41112.1.6.3.3.0','.1.3.6.1.4.1.41112.1.6.3.6.0')
       session.get(extobj)
       info['model']  = extobj[0].val.decode()
       info['version'] = extobj[1].val.decode()
      except: pass
     else:
      os = {'8':'freebsd','10':'linux','13':'win32','16':'macosx'}.get(devoid[2].val.decode().split('.')[10],'unknown')
      info['type'] = os
    elif enterprise == '4413':
     if infolist[0][0:3] == 'USW':
      info['type'] = 'unifi_switch'
      try:
       extobj = VarList('.1.3.6.1.4.1.4413.1.1.1.1.1.2.0','.1.3.6.1.4.1.4413.1.1.1.1.1.13.0')
       session.get(extobj)
       info['model']  = extobj[0].val.decode()
       info['version'] = extobj[1].val.decode()
      except: pass
     else:
      info['model'] = ' '.join(infolist[0:4])
    # Linux
    elif infolist[0] == 'Linux':
     info['model'] = 'debian' if 'Debian' in devoid[0].val.decode() else 'generic'
    else:
     info['model'] = ' '.join(infolist[0:4])
  for k,l in [('model',30),('snmp',20),('version',20),('serial',20)]:
   if info.get(k):
    info[k] = info[k][:l]
 return ret
