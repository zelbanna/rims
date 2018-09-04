"""Device API module. This is the main device interaction module for device info, update, listing,discovery etc"""
__author__ = "Zacharias El Banna"
__version__ = "1.0GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

from zdcp.core.common import DB

#
#
def info(aDict):
 """Function docstring for info. Retrieves and updates device info (excluding rack info which is only fetched)

 Args:
  - ip (optional)
  - id (optional)
  - op (optional), None/'basic'/'update'
  - extra (optional) list of extra info, 'types' only today

 Output:
 """
 if   aDict.get('id'):
  srch = "devices.id = %s"%aDict.get('id')
 elif aDict.get('ip'):
  srch = "ia.ip = INET_ATON('%s')"%aDict.get('ip')
 elif aDict.get('ipam_id'):
  srch = "devices.ipam_id = %s"%aDict.get('ipam_id')
  aDict.pop('op',None)
 else:
  return {'found':False}
 ret = {'id':aDict.pop('id',None),'ip':aDict.pop('ip',None)}

 op = aDict.pop('op',None)
 with DB() as db:
  extra = aDict.pop('extra',[])
  if 'types' in extra or op == 'lookup':
   db.do("SELECT id, name FROM device_types ORDER BY name")
   ret['types'] = db.get_rows()

  if op == 'lookup' and ret['ip']:
   from zdcp.devices.generic import Device
   dev = Device(ret['ip'])
   lookup = dev.detect()
   ret['result'] = lookup
   if lookup['result'] == 'OK':
    args = {'model':lookup['info']['model'],'snmp':lookup['info']['snmp'],'type_id':0}
    for type in ret['types']:
     if type['name'] == lookup['info']['type']:
      args['type_id'] = type['id']
      break
    ret['update'] = (db.update_dict('devices',args,"id=%s"%ret['id']) == 1)

  elif op == 'update' and ret['id']:
   args = aDict
   args['vm'] = args.get('vm',0)
   if not args.get('comment'):
    args['comment'] = 'NULL'
   if not args.get('webpage'):
    args['webpage'] = 'NULL'
   if args.get('mac'):
    try: args['mac'] = int(args['mac'].replace(":",""),16)
    except: args['mac'] = 0
   ret['update'] = (db.update_dict('devices',args,"id=%s"%ret['id']) == 1)

  # Basic or complete info?
  if op == 'basics':
   sql = "SELECT devices.id, devices.webpage, devices.hostname, domains.name AS domain, INET_NTOA(ia.ip) as ip FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id LEFT JOIN domains ON devices.a_dom_id = domains.id WHERE %s"
  else:
   sql = "SELECT devices.*, dt.base AS type_base, dt.name as type_name, functions, a.name as domain, INET_NTOA(ia.ip) as ip FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id LEFT JOIN domains AS a ON devices.a_dom_id = a.id LEFT JOIN device_types AS dt ON dt.id = devices.type_id WHERE %s"
  ret['found'] = (db.do(sql%srch) == 1)
  if ret['found']:
   ret['info'] = db.get_row()
   ret['id'] = ret['info'].pop('id',None)
   ret['ip'] = ret['info'].pop('ip',None)
   # Pick login name from settings
   db.do("SELECT parameter,value FROM settings WHERE node = 'master' AND section = 'netconf'")
   netconf = db.get_dict('parameter')
   ret['username'] = netconf['username']['value']
   if not op == 'basics':
    ret['info']['mac'] = ':'.join(s.encode('hex') for s in str(hex(ret['info']['mac']))[2:].zfill(12).decode('hex')).lower() if ret['info']['mac'] != 0 else "00:00:00:00:00:00"
    if not ret['info']['functions']:
     ret['info']['functions'] = ""
    ret['reserved'] = (db.do("SELECT users.alias, reservations.user_id, NOW() < ADDTIME(time_start, '30 0:0:0.0') AS valid FROM reservations LEFT JOIN users ON reservations.user_id = users.id WHERE device_id ='{}'".format(ret['id'])) == 1)
    if ret['reserved']:
     ret['reservation'] = db.get_row()
    # Rack infrastructure ?
    if ret['info']['vm'] == 1:
     ret['racked'] = False
    else:
     ret['racked'] = (db.do("SELECT rack_unit,rack_size, console_id, console_port, rack_id, racks.name AS rack_name FROM rack_info LEFT JOIN racks ON racks.id = rack_info.rack_id WHERE rack_info.device_id = %i"%ret['id']) == 1)
     if ret['racked']:
      rack = db.get_row()
      ret['rack'] = rack
      infra_ids = [str(rack['console_id'])] if rack['console_id'] else []
      db.do("SELECT id,name,pdu_id,pdu_slot,pdu_unit FROM device_pems WHERE device_id = %(id)s"%ret)
      ret['pems'] = db.get_rows()
      pdu_ids = [str(x['pdu_id']) for x in ret['pems'] if x['pdu_id']]
      infra_ids.extend(pdu_ids)
      if len(infra_ids) > 0:
       db.do("SELECT devices.id, INET_NTOA(ia.ip) AS ip, hostname FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id WHERE devices.id IN (%s)"%','.join(infra_ids))
      devices = db.get_dict('id') if len(infra_ids) > 0 else {}
      if len(pdu_ids) > 0:
       db.do("SELECT * FROM pdu_info WHERE device_id IN (%s)"%','.join(pdu_ids))
      pdus = db.get_dict('device_id') if len(pdu_ids) > 0 else {}
      console = devices.get(rack['console_id'],{'hostname':None,'ip':None})
      rack.update({'console_name':console['hostname'],'console_ip':console['ip']})
      for pem in ret['pems']:
       pdu = pdus.get(pem['pdu_id'])
       pem['pdu_name'] = "%s:%s"%(devices[pem['pdu_id']]['hostname'],pdu['%s_slot_name'%pem['pdu_slot']]) if pdu else None
       pem['pdu_ip'] = devices[pem['pdu_id']]['ip'] if pdu else None
 return ret

