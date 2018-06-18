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
  - op (optional)

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
  return {'xist':0}
 ret = {'id':aDict.pop('id',None),'ip':aDict.get('ip',None)}

 op = aDict.pop('op',None)
 with DB() as db:
  if op == 'update' and ret['id']:
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
  # Now fetch info
  ret['xist'] = (db.do("SELECT devices.*, device_types.base AS type_base, device_types.name as type_name, functions, a.name as domain, ia.ip, INET_NTOA(ia.ip) as ipasc FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id LEFT JOIN domains AS a ON devices.a_dom_id = a.id LEFT JOIN device_types ON device_types.id = devices.type_id WHERE {}".format(srch)) == 1)
  if ret['xist']:
   ret['info'] = db.get_row()
   ret['id'] = ret['info'].pop('id',None)
   ret['ip'] = ret['info'].pop('ipasc',None)
   ret['info']['mac']  = ':'.join(s.encode('hex') for s in str(hex(ret['info']['mac']))[2:].zfill(12).decode('hex')).lower() if ret['info']['mac'] != 0 else "00:00:00:00:00:00"
   if not ret['info']['functions']:
    ret['info']['functions'] = ""
   # Pick login name from settings
   db.do("SELECT parameter,value FROM settings WHERE node = 'master' AND section = 'netconf'")
   netconf = db.get_dict('parameter')
   ret['username'] = netconf['username']['value']
   ret['booked'] = (db.do("SELECT users.alias, bookings.user_id, NOW() < ADDTIME(time_start, '30 0:0:0.0') AS valid FROM bookings LEFT JOIN users ON bookings.user_id = users.id WHERE device_id ='{}'".format(ret['id'])) == 1)
   if ret['booked']:
    ret['booking'] = db.get_row()

   # Rack infrastructure
   if ret['info']['vm'] == 1:
    ret['racked'] = False
   else:
    ret['racked'] = (db.do("SELECT rack_info.*, racks.name AS rack_name FROM rack_info LEFT JOIN racks ON racks.id = rack_info.rack_id WHERE rack_info.device_id = %i"%ret['id']) == 1)
    if ret['racked']:
     rack = db.get_row()
     ret['rack'] = rack
     infra = ['console','pem0_pdu','pem1_pdu']
     dev_ids = ",".join([str(rack["%s_id"%x]) for x in infra if rack["%s_id"%x]])
     if len(dev_ids) > 0:
      db.do("SELECT devices.id, INET_NTOA(ia.ip) AS ip, hostname FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id WHERE devices.id IN (%s)"%dev_ids)
     devices = db.get_dict('id') if len(dev_ids) > 0 else {}
     pdu_ids = ",".join([str(x) for x in [rack["pem0_pdu_id"],rack["pem1_pdu_id"]] if x])
     if len(pdu_ids) > 0:
      db.do("SELECT * FROM pdu_info WHERE device_id IN (%s)"%pdu_ids)
     pdus = db.get_dict('device_id') if len(pdu_ids) > 0 else {}
     console = devices.get(rack['console_id'],{'hostname':None,'ip':None})
     rack.update({'console_name':console['hostname'],'console_ip':console['ip']})
     for pem in ['pem0','pem1']:
      pdu = pdus.get(rack["%s_pdu_id"%pem])
      rack["%s_pdu_name"%pem] = "%s:%s"%(devices[pdu['device_id']]['hostname'],pdu['%s_slot_name'%(rack["%s_pdu_slot"%pem])]) if pdu else None
      rack["%s_pdu_ip"%pem] = devices[pdu['device_id']]['ip'] if pdu else None
 return ret

