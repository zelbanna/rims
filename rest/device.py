"""Device API module. This is the main device interaction module for device info, update, listing,discovery etc"""
__author__ = "Zacharias El Banna"
__version__ = "18.05.31GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

from sdcp.core.common import DB

#
#
def info(aDict):
 """Function docstring for info. "One function to rule them all", does retrieve both device info and performs update, lookup and infra retrieval

 Args:
  - ip (optional)
  - id (optional)
  - info (optional)
  - op (optional)

 Output:
 """
 srch = "devices.id = '{}'".format(aDict.get('id')) if aDict.get('id') else "devices.ip = INET_ATON('%s')"%(aDict.get('ip'))
 ret  = {'id':aDict.pop('id',None),'ip':aDict.pop('ip',None)}

 with DB() as db:
  # Fetch selection info
  info = aDict.pop('info',[])
  # Prep types for lookup
  typexist = db.do("SELECT id, name, base FROM device_types")
  types    = db.get_dict('name') 

  # Move aDict to args for op
  operation = aDict.pop('op',None)
  if operation:
   args = aDict
   ret['result'] = {}

   if operation == 'lookup' and ret['ip']:
    from sdcp.devices.generic import Device
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
    if args.get('devices_ip'):
     def GL_ip2int(addr):
      from struct import unpack
      from socket import inet_aton
      return unpack("!I", inet_aton(addr))[0]
     args['ip'] = GL_ip2int(args['ip'])
    if args.get('devices_mac'):
     try: args['devices_mac'] = int(args['devices_mac'].replace(":",""),16)
     except: aDict['devices_mac'] = 0
    racked = args.pop('racked',None)
    if racked:
     if   racked == '1' and args.get('rackinfo_rack_id') == 'NULL':
      db.do("DELETE FROM rackinfo WHERE device_id = %s"%ret['id'])
      args.pop('rackinfo_pem0_pdu_slot_id',None)
      args.pop('rackinfo_pem1_pdu_slot_id',None)
     elif racked == '0' and args.get('rackinfo_rack_id') != 'NULL':
      db.do("INSERT INTO rackinfo SET device_id = %s,rack_id=%s ON DUPLICATE KEY UPDATE rack_id = rack_id"%(ret['id'],args.get('rackinfo_rack_id')))
     elif racked == '1':
      for pem in ['pem0','pem1']:
       try:
        pem_pdu_slot_id = args.pop('rackinfo_%s_pdu_slot_id'%pem,None)
        (args['rackinfo_%s_pdu_id'%pem],args['rackinfo_%s_pdu_slot'%pem]) = pem_pdu_slot_id.split('.')
       except: pass

    #
    # Make sure everything is there to update DNS records, if records are not the same as old ones, update device, otherwise pop
    #
    if args.get('devices_a_id') and args.get('devices_ptr_id') and args.get('devices_a_dom_id') and args.get('devices_hostname') and ret['ip']:
     import sdcp.rest.dns as DNS
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

    ret['result']['update'] = {'device_info':db.update_dict_prefixed('devices',args,"id='%s'"%(ret['id'])),'rack_info':db.update_dict_prefixed('rackinfo',args,"device_id='%s'"%(ret['id']))}

  # Now fetch info
  ret['xist'] = db.do("SELECT devices.*, base, device_types.name as type_name, functions, a.name as domain, INET_NTOA(ip) as ipasc FROM devices LEFT JOIN domains AS a ON devices.a_dom_id = a.id LEFT JOIN device_types ON device_types.id = devices.type_id WHERE {}".format(srch))
  if ret['xist'] > 0:
   ret['info'] = db.get_row()
   ret['id'] = ret['info'].pop('id',None)
   ret['ip'] = ret['info'].pop('ipasc',None)
   ret['fqdn'] = "{}.{}".format(ret['info']['hostname'],ret['info']['domain'])
   ret['type'] = ret['info'].pop('base',None)
   ret['mac']  = ':'.join(s.encode('hex') for s in str(hex(ret['info']['mac']))[2:].zfill(12).decode('hex')).lower() if ret['info']['mac'] != 0 else "00:00:00:00:00:00"
   if not ret['info']['functions']:
    ret['info']['functions'] = ""
   # Pick login name from settings
   db.do("SELECT parameter,value FROM settings WHERE node = 'master' AND section = 'netconf'")
   netconf = db.get_dict('parameter')
   ret['username'] = netconf['username']['value']
   ret['booked'] = db.do("SELECT users.alias, bookings.user_id, NOW() < ADDTIME(time_start, '30 0:0:0.0') AS valid FROM bookings LEFT JOIN users ON bookings.user_id = users.id WHERE device_id ='{}'".format(ret['id']))
   if ret['booked'] > 0:
    ret['booking'] = db.get_row()

   # Rack infrastructure
   ret['infra'] = {'racks':[{'id':'NULL', 'name':'Not used'}]}
   ret['infra']['types'] = types
   db.do("SELECT domains.* FROM domains WHERE name NOT LIKE '%%arpa' ORDER BY name")
   ret['infra']['domains'] = db.get_rows()
   if ret['info']['vm'] == 1:
    ret['racked'] = 0
   else:
    db.do("SELECT id, name FROM racks")
    ret['infra']['racks'].extend(db.get_rows())
    ret['racked'] = db.do("SELECT rackinfo.*, INET_NTOA(devices.ip) AS console_ip, devices.hostname AS console_name FROM rackinfo LEFT JOIN devices ON devices.id = rackinfo.console_id WHERE rackinfo.device_id = %i"%(ret['id']))
    if ret['racked'] > 0:
     ret['info'].update(db.get_row())
     sqlbase = "SELECT devices.id, devices.hostname FROM devices INNER JOIN device_types ON devices.type_id = device_types.id WHERE device_types.base = '%s' ORDER BY devices.hostname"
     db.do(sqlbase%('console'))
     ret['infra']['consoles'] = db.get_rows()
     ret['infra']['consoles'].append({ 'id':'NULL', 'hostname':'No Console' })
     db.do(sqlbase%('pdu'))
     ret['infra']['pdus'] = db.get_rows()
     ret['infra']['pdus'].append({ 'id':'NULL', 'hostname':'No PDU' })
     db.do("SELECT pduinfo.* FROM pduinfo")
     ret['infra']['pduinfo'] = db.get_dict('device_id')
     ret['infra']['pduinfo']['NULL'] = {'slots':1, '0_slot_id':0, '0_slot_name':'', '1_slot_id':0, '1_slot_name':''}

  if operation == 'update' and ret['racked']:
   for pem in [0,1]:
    if ret['info']['pem%i_pdu_id'%(pem)] > 0:
     db.do("SELECT INET_NTOA(ip) AS ip, hostname, name FROM devices LEFT JOIN device_types ON devices.type_id = device_types.id WHERE devices.id = %i"%(ret['info']['pem%i_pdu_id'%(pem)]))
     pdu_info = db.get_row()
     args_pem = {'ip':pdu_info['ip'],'unit':ret['info']['pem%i_pdu_unit'%(pem)],'slot':ret['info']['pem%i_pdu_slot'%(pem)],'text':"%s-P%s"%(ret['info']['hostname'],pem)}
     try:
      module = import_module("sdcp.rest.%s"%pdu_info['name'])
      pdu_update = getattr(module,'pdu_update',None)
      ret['result']['pem%i'%pem] = "%s.%s"%(pdu_info['hostname'],pdu_update(args_pem))
     except Exception as err:
      ret['result']['pem%i'%pem] = str(err)
 return ret