#
#
def extended(aDict):
 """Function extended updates 'extended' device info (DNS, PTR, RACK info etc)

 Args:
  - id (required)
  - ip (required)
  - op (optional), 'update'
  - racked (optional)
  - a_id
  - ptr_id
  - a_dom_id
  - hostname
  - rack_info_<key>
  - pems_<id>_<key>

 Output:
  - extended device info
 """
 ret = {'id':aDict.pop('id',None), 'ip':aDict.pop('ip',None)}

 with DB() as db:
  operation = aDict.pop('op',None)
  if operation:
   args = aDict
   ret['result'] = {}
   if operation == 'add_pem' and ret['id']:
    ret['result'] = (db.do("INSERT INTO device_pems(device_id) VALUES(%s)"%ret['id']) > 0)
   if operation == 'remove_pem' and ret['id']:
    ret['result'] = (db.do("DELETE FROM device_pems WHERE device_id = %s AND id = %s "%(ret['id'],aDict['pem_id'])) > 0)

   if operation == 'update' and ret['id']:
    racked = args.pop('racked',None)
    if racked:
     if   racked == '1' and args.get('rack_info_rack_id') == 'NULL':
      db.do("DELETE FROM rack_info WHERE device_id = %s"%ret['id'])
     elif racked == '0' and args.get('rack_info_rack_id') != 'NULL':
      db.do("INSERT INTO rack_info SET device_id = %s,rack_id=%s ON DUPLICATE KEY UPDATE rack_id = rack_id"%(ret['id'],args.get('rack_info_rack_id')))
    # PEMs
    for id in [k.split('_')[1] for k in args.keys() if k.startswith('pems_') and 'name' in k]:
     pdu_slot = args.pop('pems_%s_pdu_slot'%id,"0.0").split('.')
     pem = {'name':args.pop('pems_%s_name'%id,None),'pdu_unit':aDict.pop('pems_%s_pdu_unit'%id,0),'pdu_id':pdu_slot[0],'pdu_slot':pdu_slot[1]}
     ret['result']["PEM_%s"%id] = db.update_dict('device_pems',pem,'id=%s'%id)
    # DNS management

    if args.get('a_dom_id') and args.get('hostname') and ret['ip']:
     # Fetch info first
     # .. then check if anything has changed
     db.do("SELECT hostname, a_id, ptr_id, a_dom_id, INET_NTOA(ia.ip) AS ip FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id WHERE devices.id = %s"%ret['id'])
     old_info = db.get_row()

     if not (old_info['hostname'] == args['hostname']) or not (str(old_info['a_dom_id']) == str(args['a_dom_id'])):
      dns_args = {'a_id':old_info['a_id'],'ptr_id':old_info['ptr_id'],'a_domain_id_new':args['a_dom_id'],'a_domain_id_old':old_info['a_dom_id'],'hostname':args['hostname'],'ip_new':ret['ip'],'ip_old':old_info['ip'],'id':ret['id']}
      from zdcp.rest.dns import record_device_update
      dns_res = record_device_update(dns_args)
      new_info = {'hostname':args['hostname'],'a_dom_id':dns_res['A']['domain_id']}
      for type in ['a','ptr']:
       if dns_res[type.upper()]['found']:
        if not (str(dns_res[type.upper()]['record_id']) == str(dns_args['%s_id'%type])):
         new_info['%s_id'%type] = dns_res[type.upper()]['record_id']
       else:
        new_info['%s_id'%type] = 0
      ret['result']['device_info'] = db.update_dict('devices',new_info,"id='%s'"%ret['id'])
    rack_args = {k[10:]:v for k,v in args.iteritems() if k[0:10] == 'rack_info_'}
    ret['result']['rack_info'] = db.update_dict('rack_info',rack_args,"device_id='%s'"%ret['id']) if len(rack_args) > 0 else "NO_RACK_INFO"

  # Now fetch info
  ret['found'] = (db.do("SELECT vm, hostname, a_id, ptr_id, a_dom_id, ipam_id, a.name AS domain, INET_NTOA(ia.ip) AS ip, dt.base AS type_base FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id LEFT JOIN domains AS a ON devices.a_dom_id = a.id LEFT JOIN device_types AS dt ON dt.id = devices.type_id WHERE devices.id = %s"%ret['id']) == 1)
  if ret['found']:
   ret['info'] = db.get_row()
   ret['ip'] = ret['info'].pop('ip',None)
   vm = ret['info'].pop('vm',None)
   # Rack infrastructure
   ret['infra'] = {'racks':[{'id':'NULL', 'name':'Not used'}]}
   if vm == 1:
    ret['racked'] = 0
   else:
    db.do("SELECT id, name FROM racks")
    ret['infra']['racks'].extend(db.get_rows())
    ret['racked'] = db.do("SELECT rack_info.* FROM rack_info WHERE rack_info.device_id = %(id)s"%ret)
    if ret['racked'] > 0:
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
  if operation == 'update' and ret['racked']:
   for pem in ret['pems']:
    if pem['pdu_id']:
     db.do("SELECT INET_NTOA(ia.ip) AS ip, hostname, name FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id LEFT JOIN device_types ON devices.type_id = device_types.id WHERE devices.id = %i"%(pem['pdu_id']))
     pdu_info = db.get_row()
     # Slot id is actually local slot ID, so we need to look up infra -> pdu_info -> pdu and then pdu[x_slot_id] to get the right ID
     args_pem = {'ip':pdu_info['ip'],'unit':pem['pdu_unit'],'slot':ret['infra']['pdu_info'][pem['pdu_id']]['%s_slot_id'%pem['pdu_slot']],'text':"%s-%s"%(ret['info']['hostname'],pem['name'])}
     try:
      module = import_module("zdcp.rest.%s"%pdu_info['name'])
      pdu_update = getattr(module,'update',None)
      ret['result']["PDU_%s"%pem['id']] = "%s.%s"%(pdu_info['hostname'],pdu_update(args_pem))
     except Exception as err:
      ret['result']["PDU_%s"%pem['id']] = "Error: %s"%str(err)
 return ret