#
#
def update(aDict):
 """Function update updates device info, either through direct fields or through lookup

 Args:
  - id (required)
  - op (optional)

 Output:
  - all device info
 """
 ret = {'id':aDict.pop('id',None), 'ip':aDict.pop('ip',None)}

 with DB() as db:
  # Prep types for lookup
  typexist = db.do("SELECT id, name, base FROM device_types")
  types    = db.get_dict('name')

  # Move aDict to args for op
  operation = aDict.pop('op',None)
  if operation:
   # Make sure we don't change IP here as it breaks too much, instead user must resync to another VRF and network
   _ = aDict.pop('devices_ip',None)
   args = aDict
   ret['result'] = {}

   if operation == 'lookup' and ret['ip']:
    from zdcp.devices.generic import Device
    dev = Device(ret['ip'])
    lookup = dev.detect()
    ret['result']['lookup'] = lookup['result']
    if lookup['result'] == 'OK':
     args.update({'devices_model':lookup['info']['model'],'devices_snmp':lookup['info']['snmp'],'devices_type_id':types[lookup['info']['type']]['id']})

   if (operation == 'update' or (operation == 'lookup' and ret['result']['lookup'] == 'OK')) and ret['id']:
    args['devices_vm'] = args.get('devices_vm',0)
    if not args.get('devices_comment'):
     args['devices_comment'] = 'NULL'
    if not args.get('devices_webpage'):
     args['devices_webpage'] = 'NULL'
    if args.get('devices_mac'):
     try: args['devices_mac'] = int(args['devices_mac'].replace(":",""),16)
     except: args['devices_mac'] = 0
    racked = args.pop('racked',None)
    if racked:
     if   racked == '1' and args.get('rack_info_rack_id') == 'NULL':
      db.do("DELETE FROM rack_info WHERE device_id = %s"%ret['id'])
      args.pop('rack_info_pem0_pdu_slot_id',None)
      args.pop('rack_info_pem1_pdu_slot_id',None)
     elif racked == '0' and args.get('rack_info_rack_id') != 'NULL':
      db.do("INSERT INTO rack_info SET device_id = %s,rack_id=%s ON DUPLICATE KEY UPDATE rack_id = rack_id"%(ret['id'],args.get('rack_info_rack_id')))
     elif racked == '1':
      for pem in ['pem0','pem1']:
       try:
        pem_pdu_slot_id = args.pop('rack_info_%s_pdu_slot_id'%pem,None)
        (args['rack_info_%s_pdu_id'%pem],args['rack_info_%s_pdu_slot'%pem]) = pem_pdu_slot_id.split('.')
       except: pass

    #
    # Make sure everything is there to update DNS records, if records are not the same as old ones, update device, otherwise pop
    #
    if args.get('devices_a_id') and args.get('devices_ptr_id') and args.get('devices_a_dom_id') and args.get('devices_hostname') and ret['ip']:
     import zdcp.rest.dns as DNS
     DNS.__add_globals__({'import_module':import_module})
     dns = DNS.record_device_update({'a_id':args['devices_a_id'],'ptr_id':args['devices_ptr_id'],'a_domain_id':args['devices_a_dom_id'],'hostname':args['devices_hostname'],'ip':ret['ip'],'id':ret['id']})
     # ret['result']['dns'] = dns
     for type in ['a','ptr']:
      if dns[type.upper()]['xist'] > 0:
       if not (str(dns[type.upper()]['record_id']) == str(args['devices_%s_id'%type])):
        args['devices_%s_id'%type] = dns[type.upper()]['record_id']
       else:
        args.pop('devices_%s_id'%type,None)
     if (str(dns['A']['domain_id']) == str(args['devices_a_dom_id'])):
      args['devices_a_dom_id'] = dns['A']['domain_id']
     else:
      args.pop('devices_a_dom_id',None)

    ret['result']['update'] = {'device_info':db.update_dict_prefixed('devices',args,"id='%s'"%ret['id']),'rack_info':db.update_dict_prefixed('rack_info',args,"device_id='%s'"%ret['id'])}

  # Now fetch info
  ret['xist'] = (db.do("SELECT devices.*, device_types.base AS type_base, device_types.name as type_name, a.name as domain, ia.ip, INET_NTOA(ia.ip) as ipasc FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id LEFT JOIN domains AS a ON devices.a_dom_id = a.id LEFT JOIN device_types ON device_types.id = devices.type_id WHERE devices.id = %s"%ret['id']) == 1)
  if ret['xist']:
   ret['info'] = db.get_row()
   ret['id'] = ret['info'].pop('id',None)
   ret['ip'] = ret['info'].pop('ipasc',None)
   ret['info']['mac'] = ':'.join(s.encode('hex') for s in str(hex(ret['info']['mac']))[2:].zfill(12).decode('hex')).lower() if ret['info']['mac'] != 0 else "00:00:00:00:00:00"
   # Rack infrastructure
   ret['infra'] = {'racks':[{'id':'NULL', 'name':'Not used'}]}
   ret['infra']['types'] = types
   if ret['info']['vm'] == 1:
    ret['racked'] = 0
   else:
    db.do("SELECT id, name FROM racks")
    ret['infra']['racks'].extend(db.get_rows())
    ret['racked'] = db.do("SELECT rack_info.* FROM rack_info WHERE rack_info.device_id = %(id)i"%ret)
    if ret['racked'] > 0:
     ret['rack'] = db.get_row()
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

  if operation == 'update' and ret['racked']:
   for pem in ['pem0','pem1']:
    if ret['rack']['%s_pdu_id'%pem] > 0:
     db.do("SELECT INET_NTOA(ia.ip) AS ip, hostname, name FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id LEFT JOIN device_types ON devices.type_id = device_types.id WHERE devices.id = %i"%(ret['rack']['%s_pdu_id'%pem]))
     pdu_info = db.get_row()
     args_pem = {'ip':pdu_info['ip'],'unit':ret['rack']['%s_pdu_unit'%pem],'slot':ret['rack']['%s_pdu_slot'%pem],'text':"%s-P%s"%(ret['info']['hostname'],pem[3])}
     try:
      module = import_module("zdcp.rest.%s"%pdu_info['name'])
      pdu_update = getattr(module,'update',None)
      ret['result'][pem] = "%s.%s"%(pdu_info['hostname'],pdu_update(args_pem))
     except Exception as err:
      ret['result'][pem] = "Error: %s"%str(err)
 return ret

