"""Device API module. This is the main device interaction module for device info, update, listing,discovery etc"""
__author__ = "Zacharias El Banna"
__version__ = "18.04.07GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

from sdcp.core.common import DB,SC

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
  - info: username,booking,infra => make 'exclude' arg in final function instead
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
    lookup = detect({'ip':ret['ip']})
    ret['result']['lookup'] = lookup['result']
    # Add DNS to lookup
    #if args.get('devices_a_id') or args.get('devices_ptr_id'):
    # from sdcp.rest.dns import record_lookup
    # for type in ['a_id','ptr_id']:
    #  if args.get('devices_%s'%type):
    #   ret['result'][type] = record_lookup({'id':args.get('devices_%s'%type)})['data']['content']

    if lookup['result'] == 'OK':
     args.update({'devices_model':lookup['info']['model'],'devices_snmp':lookup['info']['snmp'],'devices_type_id':types[lookup['info']['type']]['id']})

   if (operation == 'update' or (operation == 'lookup' and ret['result']['lookup'] == 'OK')) and ret['id']:
    if not args.get('devices_vm'):
     args['devices_vm'] = 0
    if not args.get('devices_comment'):
     args['devices_comment'] = 'NULL'
    if not args.get('devices_webpage'):
     args['devices_webpage'] = 'NULL'
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

    # Make sure everything is there to update DNS records, if records are not the same as old ones, update device, otherwise pop
    if args.get('devices_a_id') and args.get('devices_ptr_id') and args.get('devices_a_dom_id') and args.get('devices_hostname') and ret['ip']:
     from dns import record_device_update
     dns = record_device_update({'a_id':args['devices_a_id'],'ptr_id':args['devices_ptr_id'],'a_domain_id':args['devices_a_dom_id'],'hostname':args['devices_hostname'],'ip':ret['ip']})
     # ret['result']['dns'] = dns
     for type in ['a','ptr']:
      if not str(dns[type.upper()]['id']) == str(args['devices_%s_id'%type]):
       args['devices_%s_id'%type] = dns[type.upper()]['id']
      else:
       args.pop('devices_%s_id'%type,None)

    ret['result']['update'] = {'device_info':db.update_dict_prefixed('devices',args,"id='%s'"%(ret['id'])),'rack_info':db.update_dict_prefixed('rackinfo',args,"device_id='%s'"%(ret['id']))}

  # Now fetch info
  ret['xist'] = db.do("SELECT devices.*, base, device_types.name as type_name, functions, a.name as domain, INET_NTOA(ip) as ipasc, CONCAT(INET_NTOA(subnets.subnet),'/',subnets.mask) AS subnet, INET_NTOA(subnets.gateway) AS gateway FROM devices LEFT JOIN domains AS a ON devices.a_dom_id = a.id LEFT JOIN device_types ON device_types.id = devices.type_id LEFT JOIN subnets ON subnets.id = subnet_id WHERE {}".format(srch))
  if ret['xist'] > 0:
   ret['info'] = db.get_row()
   ret['id'] = ret['info'].pop('id',None)
   ret['ip'] = ret['info'].pop('ipasc',None)
   ret['fqdn'] = "{}.{}".format(ret['info']['hostname'],ret['info']['domain'])
   ret['type'] = ret['info'].pop('base',None)
   ret['mac']  = ':'.join(s.encode('hex') for s in str(hex(ret['info']['mac']))[2:].zfill(12).decode('hex')).lower() if ret['info']['mac'] != 0 else "00:00:00:00:00:00"
   if not ret['info']['functions']:
    ret['info']['functions'] = ""
   ret['username'] = SC['netconf']['username']
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
 """Function docstring for basics TBD

 Args:
  - id (required)

 Output:
 """
 ret = {}
 with DB() as db:
  ret['xist'] = db.do("SELECT INET_NTOA(ip) as ip, hostname, domains.name AS domain FROM devices LEFT JOIN domains ON devices.a_dom_id = domains.id WHERE devices.id = '%s'"%aDict['id'])
  ret.update(db.get_row())
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
  db.do("SELECT devices.id, CONCAT(hostname,'.',domains.name) as fqdn, INET_NTOA(ip) as ip, mac, subnet_id FROM devices JOIN domains ON domains.id = devices.a_dom_id WHERE NOT mac = 0 ORDER BY ip")
  rows = db.get_rows()
 for row in rows:
  row['mac'] = GL_int2mac(row['mac'])
 return rows