#
#
def list(aDict):
 """Function docstring for list TBD

 Args:
  - field (optional) 'id/ip/mac/hostname/type/base/vm' as search fields 
  - search (optional) content to match on field, special case for mac where non-correct MAC will match all that are not '00:00:00:00:00:00'
  - extra (optional) list of extra info to add, None/'type'/'webpage'
  - rack (optional), id of rack to filter devices from
  - sort (optional) (sort on id or hostname or...)
  - dict (optional) (output as dictionary instead of list)

 Output:
 """
 ret = {}
 sort = 'ORDER BY ia.ip' if aDict.get('sort','ip') == 'ip' else 'ORDER BY devices.hostname'
 fields = ['devices.id', 'devices.hostname', 'INET_NTOA(ia.ip) AS ip', 'domains.name AS domain','model']
 tune = ['ipam_addresses AS ia ON ia.id = devices.ipam_id','domains ON domains.id = devices.a_dom_id']
 filter = ['TRUE']
 if aDict.get('rack'):
  tune.append("rack_info AS ri ON ri.device_id = devices.id")
  filter.append("ri.rack_id = %(rack)s"%aDict)
 if aDict.get('search'):
  if aDict['field'] == 'hostname':
   filter.append("devices.hostname LIKE '%%%(search)s%%'"%aDict)
  elif aDict['field'] == 'ip':
   filter.append("ia.ip = INET_ATON('%(search)s')"%aDict)
  elif aDict['field'] == 'type':
   tune.append("device_types AS dt ON dt.id = devices.type_id")
   filter.append("dt.name = '%(search)s'"%aDict)
  elif aDict['field'] == 'base':
   tune.append("device_types AS dt ON dt.id = devices.type_id")
   filter.append("dt.base = '%(search)s'"%aDict)
  elif aDict['field'] == 'mac':
   try:    filter.append("mac = %i"%int(aDict['search'].replace(":",""),16))
   except: filter.append("mac <> 0")
  else:
   filter.append("devices.%(field)s IN (%(search)s)"%aDict)

 extras = aDict.get('extra')
 if  extras:
  if 'type' in extras:
   fields.append('dt.name AS type_name, dt.base AS type_base')
   if not (aDict.get('field') == 'type' or aDict.get('field') == 'base'):
    tune.append("device_types AS dt ON dt.id = devices.type_id")
  if 'webpage' in extras:
   fields.append('devices.webpage')
  if 'mac' in extras:
   fields.append('devices.mac')

 with DB() as db:
  sql = "SELECT %s FROM devices LEFT JOIN %s WHERE %s %s"%(", ".join(fields)," LEFT JOIN ".join(tune)," AND ".join(filter),sort)
  ret['count'] = db.do(sql)
  data = db.get_rows()
  if extras and 'mac' in extras:
   def GL_int2mac(aInt):
    return ':'.join(s.encode('hex') for s in str(hex(aInt))[2:].zfill(12).decode('hex')).lower()
   for row in data:
    row['mac'] = GL_int2mac(row['mac'])
  ret['data'] = data if not aDict.get('dict') else { row[aDict['dict']]: row for row in data }
 return ret