#
#
def basics(aDict):
 """Find basic info given device id

 Args:
  - id

 Output:
 """
 ret = {}
 with DB() as db:
  ret['xist'] = db.do("SELECT devices.id, INET_NTOA(ia.ip) as ip, hostname, domains.name AS domain FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id LEFT JOIN domains ON devices.a_dom_id = domains.id WHERE devices.id = %s"%aDict['id'])
  ret.update(db.get_row()) if ret['xist'] > 0 else {}
 return ret

#
#
def list(aDict):
 """Function docstring for list TBD

 Args:
  - filter (optional)
  - sort (optional) (sort on id or hostname or...)
  - dict (optional) (output as dictionary instead of list)

  - rack (optional)
  - field (optional) 'id/ip/mac/hostname/type' as search fields
  - search (optional)

 Output:
 """
 tune = ""
 if aDict.get('rack'):
  tune = "WHERE vm = 1" if aDict.get('rack') == 'vm' else "INNER JOIN rack_info ON rack_info.device_id = devices.id WHERE rack_info.rack_id = %(rack)s"%aDict
  if aDict.get('filter'):
   tune += " AND type_id IN (%(filter)s)"%aDict
 elif aDict.get('filter'):
  tune = "WHERE type_id IN (%(filter)s)"%aDict
 elif aDict.get('search'):
  if   aDict['field'] == 'hostname':
   tune = "WHERE hostname LIKE '%%%(search)s%%'"%aDict
  elif aDict['field'] == 'ip':
   tune = "WHERE ia.ip = INET_ATON('%(search)s')"%aDict
  elif aDict['field'] == 'type':
   tune = "LEFT JOIN device_types AS dt ON dt.id = devices.type_id WHERE dt.name = '%(search)s'"%aDict
  elif aDict['field'] == 'mac':
   def GL_mac2int(aMAC):
    try:    return int(aMAC.replace(":",""),16)
    except: return 0
   tune = "WHERE mac = %s"%GL_mac2int(aDict['search'])
  elif aDict['field']== 'id':
   tune = "WHERE devices.id = %(id)s"%aDict

 ret = {}
 sort = 'ia.ip' if aDict.get('sort','ip') == 'ip' else 'devices.hostname'
 with DB() as db:
  sql = "SELECT devices.id, devices.hostname, INET_NTOA(ia.ip) AS ipasc, domains.name AS domain, model FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id JOIN domains ON domains.id = devices.a_dom_id %s ORDER BY %s"%(tune,sort)
  ret['xist'] = db.do(sql)
  ret['data'] = db.get_rows() if not aDict.get('dict') else db.get_dict(aDict.get('dict'))
 return ret

