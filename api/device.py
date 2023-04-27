"""Device API module. This is the main device interaction module for device info, update, listing,discovery etc"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

from time import time
from importlib import import_module
from ipaddress import ip_address

############################################ Device Basics ###########################################
#
#
def list(aRT, aArgs):
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
 fields = ['devices.id', 'devices.hostname', 'INET6_NTOA(ia.ip) AS ip', 'ia.state AS ip_state']
 joins = ['ipam_addresses AS ia ON devices.ipam_id = ia.id']
 where = ['TRUE']
 extras = aArgs.get('extra')
 srch = aArgs.get('search')

 if aArgs.get('rack_id'):
  joins.append("rack_info AS ri ON ri.device_id = devices.id")
  where.append("ri.rack_id = %(rack_id)s"%aArgs)

 if srch:
  sfield = aArgs['field']
  if   sfield == 'hostname':
   where.append("devices.hostname LIKE '%%%s%%'"%srch)
  elif sfield == 'ip':
   where.append("ia.ip = INET6_ATON('%s')"%srch)
  elif sfield == 'type':
   joins.append("device_types AS dt ON dt.id = devices.type_id")
   where.append("dt.name = '%s'"%srch)
  elif sfield == 'model':
   where.append("devices.model LIKE '%%%s%%'"%srch)
  elif sfield == 'base':
   joins.append("device_types AS dt ON dt.id = devices.type_id")
   where.append("dt.base = '%s'"%srch)
  elif sfield == 'mac':
   try:
    mac = int(srch.replace(':',""),16)
   except:
    where.append("devices.mac <> 0")
   else:
    where.append("devices.mac = %i OR di.mac = %i"%(mac,mac))
    joins.append("interfaces AS di ON di.device_id = devices.id")
  elif sfield == 'interface_id':
   joins.append("interfaces AS di ON di.device_id = devices.id")
   where.append("di.interface_id = %s"%srch)
  else:
   where.append("devices.%(field)s IN (%(search)s)"%aArgs)

 if  extras:
  if 'domain' in extras:
   fields.append('domains.name AS domain')
   joins.append('domains ON domains.id = ia.a_domain_id')
  if 'type' in extras or 'functions' in extras:
   if 'functions' in extras:
    fields.append('dt.functions AS type_functions')
   if 'type' in extras:
    fields.append('dt.name AS type_name, dt.base AS type_base')
   if aArgs.get('field') not in ['type','base']:
    joins.append("device_types AS dt ON dt.id = devices.type_id")
  if 'url' in extras:
   fields.append('devices.url')
  if 'model' in extras:
   fields.append('devices.model')
  if any(i in extras for i in ['mac','oui']):
   fields.append('LPAD(hex(devices.mac),12,0) AS mac')
   if 'oui' in extras:
    fields.append('oui.company AS oui')
    joins.append("oui ON oui.oui = (devices.mac >> 24) and devices.mac != 0")
  if 'system' in extras:
   fields.extend(['devices.serial','devices.version','ia.state','devices.oid','devices.model'])
  if 'class' in extras:
   fields.append('devices.class')

 with aRT.db as db:
  ret['count'] = db.query("SELECT DISTINCT %s FROM devices LEFT JOIN %s WHERE %s %s"%(','.join(fields),' LEFT JOIN '.join(joins),' AND '.join(where),sort), True)
  ret['data'] = db.get_rows() if 'dict' not in aArgs else db.get_dict(aArgs['dict'])
  if extras and any(i in extras for i in ['mac','mgmtmac']):
   sys = 'mac' in extras
   mgmt= 'mgmtmac' in extras
   for row in ret['data']:
    if sys:
     row['mac'] = ':'.join(row['mac'][i:i+2] for i in [0,2,4,6,8,10]) if row['mac'] else "00:00:00:00:00:00"
    if mgmt:
     row['mgmtmac'] = ':'.join(row['mgmtmac'][i:i+2] for i in [0,2,4,6,8,10]) if row['mgmtmac'] else "00:00:00:00:00:00"
 return ret

#
#
def management(aRT, aArgs):
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
 with aRT.db as db:
  if db.query("SELECT INET6_NTOA(ia.ip) AS ip, devices.hostname, devices.url FROM devices LEFT JOIN ipam_addresses AS ia ON devices.ipam_id = ia.id WHERE devices.id = %s"%aArgs['id']):
   ret['data'] = db.get_row()
   ret['data']['username'] = aRT.config['netconf']['username']
   ret['status'] = 'OK'
  else:
   ret['status'] = 'NOT_OK'
 return ret

#
#
def hostname(aRT, aArgs):
 """Retrieves hostname

 Args:
  - id (required)

 Output:
  - hostname
 """
 ret = {}
 with aRT.db as db:
  if db.query("SELECT devices.hostname FROM devices WHERE devices.id = %s"%aArgs['id']):
   ret['data'] = db.get_val('hostname')
   ret['status'] = 'OK'
  else:
   ret['status'] = 'NOT_OK'
 return ret

#
#
def info(aRT, aArgs):
 """Function docstring for info. Retrieves and updates device info (excluding rack info which is only fetched)

 Args:
  - id (required)
  - op (optional), None/'update'/'lookup'
  - extra (optional) list of extra info, 'types'/'classes'

 Output:
 """
 if 'id' not in aArgs:
  return {'found':False,'status':'NOT_OK','info':'device info requires id'}

 id = int(aArgs.pop('id',None))
 ret = {}

 op = aArgs.pop('op',None)
 with aRT.db as db:
  extra = aArgs.pop('extra',[])
  if 'types' in extra or op == 'lookup':
   db.query("SELECT id, name, base FROM device_types ORDER BY name")
   ret['types'] = db.get_rows()
  if 'classes' in extra:
   db.query("SHOW COLUMNS FROM devices LIKE 'class'")
   parts = (db.get_val('Type')).split("'")
   ret['classes'] = [parts[i] for i in range(1,len(parts),2)]
  if op == 'lookup':
   db.query("SELECT INET6_NTOA(ia.ip) AS ip FROM ipam_addresses AS ia LEFT JOIN devices ON devices.ipam_id = ia.id WHERE devices.id = '%s'"%id)
   from rims.devices.detector import execute as execute_detect
   res = execute_detect(db.get_val('ip'), aRT.config['snmp'])
   ret['status'] = res['status']
   if res['status'] == 'OK':
    args = res['data']
    type_name = args.pop('type',None)
    for type in ret['types']:
     if type['name'] == type_name:
      args['type_id'] = type['id']
      break
    ret['update'] = (db.update_dict('devices',args,"id=%s"%id) == 1)
   else:
    ret['info'] = res.get('info','NO_INFO')
    if 'types' not in extra:
     ret.pop('types',None)
   if 'types' not in extra:
    ret.pop('types',None)

  elif op == 'update':
   aArgs.pop('ipam_id',None)
   if 'mac' in aArgs:
    # This is the system MAC, used by LLDP
    try:   aArgs['mac'] = int(aArgs.get('mac','0').replace(':',""),16)
    except:aArgs['mac'] = 0
   if aArgs.get('class') == 'vm':
    db.execute("UPDATE interfaces SET class = 'virtual' WHERE device_id = %i"%id)
   ret['update'] = (db.update_dict('devices',aArgs,"id=%s"%id) == 1)

  ret['found'] = (db.query("SELECT * FROM devices WHERE id = %s"%id) == 1)
  if ret['found']:
   ret['data'] = db.get_row()
   db.query("SELECT ia.state AS state, devices.ipam_id, dt.base AS type_base, dt.name as type_name, dt.functions, INET6_NTOA(ia.ip) as ip FROM devices LEFT JOIN ipam_addresses AS ia ON devices.ipam_id = ia.id LEFT JOIN device_types AS dt ON dt.id = devices.type_id WHERE devices.id = %s"%id)
   ret['extra'] = db.get_row()
   # Pick login name from netconf
   ret['extra']['username'] = aRT.config['netconf']['username']
   ret['data']['mac'] = ':'.join(("%s%s"%x).upper() for x in zip(*[iter("{:012x}".format(ret['data']['mac']))]*2))
   if not ret['extra']['functions']:
    ret['extra']['functions'] = ""
   # Rack infrastructure ?
   if ret['data']['class'] == 'vm' and (db.query("SELECT dvu.vm AS name, dvu.bios_uuid, dvu.instance_uuid, dvu.config, devices.hostname AS host FROM device_vm_uuid AS dvu LEFT JOIN devices ON devices.id = dvu.host_id WHERE dvu.device_id = %s"%id) == 1):
    ret['vm'] = db.get_row()
   elif db.query("SELECT rack_unit,rack_size, console_id, console_port, rack_id, racks.name AS rack_name FROM rack_info LEFT JOIN racks ON racks.id = rack_info.rack_id WHERE rack_info.device_id = %i"%id):
    rack = db.get_row()
    ret['rack'] = rack
    infra_ids = [str(rack['console_id'])] if rack['console_id'] else []
    db.query("SELECT id,name,pdu_id,pdu_slot,pdu_unit FROM device_pems WHERE device_id = %s"%id)
    ret['pems'] = db.get_rows()
    pdu_ids = [str(x['pdu_id']) for x in ret['pems'] if x['pdu_id']]
    infra_ids.extend(pdu_ids)
    if infra_ids:
     db.query("SELECT devices.id, INET6_NTOA(ia.ip) AS ip, devices.hostname FROM devices LEFT JOIN ipam_addresses AS ia ON devices.ipam_id = ia.id WHERE devices.id IN (%s)"%','.join(infra_ids))
     devices = db.get_dict('id')
    else:
     devices = {}
    if pdu_ids:
     db.query("SELECT * FROM pdu_info WHERE device_id IN (%s)"%','.join(pdu_ids))
     pdus = db.get_dict('device_id')
    else:
     pdus = {}
    if rack['console_id']:
     rack['console_name'] = devices.get(rack['console_id'],{'hostname':None})['hostname']
     if db.query("SELECT CONCAT(access_url,':',port+%s) AS url FROM console_info WHERE device_id = '%s'"%(rack['console_port'],rack['console_id'])):
      rack['console_url'] = db.get_val('url')
    for pem in ret['pems']:
     pdu = pdus.get(pem['pdu_id'])
     pem['pdu_name'] = "%s:%s"%(devices[pem['pdu_id']]['hostname'],pdu['%s_slot_name'%pem['pdu_slot']]) if pdu else None
     pem['pdu_ip'] = devices[pem['pdu_id']]['ip'] if pdu else None
 return ret

#
#
def extended(aRT, aArgs):
 """Function extended updates 'extended' device info (RACK info etc)

 Args:
  - id (required)
  - op (optional), 'update'
  - hostname (optional required). if updating this is required
  - ipam_id (optional required). if updating this is required
  - a_domain_id (optional required)
  - extra: 'domains'

 Output:
  - extended device info
 """
 op = aArgs.pop('op',None)
 extra = aArgs.pop('extra',[])
 ret = {}
 with aRT.db as db:
  if 'domains' in extra or op:
   db.query("SELECT id,name FROM domains WHERE type = 'forward'")
   ret['domains'] = db.get_rows()
   domains = {x['id']:x['name'] for x in ret['domains']}

  if op == 'update':
   from rims.api.dns import record_info, record_delete
   ret['dns'] = {}
   if db.query("SELECT devices.hostname, devices.a_domain_id, devices.ipam_id, IF(IS_IPV4(INET6_NTOA(ia.ip)),'A','AAAA') AS type FROM devices LEFT JOIN ipam_addresses AS ia ON devices.ipam_id = ia.id WHERE devices.id = %(id)s"%aArgs):
    entry = db.get_row()
    if entry['a_domain_id'] and entry['ipam_id']:
     ret['dns']['delete'] = record_delete(aRT, {'domain_id':entry['a_domain_id'], 'name':'%s.%s'%(entry['hostname'],domains[entry['a_domain_id']]), 'type':entry['type']})['status']

   ret['update'] = (db.update_dict('devices',aArgs,"id = %s"%aArgs['id']) == 1)

   if aArgs.get('a_domain_id') not in (None,'NULL') and aArgs['ipam_id'] not in (None,'NULL') and db.query("SELECT ia.hostname, ia.a_domain_id, INET6_NTOA(ia.ip) AS ip, IF(IS_IPV4(INET6_NTOA(ia.ip)),'A','AAAA') AS type FROM ipam_addresses AS ia WHERE ia.id = %(ipam_id)s"%aArgs) > 0:
    entry = db.get_row()
    if entry['a_domain_id']:
     ret['dns']['create'] = record_info(aRT, {'op':'insert', 'domain_id':aArgs['a_domain_id'], 'name':'%s.%s'%(aArgs['hostname'],domains[int(aArgs['a_domain_id'])]), 'type':entry['type'], 'content':entry['ip']})['status']
   else:
    ret['dns']['create'] = False
   ret['status'] = 'OK'

  ret['found'] = (db.query("SELECT devices.id, ipam_id, a_domain_id, snmp, CONCAT('.1.3.6.1.4.1.',devices.oid) AS oid, devices.hostname, oui.company AS oui FROM devices LEFT JOIN oui ON oui.oui = (devices.mac >> 24) AND devices.mac != 0  WHERE devices.id = %(id)s"%aArgs) == 1)
  if ret['found']:
   ret['data'] = db.get_row()
   ret['extra'] = {'oid':ret['data'].pop('oid',None),'oui':ret['data'].pop('oui',None)}
   db.query("SELECT di.ipam_id, di.interface_id, di.name, INET6_NTOA(ia.ip) AS ip FROM interfaces AS di LEFT JOIN ipam_addresses AS ia ON di.ipam_id = ia.id WHERE di.device_id = %(id)s AND di.ipam_id IS NOT NULL"%aArgs)
   ret['interfaces'] = [{'ipam_id':'NULL','interface_id':None, 'name':'N/A','ip':None}]
   ret['interfaces'].extend(db.get_rows())
 return ret

#
#
def rack(aRT, aArgs):
 """ Function provides rack information for a specific device

 Args:
  - device_id (required)
  - op
  - <data>

 Output:
  - data
 """
 id = aArgs['device_id']
 op = aArgs.pop('op',None)
 ret ={'racks':[{'id':'NULL', 'name':'Not used'}]}
 with aRT.db as db:
  if op == 'update':
   if aArgs.get('rack_id') in (None,'NULL'):
    ret['deleted'] = bool(db.execute("DELETE FROM rack_info WHERE device_id = %s"%id))
   else:
    ret['insert'] = bool(db.execute("INSERT INTO rack_info SET device_id = %s,rack_id=%s ON DUPLICATE KEY UPDATE rack_id = rack_id"%(id,aArgs['rack_id'])))
    ret['update'] = bool(db.update_dict('rack_info',aArgs,'device_id=%s'%id))
  db.query("SELECT id, name FROM racks")
  ret['racks'].extend(db.get_rows())
  ret['data'] = db.get_row()
  db.query("SELECT devices.id, devices.hostname FROM devices INNER JOIN device_types ON devices.type_id = device_types.id WHERE device_types.base = 'console' ORDER BY devices.hostname")
  ret['consoles'] = db.get_rows()
  ret['consoles'].append({ 'id':'NULL', 'hostname':'No Console' })
  if db.query("SELECT rack_info.* FROM rack_info WHERE rack_info.device_id = %s"%id):
   ret['data'] = db.get_row()
  else:
   ret['data'] = {'device_id':id,'rack_id':None,'rack_size':1,'rack_unit':0,'console_id':None,'console_port':0}
 return ret

#
#
def control(aRT, aArgs):
 """ Function provides an operational interface towards device, either using ID or IP

 Args:
  - id (optional required)
  - user_id (required)
  - device_op (optional required). Apply op (shutdown|reboot) to device
  - pem_op (optional required). Apply op (on|off|reboot) to pdu connected to pem
  - pem_id (optional required). Select which pem (or 'all') to apply op to

 Output:
  - pems. list of pems
 """
 ret = {}
 id = aArgs['id']
 with aRT.db as db:
  db.query("SELECT INET6_NTOA(ia.ip) AS ip, devices.class, dt.name AS type FROM devices LEFT JOIN device_types AS dt ON dt.id = devices.type_id LEFT JOIN ipam_addresses AS ia ON devices.ipam_id = ia.id WHERE devices.id = %s"%id)
  info = db.get_row()
  if info['class'] != 'vm' and (db.query("SELECT dp.id, dp.name, dp.pdu_id, dp.pdu_slot, dp.pdu_unit, pi.0_slot_id, pi.1_slot_id, dt.name AS pdu_type, INET6_NTOA(ia.ip) AS pdu_ip FROM device_pems AS dp LEFT JOIN pdu_info AS pi ON pi.device_id = dp.pdu_id LEFT JOIN devices ON devices.id = dp.pdu_id LEFT JOIN device_types AS dt ON devices.type_id = dt.id LEFT JOIN ipam_addresses AS ia ON devices.ipam_id = ia.id WHERE dp.device_id = %s AND dp.pdu_id IS NOT NULL"%id) > 0):
   ret['pems'] = db.get_rows()
  elif info['class'] == 'vm' and (db.query("SELECT dvu.host_id, snmp_id AS device_snmp_id, bios_uuid, INET6_NTOA(ia.ip) AS host_ip, dt.name AS host_type FROM device_vm_uuid AS dvu LEFT JOIN devices ON dvu.host_id = devices.id LEFT JOIN ipam_addresses AS ia ON devices.ipam_id = ia.id LEFT JOIN device_types AS dt ON dt.id = devices.type_id WHERE dvu.device_id = %s"%id) == 1):
   ret['mapping'] = db.get_row()

 if aArgs.get('device_op'):
  try:
   if info['class'] != 'vm':
    module = import_module("rims.devices.%s"%info['type'])
    with getattr(module,'Device',None)(aRT,id,info['ip']) as dev:
     ret['result'] = dev.operation(aArgs['device_op'])
   elif ret.get('mapping'):
    module = import_module("rims.devices.%s"%ret['mapping']['host_type'])
    with getattr(module,'Device',None)(aRT,ret['mapping']['host_id'],ret['mapping']['host_ip']) as dev:
     ret['result'] = dev.vm_operation(aArgs['device_op'],ret['mapping']['device_snmp_id'], aUUID = ret['mapping']['bios_uuid'])
   else:
    ret['result'] = 'NO_VM_MAPPING'
  except Exception as e:
   ret.update({'status':'NOT_OK_DEVICE','op':'NOT_OK','info':str(e)})

 if ret.get('pems'):
  for pem in ret['pems']:
   if not pem['pdu_id']:
    continue
   op_id = str(aArgs.get('pem_id','NULL'))
   try:
    module = import_module("rims.devices.%s"%pem['pdu_type'])
    pdu = getattr(module,'Device',None)(aRT, pem['pdu_id'],pem['pdu_ip'])
    if op_id == 'all' or op_id == str(pem['id']):
     pem['op'] = pdu.set_state(pem['%s_slot_id'%pem['pdu_slot']],pem['pdu_unit'],aArgs['pem_op'])
    pem['state'] = pdu.get_state(pem['%s_slot_id'%pem['pdu_slot']],pem['pdu_unit']).get('state','unknown')
   except Exception as e:
    pem.update({'status':'NOT_OK_PEM','op':'NOT_OK','info':str(e)})
 else:
  ret['pems'] = []
 return ret

#
#
def search(aRT, aArgs):
 """ Functions returns device id for device matching name conditions

 Args:
  - hostname (optional required)
  - node (optional required)

 Output:
  - found (boolean)
  - device (object with id,hostname and domain of device or None)
 """
 ret = {}
 with aRT.db as db:
  if aArgs.get('node'):
   url = aRT.nodes[aArgs['node']]['url']
   arg = url.split(':')[1][2:].split('/')[0]
   try: ip_address(arg)
   except: search = "WHERE devices.hostname LIKE '%{0}%' OR CONCAT(devices.hostname,'.',domains.name) LIKE '%{0}%'".format(arg)
   else:   search = "LEFT JOIN interfaces AS di ON di.device_id = devices.id LEFT JOIN ipam_addresses AS ia ON ia.id = di.ipam_id WHERE ia.ip = INET6_ATON('%s')"%arg
  else:
   search = "WHERE devices.hostname LIKE '%{0}%' OR CONCAT(devices.hostname,'.',domains.name) LIKE '%{0}%'".format(aArgs['hostname'])
  ret['found'] = (db.query("SELECT devices.id, devices.hostname, domains.name AS domain FROM devices LEFT JOIN domains ON domains.id = devices.a_domain_id %s"%search) > 0)
  ret['data']= db.get_row()
 return ret

#
#
def new(aRT, aArgs):
 """Function creates a new host and sets up IP, management interface and DNS records

 Args:
  - hostname (required)
  - class (optional)
  - mac (optional) NOTE - THIS IS THE MGMT INTERFACE MAC (!). For quicker deployment of new devices
  - ipam_network_id (optional)
  - ip (optional)
  - if_domain_id (optional required). If ip submitted, can be None/'NULL'
  - a_domain_id (optional)

 Output:
 """
 data = {}
 ret = {'status':'NOT_OK','data':data}

 with aRT.db as db:
  from rims.api.ipam import address_info, address_sanitize
  try:
   ip = ip_address(aArgs.get('ip'))
  except:
   ip = None
  hostname = address_sanitize(aRT, {'hostname':aArgs['hostname']})['sanitized']

  if aArgs.get('ipam_network_id') and ip:
   res = address_info(aRT, {'op':'insert','ip':str(ip),'network_id':aArgs['ipam_network_id'],'hostname':'%s-me'%hostname,'a_domain_id':aArgs.get('if_domain_id')})
   if res['status'] != 'OK':
    return {'status':'NOT_OK','info':res['info']}
   else:
    data['ipam'] = res['data']['id']
  else:
   data['ipam'] = "NULL"

  try:
   data['mac'] = int(aArgs['mac'].replace(':',""),16)
  except:
   data['mac'] = 0

  # Insert ipam_id if existing
  db.execute("INSERT INTO devices (hostname,class,a_domain_id,type_id,ipam_id) SELECT '%s', '%s', %s, id AS type_id, %s FROM device_types WHERE name = 'generic'"%(aArgs['hostname'],aArgs.get('class','device'),aArgs.get('a_domain_id','NULL'),data['ipam']))
  data['id']= db.get_last_id()

  if data['ipam'] != 'NULL' or data['mac']:
   data['interface'] = bool(db.execute("INSERT INTO interfaces (device_id,mac,ipam_id,name,description) VALUES(%(id)s,%(mac)s,%(ipam)s,'me','auto_created')"%data))
   if aArgs.get('a_domain_id') not in (None,'NULL'):
    from rims.api.dns import record_info
    db.query("SELECT name FROM domains WHERE id = %s"%aArgs['a_domain_id'])
    data['dns'] = record_info(aRT, {'op':'insert', 'domain_id':aArgs['a_domain_id'], 'name':'%s.%s'%(hostname,db.get_val('name')), 'type':'A' if ip.version == 4 else 'AAAA', 'content':str(ip)})['status']

 ret['status'] = 'OK'
 return ret

#
#
def delete(aRT, aArgs):
 """Function deletes a device, first removing all dependeing interfaces (an IPs)

 Args:
  - id (required)

 Output:
 """
 ret = {'status':'OK'}
 with aRT.db as db:
  if db.query("SELECT devices.a_domain_id, CONCAT(devices.hostname,'.',domains.name) AS fqdn, IF(IS_IPV4(INET6_NTOA(ia.ip)),'A','AAAA') AS type FROM devices LEFT JOIN ipam_addresses AS ia ON devices.ipam_id = ia.id LEFT JOIN domains ON domains.id = devices.a_domain_id WHERE devices.id = %s"%aArgs['id']):
   dns = db.get_row()
   if dns['a_domain_id'] and dns['fqdn'] and dns['type']:
    from rims.api.dns import record_delete
    ret['dns'] = record_delete(aRT, {'domain_id':dns['a_domain_id'], 'name':dns['fqdn'], 'type':dns['type']})['status']
  if db.query("SELECT interface_id FROM interfaces WHERE device_id = %s"%aArgs['id']):
   from rims.api.interface import delete as interface_delete
   interface_delete(aRT, {'interfaces':[x['interface_id'] for x in db.get_rows()]} )
  if (db.query("SELECT dt.base FROM devices LEFT JOIN device_types AS dt ON devices.type_id = dt.id WHERE devices.id = %s"%aArgs['id']) > 0) and (db.get_val('base') == 'pdu'):
   ret['pems'] = db.execute("UPDATE device_pems SET pdu_id = NULL WHERE pdu_id = %s"%aArgs['id'])
  ret['deleted'] = bool(db.execute("DELETE FROM devices WHERE id = %s"%aArgs['id']))
 return ret

#
#
def discover(aRT, aArgs):
 """Function docstring for discover TBD

 Args:
  - network_id (required)
  - a_domain_id (optional). Device domain id
  - if_domain_id (optional). Domain id for interfaces

 Output:
 """
 from rims.devices.detector import execute as execute_detect
 from rims.api.ipam import network_discover, address_info, address_delete
 from rims.api.dns import record_info

 def __detect_thread(aIP, aDB, aRT):
  res = execute_detect(aIP, aRT.config['snmp'])
  aDB[aIP] = res['data'] if res['status'] == 'OK' else {}
  return res['status'] == 'OK'

 start_time = int(time())
 ipam = network_discover(aRT, {'id':aArgs['network_id'],'internal':True})
 if ipam['status'] != 'OK':
  return {'time':int(time()) - start_time,'status':ipam['status'],'info':ipam.get('info')}

 ret = {'addresses':len(ipam['addresses'])}

 ip_addresses = {}
 if aArgs.get('a_domain_id') == 'NULL':
  aArgs['a_domain_id'] = None
 if aArgs.get('if_domain_id') == 'NULL':
  aArgs['if_domain_id'] = None

 sema = aRT.semaphore(20)
 for ip_str in ipam['addresses']:
  aRT.queue_semaphore(__detect_thread, sema, ip_str, ip_addresses, aRT)
 for _ in range(20):
  sema.acquire()

 # We can now do inserts only (no update) as we skip existing :-)
 if ip_addresses:
  from rims.api.dns import record_info
  with aRT.db as db:
   if aArgs['a_domain_id'] and (db.query("SELECT name FROM domains WHERE type = 'forward' AND id = %s"%aArgs['a_domain_id']) > 0):
    domain = db.get_val('name')
   db.query("SELECT id,name FROM device_types")
   devtypes = {x['name']:x['id'] for x in db.get_rows()}
   for ip_str,entry in ip_addresses.items():
    ip = ip_address(ip_str)
    ip_int = int(ip)
    ipam = address_info(aRT, {'op':'insert','ip':ip_str,'network_id':aArgs['network_id'],'a_domain_id':aArgs['if_domain_id'],'hostname':'host-%s-me'%ip_int})
    if ipam['status'] == 'OK':
     entry['type_id'] = devtypes[entry.pop('type','generic')] if entry else devtypes['generic']
     entry['hostname'] = 'host-%s'%ip_int
     entry['a_domain_id'] = aArgs['a_domain_id']
     entry['ipam_id'] = ipam['data']['id']
     if db.insert_dict('devices',entry):
      dev_id = db.get_last_id()
      db.execute("INSERT INTO interfaces (device_id,ipam_id,name,description) VALUES(%s,%s,'me','auto_created')"%(dev_id, ipam['data']['id']))
      if aArgs['a_domain_id']:
       record_info(aRT, {'op':'insert', 'domain_id':aArgs['a_domain_id'], 'name':'%s.%s'%(entry['hostname'],domain), 'type':'A' if ip.version == 4 else 'AAAA', 'content':ip_str})
     else:
      address_delete(aRT,{'id':ipam['data']['id']})
 ret['time'] = int(time()) - start_time
 ret['found']= len(ip_addresses)
 return ret

#
#
def oids(aRT, aArgs):
 """ Function returns unique oids found

  Args:

  Output:
   oids. List of unique enterprise oids
 """
 ret = {}
 with aRT.db as db:
  for tp in ['devices','device_types']:
   db.query(f"SELECT DISTINCT oid FROM {tp}")
   ret[tp] = [x['oid'] for x in db.get_rows()]
 ret['unhandled'] = [x for x in ret['devices'] if x not in ret['device_types']]
 return ret

############################################## Specials ###############################################
#
#
def function(aRT, aArgs):
 """Function docstring for function TBD

 Args:
  - id (required)
  - op (required)
  - type (required)

 Output:
 """
 ret = {}
 try:
  module = import_module("rims.devices.%s"%(aArgs['type']))
  dev = getattr(module,'Device',lambda x,y: None)(aRT, aArgs['id'])
  with dev:
   ret['data'] = getattr(dev,aArgs['op'],None)()
  ret['status'] = 'OK'
 except Exception as err:
  ret = {'status':'NOT_OK','info':repr(err)}
 return ret

#
#
def configuration_template(aRT, aArgs):
 """Function docstring for configuration_template TBD

 Args:
  - id (required)

 Output:
 """
 ret = {}
 with aRT.db as db:
  db.query("SELECT ine.mask,INET6_NTOA(ine.gateway) AS gateway,INET6_NTOA(ine.network) AS network, INET6_NTOA(ia.ip) AS ip, devices.hostname, device_types.name AS type, domains.name AS domain FROM devices LEFT JOIN ipam_addresses AS ia ON devices.ipam_id = ia.id LEFT JOIN ipam_networks AS ine ON ine.id = ia.network_id LEFT JOIN domains ON domains.id = devices.a_domain_id LEFT JOIN device_types ON device_types.id = devices.type_id WHERE devices.id = '%s'"%aArgs['id'])
  data = db.get_row()
 ip = data['ip']
 try:
  module = import_module("rims.devices.%s"%data['type'])
  dev = getattr(module,'Device',lambda x,y: None)(aRT, aArgs['id'], ip)
  ret['data'] = dev.configuration(data)
 except Exception as err:
  ret['info'] = "Error loading configuration template, make sure configuration is ok (netconf -> encrypted, ntpsrv, dnssrv, anonftp): %s"%repr(err)
  ret['status'] = 'NOT_OK'
 else:
  ret['status'] = 'OK'
 return ret

#
#
def system_info_discover(aRT, aArgs):
 """Function discovers system macs and enterprise oid for devices (on a network segment)

 Args:
  - network_id (optional)
  - lookup (optional). Bool, default False. Will do extra update of device models based on learned info

 Output:
 """
 from rims.devices.detector import execute as execute_detect
 def __detect_thread(aRT, aDev, aInfo):
  res = execute_detect(aDev['ip'], aRT.config['snmp'], aBasic = aInfo)
  if res['status'] == 'OK':
   aDev.update(res['data'])
  return True

 ret = {'updated':0,'empty':0}
 with aRT.db as db:
  network = "TRUE" if not aArgs.get('network_id') else "ia.network_id = %s"%aArgs['network_id']
  if aArgs.get('lookup'):
   lookup = "TRUE"
   db.query("SELECT id, name FROM device_types")
   types = {x['name']:x['id'] for x in db.get_rows()}
  else:
   lookup = "(devices.mac = 0 OR devices.oid = 0)"

  if db.query("SELECT devices.id, INET6_NTOA(ia.ip) AS ip FROM devices LEFT JOIN ipam_addresses AS ia ON devices.ipam_id = ia.id WHERE ia.state = 'up' AND %s AND %s"%(network,lookup)) > 0:
   devices = db.get_rows()
   sema = aRT.semaphore(20)
   for dev in devices:
    aRT.queue_semaphore(__detect_thread, sema, aRT, dev, lookup != 'TRUE')
   for _ in range(20):
    sema.acquire()
   for dev in devices:
    id = dev.pop('id',None)
    dev.pop('ip',None)
    if dev.get('type'):
     dev['type_id'] = types[dev.pop('type',None)]
    if dev:
     ret['updated'] += db.update_dict('devices',dev,f"id = {id}")
    else:
     ret['empty'] += 1
  if aArgs.get('lookup'):
   ret['sync'] = model_sync(aRT, {})['status']
 return ret

################################################## TYPES ##################################################
#
#
def type_list(aRT, aArgs):
 """Function lists currenct device types

 Args:
  - sort (optional), type/name

 Output:
 """
 ret = {}
 sort = 'name' if aArgs.get('sort','name') == 'name' else 'base'
 with aRT.db as db:
  ret['count'] = db.query("SELECT * FROM device_types ORDER BY %s"%sort)
  ret['data'] = db.get_rows()
 return ret

################################################## MODELS #################################################
#
# Models can be used to provision DHCP and PXE stuff

#
#
def model_list(aRT, aArgs):
 """ Function returns the current models inventory.
  Models are cumulative, whenever synced newly found ones are added to the system

 Args:
  - op (optional). 'sync' triggers a resync before listing

 Output:
  - data
 """
 ret = {'status':'OK'}
 op = aArgs.pop('op',None)
 with aRT.db as db:
  if op == 'sync':
   # INTERNAL from rims.api.device import models_sync
   ret['result'] = model_sync(aRT,{})['status']
  ret['count'] = db.query("SELECT dm.id, dm.name, dt.name AS type FROM device_models AS dm LEFT JOIN device_types AS dt ON dt.id = dm.type_id ORDER BY dm.name, dt.name")
  ret['data'] = db.get_rows()
 return ret

#
#
def model_sync(aRT, aArgs):
 """ Function syncs device models table with devices tables' models.

 Args:

 Output:
 """
 ret = {}
 with aRT.db as db:
  ret['status'] = "UPDATED" if (db.execute("INSERT INTO device_models (name, type_id) SELECT DISTINCT model AS name, type_id FROM devices ON DUPLICATE KEY UPDATE device_models.id=device_models.id") > 0) else "NO_NEW_MODELS"
 return ret

#
#
def model_info(aRT, aArgs):
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
 with aRT.db as db:
  if op == 'update':
   if aArgs.get('defaults_file') == 'None' :
    aArgs['defaults_file'] = None
   if aArgs.get('image_file') == 'None' :
    aArgs['image_file'] = None
   db.update_dict('device_models',aArgs,'id=%s'%id)

  ret['found'] = (db.query("SELECT dm.*, dt.name AS type FROM device_models AS dm LEFT JOIN device_types AS dt ON dt.id = dm.type_id WHERE dm.id = %s"%id) == 1)
  ret['data'] = db.get_row()
  ret['extra'] = {'type':ret['data'].pop('type',None)}
 return ret

#
#
def model_delete(aRT, aArgs):
 """ Delete a specific model

 Args:
  - id

 Output:
  - deleted
 """
 ret = {}
 with aRT.db as db:
  ret['deleted'] = bool(db.execute("DELETE FROM device_models WHERE id = %s"%aArgs['id']))
 return ret

################################################### VM ###################################################
#
#
def vm_mapping(aRT, aArgs):
 """ Function maps VMs on existing hypervisors using device management (!) interface MAC

 TODO+:
 1) go through all interfaces to see if they exists, as soon as there is a mapping, create them automatically for that VM

 Args:
  - device_id (optional) perform mapping for a particular host only
  - clear (optional). Default false

 Output:
 """
 ret = {'inventory':[],'database':None,'discovered':[],'existing':[],'update':{}}
 vms = {}
 with aRT.db as db:
  if aArgs.get('clear'):
   db.execute("TRUNCATE device_vm_uuid")
   existing = {}
  else:
   db.query("SELECT device_id, vm, bios_uuid FROM device_vm_uuid")
   existing = {row.pop('bios_uuid',None):row for row in db.get_rows()}
  db.query("SELECT di.device_id, di.interface_id, LPAD(hex(di.mac),12,0) AS mac FROM devices LEFT JOIN interfaces AS di ON di.device_id = devices.id WHERE devices.class = 'vm' and di.mac > 0")
  interfaces = {row.pop('mac',None):row for row in db.get_rows()}
  db.query("SELECT devices.id, INET6_NTOA(ia.ip) AS ip, dt.name AS type FROM devices LEFT JOIN ipam_addresses AS ia ON devices.ipam_id = ia.id LEFT JOIN device_types AS dt ON dt.id = devices.type_id WHERE dt.base = 'hypervisor' AND ia.state = 'up' AND %s"%("TRUE" if not aArgs.get('device_id') else "devices.id = %s"%aArgs['device_id']))
  for row in db.get_rows():
   try:
    module    = import_module("rims.devices.%s"%row['type'])
    inventory = getattr(module,'Device',None)(aRT,row['id'],row['ip']).get_inventory()
   except:
    pass
   else:
    for id,vm in inventory.items():
     vm.update({'host_id':row['id'],'snmp_id':id})
     vm['config'] = vm['config'][:140]
     vm['vm'] = vm['vm'][:30]
     for intf in vm.pop('interfaces',{}).values():
      db_vm = interfaces.pop(intf['mac'],None)
      if db_vm:
       vm['device_id'] = db_vm['device_id']
       existed = existing.pop(vm['bios_uuid'],None)
       if existed:
        ret['existing'].append(vm)
       else:
        ret['discovered'].append(vm)
       break
     else:
      ret['inventory'].append(vm)

  for vm in ret['discovered']:
   ret['update']['discovered'] = db.execute("INSERT INTO device_vm_uuid (device_id,host_id,snmp_id,bios_uuid,config,vm) VALUES(%(device_id)s,%(host_id)s,%(snmp_id)s,'%(bios_uuid)s','%(config)s','%(vm)s') ON DUPLICATE KEY UPDATE host_id = %(host_id)s, snmp_id = %(snmp_id)s, config = '%(config)s', vm = '%(vm)s'"%vm)
  for vm in ret['existing']:
   ret['update']['existing'] = db.execute("UPDATE device_vm_uuid SET device_id = %(device_id)s, host_id = %(host_id)s, snmp_id = %(snmp_id)s, config = '%(config)s', vm = '%(vm)s' WHERE bios_uuid = '%(bios_uuid)s'"%vm)
  for vm in ret['inventory']:
   ret['update']['inventory'] = db.execute("INSERT INTO device_vm_uuid (device_id,host_id,snmp_id,bios_uuid,config,vm) VALUES(NULL,%(host_id)s,%(snmp_id)s,'%(bios_uuid)s','%(config)s','%(vm)s') ON DUPLICATE KEY UPDATE device_id = NULL, host_id = %(host_id)s, snmp_id = %(snmp_id)s, config = '%(config)s', vm = '%(vm)s'"%vm)
 ret['database'] = [{'device_id':x['device_id'],'host_id':'-','bios_uuid':'-','vm':'-','config':'-'} for x in vms.values()]
 return ret

################################################### Classes ###################################################
#
#
def class_list(aRT, aArgs):
 """ Function list available device classes

 Args:
  - type (optional), 'device'/'interface'

 Output:
 """
 ret = {}
 with aRT.db as db:
  if aArgs.get('type','device') == 'device':
   db.query("SHOW COLUMNS FROM devices LIKE 'class'")
  else:
   db.query("SHOW COLUMNS FROM interfaces LIKE 'class'")
  parts = (db.get_val('Type')).split("'")
  ret['data'] = [parts[i] for i in range(1,len(parts),2)]
 return ret

#
#
def detect_info(aRT, aArgs):
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
 from rims.devices.detector import execute as execute_detect
 ret = execute_detect(aArgs['ip'],aRT.config['snmp'], aArgs.get('basic',False))
 if aArgs.get('decode',False):
  try: ret['data']['mac'] = ':'.join(("%s%s"%x).upper() for x in zip(*[iter("{:012x}".format(ret['data']['mac']))]*2))
  except: pass
 return ret