#
#
def search(aDict):
 """ Functions returns device id for device matching conditions

 Args:
  - device

 Output:
 """
 ret = {}
 with DB() as db:
  ret['found'] = db.do("SELECT devices.id, devices.hostname, domains.name AS domain FROM devices LEFT JOIN domains ON domains.id = devices.a_dom_id WHERE hostname LIKE '%%%(device)s%%' OR CONCAT(hostname,'.',domains.name) LIKE '%%%(device)s%%'"%aDict)
  ret['device']= db.get_row()
 return ret

#
#
def new(aDict):
 """Function docstring for new TBD

 Args:
  - a_dom_id (required)
  - hostname (required)
  - ipam_network_id (optional)
  - ip (optional)
  - vm (optional)
  - mac (optional)
  - rack (optional)
  - consecutive (optional)

 Output:
 """
 alloc = None
 # Test if hostname ok or if IP supplied and then if ok and available
 if aDict['hostname'] == 'unknown':
  return {'info':'Hostname unknown not allowed'}
 elif aDict.get('ipam_network_id') and aDict.get('ip'):
  from zdcp.rest.ipam import address_allocate
  alloc = address_allocate({'ip':aDict['ip'],'network_id':aDict['ipam_network_id']})
  if   not alloc['valid']:
   return {'info':'IP not in network range'}
  elif not alloc['success']:
   return {'info':'IP not available'}

 ret = {'info':None}
 with DB() as db:
  ret['fqdn'] = (db.do("SELECT id AS existing_device_id, hostname, a_dom_id FROM devices WHERE hostname = '%(hostname)s' AND a_dom_id = %(a_dom_id)s"%aDict) == 0)
  if ret['fqdn']:
   try:    mac = int(aDict.get('mac','0').replace(":",""),16)
   except: mac = 0
   if alloc:
    from zdcp.rest.dns import record_device_update
    dns = record_device_update({'id':'new','a_id':'new','ptr_id':'new','a_domain_id_new':aDict['a_dom_id'],'hostname':aDict['hostname'],'ip_new':aDict['ip']})
    ret['insert'] = db.do("INSERT INTO devices(vm,mac,a_dom_id,a_id,ptr_id,ipam_id,hostname,snmp,model) VALUES(%s,%s,%s,%s,%s,%s,'%s','unknown','unknown')"%(aDict.get('vm','0'),mac,aDict['a_dom_id'],dns['A']['record_id'],dns['PTR']['record_id'],alloc['id'],aDict['hostname']))
   else:
    ret['insert'] = db.do("INSERT INTO devices(vm,mac,hostname,snmp,model) VALUES(%s,%s,'%s','unknown','unknown')"%(aDict.get('vm','0'),mac,aDict['hostname']))
   ret['id']   = db.get_last_id()
   if aDict.get('rack'):
    ret['racked'] = (db.do("INSERT INTO rack_info SET device_id = %s, rack_id = %s ON DUPLICATE KEY UPDATE rack_unit = 0, rack_size = 1"%(ret['id'],aDict['rack'])) == 1)
  else:
   ret.update(db.get_row())

 # also remove allocation if fqdn busy..
 if alloc['success'] and not ret['fqdn']:
  from zdcp.rest.ipam import address_delete
  ret['info'] = "deallocating ip (%s)"%address_delete({'id':alloc['id']})['result']
 return ret