#
#
def new(aDict):
 """Function docstring for new TBD

 Args:
  - a_dom_id (required)
  - hostname (required)
  - target (optional)
  - ipam_network_id (optional)
  - ip (optional)
  - vm (optional)
  - mac (optional)
  - arg (optional)

 Output:
  - target is 'rack_id' or nothing
  - arg is rack_id
 """
 alloc = None
 # Test if hostname ok or if IP supplied and then if ok and available
 if aDict['hostname'] == 'unknown':
  return {'info':'Hostname unknown not allowed'}
 elif aDict.get('ipam_network_id') and aDict.get('ip'):
  from zdcp.rest.ipam import ip_allocate
  alloc = ip_allocate({'ip':aDict['ip'],'network_id':aDict['ipam_network_id']})
  if   not alloc['valid']:
   return {'info':'IP not in network range'}
  elif not alloc['success']:
   return {'info':'IP not available'}

 def GL_mac2int(aMAC):
  try:    return int(aMAC.replace(":",""),16)
  except: return 0

 ret = {'info':None}
 with DB() as db:
  ret['xist'] = db.do("SELECT id, hostname, a_dom_id FROM devices WHERE hostname = '%(hostname)s' AND a_dom_id = %(a_dom_id)s"%aDict)
  if ret['xist'] == 0:
   mac     = GL_mac2int(aDict.get('mac',0))
   ipam_id = alloc['id'] if alloc else 'NULL'
   ret['insert'] = db.do("INSERT INTO devices(vm,mac,a_dom_id,ipam_id,hostname,snmp,model) VALUES(%s,%s,%s,%s,'%s','unknown','unknown')"%(aDict.get('vm','0'),mac,aDict['a_dom_id'],ipam_id,aDict['hostname']))
   ret['id']   = db.get_last_id()
   if aDict.get('target') == 'rack_id' and aDict.get('arg'):
    db.do("INSERT INTO rack_info SET device_id = %s, rack_id = %s ON DUPLICATE KEY UPDATE rack_unit = 0, rack_size = 1"%(ret['id'],aDict.get('arg')))
    ret['rack'] = aDict.get('arg')
    ret['info'] = "rack"
  else:
   ret.update(db.get_row())

 # also remove allocation if existed..
 if ret['xist'] > 0 and alloc['success']:
  from zdcp.rest.ipam import ip_delete
  ret['info'] = "existing (%s)"%ip_delete({'id':alloc['id']})
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
  existing = db.do("SELECT hostname, ine.reverse_zone_id, ipam_id, mac, a_id, ptr_id, a_dom_id, device_types.* FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id LEFT JOIN ipam_networks AS ine ON ine.id = ia.network_id LEFT JOIN device_types ON devices.type_id = device_types.id WHERE devices.id = %s"%aDict['id'])
  if existing == 0:
   ret = { 'deleted':0, 'dns':{'a':0, 'ptr':0}}
  else:
   data = db.get_row()
   args = {'a_id':data['a_id'],'a_domain_id':data['a_dom_id']}
   import zdcp.rest.dns as DNS
   DNS.__add_globals__({'import_module':import_module})
   from zdcp.rest.ipam import ip_delete

   if data['ptr_id'] != 0 and data['reverse_zone_id']:
    args['ptr_id']= data['ptr_id']
    args['ptr_domain_id'] = data['reverse_zone_id']
   ret = DNS.record_device_delete(args)
   if data['base'] == 'pdu':
    ret['pem0'] = db.update_dict('rack_info',{'pem0_pdu_unit':0,'pem0_pdu_slot':0},'pem0_pdu_id = %s'%(aDict['id']))
    ret['pem1'] = db.update_dict('rack_info',{'pem1_pdu_unit':0,'pem1_pdu_slot':0},'pem1_pdu_id = %s'%(aDict['id']))
   ret.update({'deleted':db.do("DELETE FROM devices WHERE id = %(id)s"%aDict)})
 # Avoid race condition on DB, do this when DB is closed...
 if data['ipam_id']:
  ret.update(ip_delete({'id':data['ipam_id']}))
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
 from zdcp.rest.ipam import network_discover as ipam_discover
 from zdcp.devices.generic import Device
 from zdcp.rest.ipam import ip_allocate

 def __detect_thread(aIP,aDB,aSema):
  __dev = Device(aIP['ipasc'])
  aDB[aIP['ip']] = __dev.detect()['info']
  aDB[aIP['ip']]['ipasc'] = aIP['ipasc'] 
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
   t.name = "Detect %s"%ip['ipasc']
   t.start()
  for i in range(20):
   sema.acquire()
 except Exception as err:
  ret['error']   = "Error:{}".format(str(err))

 # We can now do inserts only (no update) as we skip existing :-)
 with DB() as db:
  sql = "INSERT INTO devices (a_dom_id, ipam_id, snmp, model, type_id, hostname) VALUES ("+aDict['a_dom_id']+",{},'{}','{}','{}','{}')"
  count = 0
  for entry in dev_list.values():
   count += 1
   alloc = ip_allocate({'ip':entry['ipasc'],'network_id':aDict['network_id']})
   if alloc['success']:
    db.do(sql.format(alloc['id'],entry['snmp'],entry['model'],devtypes[entry['type']]['id'],"unknown_%i"%count))
 ret['time'] = int(time()) - start_time
 ret['found']= len(dev_list)
 return ret

