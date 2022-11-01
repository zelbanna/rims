"""IPAM API module. Provides IP network and address management"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

from ipaddress import ip_address, ip_network
from subprocess import run, DEVNULL
from time import time

def __detect_state(aIP):
 """ Ping 'IP' once to detect presence """
 return run(['ping','-c','1','-w','1',aIP], stdout=DEVNULL).returncode == 0
##################################### Networks ####################################
#
#
def network_list(aCTX, aArgs):
 """Lists networks

 Args:

 Output:
  - data. List of:
  -- id
  -- netasc
  -- gateway
  -- description
  -- network
  -- mask
  -- class
 """
 ret = {}
 with aCTX.db as db:
  ret['count'] = db.query("SELECT ipam_networks.id, CONCAT(INET6_NTOA(network),'/',mask) AS netasc, INET6_NTOA(gateway) AS gateway, description, st.service, IF(IS_IPV4(INET6_NTOA(network)),'v4','v6') AS class FROM ipam_networks LEFT JOIN servers ON ipam_networks.server_id = servers.id LEFT JOIN service_types AS st ON servers.type_id = st.id ORDER by network")
  ret['data'] = db.get_rows()
 return ret

#
#
def network_info(aCTX, aArgs):
 """Function docstring for info

 Args:
  - id (required)
  - op (optional)
  - network (optional required)
  - mask (optional required)
  - gateway (optional required)
  - description (optional)
  - vrf (optional)
  - reverse_zone_id (optional required)

  - extra (optional). 'servers'/'domains'

 Output:
  - Same as above
 """
 ret = {}
 id = aArgs.pop('id','new')
 op = aArgs.pop('op',None)
 extra = aArgs.pop('extra',[])

 with aCTX.db as db:
  if 'servers' in extra:
   ret['servers'] = [{'id':'NULL','service':'N/A','node':'N/A'}]
   ret['servers'].extend({'id':k,'service':v['service'],'node':v['node']} for k,v in aCTX.services.items() if v['type'] == 'DHCP')

  if op == 'update':
   try:
    network = ip_address(aArgs['network'])
    gateway = ip_address(aArgs['gateway'])
    broadcast= str(ip_network('%s/%s'%(aArgs['network'],aArgs['mask'])).broadcast_address)
    mask = int(aArgs['mask'])
   except Exception as e:
    ret['status'] = 'NOT_OK'
    ret['info'] = str(e)
   else:
    if id == 'new':
     ret['update'] = (db.execute("INSERT INTO ipam_networks SET network = INET6_ATON('%s'), mask = %s, gateway = INET6_ATON('%s'), broadcast = INET6_ATON('%s'), description = '%s', vrf = '%s', server_id = %s, reverse_zone_id = %s ON DUPLICATE KEY UPDATE id = LAST_INSERT_ID(id)"%(aArgs['network'],mask,aArgs['gateway'], broadcast, aArgs.get('description','N/A'), aArgs.get('vrf','default'), aArgs['server_id'] if aArgs.get('server_id') else 'NULL' ,aArgs['reverse_zone_id'] if aArgs.get('reverse_zone_id') else 'NULL')) == 1)
     id = db.get_last_id() if ret['update'] > 0 else 'new'
    else:
     ret['update'] = (db.execute("UPDATE ipam_networks SET network = INET6_ATON('%s'), mask = %s, gateway = INET6_ATON('%s'), broadcast = INET6_ATON('%s'), description = '%s', vrf = '%s', server_id = %s, reverse_zone_id = %s WHERE id = %s"%(aArgs['network'],aArgs['mask'],aArgs['gateway'],broadcast, aArgs.get('description','N/A'), aArgs.get('vrf','default'), aArgs['server_id'] if aArgs.get('server_id') else 'NULL' ,aArgs['reverse_zone_id'] if aArgs.get('reverse_zone_id') else 'NULL',id)) == 1)

  if id != 'new':
   ret['found'] = (db.query("SELECT id, mask, description, INET6_NTOA(network) AS network, INET6_NTOA(gateway) AS gateway, reverse_zone_id, server_id FROM ipam_networks WHERE id = %s"%id) > 0)
   ret['data'] = db.get_row()
  else:
   ret['data'] = { 'id':'new', 'network':'0.0.0.0', 'mask':'24', 'gateway':'0.0.0.0', 'description':'New','reverse_zone_id':None,'server_id':None }
  if 'domains' in extra:
   from rims.api.dns import domain_ptr_list
   ret['domains'] = domain_ptr_list(aCTX, {'prefix':ret['data']['network']})
 return ret


#
#
def network_delete(aCTX, aArgs):
 """Function docstring for network_delete TBD.

 Args:
  - id (required)

 Output:
 """
 ret = {}
 with aCTX.db as db:
  db.query("SELECT id, a_domain_id FROM ipam_addresses AS ia WHERE network_id = %s AND a_domain_id IS NOT NULL"%aArgs['id'])
  for id in db.get_rows():
    # INTERNAL from rims.api.ipam import address_delete
   address_delete(aCTX, id)
  ret['deleted'] = bool(db.execute("DELETE FROM ipam_networks WHERE id = %s"%aArgs['id']))
 return ret

#
#
def network_discover(aCTX, aArgs):
 """ Function discovers _new_ IP:s that answer to ping within a certain network. A list of such IP:s are returned

 Args:
  - id (required)
  - simultaneous (optional). Simultaneouse threads

 Output:
  - addresses. list of ip:s (objects) that answer to ping
 """
 def __detect_thread(aIP,aIPs):
  if __detect_state(aIP) or __detect_state(aIP):
   aIPs.append(aIP)
  return True

 addresses = []
 simultaneous = int(aArgs.get('simultaneous',20))
 ret = {'addresses':addresses}

 with aCTX.db as db:
  db.query("SELECT CONCAT(INET6_NTOA(network),'/',mask) AS network, reverse_zone_id FROM ipam_networks WHERE id = %s"%aArgs['id'])
  info  = db.get_row()
  net = ip_network(info['network'])
  ret.update({'network':str(net),'reverse_zone_id':info['reverse_zone_id']})
  db.query("SELECT INET6_NTOA(ia.ip) AS ip FROM ipam_addresses AS ia WHERE network_id = %s"%aArgs['id'])
  existing = [x['ip'] for x in db.get_rows()]

 if net.version == 4:
  try:
   sema = aCTX.semaphore(simultaneous)
   for ip in net.hosts():
    if ip not in existing:
     aCTX.queue_semaphore(__detect_thread,sema,str(ip),addresses)
   for _ in range(simultaneous):
    sema.acquire()
  except Exception as err:
   ret['status'] = 'NOT_OK'
   ret['info']   = repr(err)
  else:
   ret['status'] = 'OK'
 else:
  ret['status'] = 'OK'
 return ret

################################## Addresses #############################
#
# Addresses contains types, IP (v4 for now)
#
def address_list(aCTX, aArgs):
 """Allocation of IP addresses within a network.

 Args:
  - network_id (required)
  - dict(optional)
  - extra (optional) list of extra info, 'device_id' will give device_id

 Output:
 """
 with aCTX.db as db:
  if db.query("SELECT mask, INET6_NTOA(network) as network, INET6_NTOA(gateway) as gateway, IF(IS_IPV4(INET6_NTOA(network)),'v4','v6') AS class FROM ipam_networks WHERE id = %(network_id)s"%aArgs):
   ret = db.get_row()
   ret['status'] = 'OK'
   net = ip_network(f"{ret['network']}/{ret['mask']}")
   ret['size'] = net.num_addresses
   fields = ['INET6_NTOA(ia.ip) AS ip','ia.id','ia.state']
   joins = ['ipam_addresses AS ia']
   extras = aArgs.get('extra')
   if extras:
    if 'ip_integer' in extras:
     # EXTRA: This is the only location for IPv4 to integer translation - Can only be used with v4 addresses
     fields.append('INET_ATON(INET6_NTOA(ia.ip)) AS ip_integer')
    if 'device_id' in extras:
     fields.append('di.device_id')
     joins.append('interfaces AS di ON ia.id = di.ipam_id')
    if 'a_domain_id' in extras:
     fields.extend(['a_domain_id','domains.name AS domain'])
     joins.append('domains ON a_domain_id = domains.id')
    if 'hostname' in extras:
     fields.append('ia.hostname')
    if 'reservation' in extras:
     fields.append('ir.id AS resv_id')
     joins.append('ipam_reservations AS ir ON ir.id = ia.id')
   ret['count']   = db.query("SELECT %s FROM %s WHERE network_id = %s ORDER BY ia.ip"%(",".join(fields)," LEFT JOIN ".join(joins),aArgs['network_id']))
   ret['data'] = db.get_rows() if 'dict' not in aArgs else db.get_dict(aArgs['dict'])
  else:
   ret = {'status':'NOT_OK'}
 return ret

#
#
def address_info(aCTX, aArgs):
 """ Function manages IPAM address instance info and also updates DNS

 Args:
  - id (required) <id>/'new'
  - op (optional) 'update'/'update_only'

  - ip (optional required)
  - network_id (optional required)
  - hostname (optional required)
  - a_domain_id (optional required)

 Output:
  - same as above + ptr_domain_id
  - A/PTR, from dns as result from DNS operation
  - status, if there has been an operation
 """
 ret = {}
 id = aArgs.pop('id','new')
 op = aArgs.pop('op',None)
 aArgs.pop('ptr_domain_id',None)
 aArgs.pop('state',None)
 with aCTX.db as db:
  if op:
   if id != 'new':
    if db.query("SELECT INET6_NTOA(ia.ip) AS ip, network_id, a_domain_id, hostname, reverse_zone_id AS ptr_domain_id, IF(IS_IPV4(INET6_NTOA(ia.ip)),'v4','v6') AS class FROM ipam_addresses AS ia LEFT JOIN ipam_networks AS ine ON ia.network_id = ine.id WHERE ia.id = %s"%id):
     old = db.get_row()
    else:
     return {'status':'NOT_OK', 'info':'Illegal id'}
   else:
    old = {'ip':'0.0.0.0','network_id':None,'a_domain_id':None,'hostname':'unknown','ptr_domain_id':None, 'class':None }
   ret = {'status':'OK','info':None}
   # Save for DNS
   ip  = ip_address(aArgs.get('ip',old['ip']))
   aArgs['network_id'] = aArgs.get('network_id',old['network_id'])
   # if valid in network range AND available => then go
   # Fetch network here and use with PTR
   if db.query("SELECT INET6_NTOA(ine.network) AS network, mask, reverse_zone_id FROM ipam_networks AS ine WHERE ine.id = %s AND INET6_ATON('%s') >= ine.network AND INET6_ATON('%s') <= ine.broadcast"%(aArgs['network_id'],ip,ip)):
    network_db = db.get_row()
    if db.query("SELECT ia.id FROM ipam_addresses AS ia WHERE ia.network_id = %s AND ia.ip = INET6_NTOA('%s')"%(aArgs['network_id'],ip)):
     existing = db.get_val('id')
     if (existing and id == 'new') or (existing != int(id)):
      ret['status'] = 'NOT_OK'
      ret['info'] = f"IP/Network combination in use ({existing})"
   else:
    ret['status'] = 'NOT_OK'
    ret['info'] = 'IP not in network range'

   if ret['status'] == 'OK':
    # INTERNAL from rims.api.ipam import address_sanitize
    aArgs['hostname'] = address_sanitize(aCTX, {'hostname':aArgs.get('hostname',old['hostname'])})['sanitized']
    aArgs['a_domain_id'] = aArgs.get('a_domain_id',old['a_domain_id'])
    if id != 'new':
     try: ret['update'] = (db.execute("UPDATE ipam_addresses SET network_id = %s, a_domain_id = %s, hostname = '%s', ip = INET6_ATON('%s') WHERE id = %s"%(aArgs['network_id'],aArgs['a_domain_id'] if aArgs.get('a_domain_id') else 'NULL', aArgs['hostname'], ip,id)) == 1)
     except:
      ret['status'] = 'NOT_OK'
      ret['info']   = "IPAM update failed"
    else:
     try: ret['insert'] = (db.execute("INSERT INTO ipam_addresses SET network_id = %s, a_domain_id = %s, hostname = '%s', ip = INET6_ATON('%s')"%(aArgs['network_id'], aArgs['a_domain_id'] if aArgs.get('a_domain_id') else 'NULL', aArgs['hostname'], ip)) == 1)
     except Exception as e:
      ret['status'] = 'NOT_OK'
      ret['info']   = 'IPAM insert failed (%s)'%repr(e)
     else:
      id = db.get_last_id()

    # DNS
    if ret['status'] == 'OK':
     FWD = 'A' if ip.version == 4 else 'AAAA'
     from rims.api.dns import record_info, record_delete
     db.query("SELECT id, name FROM domains")
     domains = {x['id']:x['name'] for x in db.get_rows()}
     ret.update({FWD:{},'PTR':{}})

     # Remove (PTR could remain, if we are sure that the old actually existed (!))
     if old['a_domain_id']:
      ret[FWD]['delete'] = record_delete(aCTX, {'domain_id':old['a_domain_id'],'name':'%s.%s'%(old['hostname'],domains[old['a_domain_id']]), 'type':FWD})['status']
     if old['ptr_domain_id'] and ip.version == 4:
      ret['PTR']['delete'] = record_delete(aCTX, {'domain_id':old['ptr_domain_id'], 'name':ip.reverse_pointer, 'type':'PTR'})['status']

     # Create - let record_info handle errors, if we have a domain we can create both A and PTR otherwise none (!)
     if aArgs.get('a_domain_id') not in (None,'NULL'):
      fqdn = '%s.%s'%(aArgs.get('hostname',old['hostname']),domains[int(aArgs['a_domain_id'])])
      ret[FWD]['create'] = record_info(aCTX, {'domain_id':aArgs['a_domain_id'], 'name':fqdn, 'type':FWD, 'content':str(ip), 'op':'insert'})['status']
      ret[FWD]['fqdn'] = fqdn
      # PTR: If there is a new ip/net combo, try that one, else try restore the old one (neither might work!)
      # PTR: .. could have saved a delete above but then we don't know if there anyway wasn't a record
      if ip.version == 4 and (network_db['mask'] >= 24 or ip in ip_network('%(network)s/24'%network_db)):
       ret['PTR']['create'] = record_info(aCTX, {'domain_id':network_db['reverse_zone_id'], 'name':ip.reverse_pointer, 'type':'PTR', 'content':fqdn, 'op':'insert'})['status']
      else:
       ret['PTR']['create'] ='NOT_OK_V%s_DOMAIN'%ip.version

  if op and op == 'update_only':
   ret['id'] = id
   ret['ip'] = str(ip)
  elif id != 'new' and (db.query("SELECT ia.id, INET6_NTOA(ia.ip) AS ip, ia.state, network_id, INET6_NTOA(ine.network) AS network, a_domain_id, ine.reverse_zone_id AS ptr_domain_id, hostname FROM ipam_addresses AS ia LEFT JOIN ipam_networks AS ine ON ia.network_id = ine.id WHERE ia.id = %s"%id) == 1):
   ret['data'] = db.get_row()
   ret['extra']= {'network':ret['data'].pop('network',None), 'ptr_domain_id': ret['data'].pop('ptr_domain_id',None)}
  else:
   if aArgs.get('network_id') and (db.query("SELECT INET6_NTOA(network) AS network FROM ipam_networks WHERE id = %s"%aArgs['network_id']) > 0):
    network = db.get_val('network')
    network_id = int(aArgs['network_id'])
   else:
    network,network_id = 'N/A', None
   ret['data'] = {'id':id,'network_id':network_id,'ip':network,'a_domain_id':None, 'hostname':'unknown','state':'unknown'}
   ret['extra']= {'network':network, 'ptr_domain_id':None}
 return ret

#
#
def address_sanitize(aCTX, aArgs):
 """ Function sanitize info, e.g. hostnames, so that they will fit into DNS records

 Args:
  - hostname

 Output:
  - santizie
 """
 ret = {}
 hostname = aArgs['hostname'].lower()
 if hostname.isalnum():
  ret['sanitized'] = hostname
 else:
  parsed , special = [] , True
  for i in range(0,len(hostname)):
   if hostname[i].isalnum():
    special = False
    parsed.append(hostname[i])
   elif hostname[i] in ['-',' ','.','/'] and not special:
    parsed.append('-')
    special = True
  ret['sanitized'] = ''.join(parsed)

 return ret

#
#
def address_find(aCTX, aArgs):
 """Function docstring for address_find TBD

 Args:
  - network_id (required)

 Output:
 """
 with aCTX.db as db:
  if not db.query("SELECT CONCAT(INET6_NTOA(network),'/',mask) AS network FROM ipam_networks WHERE id = %(network_id)s"%aArgs):
   return {'status':'NOT_OK', 'info':'Network not found'}
  net = ip_network(db.get_val('network'))
  if net.version == 4:
   db.query("SELECT INET6_NTOA(ia.ip) AS ip FROM ipam_addresses AS ia WHERE ia.network_id = %(network_id)s"%aArgs)
   existing = [x['ip'] for x in db.get_rows()]
   for addr in net.hosts():
    ipstr = str(addr)
    if ipstr not in existing:
     return {'status':'OK', 'ip':ipstr}
  else:
   from random import randint
   return {'status':'OK','ip':str(ip_address(int.from_bytes(net.network_address.packed,byteorder='big') + randint(1,min(100000,net.num_addresses))))}
 return {'status':'NOT_OK','info':'No IP found'}

#
#
def address_delete(aCTX, aArgs):
 """Function deletes an IP id

 Args:
  - id (required)

 Output:
  - status
 """
 ret = {}
 from rims.api.dns import record_delete
 with aCTX.db as db:
  if db.query("SELECT INET6_NTOA(ia.ip) AS ip, ia.hostname, ia.a_domain_id, reverse_zone_id AS ptr_domain_id FROM ipam_addresses AS ia LEFT JOIN ipam_networks AS ine ON ia.network_id = ine.id WHERE ia.id = %s"%aArgs['id']):
   old = db.get_row()
   ip = ip_address(old['ip'])
   db.query("SELECT id, name FROM domains")
   domains = {x['id']:x['name'] for x in db.get_rows()}
   FWD = 'A' if ip.version == 4 else 'AAAA'
   if old['a_domain_id']:
    ret[FWD] = record_delete(aCTX, {'name':'%s.%s'%(old['hostname'],domains[old['a_domain_id']]), 'domain_id':old['a_domain_id'], 'type':FWD})['status']
   if old['ptr_domain_id'] and ip.version == 4:
    ret['PTR'] = record_delete(aCTX, {'name':ip.reverse_pointer, 'domain_id':old['ptr_domain_id'],'type':'PTR'})['status']
  ret['deleted'] = bool(db.execute("DELETE FROM ipam_addresses WHERE id = %s"%aArgs['id']))
  ret['status'] = 'OK' if ret['deleted'] else 'NOT_OK'
 return ret

#################################### Monitor #################################
#
#
def clear(aCTX, aArgs):
 """ Clear all interface statistics, for all or subset of ipam addresses

 Args:
  - device_id (optional)
  - network_id (optional)

 """
 ret = {'status':'OK'}
 with aCTX.db as db:
  if aArgs.get('device_id'):
   flter = "id IN (SELECT ia.id FROM ipam_addresses AS ia LEFT JOIN interfaces AS di ON di.ipam_id = ia.id LEFT JOIN devices ON devices.id = di.device_id WHERE devices.id = %s)"%aArgs['device_id']
  elif aArgs.get('network_id'):
   flter = "network_id = %s"%aArgs['network_id']
  else:
   flter = 'TRUE'
  ret['count'] = db.execute("UPDATE ipam_addresses AS ia SET ia.state = 'unknown' WHERE %s"%flter)
 return ret

#
#
def check(aCTX, aArgs):
 """ Initiate a status check for all or a subset of IP:s that belongs to proper interfaces

 TODO: check all alternatives, LEFT JOIN interface_alternatives AS iia ON iia.interface_id = di.interface_id .... OR iia.ipam_id = ia.id

 Args:
  - networks (optional). List of network ids to check
  - repeat (optional). If declared, it's an integer with frequency.. This is the way to keep status checks 'in-memory'

 """
 addresses = []
 with aCTX.db as db:
  if db.query("SELECT id FROM ipam_networks" if 'networks' not in aArgs else "SELECT id FROM ipam_networks WHERE ipam_networks.id IN (%s)"%(','.join(str(x) for x in aArgs['networks']))):
   networks = db.get_rows()
   db.query("SELECT ia.id, INET6_NTOA(ia.ip) AS ip, ia.state FROM ipam_addresses AS ia WHERE network_id IN (%s)"%(','.join(str(x['id']) for x in networks)))
   addresses = db.get_rows()

 if addresses:
  report = aCTX.node_function(aCTX.node if aCTX.db else 'master','ipam','report', aHeader= {'X-Log':'false'})

  if 'repeat' in aArgs:
   # INTERNAL from rims.api.ipam import process
   aCTX.schedule_api_periodic(process,'ipam_process',int(aArgs['repeat']),args = {'addresses':addresses,'report':report}, output = aCTX.debug)
   return {'status':'OK','function':'ipam_check','detach_frequency':aArgs['repeat']}
  else:
   # INTERNAL from rims.api.ipam import process
   process(aCTX,{'addresses':addresses,'report':report})
   return {'status':'OK','function':'ipam_check'}
 else:
  return {'status':'OK','function':'ipam_check','info':'no addresses'}

#
#
def process(aCTX, aArgs):
 """ Function checks all IP addresses

 Args:
  - addresses (required). List of addresses

 Output:
 """
 ret = {'status':'OK','function':'ipam_process'}

 def __check_IP(aDev):
  aDev['old'] = aDev['state']
  try:
   aDev['state'] = 'up' if __detect_state(aDev['ip']) or __detect_state(aDev['ip']) else 'down'
  except:
   aDev['state'] = 'unknown'
  return True

 aCTX.queue_block(__check_IP,aArgs['addresses'])

 changed = [dev for dev in aArgs['addresses'] if dev['state'] != dev['old']]
 if changed:
  report = aArgs['report'] if aArgs.get('report') else aCTX.node_function(aCTX.node if aCTX.db else 'master','ipam','report', aHeader= {'X-Log':'false'})

  # Assume/hope influxdb client is configured locally
  tmpl = 'ipam,host_id=%s,host_ip=%s state=%s {0}'.format(int(time()))
  records = [tmpl%( x['id'], x['ip'] ,1 if x['state'] == 'up' else 0) for x in changed]
  aCTX.influxdb.write(records)
  args = {'up':[x['id'] for x in changed if x['state'] == 'up'], 'down':[x['id'] for x in changed if x['state'] == 'down']}
  ret['up'] = len(args['up'])
  ret['down'] = len(args['down'])
  report(aArgs = args)
 return ret

#
#
def report(aCTX, aArgs):
 """ Updates addresses' status

 Args:
  - up (optional).   List of id that changed to up
  - down (optional). List of id that changed to down

 Output:
  - up (number of updated up state)
  - down (number of updated down state)
 """
 ret = {'function':'ipam_report'}
 with aCTX.db as db:
  for chg in ['up','down']:
   change = aArgs.get(chg)
   if change:
    ret[chg] = db.execute("UPDATE ipam_addresses AS ia SET ia.state = '%s' WHERE id IN (%s)"%(chg,",".join(str(x) for x in change)))
 return ret

#################################### DHCP ###############################
#
#
def server_leases(aCTX, aArgs):
 """Server_leases returns free or active server leases for DHCP servers

 Args:
  - type (required). active/free

 Output:
 """
 ret = {'data':[],'type':aArgs.get('type','active')}
 for infra in [{'service':v['service'],'node':v['node']} for v in aCTX.services.values() if v['type'] == 'DHCP']:
  data = aCTX.node_function(infra['node'],"services.%s"%infra['service'],'status')(aArgs = {'binding':ret['type']})['data']
  if data:
   ret['data'].extend(data)
 oui_s = set([str(int(x.get('mac')[0:8].replace(':',''),16)) for x in ret['data']])
 if oui_s:
  with aCTX.db as db:
   db.query("SELECT LPAD(HEX(oui),6,0) AS oui, company FROM oui WHERE oui in (%s)"%','.join(oui_s))
   oui_d = {x['oui']:x['company'] for x in db.get_rows()}
  for lease in ret['data']:
   lease['oui'] = oui_d.get(lease['mac'][0:8].replace(':','').upper())
 return ret

#
#
def server_macs(aCTX, aArgs):
 """Function returns all MACs for ip addresses belonging to networks belonging to particular server.

 TODO:  optimize into one query?
 Args:
  - server_id (required)
  - alternatives (optional), default: False

 Output:
 """
 tmpl = "ia.id, LPAD(hex(di.mac),12,0) AS mac, INET6_NTOA(ia.ip) AS ip, ia.network_id AS network FROM ipam_addresses AS ia JOIN ipam_networks AS ine ON ia.network_id = ine.id"
 ret = {'status':'OK'}
 with aCTX.db as db:
  ret['count']  = db.query("SELECT %s INNER JOIN interfaces AS di ON di.ipam_id = ia.id WHERE di.mac > 0 AND ine.server_id = %s"%(tmpl, aArgs['server_id']))
  ret['data']   = db.get_rows()
  if aArgs.get('alternatives'):
   ret['count'] += db.query("SELECT %s INNER JOIN interface_alternatives AS dia ON dia.ipam_id = ia.id INNER JOIN interfaces AS di ON di.interface_id = dia.interface_id WHERE di.mac > 0 AND ine.server_id = %s"%(tmpl, aArgs['server_id']))
   ret['data'].extend(db.get_rows())
  for row in ret['data']:
   row['mac'] = ':'.join(row['mac'][i:i+2] for i in [0,2,4,6,8,10])
 return ret

#
#
def reservation_list(aCTX, aArgs):
 """ Function retrieves allocated ip addresses for either server_id or network_id

 Args:
  - server_id (optional)
  - network_id (optional)

 Output:
  - data
 """
 ret = {}
 with aCTX.db as db:
  if aArgs.get('network_id'):
   ret['count'] = db.query("SELECT ir.id, INET6_NTOA(ia.ip) AS ip, type FROM ipam_reservations AS ir LEFT JOIN ipam_addresses AS ia ON ir.id = ia.id WHERE ia.network_id = %s ORDER BY ia.ip"%aArgs['network_id'])
  else:
   ret['count'] = db.query("SELECT ir.id, INET6_NTOA(ia.ip) AS ip, type, ia.network_id, INET6_NTOA(ine.network) AS network FROM ipam_reservations AS ir LEFT JOIN ipam_addresses AS ia ON ir.id = ia.id LEFT JOIN ipam_networks AS ine ON ia.network_id = ine.id WHERE ine.server_id = %s AND IS_IPV4(INET6_NTOA(ine.network)) ORDER BY ia.ip"%aArgs['server_id'])
  ret['data'] = db.get_rows()
 return ret

#
#
def reservation_new(aCTX, aArgs):
 """ Function inserts a new reservation for address (ip) or scope of addresses (start => end)

 aArgs:
  - network_id (required)
  - type (required) 'dhcp'/'reservation'
  - ip (optional)
  - start (optional)
  - end (optional)
  - a_domain_id (optional)

 Output:
 """
 with aCTX.db as db:
  if aArgs.get('ip'):
   try:
    ip = ip_address(aArgs['ip'])
   except:
    ret = {'status':'NOT_OK','info':'Illegal IP'}
   else:
    ret = address_info(aCTX, {'op':'update_only', 'id':'new', 'network_id':aArgs['network_id'], 'ip':str(ip), 'hostname':'resv-%i'%int(ip), 'a_domain_id':aArgs['a_domain_id'] if aArgs.get('a_domain_id') else 'NULL'})
    ret['reserved'] = (db.execute("INSERT INTO ipam_reservations (id, type) VALUES (%s, '%s')"%(ret['id'],aArgs.get('type','dhcp'))) > 0) if ret['status'] == 'OK' else False
  else:
   ret = {'status':'NOT_OK'}
   net = aArgs['network_id']
   dom = aArgs['a_domain_id'] if aArgs.get('a_domain_id') else 'NULL'
   # v4
   if db.query("SELECT ine.network FROM ipam_networks AS ine WHERE ine.id = %s AND INET6_ATON('%s') >= ine.network AND INET6_ATON('%s') <= ine.broadcast"%(net,aArgs['start'],aArgs['end'])):
    if db.query("SELECT ia.id, INET6_NTOA(ia.ip) AS ip FROM ipam_addresses AS ia WHERE ia.network_id = %s AND INET6_ATON('%s') <= ia.ip AND ia.ip <= INET6_ATON('%s')"%(net,aArgs['start'],aArgs['end'])):
     ret['info'] = 'Occupied range'
     ret['data'] = db.get_rows()
    else:
     ret['status'] = 'OK'
     ret['reserved'] = True
     ip = ip_address(aArgs['start'])
     end = ip_address(aArgs['end'])
     while ip <= end:
      res = address_info(aCTX, {'op':'update_only', 'id':'new', 'network_id':net, 'ip':str(ip), 'hostname':'resv-%i'%int(ip), 'a_domain_id':dom})
      if not (res['status'] == 'OK' and (db.execute("INSERT INTO ipam_reservations (id, type) VALUES (%s, '%s')"%(res['id'], aArgs.get('type','dhcp'))) > 0)):
       ret['reserved'] = False
      ip = ip + 1
   else:
    ret['info'] = 'IP not in network range'
 return ret

#
#
def reservation_delete(aCTX, aArgs):
 """ Function deletes a reserved address (id)

 Args:
  - id (optional)

 Output:
 """
 # Since DB constraints will delete reservation entry, with IPAM entry this is really a No OP
 return address_delete(aCTX, {'id':aArgs['id']})