#
#
def delete(aDict):
 """Function docstring for delete TBD

 Args:
  - id (required)

 Output:
 """
 with DB() as db:
  found = (db.do("SELECT hostname, ine.reverse_zone_id, ipam_id, mac, a_id, ptr_id, a_dom_id, device_types.* FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id LEFT JOIN ipam_networks AS ine ON ine.id = ia.network_id LEFT JOIN device_types ON devices.type_id = device_types.id WHERE devices.id = %s"%aDict['id']) > 0)
  if not found:
   ret = { 'deleted':0, 'dns':{'a':0, 'ptr':0}}
  else:
   data = db.get_row()
   args = {'a_id':data['a_id'],'a_domain_id':data['a_dom_id']}
   from zdcp.rest.dns import record_device_delete
   if data['ptr_id'] != 0 and data['reverse_zone_id']:
    args['ptr_id']= data['ptr_id']
    args['ptr_domain_id'] = data['reverse_zone_id']
   ret = record_device_delete(args)
   if data['base'] == 'pdu':
    ret['pem0'] = db.update_dict('rack_info',{'pem0_pdu_unit':0,'pem0_pdu_slot':0},'pem0_pdu_id = %s'%(aDict['id']))
    ret['pem1'] = db.update_dict('rack_info',{'pem1_pdu_unit':0,'pem1_pdu_slot':0},'pem1_pdu_id = %s'%(aDict['id']))
   ret.update({'deleted':(db.do("DELETE FROM devices WHERE id = %(id)s"%aDict) > 0)})
 # Avoid race condition on DB, do this when DB is closed...
 if found and data['ipam_id']:
  from zdcp.rest.ipam import address_delete
  ret.update(address_delete({'id':data['ipam_id']}))
 return ret

#
#
def discover(aDict):
 """Function docstring for discover TBD

 Args:
  - a_dom_id (required)
  - network_id (required)

 Output:
 """
 from time import time
 from threading import Thread, BoundedSemaphore
 from zdcp.rest.ipam import network_discover as ipam_discover, address_allocate
 from zdcp.devices.generic import Device

 def __detect_thread(aIP,aDB,aSema):
  __dev = Device(aIP)
  aDB[aIP['ip']] = __dev.detect()['info']
  aSema.release()
  return True

 start_time = int(time())
 ipam = ipam_discover({'id':aDict['network_id']})
 ret = {'errors':0, 'start':ipam['start'],'end':ipam['end'] }

 with DB() as db:
  db.do("SELECT id,name FROM device_types")
  devtypes = db.get_dict('name')
 dev_list = {}
 try:
  sema = BoundedSemaphore(20)
  for ip in ipam['addresses']:
   sema.acquire()
   t = Thread(target = __detect_thread, args=[ip, dev_list, sema])
   t.name = "Detect %s"%ip
   t.start()
  for i in range(20):
   sema.acquire()
 except Exception as err:
  ret['error']   = "Error:{}".format(str(err))

 # We can now do inserts only (no update) as we skip existing :-)
 with DB() as db:
  sql = "INSERT INTO devices (a_dom_id, ipam_id, snmp, model, type_id, hostname) VALUES ("+aDict['a_dom_id']+",{},'{}','{}','{}','{}')"
  count = 0
  for ip,entry in dev_list.iteritems():
   count += 1
   alloc = address_allocate({'ip':ip,'network_id':aDict['network_id']})
   if alloc['success']:
    db.do(sql.format(alloc['id'],entry['snmp'],entry['model'],devtypes[entry['type']]['id'],"unknown_%i"%count))
 ret['time'] = int(time()) - start_time
 ret['found']= len(dev_list)
 return ret