#
#
def type_list(aDict):
 """Function lists currenct device types

 Args:
  - sort (optional), class/name

 Output:
 """
 ret = {}
 sort = 'name' if aDict.get('sort','name') == 'name' else 'base'
 with DB() as db:
  ret['xist'] = db.do("SELECT * FROM device_types ORDER BY %s"%sort)
  ret['types'] = db.get_rows()
 return ret

############################################## Specials ###############################################
#
#
def list_type(aDict):
 """Function docstring for list_type TBD

 Args:
  - base (optional)
  - name (optional)

 Output:
 """
 ret = {}
 with DB() as db:
  select = "device_types.%s ='%s'"%(('name',aDict['name']) if aDict.get('name') else ('base',aDict['base']))
  ret['xist'] = db.do("SELECT devices.id, INET_NTOA(ia.ip) AS ipasc, hostname, device_types.base AS type_base, device_types.name AS type_name FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id LEFT JOIN device_types ON devices.type_id = device_types.id WHERE %s ORDER BY type_name,hostname"%select)
  ret['data'] = db.get_rows()
 return ret

#
#
def list_mac(aDict):
 """Function docstring for list_mac. Used by IPAM DHCP update to fetch all mac address, IP, FQDN pairs 

 Args:

 Output:
 """
 def GL_int2mac(aInt):
  return ':'.join(s.encode('hex') for s in str(hex(aInt))[2:].zfill(12).decode('hex')).lower()

 with DB() as db:
  db.do("SELECT devices.id, CONCAT(hostname,'.',domains.name) as fqdn, INET_NTOA(ia.ip) as ip, mac FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id LEFT JOIN domains ON domains.id = devices.a_dom_id WHERE NOT mac = 0 ORDER BY ip")
  rows = db.get_rows()
 for row in rows:
  row['mac'] = GL_int2mac(row['mac'])
 return rows

#
#
def to_node(aDict):
 """Function docstring for to_node TBD

 Args:
  - id

 Output:
 """
 ret = {}
 with DB() as db:
  db.do("SELECT INET_NTOA(ia.ip) as ip, hostname, CONCAT(hostname,'.',domains.name) AS fqdn FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id LEFT JOIN domains ON devices.a_dom_id = domains.id WHERE devices.id = %(id)s"%aDict)
  ret['device'] = db.get_row()
  ret['found'] = (db.do("SELECT node FROM nodes WHERE url LIKE '%%%(ip)s%%' OR url LIKE '%%%(hostname)s%%' OR url LIKE '%%%(fqdn)s%%'"%ret['device']) > 0)
  ret['node'] = db.get_val('node') if ret['found'] else None
 return ret