#
#
def new(aDict):
 """Function docstring for new TBD

 Args:
  - a_dom_id (required)
  - hostname (required)
  - target (optional)
  - subnet_id (optional)
  - ip (optional)
  - vm (optional)
  - mac (optional)
  - arg (optional)

 Output:
  - target is 'rack_id' or nothing
  - arg is rack_id
 """
 from sdcp.core.logger import log
 log("device_new({})".format(aDict))
 def GL_ip2int(addr):
  from struct import unpack
  from socket import inet_aton
  return unpack("!I", inet_aton(addr))[0]
 def GL_mac2int(aMAC):
  try:    return int(aMAC.replace(":",""),16)
  except: return 0

 ip    = aDict.get('ip')
 ipint = GL_ip2int(ip)
 subnet_id = aDict.get('subnet_id')
 ret = {'info':None}
 with DB() as db:
  in_sub = db.do("SELECT subnet FROM subnets WHERE id = {0} AND {1} > subnet AND {1} < (subnet + POW(2,(32-mask))-1)".format(subnet_id,ipint))
  if in_sub == 0:
   ret['info'] = "IP not in subnet range"
  elif aDict['hostname'] == 'unknown':
   ret['info'] = "Hostname unknown not allowed"
  else:
   ret['xist'] = db.do("SELECT id, hostname, INET_NTOA(ip) AS ipasc, a_dom_id FROM devices WHERE subnet_id = {} AND (ip = {} OR hostname = '{}')".format(subnet_id,ipint,aDict['hostname']))
   if ret['xist'] == 0:
    mac = GL_mac2int(aDict.get('mac',0))
    args = {'ip':str(ipint), 'vm':str(aDict.get('vm','0')), 'mac':str(mac), 'a_dom_id':aDict['a_dom_id'], 'subnet_id':str(subnet_id), 'hostname':aDict['hostname'], 'snmp':'unknown', 'model':'unknown'}
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
 from sdcp.core.logger import log
 log("device_remove({})".format(aDict))
 with DB() as db:
  existing = db.do("SELECT hostname, mac, a_id, ptr_id, device_types.* FROM devices LEFT JOIN device_types ON devices.type_id = device_types.id WHERE devices.id = {}".format(aDict['id']))
  if existing == 0:
   ret = { 'deleted':0, 'dns':{'a':0, 'ptr':0}}
  else:
   data = db.get_row()
   from dns import record_device_delete
   ret = record_device_delete({'A':data['a_id'],'PTR':data['ptr_id']})
   if data['base'] == 'pdu':
    ret['pem0'] = db.update_dict('rackinfo',{'pem0_pdu_unit':0,'pem0_pdu_slot':0},'pem0_pdu_id = %s'%(aDict['id']))
    ret['pem1'] = db.update_dict('rackinfo',{'pem1_pdu_unit':0,'pem1_pdu_slot':0},'pem0_pdu_id = %s'%(aDict['id']))
   ret.update({'deleted':db.do("DELETE FROM devices WHERE id = '%s'"%aDict['id'])})
 return ret