#
#
def types_list(aDict):
 """Function lists currenct device types

 Args:
  - sort (optional), class/name

 Output:
 """
 ret = {}
 sort = 'name' if aDict.get('sort','name') == 'name' else 'base'
 with DB() as db:
  ret['count'] = db.do("SELECT * FROM device_types ORDER BY %s"%sort)
  ret['types'] = db.get_rows()
 return ret

#
#
def server_macs(aDict):
 """Function returns all MACs for devices belonging to networks beloning to particular server

 Args:
  - id (required)

 Output:
 """
 ret = {}
 def GL_int2mac(aInt):
  return ':'.join(s.encode('hex') for s in str(hex(aInt))[2:].zfill(12).decode('hex')).lower()
 with DB() as db:
  ret['count'] = db.do("SELECT devices.id, hostname, mac, name AS domain, INET_NTOA(ia.ip) AS ip, ia.network_id AS network FROM devices LEFT JOIN domains ON domains.id = devices.a_dom_id LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id LEFT JOIN ipam_networks ON ipam_networks.id = ia.network_id WHERE mac > 0 AND ipam_networks.server_id = %s"%aDict['id'])
  ret['data']  = db.get_rows()
  for row in ret['data']:
   row['mac'] = GL_int2mac(row['mac'])
 return ret

############################################## Specials ###############################################
#
#
def node_mapping(aDict):
 """Node mapping translates between nodes and devices and provide the same info, it depends on the device existing or node having mapped a device (else 'found' is false)

 Args:
  - id (optional required)
  - node (optional required)

 Output:
  - found. boolean
  - id. device id
  - node. node name
  - hostname. device hostname
  - ip. device ip
  - domain. Device domain name
  - webpage
 """
 with DB() as db:
  if aDict.get('id'):
   found = (db.do("SELECT hostname, INET_NTOA(ia.ip) as ip, domains.name AS domain, webpage FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id LEFT JOIN domains ON domains.id = devices.a_dom_id WHERE devices.id = %s"%aDict['id']) > 0)
   ret = db.get_row() if found else {}
   ret['found'] = (db.do("SELECT node FROM nodes WHERE device_id = %s"%aDict['id']) > 0)
   ret['node']  = db.get_val('node') if ret['found'] else None
   ret['id']    = int(aDict['id'])
  else:
   found = (db.do("SELECT device_id FROM nodes WHERE node = '%s'"%aDict['node']) > 0)
   ret = {'id':db.get_val('device_id') if found else None, 'node':aDict['node'], 'found':False}
   if ret['id']:
    ret['found'] = (db.do("SELECT hostname, INET_NTOA(ia.ip) as ip, domains.name AS domain, webpage FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id LEFT JOIN domains ON domains.id = devices.a_dom_id WHERE devices.id = %s"%ret['id']) > 0)
    ret.update(db.get_row())
 return ret

#
#
def function(aDict):
 """Function docstring for function TBD

 Args:
  - ip (required)
  - op (required)
  - type (required)

 Output:
 """
 ret = {}
 try:
  module = import_module("zdcp.devices.%s"%(aDict['type']))
  dev = getattr(module,'Device',lambda x: None)(aDict['ip'])
  with dev:
   ret['data'] = getattr(dev,aDict['op'],None)()
  ret['result'] = 'OK'
 except Exception as err:
  ret = {'result':'ERROR','info':str(err)}
 return ret

#
#
def configuration_template(aDict):
 """Function docstring for configuration_template TBD

 Args:
  - id (required)

 Output:
 """
 ret = {}
 with DB() as db:
  db.do("SELECT ine.mask,INET_NTOA(ine.gateway) AS gateway,INET_NTOA(ine.network) AS network, INET_NTOA(ia.ip) AS ip, hostname, device_types.name AS type, domains.name AS domain FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id LEFT JOIN ipam_networks AS ine ON ine.id = ia.network_id LEFT JOIN domains ON domains.id = devices.a_dom_id LEFT JOIN device_types ON device_types.id = devices.type_id WHERE devices.id = '%s'"%aDict['id'])
  data = db.get_row()
 ip = data.pop('ip',None)
 try:
  module = import_module("zdcp.devices.%s"%data['type'])
  dev = getattr(module,'Device',lambda x: None)(ip)
  ret['data'] = dev.configuration(data)
 except Exception as err:
  ret['info'] = "Error loading configuration template, make sure settings are ok (netconf -> encrypted, ntpsrv, dnssrv, anonftp): %s"%str(err)
  ret['result'] = 'NOT_OK'
 else:
  ret['result'] = 'OK'

 return ret 