#
#
def webpage_list(aDict):
 """ List webpages for devices

 Args:

 Output:
 """
 ret = {}
 with DB() as db:
  ret['xist'] = db.do("SELECT id,hostname,webpage FROM devices WHERE webpage IS NOT NULL")
  ret['data'] = db.get_rows()
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
  db.do("SELECT ine.mask,INET_NTOA(ine.gateway) AS gateway,INET_NTOA(ine.network) AS network, INET_NTOA(ia.ip) AS ipasc, hostname, device_types.name AS type, domains.name AS domain FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id LEFT JOIN ipam_networks AS ine ON ine.id = ia.network_id LEFT JOIN domains ON domains.id = devices.a_dom_id LEFT JOIN device_types ON device_types.id = devices.type_id WHERE devices.id = '%s'"%aDict['id'])
  data = db.get_row()
 ip = data.pop('ipasc',None)
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
   ret['xist'] = db.do("SELECT id,name,description,snmp_index,peer_interface,multipoint FROM device_interfaces WHERE device = %s ORDER BY %s"%(ret['id'],sort))
   ret['data'] = db.get_rows()
  else:
   ret = {'id':None,'hostname':None,'data':[],'xist':0}
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
   ret['xist'] = db.do("SELECT dc.*, peer.device AS peer_device FROM device_interfaces AS dc LEFT JOIN device_interfaces AS peer ON dc.peer_interface = peer.id WHERE dc.id = '%s'"%id)
   ret['data'] = db.get_row()
   ret['data'].pop('manual',None)
  else:
   ret['data'] = {'id':'new','device':int(aDict['device']),'name':'Unknown','description':'Unknown','snmp_index':None,'peer_interface':None,'peer_device':None,'multipoint':0}
 return ret

#
#
def interface_delete(aDict):
 """Function docstring for interface_delete TBD. Delete a certain interface

 Args:
  - id (required)

 Output:
 """
 ret = {}
 id = aDict['id']
 with DB() as db:
  ret['cleared'] = db.do("UPDATE device_interfaces SET peer_interface = NULL WHERE peer_interface = %s"%id)
  ret['deleted'] = db.do("DELETE FROM device_interfaces WHERE id = %s"%id)
 return ret

#
#
def interface_delete_list(aDict):
 """Function docstring for interface_delete TBD. Delete a certain interface

 Args:
  - interface_<x> (required). 0/1, deletes interface x if set to 1

 Output:
  - interfaces. List of id:s of deleted interfaces
 """
 ret = {'interfaces':[],'cleared':0,'deleted':0}
 op  = aDict.pop('op')
 with DB() as db:
  for intf,value in aDict.iteritems():
   if intf[0:10] == 'interface_' and str(value) == '1':
    try: id = int(intf[10:])
    except:pass
    else:
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
   xist = db.do(sql_dev%aDict['%s_ip'%peer])
   if xist > 0:
    ret[peer]['device'] = db.get_val('id')
    xist = db.do(sql_indx%(ret[peer]['device'],aDict['%s_index'%peer]))
    if xist > 0:
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
  db.do("SELECT INET_NTOA(ia.ip) AS ipasc, hostname, device_types.name AS type FROM devices LEFT JOIN ipam_addresses AS ia ON ia.id = devices.ipam_id LEFT JOIN device_types ON type_id = device_types.id  WHERE devices.id = %s"%aDict['device'])
  info = db.get_row()
  db.do("SELECT id, snmp_index, name, description FROM device_interfaces WHERE device = %s"%aDict['device'])
  existing = db.get_rows()
  try:
   module  = import_module("zdcp.devices.%s"%(info['type']))
   dev = getattr(module,'Device',lambda x: None)(info['ipasc'])
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