#
#
def basics(aDict):
 """Find basic info give a number of options (use either id or field + search-string)

 Args:
  - id (optional)
  - field (optional) 'ip/mac/hostname'
  - search (optional) 

 Output:
 """
 ret = {}
 with DB() as db:
  if aDict.get('field'):
   if   aDict['field'] == 'ip':
    search = "devices.ip = INET_ATON('%s')"%aDict['search']
   elif aDict['field'] == 'hostname':
    search = "hostname = '%s'"%aDict['search']
   elif aDict['field'] == 'mac':
    def GL_mac2int(aMAC):               
     try:    return int(aMAC.replace(":",""),16)
     except: return 0
    search = "mac = %s"%GL_mac2int(aDict['search'])
  else:
   search = "devices.id = %s"%aDict['id']
  ret['xist'] = db.do("SELECT devices.id, INET_NTOA(ip) as ip, hostname, domains.name AS domain FROM devices LEFT JOIN domains ON devices.a_dom_id = domains.id WHERE %s"%search)
  ret.update(db.get_row() if ret['xist'] > 0 else {})
 return ret

#
#
def list(aDict):
 """Function docstring for list TBD

 Args:
  - filter (optional)
  - sort (optional)
  - dict (optional)
  - rack (optional)

 Output:
 """
 ret = {}
 if aDict.get('rack'):
  if aDict.get('rack') == 'vm':
   tune = "WHERE vm = 1"
  else:
   tune = "INNER JOIN rackinfo ON rackinfo.device_id = devices.id WHERE rackinfo.rack_id = %s"%(aDict.get('rack'))
  if aDict.get('filter'):
   tune += " AND type_id = %s"%(aDict.get('filter'))
 elif aDict.get('filter'):
  tune = "WHERE type_id = %s"%(aDict.get('filter'))
 else:
  tune = ""

 ret = {'sort':aDict.get('sort','devices.id')}
 with DB() as db:
  sql = "SELECT devices.id, INET_NTOA(ip) AS ipasc, CONCAT(devices.hostname,'.',domains.name) AS fqdn, model FROM devices JOIN domains ON domains.id = devices.a_dom_id {0} ORDER BY {1}".format(tune,ret['sort'])
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
  - ipam_id (optional)
  - ip (optional)
  - vm (optional)
  - mac (optional)
  - arg (optional)

 Output:
  - target is 'rack_id' or nothing
  - arg is rack_id
 """
 def GL_ip2int(addr):
  from struct import unpack
  from socket import inet_aton
  return unpack("!I", inet_aton(addr))[0]
 def GL_mac2int(aMAC):
  try:    return int(aMAC.replace(":",""),16)
  except: return 0

 ip    = aDict.get('ip')
 ipint = GL_ip2int(ip)
 ipam_id = aDict.get('ipam_id')
 ret = {'info':None}
 with DB() as db:
  from sdcp.rest.ipam import allocate_ip
  alloc = allocate_ip({'ip':ip,'network':ipam_id})
  if   not alloc['valid']:
   ret['info'] = "IP not in network range"
  elif not alloc['success']:
   ret['info'] = "IP not available"
  elif aDict['hostname'] == 'unknown':
   ret['info'] = "Hostname unknown not allowed"
  else:
   ret['xist'] = db.do("SELECT id, hostname, INET_NTOA(ip) AS ipasc, a_dom_id FROM devices WHERE ipam_id = {} AND (ip = {} OR hostname = '{}')".format(ipam_id,ipint,aDict['hostname']))
   if ret['xist'] == 0:
    mac = GL_mac2int(aDict.get('mac',0))
    args = {'ip':str(ipint), 'vm':str(aDict.get('vm','0')), 'mac':str(mac), 'a_dom_id':aDict['a_dom_id'], 'ipam_id':str(ipam_id), 'hostname':aDict['hostname'], 'snmp':'unknown', 'model':'unknown'}
    ret['insert'] = db.insert_dict('devices',args)
    ret['id']   = db.get_last_id()
    if aDict.get('target') == 'rack_id' and aDict.get('arg'):
     db.do("INSERT INTO rackinfo SET device_id = %s, rack_id = %s ON DUPLICATE KEY UPDATE rack_unit = 0, rack_size = 1"%(ret['id'],aDict.get('arg')))
     ret['rack'] = aDict.get('arg')
     ret['info'] = "rack"
   else:
    ret['info']  = "existing"
    ret.update(db.get_row())
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
  existing = db.do("SELECT hostname, INET_NTOA(ip) AS ipasc, mac, a_id, ptr_id, a_dom_id, device_types.* FROM devices LEFT JOIN device_types ON devices.type_id = device_types.id WHERE devices.id = {}".format(aDict['id']))
  if existing == 0:
   ret = { 'deleted':0, 'dns':{'a':0, 'ptr':0}}
  else:
   data = db.get_row()
   args = {'a_id':data['a_id'],'a_domain_id':data['a_dom_id']}
   import sdcp.rest.dns as DNS
   DNS.__add_globals__({'import_module':import_module})

   if data['ptr_id'] != 0:
    def GL_ip2ptr(addr):
     octets = addr.split('.')
     octets.reverse()
     octets.append("in-addr.arpa")
     return ".".join(octets)
    ptr    = GL_ip2ptr(data['ipasc'])
    arpa   = ptr.partition('.')[2]
    if db.do("SELECT id FROM domains WHERE name = '%s'"%(arpa)) > 0:
     args['ptr_id']= data['ptr_id']
     args['ptr_domain_id'] = db.get_val('id')
   ret = DNS.record_device_delete(args)
   if data['base'] == 'pdu':
    ret['pem0'] = db.update_dict('rackinfo',{'pem0_pdu_unit':0,'pem0_pdu_slot':0},'pem0_pdu_id = %s'%(aDict['id']))
    ret['pem1'] = db.update_dict('rackinfo',{'pem1_pdu_unit':0,'pem1_pdu_slot':0},'pem0_pdu_id = %s'%(aDict['id']))
   ret.update({'deleted':db.do("DELETE FROM devices WHERE id = '%s'"%aDict['id'])})
 return ret

#
#
def discover(aDict):
 """Function docstring for discover TBD

 Args:
  - a_dom_id (required)
  - network (required)

 Output:
 """
 from time import time
 from threading import Thread, BoundedSemaphore
 from sdcp.rest.ipam import discover as ipam_discover
 from sdcp.devices.generic import Device

 def __detect_thread(aIP,aDB,aSema):
  __dev = Device(aIP['ipasc'])
  aDB[aIP['ip']] = __dev.detect()['info']
  aSema.release()
  return True

 start_time = int(time())
 ipam = ipam_discover({'network':aDict['network']})
 ret = {'errors':0, 'start':ipam['start'],'end':ipam['end'] }

 with DB() as db:
  db.do("SELECT id,name FROM device_types")
  devtypes = db.get_dict('name')
  ret['xist'] = db.do("SELECT ip, INET_NTOA(ip) AS ipasc FROM devices WHERE ip >= {} and ip <= {} and ipam_id = {}".format(ipam['start']['ip'],ipam['end']['ip'],aDict['network']))
 db_old = db.get_dict('ip')
 db_new = {}
 try:
  sema = BoundedSemaphore(20)
  for ip in ipam['addresses']:
   if db_old.get(ip['ip']):
    continue
   sema.acquire()
   t = Thread(target = __detect_thread, args=[ip, db_new, sema])
   t.name = "Detect %s"%ip['ipasc']
   t.start()
  for i in range(20):
   sema.acquire()
 except Exception as err:
  ret['error']   = "Error:{}".format(str(err))

 # We can now do inserts only (no update) as we skip existing :-)
 with DB() as db:
  sql = "INSERT INTO devices (ip, a_dom_id, ipam_id, snmp, model, type_id, hostname) VALUES ('{}',"+aDict['a_dom_id']+",{},'{}','{}','{}','{}')"
  count = 0
  for ipint,entry in db_new.iteritems():
   count += 1
   db.do(sql.format(ipint,aDict['network'],entry['snmp'],entry['model'],devtypes[entry['type']]['id'],"unknown_%i"%count))
 ret['time'] = int(time()) - start_time
 ret['found']= len(db_new)
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
  select = "device_types.%s ='%s'"%(('name',aDict.get('name')) if aDict.get('name') else ('base',aDict.get('base')))
  ret['xist'] = db.do("SELECT devices.id, INET_NTOA(ip) AS ipasc, hostname, device_types.base as type_base, device_types.name as type_name FROM devices LEFT JOIN device_types ON devices.type_id = device_types.id WHERE %s ORDER BY type_name,hostname"%select)
  ret['data'] = db.get_rows()
 return ret

#
#
def list_mac(aDict):
 """Function docstring for list_mac TBD

 Args:

 Output:
 """
 def GL_int2mac(aInt):
  return ':'.join(s.encode('hex') for s in str(hex(aInt))[2:].zfill(12).decode('hex')).lower()

 with DB() as db:
  db.do("SELECT devices.id, CONCAT(hostname,'.',domains.name) as fqdn, INET_NTOA(ip) as ip, mac, ipam_id FROM devices JOIN domains ON domains.id = devices.a_dom_id WHERE NOT mac = 0 ORDER BY ip")
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
  res = db.do("SELECT INET_NTOA(ip) as ip, hostname, CONCAT(hostname,'.',domains.name) AS fqdn FROM devices LEFT JOIN domains ON devices.a_dom_id = domains.id WHERE devices.id = %s"%aDict['id'])
  dev = db.get_row()
  for test in ['ip','fqdn','hostname']:
   if db.do("SELECT node FROM nodes WHERE url LIKE '%{}%'".format(dev[test])) > 0:
    ret['node']  = db.get_val('node')
    ret['found'] = test
    break
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
  module = import_module("sdcp.devices.%s"%(aDict['type']))
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
 from sdcp.rest.ipam import info as ipam_info
 ret = {}
 with DB() as db:
  db.do("SELECT ipam_id, INET_NTOA(ip) AS ipasc, hostname, device_types.name AS type, domains.name AS domain FROM devices LEFT JOIN domains ON domains.id = devices.a_dom_id LEFT JOIN device_types ON device_types.id = devices.type_id WHERE devices.id = '%s'"%aDict['id'])
  data = db.get_row()
 ip = data.pop('ipasc',None)
 ipam = ipam_info({'id':data.pop('ipam_id',None)})['data']
 data.update({'mask':ipam['mask'],'gateway':ipam['gateway'],'network':ipam['network']})
 try:
  module = import_module("sdcp.devices.%s"%data['type'])
  dev = getattr(module,'Device',lambda x: None)(ip)
  ret['data'] = dev.configuration(data)
 except Exception as err:
  ret['info'] = "Error loading configuration template, make sure settings are ok (netconf -> encrypted, ntpsrv, dnssrv, anonftp): %s"%str(err)
  ret['result'] = 'NOT_OK'
 else:
  ret['result'] = 'OK'

 return ret 

#
#
def mac_sync(aDict):
 """Function docstring for mac_sync TBD

 Args:

 Output:
 """
 def GL_mac2int(aMAC):
  try:    return int(aMAC.replace(":",""),16)
  except: return 0
 ret = []
 try:
  arps = {}
  with open('/proc/net/arp') as f:
   _ = f.readline()
   for data in f:
    ( ip, _, _, mac, _, _ ) = data.split()
    if not mac == '00:00:00:00:00:00':
     arps[ip] = mac
  with DB() as db:
   db.do("SELECT id, hostname, INET_NTOA(ip) as ipasc, mac FROM devices WHERE hostname <> 'unknown' ORDER BY ip")
   rows = db.get_rows()
   for row in rows:
    if arps.get(row['ipasc']):
     row['found'] = arps.get(row['ipasc'])
     ret.append(row)
     db.do("UPDATE devices SET mac = {} WHERE id = {}".format(GL_mac2int(row['found']),row['id']))
 except: pass
 return ret

#
#
def interface_list(aDict):
 """List interfaces for a specific device

 Args:
  - device_id (optional)
  - device_ip (optional)
  - device    (ip or id... :-))
  - sort (optional, default to 'snmp_index')
 Output:
 """
 def is_int(val):
  try: int(val)
  except: return False
  else:   return True

 with DB() as db:
  id, ip = None,None
  if aDict.get('device_id'):
   db.do("SELECT id, hostname FROM devices WHERE id = %s"%aDict['device_id'])
  elif is_int(aDict.get('device')):
   db.do("SELECT id, hostname FROM devices WHERE id = %s"%aDict['device'])
  else:
   db.do("SELECT id, hostname FROM devices WHERE ip = INET_ATON('%s')"%(aDict['device_ip'] if aDict.get('device_ip') else aDict['device']))
  ret = db.get_row()
  if ret:
   sort = aDict.get('sort','snmp_index')
   ret['xist'] = db.do("SELECT id,name,description,snmp_index,peer_interface,multipoint FROM device_interfaces WHERE device_id = %s ORDER BY %s"%(ret['id'],sort))
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
  - device_id (required)
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
   ret['xist'] = db.do("SELECT dc.*, peer.device_id AS peer_device FROM device_interfaces AS dc LEFT JOIN device_interfaces AS peer ON dc.peer_interface = peer.id WHERE dc.id = '%s'"%id)
   ret['data'] = db.get_row()
   ret['data'].pop('manual',None)
  else:
   ret['data'] = {'id':'new','device_id':int(aDict['device_id']),'name':'Unknown','description':'Unknown','snmp_index':None,'peer_interface':None,'peer_device':None,'multipoint':0}
 return ret

#
#
def interface_delete(aDict):
 """Function docstring for interface_delete TBD. Delete a certain interface

 Args:
  - id (required)
  - device_id (required)

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
  - device_id (required)
  - interface_<x> (required). 0/1, deletes interface x if set to 1

 Output:
  - interfaces. List of id:s of deleted interfaces
 """
 ret = {'interfaces':[],'cleared':0,'deleted':0}
 dev = aDict.pop('device_id')
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
  sql_dev  ="SELECT id FROM devices WHERE ip = INET_ATON('%s')"
  sql_indx = "SELECT id FROM device_interfaces WHERE device_id = '%s' AND snmp_index = '%s'"
  for peer in ['a','b']:
   xist = db.do(sql_dev%aDict['%s_ip'%peer])
   if xist > 0:
    ret[peer]['device'] = db.get_val('id')
    xist = db.do(sql_indx%(ret[peer]['device'],aDict['%s_index'%peer]))
    if xist > 0:
     ret[peer]['index'] = db.get_val('id')
    else:
     db.insert_dict('device_interfaces',{'device_id':ret[peer]['device'],'name':'Unknown','description':'Unknown','snmp_index':aDict['%s_index'%peer]})
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
  Later stage is to do LLDP or similar to populate neighbor information

 Args:
  - device_id (required)
  - cleanup (optional, boolean). Deletes non-existing interfaces (except manually added) by default

 Output:
 """
 ret = {'insert':0,'update':0,'delete':0}
 with DB() as db:
  db.do("SELECT INET_NTOA(ip) AS ipasc, hostname, device_types.name AS type FROM devices LEFT JOIN device_types ON type_id = device_types.id  WHERE devices.id = %s"%aDict['device_id'])
  info = db.get_row()
  db.do("SELECT id, snmp_index, name, description FROM device_interfaces WHERE device_id = %s"%aDict['device_id'])
  existing = db.get_rows()
  try:
   module  = import_module("sdcp.devices.%s"%(info['type']))
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
    args = {'device_id':int(aDict['device_id']),'name':entry['name'][0:24],'description':entry['description'],'snmp_index':key}
    ret['insert'] += db.insert_dict('device_interfaces',args)
 return ret