############################################### INTERFACES ################################################
#
#
def interface_list(aDict):
 """List interfaces for a specific device

 Args:
  - device    (ip or id... :-))
  - sort (optional, default to 'snmp_index')
 Output:
 """
 def is_int(val):
  try: int(val)
  except: return False
  else:   return True

 with DB() as db:
  if is_int(aDict.get('device')):
   db.do("SELECT devices.id, hostname FROM devices WHERE id = %s"%aDict['device'])
  else:
   db.do("SELECT devices.id, hostname FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id WHERE ia.ip = INET_ATON('%s')"%aDict['device'])
  ret = db.get_row()
  if ret:
   sort = aDict.get('sort','snmp_index')
   ret['count'] = db.do("SELECT id,name,description,snmp_index,peer_interface,multipoint FROM device_interfaces WHERE device = %s ORDER BY %s"%(ret['id'],sort))
   ret['data'] = db.get_rows()
  else:
   ret = {'id':None,'hostname':None,'data':[],'count':0}
 return ret

#
#
def interface_info(aDict):
 """Show or update a specific interface for a device

 Args:
  - id (required)
  - device (required)
  - name
  - description
  - snmp_index
  - peer_interface
  - multipoint (0/1)

 Output:
 """
 ret = {}
 args = aDict
 id = args.pop('id','new')
 op = args.pop('op',None)
 with DB() as db:
  if op == 'update':
   # If multipoint there should not be any single peer interface
   args['multipoint'] = aDict.get('multipoint',0)
   if int(args['multipoint']) == 1:
    args['peer_interface'] = 'NULL'
   if not id == 'new':
    ret['update'] = db.update_dict('device_interfaces',args,"id=%s"%id)
   else:
    args['manual'] = 1
    ret['insert'] = db.insert_dict('device_interfaces',args)
    id = db.get_last_id() if ret['insert'] > 0 else 'new'

  if not id == 'new':
   ret['found'] = (db.do("SELECT dc.*, peer.device AS peer_device FROM device_interfaces AS dc LEFT JOIN device_interfaces AS peer ON dc.peer_interface = peer.id WHERE dc.id = '%s'"%id) > 0)
   ret['data'] = db.get_row()
   ret['data'].pop('manual',None)
  else:
   ret['data'] = {'id':'new','device':int(aDict['device']),'name':'Unknown','description':'Unknown','snmp_index':None,'peer_interface':None,'peer_device':None,'multipoint':0}
 return ret

#
#
def interface_delete(aDict):
 """Delete device interfaces using either id of interface, a list of interfaces or all free interfaces

 Args:
  - id (optional required) id of interface
  - interface_<xy> (optional required).  argument value must be <xy> as well (!)
  - device_id (optional required). Device to delete 'free' interfaces from

 Output:
  - interfaces. List of id:s of deleted interfaces
  - cleared. Number of cleared peer connections
  - deleted. Number of deleted interfaces
 """
 ret = {'interfaces':[],'cleared':0,'deleted':0}
 op  = aDict.pop('op',None)
 with DB() as db:
  if aDict.get('device_id'):
   ret['deleted'] = db.do("DELETE FROM device_interfaces WHERE device = %s AND peer_interface IS NULL AND multipoint = 0 AND manual = 0"%aDict['device_id'])
  else:
   for intf,value in aDict.iteritems():
    if intf[0:10] == 'interface_' or intf == 'id':
     id = int(value)
    else: continue
    ret['cleared'] += db.do("UPDATE device_interfaces SET peer_interface = NULL WHERE peer_interface = %s"%id)
    ret['deleted'] += db.do("DELETE FROM device_interfaces WHERE id = %s"%id)
    ret['interfaces'].append(id)
 return ret

