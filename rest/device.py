"""Device API module. This is the main device interaction module for device info, update, listing,discovery etc"""
__author__ = "Zacharias El Banna"
__version__ = "4.0GA"
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
   dev = Device(ret['ip'],gSettings)
   lookup = dev.detect()
   ret['result'] = lookup
   if lookup['result'] == 'OK':
    args = lookup['info']
    try:   args['mac'] = int(args['mac'].replace(":",""),16)
    except:args['mac'] = 0
    type_name = args.pop('type',None)
    for type in ret['types']:
     if type['name'] == type_name:
      args['type_id'] = type['id']
      break
    ret['update'] = (db.update_dict('devices',args,"id=%s"%ret['id']) == 1)

  elif op == 'update' and ret['id']:
   aDict.pop('state',None)
   aDict['vm'] = aDict.get('vm',0)
   aDict['shutdown'] = aDict.get('shutdown',0)
   if not aDict.get('comment'):
    aDict['comment'] = 'NULL'
   if not aDict.get('url'):
    aDict['url'] = 'NULL'
   if aDict.get('mac'):
    # This is the IP mac and not the device MAC...
    try:   mac = int(aDict.pop('mac','0').replace(":",""),16)
    except:mac = 0
    db.do("UPDATE ipam_addresses SET mac = '%s' WHERE id = (SELECT ipam_id FROM devices WHERE id = %s)"%(mac,ret['id']))
   ret['update'] = (db.update_dict('devices',aDict,"id=%s"%ret['id']) == 1)

  # Basic or complete info?
  if op == 'basics':
   sql = "SELECT devices.id, devices.url, devices.hostname, domains.name AS domain, ia.state, INET_NTOA(ia.ip) as ip, ia.network_id FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id LEFT JOIN domains ON devices.a_dom_id = domains.id WHERE %s"
  else:
   sql = "SELECT devices.*, dt.base AS type_base, dt.name as type_name, functions, a.name as domain, ia.mac AS ip_mac, ia.state, INET_NTOA(ia.ip) as ip FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id LEFT JOIN domains AS a ON devices.a_dom_id = a.id LEFT JOIN device_types AS dt ON dt.id = devices.type_id WHERE %s"
  ret['found'] = (db.do(sql%srch) == 1)
  if ret['found']:
   ret['info'] = db.get_row()
   ret['id'] = ret['info'].pop('id',None)
   ret['ip'] = ret['info'].pop('ip',None)
   ret['state'] = {0:'grey',1:'green',2:'red'}.get(ret['info']['state'],'orange')
   # Pick login name from settings
   db.do("SELECT parameter,value FROM settings WHERE node = 'master' AND section = 'netconf'")
   netconf = db.get_dict('parameter')
   ret['username'] = netconf['username']['value']
   if not op == 'basics':
    try:    ret['info']['mac'] = ':'.join(s.encode('hex') for s in str(hex(ret['info']['ip_mac']))[2:].zfill(12).decode('hex')).lower() if ret['info']['ip_mac'] != 0 else "00:00:00:00:00:00"
    except: ret['info']['mac'] = "00:00:00:00:00:00"
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
   ret['result'] = {}
   if operation == 'add_pem' and ret['id']:
    ret['result'] = (db.do("INSERT INTO device_pems(device_id) VALUES(%s)"%ret['id']) > 0)
   if operation == 'remove_pem' and ret['id']:
    ret['result'] = (db.do("DELETE FROM device_pems WHERE device_id = %s AND id = %s "%(ret['id'],aDict['pem_id'])) > 0)

   if operation == 'update' and ret['id']:
    racked = aDict.pop('racked',None)
    if racked:
     if   racked == '1' and aDict.get('rack_info_rack_id') == 'NULL':
      db.do("DELETE FROM rack_info WHERE device_id = %s"%ret['id'])
     elif racked == '0' and aDict.get('rack_info_rack_id') != 'NULL':
      db.do("INSERT INTO rack_info SET device_id = %s,rack_id=%s ON DUPLICATE KEY UPDATE rack_id = rack_id"%(ret['id'],aDict.get('rack_info_rack_id')))
    # PEMs
    for id in [k.split('_')[1] for k in aDict.keys() if k.startswith('pems_') and 'name' in k]:
     pdu_slot = aDict.pop('pems_%s_pdu_slot'%id,"0.0").split('.')
     pem = {'name':aDict.pop('pems_%s_name'%id,None),'pdu_unit':aDict.pop('pems_%s_pdu_unit'%id,0),'pdu_id':pdu_slot[0],'pdu_slot':pdu_slot[1]}
     ret['result']["PEM_%s"%id] = db.update_dict('device_pems',pem,'id=%s'%id)
    # DNS management

    if aDict.get('a_dom_id') and aDict.get('hostname') and ret['ip']:
     # Fetch info first
     # .. then check if anything has changed
     db.do("SELECT hostname, a_id, ptr_id, a_dom_id, INET_NTOA(ia.ip) AS ip FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id WHERE devices.id = %s"%ret['id'])
     old_info = db.get_row()

     if not (old_info['hostname'] == aDict['hostname']) or not (str(old_info['a_dom_id']) == str(aDict['a_dom_id'])):
      dns_args = {'a_id':old_info['a_id'],'ptr_id':old_info['ptr_id'],'a_domain_id_new':aDict['a_dom_id'],'a_domain_id_old':old_info['a_dom_id'],'hostname':aDict['hostname'],'ip_new':ret['ip'],'ip_old':old_info['ip'],'id':ret['id']}
      from zdcp.rest.dns import record_device_update
      dns_res = record_device_update(dns_args)
      new_info = {'hostname':aDict['hostname'],'a_dom_id':dns_res['A']['domain_id']}
      for type in ['a','ptr']:
       if dns_res[type.upper()]['found']:
        if not (str(dns_res[type.upper()]['record_id']) == str(dns_args['%s_id'%type])):
         new_info['%s_id'%type] = dns_res[type.upper()]['record_id']
       else:
        new_info['%s_id'%type] = 0
      ret['result']['device_info'] = db.update_dict('devices',new_info,"id='%s'"%ret['id'])
    rack_args = {k[10:]:v for k,v in aDict.iteritems() if k[0:10] == 'rack_info_'}
    ret['result']['rack_info'] = db.update_dict('rack_info',rack_args,"device_id='%s'"%ret['id']) if len(rack_args) > 0 else "NO_RACK_INFO"

  # Now fetch info
  ret['found'] = (db.do("SELECT vm, devices.mac, devices.oid, hostname, a_id, ptr_id, a_dom_id, ipam_id, a.name AS domain, INET_NTOA(ia.ip) AS ip, dt.base AS type_base FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id LEFT JOIN domains AS a ON devices.a_dom_id = a.id LEFT JOIN device_types AS dt ON dt.id = devices.type_id WHERE devices.id = %s"%ret['id']) == 1)
  if ret['found']:
   ret['info'] = db.get_row()
   ret['ip'] = ret['info'].pop('ip',None)
   vm = ret['info'].pop('vm',None)
   try:    ret['info']['mac'] = ':'.join(s.encode('hex') for s in str(hex(ret['info']['mac']))[2:].zfill(12).decode('hex')).upper() if ret['info']['mac'] != 0 else "00:00:00:00:00:00"
   except: ret['info']['mac'] = "00:00:00:00:00:00"
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
   from importlib import import_module
   for pem in ret['pems']:
    if pem['pdu_id']:
     db.do("SELECT INET_NTOA(ia.ip) AS ip, hostname, name FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id LEFT JOIN device_types ON devices.type_id = device_types.id WHERE devices.id = %i"%(pem['pdu_id']))
     pdu_info = db.get_row()
     # Slot id is actually local slot ID, so we need to look up infra -> pdu_info -> pdu and then pdu[x_slot_id] to get the right ID
     args_pem = {'ip':pdu_info['ip'],'unit':pem['pdu_unit'],'slot':ret['infra']['pdu_info'][pem['pdu_id']]['%s_slot_id'%pem['pdu_slot']],'text':"%s-%s"%(ret['info']['hostname'],pem['name'])}
     try:
      module = import_module("zdcp.rest.%s"%pdu_info['name'])
      module.__add_globals__({'gSettings':gSettings,'gWorkers':gWorkers})
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
  - extra (optional) list of extra info to add, None/'type'/'url'/'system'
  - rack (optional), id of rack to filter devices from
  - sort (optional) (sort on id or hostname or...)
  - dict (optional) (output as dictionary instead of list)

 Output:
 """
 ret = {}
 sort = 'ORDER BY ia.ip' if aDict.get('sort','ip') == 'ip' else 'ORDER BY devices.hostname'
 fields = ['devices.id', 'devices.hostname', 'INET_NTOA(ia.ip) AS ip', 'domains.name AS domain','model','ia.state']
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
   try:    filter.append("ia.mac = %i"%int(aDict['search'].replace(":",""),16))
   except: filter.append("ia.mac <> 0")
  else:
   filter.append("devices.%(field)s IN (%(search)s)"%aDict)

 extras = aDict.get('extra')
 if  extras:
  if 'type' in extras:
   fields.append('dt.name AS type_name, dt.base AS type_base')
   if not (aDict.get('field') == 'type' or aDict.get('field') == 'base'):
    tune.append("device_types AS dt ON dt.id = devices.type_id")
  if 'url' in extras:
   fields.append('devices.url')
  if 'mac' in extras:
   fields.append('ia.mac')
  if 'system' in extras:
   fields.extend(['devices.serial','devices.version','ia.state','devices.oid'])

 with DB() as db:
  sql = "SELECT %s FROM devices LEFT JOIN %s WHERE %s %s"%(", ".join(fields)," LEFT JOIN ".join(tune)," AND ".join(filter),sort)
  ret['count'] = db.do(sql)
  data = db.get_rows()
  if extras and 'mac' in extras:
   for row in data:
    try: row['mac'] = ':'.join(s.encode('hex') for s in str(hex(row['mac']))[2:].zfill(12).decode('hex')).lower()
    except: pass
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
  alloc = address_allocate({'ip':aDict['ip'],'network_id':aDict['ipam_network_id'],'mac':aDict.get('mac',0)})
  if   not alloc['valid']:
   return {'info':'IP not in network range'}
  elif not alloc['success']:
   return {'info':'IP not available'}

 ret = {'info':None}
 with DB() as db:
  ret['fqdn'] = (db.do("SELECT id AS existing_device_id, hostname, a_dom_id FROM devices WHERE hostname = '%(hostname)s' AND a_dom_id = %(a_dom_id)s"%aDict) == 0)
  if ret['fqdn']:
   if alloc:
    from zdcp.rest.dns import record_device_update
    dns = record_device_update({'id':'new','a_id':'new','ptr_id':'new','a_domain_id_new':aDict['a_dom_id'],'hostname':aDict['hostname'],'ip_new':aDict['ip']})
    ret['insert'] = db.do("INSERT INTO devices(vm,a_dom_id,a_id,ptr_id,ipam_id,hostname,snmp,model) VALUES(%s,%s,%s,%s,%s,'%s','unknown','unknown')"%(aDict.get('vm','0'),aDict['a_dom_id'],dns['A']['record_id'],dns['PTR']['record_id'],alloc['id'],aDict['hostname']))
   else:
    ret['insert'] = db.do("INSERT INTO devices(vm,hostname,snmp,model) VALUES(%s,'%s','unknown','unknown')"%(aDict.get('vm','0'),aDict['hostname']))
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
def update_ip(aDict):
 """Function docstring for update_ip TBD

 Args:
  - id (required)
  - network_id (required)
  - ip (required)
  - mac (optional)

 Output:
 """
 if not (aDict.get('network_id') and aDict.get('ip')):
  return {'info':'not_enough_info'}

 from zdcp.rest.ipam import address_allocate
 from zdcp.rest.dns import record_device_update

 alloc = address_allocate({'ip':aDict['ip'],'network_id':aDict['network_id'],'mac':aDict.get('mac',0)})
 if   not alloc['valid']:
  return {'info':'IP not in network range'}
 elif not alloc['success']:
  return {'info':'IP not available'}
 ret = {'info':'IP available'}
 with DB() as db:
  db.do("SELECT hostname, a_dom_id AS a_domain_id_new, a_dom_id AS a_domain_id_old, a_id, ptr_id, INET_NTOA(ia.ip) AS ip_old, ipam_id FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id WHERE devices.id = %s"%aDict['id'])
  dev_info = db.get_row()
  ipam_id = dev_info.pop('ipam_id',None)
  ret['update_dev'] = (db.do("UPDATE devices SET ipam_id = %s WHERE id = %s"%(alloc['id'],aDict['id'])) == 1)
  ret['remove_old'] = (db.do("DELETE FROM ipam_addresses WHERE id = %s"%ipam_id) == 1) if ipam_id else False
 dev_info.update({'id':aDict['id'],'ip_new':aDict['ip']})
 ret['dns'] = record_device_update(dev_info)
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
  found = (db.do("SELECT hostname, ine.reverse_zone_id, ipam_id, a_id, ptr_id, a_dom_id, device_types.* FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id LEFT JOIN ipam_networks AS ine ON ine.id = ia.network_id LEFT JOIN device_types ON devices.type_id = device_types.id WHERE devices.id = %s"%aDict['id']) > 0)
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
 from zdcp.rest.ipam import network_discover as ipam_discover, address_allocate
 from zdcp.devices.generic import Device

 def __detect_thread(aIP,aDB):
  __dev = Device(aIP,gSettings)
  aDB[aIP['ip']] = __dev.detect()['info']
  return True

 start_time = int(time())
 ipam = ipam_discover({'id':aDict['network_id']})
 ret = {'errors':0, 'start':ipam['start'],'end':ipam['end'] }

 with DB() as db:
  db.do("SELECT id,name FROM device_types")
  devtypes = db.get_dict('name')
 dev_list = {}

 sema = gWorkers.semaphore(20)
 for ip in ipam['addresses']:
  gWorkers.add_sema(__detect_thread, sema, ip, dev_list)
 gWorkers.block(sema,20)

 # We can now do inserts only (no update) as we skip existing :-)
 with DB() as db:
  sql = "INSERT INTO devices (a_dom_id, ipam_id, snmp, model, mac, oid, type_id, hostname) VALUES ("+aDict['a_dom_id']+",{},'{}','{}','{}','{}','{}','{}')"
  count = 0
  for ip,entry in dev_list.iteritems():
   count += 1
   alloc = address_allocate({'ip':ip,'network_id':aDict['network_id']})
   if alloc['success']:
    try:   entry['mac'] = int(entry['mac'].replace(":",""),16)
    except:entry['mac'] = 0
    db.do(sql.format(alloc['id'],entry['snmp'],entry['model'],entry['mac'],entry['oid'],devtypes[entry.get('type','generic')]['id'],"unknown_%i"%count))
 ret['time'] = int(time()) - start_time
 ret['found']= len(dev_list)
 return ret

#
#
def system_oids(aDict):
 """ Function returns unique oids found

  Args:

  Output:
   oids. List of unique enterprise oids
 """
 with DB() as db:
  db.do("SELECT DISTINCT oid FROM devices")
  oids = db.get_rows()
 return [x['oid'] for x in oids] 

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
 """Function returns all MACs for devices belonging to networks belonging to particular server

 Args:
  - id (required)

 Output:
 """
 ret = {}
 with DB() as db:
  ret['count'] = db.do("SELECT devices.id, hostname, ia.mac, name AS domain, INET_NTOA(ia.ip) AS ip, ia.network_id AS network FROM devices LEFT JOIN domains ON domains.id = devices.a_dom_id LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id LEFT JOIN ipam_networks ON ipam_networks.id = ia.network_id WHERE ia.mac > 0 AND ipam_networks.server_id = %s"%aDict['id'])
  ret['data']  = db.get_rows()
  for row in ret['data']:
   row['mac'] = ':'.join(s.encode('hex') for s in str(hex(row['mac']))[2:].zfill(12).decode('hex')).lower()
 return ret

############################################## Specials ###############################################
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
 from importlib import import_module
 ret = {}
 try:
  module = import_module("zdcp.devices.%s"%(aDict['type']))
  dev = getattr(module,'Device',lambda x: None)(aDict['ip'],gSettings)
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
 from importlib import import_module
 ret = {}
 with DB() as db:
  db.do("SELECT ine.mask,INET_NTOA(ine.gateway) AS gateway,INET_NTOA(ine.network) AS network, INET_NTOA(ia.ip) AS ip, hostname, device_types.name AS type, domains.name AS domain FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id LEFT JOIN ipam_networks AS ine ON ine.id = ia.network_id LEFT JOIN domains ON domains.id = devices.a_dom_id LEFT JOIN device_types ON device_types.id = devices.type_id WHERE devices.id = '%s'"%aDict['id'])
  data = db.get_row()
 ip = data.pop('ip',None)
 try:
  module = import_module("zdcp.devices.%s"%data['type'])
  dev = getattr(module,'Device',lambda x: None)(ip,gSettings)
  ret['data'] = dev.configuration(data)
 except Exception as err:
  ret['info'] = "Error loading configuration template, make sure settings are ok (netconf -> encrypted, ntpsrv, dnssrv, anonftp): %s"%str(err)
  ret['result'] = 'NOT_OK'
 else:
  ret['result'] = 'OK'

 return ret 

#
#
def network_info_discover(aDict):
 """Function discovers system macs and enterprise oid for devices (on a network segment)

 Args:
  - network_id (optional)

 Output:
 """
 from netsnmp import VarList, Varbind, Session
 from binascii import b2a_hex
 from __builtin__ import list

 ret = {'count':0}

 def __detect_thread(aDev):
  try:
   session = Session(Version = 2, DestHost = aDev['ip'], Community = gSettings['snmp']['read_community'], UseNumeric = 1, Timeout = 100000, Retries = 2)
   sysoid = VarList(Varbind('.1.0.8802.1.1.2.1.3.2.0'),Varbind('.1.3.6.1.2.1.1.2.0'))
   session.get(sysoid)
   if sysoid[0].val:
    aDev['mac'] = int("".join(list(b2a_hex(x) for x in list(sysoid[0].val))),16)
   if sysoid[1].val:
    try:    aDev['oid'] = sysoid[1].val.split('.')[7]
    except: pass
  except: pass
  return True

 with DB() as db:
  network = "TRUE" if not aDict.get('network_id') else "ia.network_id = %s"%aDict['network_id'] 
  count   = db.do("SELECT devices.mac, devices.oid, devices.id, INET_NTOA(ia.ip) AS ip FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id WHERE %s AND ia.state = 1 AND (devices.mac = 0 OR devices.oid = 0)"%network)
  devices = db.get_rows()
  if count > 0:
   sema = gWorkers.semaphore(20)
   for dev in devices:
    gWorkers.add_sema(__detect_thread, sema, dev)
   gWorkers.block(sema,20)
   for dev in devices:
    if dev.get('mac',0) > 0 or dev.get('oid',0) > 0:
     ret['count'] += db.do("UPDATE devices SET mac = %(mac)s, oid = %(oid)s WHERE id = %(id)s"%dev)
 return ret

#
#
def network_lldp_discover(aDict):
 """Function discovers lldp connections devices (on a network segment)

 Args:
  - network_id (optional)

 Output:
 """
 from netsnmp import VarList, Varbind, Session
 from binascii import b2a_hex
 from __builtin__ import list

 new_connections = []
 ins_interfaces = []

 def __detect_thread(aDev):
  try:
   new = list(con for con in interface_discover_lldp({'device':aDev['id']}).values() if con['result'] == 'new_connection')
   new_connections.extend(new)
   ins = list(con for con in interface_discover_lldp({'device':aDev['id']}).values() if con['extra'] == 'created_local_if')
   ins_interfaces.extend(ins)
  except: pass
  return True

 with DB() as db:
  network = "TRUE" if not aDict.get('network_id') else "ia.network_id = %s"%aDict['network_id']
  count   = db.do("SELECT hostname,devices.id AS id FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id WHERE %s AND ia.state = 1"%network)
 devices = db.get_rows()
 if count > 0:
  sema = gWorkers.semaphore(10)
  for dev in devices:
   gWorkers.add_sema( __detect_thread, sema, dev)
  gWorkers.block(sema,10)
 return {'result':'DISCOVERY_COMPLETED','new_connections':new_connections,'ins_interfaces':ins_interfaces}

#
#
def network_interface_status(aDict):
 """ Initiate a status check for all or a subset of devices' interfaces

 Args:
  - subnets (optional). List of subnet_ids to check
  - discover(optional). False/None/"up"/"all", defaults to false

 """
 from zdcp.core.common import rest_call
 ret = {'local':[],'remote':[]}
 with DB() as db:
  trim = "" if not aDict.get('subnets') else "WHERE ipam_networks.id IN (%s)"%(",".join([str(x) for x in aDict['subnets']]))
  db.do("SELECT ipam_networks.id, servers.node, servers.server FROM ipam_networks LEFT JOIN servers ON servers.id = ipam_networks.server_id %s"%trim)
  subnets = db.get_rows()
  for sub in subnets:
   count = db.do("SELECT devices.id AS device_id, INET_NTOA(ia.ip) AS ip, dt.name AS type FROM devices LEFT JOIN device_types AS dt ON devices.type_id = dt.id LEFT JOIN ipam_addresses AS ia ON devices.ipam_id = ia.id WHERE ia.network_id = %s AND ia.state = 1 ORDER BY ip"%sub['id'])
   if count > 0:
    devices = db.get_rows()
    args = {'module':'device','func':'interface_status_check','args':{'device_list':devices,'discover':aDict.get('discover',False)},'output':False}
    for dev in devices:
     db.do("SELECT snmp_index,id FROM device_interfaces WHERE device = %s AND snmp_index > 0"%dev['device_id'])
     dev['interfaces'] = db.get_rows()
    if not sub['node'] or sub['node'] == 'master':
     gWorkers.add_task(args)
     ret['local'].append(sub['id'])
    else:
     rest_call("%s/api/system_task_worker?node=%s"%(gSettings['nodes'][sub['node']],sub['node']),args)['data']
     ret['remote'].append(sub['id'])
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

 def state(val):
  return {0:'grey',1:'green',2:'red'}.get(val,'orange')

 with DB() as db:
  if is_int(aDict.get('device')):
   db.do("SELECT devices.id, hostname FROM devices WHERE id = %s"%aDict['device'])
  else:
   db.do("SELECT devices.id, hostname FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id WHERE ia.ip = INET_ATON('%s')"%aDict['device'])
  ret = db.get_row()
  if ret:
   sort = aDict.get('sort','snmp_index')
   ret['count'] = db.do("SELECT id,name,state,description,snmp_index,mac, peer_interface,multipoint FROM device_interfaces WHERE device = %s ORDER BY %s"%(ret['id'],sort))
   ret['data'] = db.get_rows()
   for row in ret['data']:
    row['state_ascii'] = state(row['state'])
    row['mac'] = ':'.join(s.encode('hex') for s in str(hex(row['mac']))[2:].zfill(12).decode('hex')).lower()
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
 id = aDict.pop('id','new')
 op = aDict.pop('op',None)
 with DB() as db:
  if op == 'update':
   # If multipoint there should not be any single peer interface
   aDict['multipoint'] = aDict.get('multipoint',0)
   if int(aDict['multipoint']) == 1:
    aDict['peer_interface'] = 'NULL'
   if not id == 'new':
    ret['update'] = db.update_dict('device_interfaces',aDict,"id=%s"%id)
   else:
    aDict['manual'] = 1
    ret['insert'] = db.insert_dict('device_interfaces',aDict)
    id = db.get_last_id() if ret['insert'] > 0 else 'new'

  if not id == 'new':
   ret['found'] = (db.do("SELECT di.*, peer.device AS peer_device FROM device_interfaces AS di LEFT JOIN device_interfaces AS peer ON di.peer_interface = peer.id WHERE di.id = '%s'"%id) > 0)
   ret['data'] = db.get_row()
   ret['data']['mac'] = ':'.join(s.encode('hex') for s in str(hex(ret['data']['mac']))[2:].zfill(12).decode('hex')).lower()
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
   ret['deleted'] = db.do("DELETE FROM device_interfaces WHERE device = %s AND peer_interface IS NULL AND multipoint = 0 AND manual = 0 and state != 1"%aDict['device_id'])
  else:
   for intf,value in aDict.iteritems():
    if intf[0:10] == 'interface_' or intf == 'id':
     id = int(value)
    else:
     continue
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
def interface_unlink(aDict):
 """Function docstring for interface_unlink. UnLink two device interfaces

 Args:
  - a_id (required)
  - b_id (required)

 Output:
 """
 ret = {'a':{},'b':{}}
 with DB() as db:
  sql_clear = "UPDATE device_interfaces SET peer_interface = NULL WHERE peer_interface = %s AND multipoint = 0"
  ret['a']['clear'] = db.do(sql_clear%(aDict['a_id']))
  ret['b']['clear'] = db.do(sql_clear%(aDict['b_id']))
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
def interface_discover_snmp(aDict):
 """ Discovery function for detecting interfaces. Will try SNMP to detect all interfaces (in state up) first.

 Args:
  - device (required)
  - cleanup (optional, boolean). Deletes non-existing interfaces (except manually added) by default
  - state (optional). 'up'(default)/'all'

 Output:
 """
 from importlib import import_module

 def mac2int(aMAC):
  try:    return int(aMAC.replace(":",""),16)
  except: return 0

 ret = {'insert':0,'update':0,'delete':0}
 with DB() as db:
  db.do("SELECT INET_NTOA(ia.ip) AS ip, hostname, device_types.name AS type FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id LEFT JOIN device_types ON type_id = device_types.id  WHERE devices.id = %s"%aDict['device'])
  info = db.get_row()
  db.do("SELECT id, snmp_index, name, description, mac FROM device_interfaces WHERE device = %s"%aDict['device'])
  existing = db.get_rows()
  try:
   module  = import_module("zdcp.devices.%s"%(info['type']))
   dev = getattr(module,'Device',lambda x: None)(info['ip'],gSettings)
   interfaces = dev.interfaces()
  except Exception as err:
   ret['error'] = str(err)
  else:
   for con in existing:
    entry = interfaces.pop(con['snmp_index'],None)
    if entry:
     mac = mac2int(entry['mac'])
     if not ((entry['name'] == con['name']) and (entry['description'] == con['description']) and (mac == con['mac'])):
      ret['update'] += db.do("UPDATE device_interfaces SET name = '%s', description = '%s', mac = %s WHERE id = %s"%(entry['name'][0:24],entry['description'],mac,con['id']))
    elif aDict.get('cleanup',True) == True:
     ret['delete'] += db.do("DELETE FROM device_interfaces WHERE id = %s AND manual = 0"%(con['id']))
   for key, entry in interfaces.iteritems():
    if entry['state'] == 'up':
     args = {'device':int(aDict['device']),'name':entry['name'][0:24],'description':entry['description'],'snmp_index':key,'mac':mac2int(entry['mac'])}
     ret['insert'] += db.insert_dict('device_interfaces',args)
 return ret

#
#
def interface_lldp(aDict):
 """Node independent funtion to find out lldp information

 Args:
  - ip (required)

 Output:
  - LLDP info
 """
 from zdcp.devices.generic import Device
 device = Device(aDict['ip'],gSettings)
 return device.lldp()

#
#
def interface_snmp(aDict):
 """Node independent funtion to find out interface information

 Args:
  - ip (required)
  - interface (required)

 Output:
  - SNMP info
 """
 from zdcp.devices.generic import Device
 device = Device(aDict['ip'],gSettings)
 return device.interface(aDict['interface'])

#
#
def interface_discover_lldp(aDict):
 """Function discovers connections using lldp info

 Args:
  - device (required)

 Output:
 """
 from struct import unpack
 from socket import inet_aton
 from zdcp.devices.generic import Device

 def mac2int(aMAC):
  try:    return int(aMAC.replace(":",""),16)
  except: return 0

 def ip2int(addr):
  return unpack("!I", inet_aton(addr))[0]

 with DB() as db:
  sql_dev = "SELECT INET_NTOA(ia.ip) AS ip, dt.name AS type FROM devices LEFT JOIN device_types AS dt ON devices.type_id = dt.id LEFT JOIN ipam_addresses AS ia ON devices.ipam_id = ia.id WHERE devices.id = %s"
  sql_lcl = "SELECT id,multipoint,peer_interface FROM device_interfaces AS di WHERE device = %s AND snmp_index = %s"
  sql_ins = "INSERT INTO device_interfaces(device, snmp_index, name, description) VALUES(%s,%s,'%s','%s') ON DUPLICATE KEY UPDATE id = LAST_INSERT_ID(id)"
  sql_rem = "SELECT di.multipoint, di.name, di.peer_interface, di.mac, di.id, di.description, INET_NTOA(ia.ip) AS ip FROM device_interfaces AS di LEFT JOIN devices ON devices.id = di.device LEFT JOIN ipam_addresses AS ia ON devices.ipam_id = ia.id WHERE %s AND (%s OR %s)"
  sql_set = "UPDATE device_interfaces SET peer_interface = %s WHERE id = %s AND multipoint = 0"
  db.do(sql_dev%aDict['device'])
  data = db.get_row()
  # TODO Run this off the right node
  device = Device(data['ip'],gSettings)
  info = device.lldp()
  for k,v in info.iteritems():
   db.do(sql_lcl%(aDict['device'],k))
   local = db.get_row()
   if not local:
    # Find a local interface
    intf = device.interface(k)
    db.do(sql_ins%(aDict['device'],k,intf['name'],intf['description']))
    local = {'id':db.get_last_id(),'multipoint':0,'peer_interface':None}
    v['local_id'] = local['id']
    v['extra'] = 'created_local_if'
   else:
    if local['multipoint'] == 0:
     v['local_id'] = local['id']
    else:
     v['result'] = 'multipoint'
     continue
   args = {}
   if   v['chassis_type'] == 4:
    args['id'] = "devices.mac = %s"%mac2int(v['chassis_id'])
   elif v['chassis_type'] == 5:
    args['id'] = "ia.ip = %s"%ip2int(v['chassis_id'])
   else:
    v['result'] = "chassis_mapping_impossible_no_id"
    continue
   if   v['port_type'] == 3:
    args['port'] = "di.mac = %s"%mac2int(v['port_id'])
   elif v['port_type'] == 5:
    args['port'] = "di.name = '%s'"%v['port_id']
   elif v['port_type'] == 7:
    # Locally defined... should really look into remote device and see what it configures.. complex, so simplify and guess
    args['port'] = "di.name = '%s' OR di.name = '%s'"%(v['port_id'],v['port_desc'])
   else:
    v['result'] = "chassis_mapping_impossible_no_port"
    continue
   if len(v['port_desc']) > 0:
    args['desc'] = "di.description COLLATE UTF8_GENERAL_CI LIKE '%s'"%v['port_desc']
   else:
    args['desc'] = "FALSE"
   db.do(sql_rem%(args['id'],args['port'],args['desc']))
   remote = db.get_row()
   if remote:
    if remote['peer_interface']:
     if local['peer_interface'] == remote['id']:
      v['peer_id'] = remote['id']
      v['result'] = 'existing_connection'
     else:
      v['peer_id'] = local['peer_interface']
      v['result'] = 'other_mapping(%s<=>%s)'%(local['peer_interface'],remote['id'])
    else:
     v['peer_id'] = remote['id']
     db.do(sql_set%(v['local_id'],remote['id']))
     db.do(sql_set%(remote['id'],v['local_id']))
     v['result'] = 'new_connection'
   else:
    v['result'] = 'chassis_mapping_impossible'

 return info

#
#
def interface_status_check(aDict):
 """ Process a list of Device IDs and IP addresses (id, ip, type) and perform an SNMP interface lookup. return state values are: 0 (not seen), 1(up), 2(down).
  Always return interface information. This function is node independent.

 Args:
  - device_list (required)
  - discover(optional). False/None/"up"/"all", defaults to false

 Output:
 """
 from os import system
 from importlib import import_module
 states = {'unseen':0,'up':1,'down':2}
 discover = aDict.get('discover')

 def __interfaces(aDev):
  try:
   module = import_module("zdcp.devices.%s"%aDev['type'])
   device = getattr(module,'Device',None)(aDev['ip'],gSettings)
   probe  = device.interfaces()
   exist  = aDev['interfaces']
   for intf in exist:
    intf.update( probe.pop(intf.get('snmp_index','NULL'),{}) )
    intf['state'] = states.get(intf.get('state','unseen'))
   if discover:
    for index, intf in probe.iteritems():
     if discover == 'all' or (discover == 'up' and intf['state'] == 'up'):
      intf.update({'snmp_index':index,'state':states.get(intf.get('state','unseen'))})
      exist.append(intf)
  except: pass
  return True

 sema = gWorkers.semaphore(20)
 for dev in aDict['device_list']:
  gWorkers.add_sema( __interfaces, sema, dev)
 gWorkers.block(sema,20)
 for dev in aDict['device_list']:
  if len(dev['interfaces']) > 0:
   if gSettings['system']['id'] == 'master':
    interface_status_report(dev)
   else:
    from zdcp.core.common import rest_call
    rest_call("%s/api/device_interface_status_report?log=false"%gSettings['system']['master'],dev)
 return {'result':'GATHERING_DATA_COMPLETED'}

#
#
def interface_status_report(aDict):
 """Function updates interface status for a particular device

 Args:
  - device_id (required). Device id
  - interfaces (required). list of interface objects {snmp_index,name,state,mac,description,<id>}. id is DB entry ID

 Output:
 """
 ret = {'update':0,'insert':0}
 def mac2int(aMAC):     
  try:    return int(aMAC.replace(":",""),16)
  except: return 0

 with DB() as db:
  for intf in aDict['interfaces']:
   args = {'device':aDict['device_id'],'snmp_index':intf['snmp_index'],'id':intf.get('id'), 'mac':mac2int(intf.get('mac',0)), 'name':intf.get('name','NA'),'state':intf.get('state',0),'description':intf.get('description','NA')}
   if args['id']:
    ret['update'] += db.do("UPDATE device_interfaces SET name = '%(name)s', mac = %(mac)s, state = %(state)s, description = '%(description)s' WHERE id = %(id)s"%args)
   else:
    ret['insert'] += db.do("INSERT INTO device_interfaces SET device = %(device)s, snmp_index = %(snmp_index)s, name = '%(name)s', mac = %(mac)s, state = %(state)s, description = '%(description)s' ON DUPLICATE KEY UPDATE mac = %(mac)s, state = %(state)s"%args)
 return ret