#
#
def clear(aDict):
 """Function docstring for clear TBD

 Args:

 Output:
 """
 with DB() as db:
  res = db.do("DELETE FROM devices")
 return { 'result':res }

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
 """Function docstring for webpage_list TBD. List webpages for devices

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
def connection_list(aDict):
 """Function docstring for connection_list TBD. List connections for a specific device

 Args:
  - device_id (required)

 Output:
 """
 ret = {}
 id = aDict['device_id']
 with DB() as db:
  ret['xist'] = db.do("SELECT id,alias,description,graph_type,graph_index,INET_NTOA(peer_ip) AS peer_ip, peer_interface FROM device_connections WHERE device_id = %s"%id)
  ret['data'] = db.get_rows()
 return ret

#
#
def connection_info(aDict):
 """Function docstring for connection_info TBD. Show specific connection for a device 

 Args:             
  - id (required)
  - device_id (required)
  - alias
  - description
  - graph_type
  - graph_index
  - peer_ip (string)
  - peer_interface

 Output:
 """
 ret = {}
 args = aDict
 id = args.pop('id','new')
 op = args.pop('op',None)
 with DB() as db:
  if op == 'update':
   from struct import unpack
   from socket import inet_aton
   def GL_ip2int(addr):
    return unpack("!I", inet_aton(addr))[0]
   args['peer_ip'] = GL_ip2int(args.get('peer_ip','0'))
   if not id == 'new':
    ret['update'] = db.update_dict('device_connections',args,"id=%s"%id) 
   else:
    ret['update'] = db.insert_dict('device_connections',args)
    id = db.get_last_id() if ret['update'] > 0 else 'new'

  if not id == 'new':
   from struct import pack
   from socket import inet_ntoa
   def GL_int2ip(addr):
    return inet_ntoa(pack("!I", addr))
   ret['xist'] = db.do("SELECT * FROM device_connections WHERE id = '%s'"%id)
   ret['data'] = db.get_row()
   ret['data']['peer_ip'] = GL_int2ip(ret['data']['peer_ip'])
  else:
   ret['data'] = {'id':'new','device_id':int(aDict['device_id']),'alias':'Unknown','description':'Unknown','graph_type':'SNMP','graph_index':None,'peer_ip':'0.0.0.0','peer_interface':None}
 return ret

#
#
def connection_delete(aDict):
 """Function docstring for connection_delete TBD. Delete a certain connection

 Args:
  - id (required)
  - device_id (required)

 Output:
 """
 ret = {}
 id = aDict['id']
 with DB() as db:
  ret['deleted'] = db.do("DELETE FROM device_connections WHERE id = %s"%id)
 return ret

############################################# Specials ###########################################
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
 ret = {}
 with DB() as db:
  db.do("SELECT INET_NTOA(ip) AS ipasc, hostname, mask, INET_NTOA(gateway) AS gateway, INET_NTOA(subnet) AS subnet, device_types.name AS type, domains.name AS domain FROM devices LEFT JOIN domains ON domains.id = devices.a_dom_id LEFT JOIN device_types ON device_types.id = devices.type_id LEFT JOIN subnets ON subnets.id = devices.subnet_id WHERE devices.id = '%s'"%aDict['id'])
  data = db.get_row()
 ip = data.pop('ipasc',None)
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
def discover(aDict):
 """Function docstring for discover TBD

 Args:
  - a_dom_id (required)
  - subnet_id (required)

 Output:
 """
 from time import time
 from threading import Thread, BoundedSemaphore
 from struct import pack
 from socket import inet_ntoa

 def GL_int2ip(addr):
  return inet_ntoa(pack("!I", addr))

 def __detect_thread(aIPint,aDB,aSema):
  res = detect({'ip':GL_int2ip(aIPint)})
  if res['result'] == 'OK':
   aDB[aIPint] = res['info']
  aSema.release()
  return True

 start_time = int(time())
 ret = {'errors':0 }

 with DB() as db:
  db.do("SELECT id,name FROM device_types")
  devtypes = db.get_dict('name')
  db.do("SELECT subnet,mask FROM subnets WHERE id = '%s'"%aDict['subnet_id'])
  net = db.get_row()

  ip_start = net['subnet'] + 1
  ip_end   = net['subnet'] + 2**(32 - net['mask']) - 1
  ret.update({'start':GL_int2ip(ip_start),'end':GL_int2ip(ip_end)})

  db_old, db_new = {}, {}
  ret['xist'] = db.do("SELECT ip FROM devices WHERE ip >= {} and ip <= {}".format(ip_start,ip_end))
  rows = db.get_rows()
  for item in rows:
   db_old[item['ip']] = True
  try:
   sema = BoundedSemaphore(10)
   for ipint in range(ip_start,ip_end):
    if db_old.get(ipint):
     continue
    sema.acquire()
    t = Thread(target = __detect_thread, args=[ipint, db_new, sema])
    t.name = "Detect %s"%ipint
    t.start()

   # Join all threads by acquiring all semaphore resources
   for i in range(10):
    sema.acquire()
   # We can now do inserts only (no update) as either we clear or we skip existing :-)
   sql = "INSERT INTO devices (ip, a_dom_id, subnet_id, snmp, model, type_id, hostname) VALUES ('{}',"+aDict['a_dom_id']+",{},'{}','{}','{}','{}')"
   count = 0
   for ipint,entry in db_new.iteritems():
    count += 1
    db.do(sql.format(ipint,aDict['subnet_id'],entry['snmp'],entry['model'],devtypes[entry['type']]['id'],"unknown_%i"%count))
  except Exception as err:
   ret['info']   = "Error:{}".format(str(err))
   ret['errors'] += 1
  else:
   ret['info'] = "Time spent:{}".format(int(time()) - start_time)
  ret['found']= len(db_new)
 return ret

#
#
def detect(aDict):
 """Function docstring for detect TBD

 Args:
  - ip (required)

 Output:
 """
 from os import system
 if system("ping -c 1 -w 1 {} > /dev/null 2>&1".format(aDict['ip'])) != 0:
  return {'result':'NOT_OK', 'info':'Not pingable' }

 ret = {'result':'OK'}

 from netsnmp import VarList, Varbind, Session
 try:
  # .1.3.6.1.2.1.1.1.0 : Device info
  # .1.3.6.1.2.1.1.5.0 : Device name
  devobjs = VarList(Varbind('.1.3.6.1.2.1.1.1.0'), Varbind('.1.3.6.1.2.1.1.5.0'))
  session = Session(Version = 2, DestHost = aDict['ip'], Community = SC['snmp']['read_community'], UseNumeric = 1, Timeout = 100000, Retries = 2)
  session.get(devobjs)
 except Exception as err:
  ret['snmp'] = "Not able to do SNMP lookup (check snmp -> read_community): %s"%str(err) 

 ret['info'] = {'model':'unknown', 'type':'generic','snmp':devobjs[1].val.lower() if devobjs[1].val else 'unknown'}


 if devobjs[0].val:
  infolist = devobjs[0].val.split()
  if infolist[0] == "Juniper":
   if infolist[1] == "Networks,":
    ret['info']['model'] = infolist[3].lower()
    for tp in [ 'ex', 'srx', 'qfx', 'mx', 'wlc' ]:
     if tp in ret['info']['model']:
      ret['info']['type'] = tp
      break
   else:
    subinfolist = infolist[1].split(",")
    ret['info']['model'] = subinfolist[2]
  elif infolist[0] == "VMware":
   ret['info']['model'] = "esxi"
   ret['info']['type']  = "esxi"
  elif infolist[0] == "Linux":
   ret['info']['model'] = 'debian' if "Debian" in devobjs[0].val else 'generic'
  else:
   ret['info']['model'] = " ".join(infolist[0:4])

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

############################################# Munin ###########################################
#
#
def graph_save(aDict):
 """Function docstring for graph_save TBD

 Args:

 Output:
 """
 ret = {}
 with DB() as db:
  db.do("SELECT value FROM settings WHERE section='graph' AND parameter = 'file'")
  graph_file = db.get_val('value')
  ret['xist'] = db.do("SELECT hostname, INET_NTOA(graph_proxy) AS proxy, domains.name AS domain FROM devices INNER JOIN domains ON domains.id = devices.a_dom_id WHERE graph_update = 1")
  rows = db.get_rows()
 with open(graph_file,'w') as output:
  for row in rows:
   output.write("[{}.{}]\n".format(row['hostname'],row['domain']))
   output.write("address {}\n".format(row['proxy']))
   output.write("update yes\n\n")
 return ret

#
#
def graph_info(aDict):
 """Function docstring for graph_info TBD

 Args:
  - id (required)
  - op (optional)
  - graph_proxy (optional)
  - graph_update (optional)


 Output:
 """
 with DB() as db:
  ret = {}
  if aDict.get('op') == 'update':
   args = {'graph_proxy':aDict.get('graph_proxy'),'id':int(aDict['id'])}
   args['graph_update'] = 0 if not aDict.get('graph_update') else int(aDict.get('graph_update'))
   ret['update'] = db.do("UPDATE devices SET graph_proxy = INET_ATON('%s'), graph_update = %i WHERE id = %i"%(args['graph_proxy'],int(args['graph_update']),args['id']))

  db.do("SELECT INET_NTOA(ip) AS ip, graph_update, device_types.name AS type_name, INET_NTOA(graph_proxy) AS graph_proxy, CONCAT(hostname,'.',domains.name) AS fqdn FROM devices LEFT JOIN domains ON devices.a_dom_id = domains.id LEFT JOIN device_types ON devices.type_id = device_types.id WHERE devices.id = '%s'"%aDict['id'])
  ret.update(db.get_row())
  db.do("SELECT value AS plugin_file FROM settings WHERE section = 'graph' AND parameter = 'plugins'")
  ret.update(db.get_row())

  if aDict.get('op') == 'detect':
   def GL_ping_os(ip):
    from os import system
    return system("ping -c 1 -w 1 " + ip + " > /dev/null 2>&1") == 0
  
   if GL_ping_os(ret['ip']):
    try:
     if ret['type_name'] in [ 'ex', 'srx', 'qfx', 'mx', 'wlc' ]:
      from sdcp.devices.junos import Junos
      activeinterfaces = []
      if not ret['type_name'] == 'wlc':
       with Junos(ret['ip']) as jdev:
        activeinterfaces = jdev.get_up_interfaces()
       with open(ret['plugin_file'], 'a') as graphfile:
        graphfile.write('ln -s /usr/local/sbin/plugins/snmp__{0} /etc/munin/plugins/snmp_{1}_{0}\n'.format(ret['type_name'],ret['fqdn']))
        graphfile.write('ln -s /usr/share/munin/plugins/snmp__uptime /etc/munin/plugins/snmp_' + ret['fqdn'] + '_uptime\n')
        graphfile.write('ln -s /usr/share/munin/plugins/snmp__users  /etc/munin/plugins/snmp_' + ret['fqdn'] + '_users\n')
        for ifd in activeinterfaces:
         graphfile.write('ln -s /usr/share/munin/plugins/snmp__if_    /etc/munin/plugins/snmp_' + ret['fqdn'] + '_if_'+ ifd['SNMP'] +'\n')
     elif ret['type_name'] == "esxi":
      with open(ret['plugin_file'], 'a') as graphfile:
       graphfile.write('ln -s /usr/share/munin/plugins/snmp__uptime /etc/munin/plugins/snmp_' + ret['fqdn'] + '_uptime\n')              
       graphfile.write('ln -s /usr/local/sbin/plugins/snmp__esxi    /etc/munin/plugins/snmp_' + ret['fqdn'] + '_esxi\n')
    except Exception as err:
     ret['op'] = "Error:%s"%str(err)
    else:
     ret['op'] = 'OK'
   else:
    ret['op'] = 'NO_PING'

 return ret