#
#
def interface_link(aDict):
 """Function docstring for interface_link. Link two device interfaces simultaneously to each other, remove old interfaces before (unless multipoint)

 Args:
  - a_id (required)
  - b_id (required)

 Output:
 """
 ret = {'a':{},'b':{}}
 with DB() as db:
  sql_clear = "UPDATE device_interfaces SET peer_interface = NULL WHERE peer_interface = %s AND multipoint = 0"
  sql_set   = "UPDATE device_interfaces SET peer_interface = %s WHERE id = %s AND multipoint = 0"
  ret['a']['clear'] = db.do(sql_clear%(aDict['a_id']))
  ret['b']['clear'] = db.do(sql_clear%(aDict['b_id']))
  ret['a']['set']   = (db.do(sql_set%(aDict['b_id'],aDict['a_id'])) == 1)
  ret['b']['set']   = (db.do(sql_set%(aDict['a_id'],aDict['b_id'])) == 1)
 return ret

#
#
def interface_link_advanced(aDict):
 """Function docstring for interface_link_advanced. Link two IP and SNMP index:s (i.e. physical or logical interfaces) to each other simultaneously

 Args:
  - a_ip (required)
  - a_index (required)
  - b_ip (required)
  - b_index (required)

 Output:
 """
 ret = {'error':None,'a':{},'b':{}}
 with DB() as db:
  sql_dev  ="SELECT devices.id FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id WHERE ia.ip = INET_ATON('%s')"
  sql_indx = "SELECT id FROM device_interfaces WHERE device = '%s' AND snmp_index = '%s'"
  for peer in ['a','b']:
   found = (db.do(sql_dev%aDict['%s_ip'%peer]) > 0)
   if found:
    ret[peer]['device'] = db.get_val('id')
    found = (db.do(sql_indx%(ret[peer]['device'],aDict['%s_index'%peer])) > 0)
    if found:
     ret[peer]['index'] = db.get_val('id')
    else:
     db.insert_dict('device_interfaces',{'device':ret[peer]['device'],'name':'Unknown','description':'Unknown','snmp_index':aDict['%s_index'%peer]})
     ret[peer]['index'] = db.get_last_id()
   else:
    ret['error'] = "IP not found (%s)"%aDict['%s_ip'%peer]
  if not ret['error']:
   sql_clear = "UPDATE device_interfaces SET peer_interface = NULL WHERE peer_interface = %s AND multipoint = 0"
   sql_set   = "UPDATE device_interfaces SET peer_interface = %s WHERE id = %s AND multipoint = 0"
   ret['a']['clear'] = db.do(sql_clear%(aDict['a_id']))
   ret['b']['clear'] = db.do(sql_clear%(aDict['b_id']))
   ret['a']['set']   = (db.do(sql_set%(aDict['b_id'],aDict['a_id'])) == 1)
   ret['b']['set']   = (db.do(sql_set%(aDict['a_id'],aDict['b_id'])) == 1)

 return ret

#
#
def interface_discover(aDict):
 """ Discovery function for detecting interfaces. Will try SNMP to detect all interfaces first.

 Args:
  - device (required)
  - cleanup (optional, boolean). Deletes non-existing interfaces (except manually added) by default

 Output:
 """
 ret = {'insert':0,'update':0,'delete':0}
 with DB() as db:
  db.do("SELECT INET_NTOA(ia.ip) AS ip, hostname, device_types.name AS type FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id LEFT JOIN device_types ON type_id = device_types.id  WHERE devices.id = %s"%aDict['device'])
  info = db.get_row()
  db.do("SELECT id, snmp_index, name, description FROM device_interfaces WHERE device = %s"%aDict['device'])
  existing = db.get_rows()
  try:
   module  = import_module("zdcp.devices.%s"%(info['type']))
   dev = getattr(module,'Device',lambda x: None)(info['ip'])
   interfaces = dev.interfaces()
  except Exception as err:
   ret['error'] = str(err)
  else:
   for con in existing:
    entry = interfaces.pop(con['snmp_index'],None)
    if entry:
     if not ((entry['name'] == con['name']) and (entry['description'] == con['description'])):
      ret['update'] += db.do("UPDATE device_interfaces SET name = '%s', description = '%s' WHERE id = %s"%(entry['name'][0:24],entry['description'],con['id']))
    elif aDict.get('cleanup',True) == True:
     ret['delete'] += db.do("DELETE FROM device_interfaces WHERE id = %s AND manual = 0"%(con['id']))
   for key, entry in interfaces.iteritems():
    args = {'device':int(aDict['device']),'name':entry['name'][0:24],'description':entry['description'],'snmp_index':key}
    ret['insert'] += db.insert_dict('device_interfaces',args)
 return ret
