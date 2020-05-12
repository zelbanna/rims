"""
IPAM API module. Provides IP network and address management
"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)


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
 """
 ret = {}
 with aCTX.db as db:
  ret['count']    = db.do("SELECT ipam_networks.id, CONCAT(INET_NTOA(network),'/',mask) AS netasc, INET_NTOA(gateway) AS gateway, description, mask, network, st.service FROM ipam_networks LEFT JOIN servers ON ipam_networks.server_id = servers.id LEFT JOIN service_types AS st ON servers.type_id = st.id ORDER by network")
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
  - reverse_zone_id (optional)

 Output:
  - Same as above
 """
 ret = {}
 id = aArgs.pop('id','new')
 op = aArgs.pop('op',None)
 with aCTX.db as db:
  ret['servers'] = [{'id':k,'service':v['service'],'node':v['node']} for k,v in aCTX.services.items() if v['type'] == 'DHCP']
  if op == 'update':
   from struct import unpack
   from socket import inet_aton
   def GL_ip2int(addr):
    return unpack("!I", inet_aton(addr))[0]

   # Check gateway
   low   = GL_ip2int(aArgs['network'])
   high  = low + 2**(32-int(aArgs['mask'])) - 1
   try:    gwint = GL_ip2int(aArgs['gateway'])
   except: gwint = 0
   if not (low < gwint and gwint < high):
    gwint = low + 1
    ret['info'] = "illegal gateway"
   aArgs['gateway'] = str(gwint)
   aArgs['network']  = str(low)
   if id == 'new':
    ret['update'] = (db.insert_dict('ipam_networks',aArgs,'ON DUPLICATE KEY UPDATE id = LAST_INSERT_ID(id)') == 1)
    id = db.get_last_id() if ret['update'] > 0 else 'new'
   else:
    ret['update'] = (db.update_dict('ipam_networks',aArgs,'id=%s'%id) == 1)

  if not id == 'new':
   ret['found'] = (db.do("SELECT id, mask, description, INET_NTOA(network) AS network, INET_NTOA(gateway) AS gateway, reverse_zone_id, server_id FROM ipam_networks WHERE id = %s"%id) > 0)
   ret['data'] = db.get_row()
  else:
   ret['data'] = { 'id':'new', 'network':'0.0.0.0', 'mask':'24', 'gateway':'0.0.0.0', 'description':'New','reverse_zone_id':None,'server_id':None }
 from rims.api.dns import domain_ptr_list
 ret['domains'] = domain_ptr_list(aCTX, {'prefix':ret['data']['network']})
 return ret


#
#
def network_delete(aCTX, aArgs):
 """Function docstring for network_delete TBD.

 TODO: check if deleting addresses even if a_domain_id is null (old PTR?)

 Args:
  - id (required)

 Output:
 """
 ret = {}
 with aCTX.db as db:
  db.do("SELECT id, a_domain_id FROM ipam_addresses WHERE network_id = %s AND a_domain_id IS NOT NULL"%aArgs['id'])
  for address in db.get_rows():
    # INTERNAL from rims.api.ipam import address_delete
   address_delete(aCTX, address)
  ret['deleted'] = db.do("DELETE FROM ipam_networks WHERE id = %s"%aArgs['id'])
 return ret

#
#
def network_discover(aCTX, aArgs):
 """ Function discovers _new_ IP:s that answer to ping within a certain network. A list of such IP:s are returned

 Args:
  - id (required)
  - simultaneous (optional). Simultaneouse threads

 Output:
  - addresses. list of ip:s and ip_int pairs that answer to ping
 """
 from struct import pack
 from socket import inet_ntoa
 from os import system

 def __detect_thread(aIPint,aIPs):
  ip = inet_ntoa(pack("!I", aIPint))
  if system("ping -c 2 -w 2 %s > /dev/null 2>&1"%ip) == 0:
   aIPs.append(ip)
  return True

 addresses = []
 simultaneous = int(aArgs.get('simultaneous',20))
 ret = {'addresses':addresses}

 with aCTX.db as db:
  db.do("SELECT network,mask,reverse_zone_id FROM ipam_networks WHERE id = %s"%aArgs['id'])
  net = db.get_row()
  ip_start = net['network'] + 1
  ip_end   = net['network'] + 2**(32 - net['mask']) - 1
  ret.update({'start':{'ipint':ip_start,'ip':inet_ntoa(pack("!I", ip_start))},'end':{'ipint':ip_end,'ip':inet_ntoa(pack("!I", ip_end))},'reverse_zone_id':net['reverse_zone_id']})
  db.do("SELECT ip FROM ipam_addresses WHERE network_id = %s"%aArgs['id'])
  ip_list = db.get_dict('ip')

 try:
  sema = aCTX.workers.semaphore(simultaneous)
  for ip in range(ip_start,ip_end):
   if not ip_list.get(ip):
    aCTX.workers.queue_semaphore(__detect_thread,sema,ip,addresses)
  aCTX.workers.block(sema,simultaneous)
 except Exception as err:
  ret['status'] = 'NOT_OK'
  ret['info']   = repr(err)
 else:
  ret['status'] = 'OK'
 return ret

#
#
def network_discrepancy(aCTX, aArgs):
 """Function retrieves orphan entries with no matching device or other use

 Args:

 Output:
  entries. list of ID and IP which are orphan
 """
 ret = {}
 with aCTX.db as db:
  db.do("SELECT id, ip AS ip_integer, INET_NTOA(ip) AS ip FROM ipam_addresses WHERE id NOT IN (SELECT ipam_id FROM devices_interfaces) AND type = 0 ORDER BY ip_integer")
  ret['data'] = db.get_rows()
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
 servers = [{'service':v['service'],'node':v['node']} for v in aCTX.services.values() if v['type'] == 'DHCP']
 ret['servers'] = len(servers)
 for srv in servers:
  data = aCTX.node_function(srv['node'],srv['service'],'status')(aArgs = {'binding':ret['type']})['data']
  if data:
   ret['data'].extend(data)
 oui_s = ",".join(set([str(int(x.get('mac')[0:8].replace(':',''),16)) for x in ret['data']]))
 if len(oui_s) > 0:
  with aCTX.db as db:
   db.do("SELECT LPAD(HEX(oui),6,0) AS oui, company FROM oui WHERE oui in (%s)"%oui_s)
   oui_d = {x['oui']:x['company'] for x in db.get_rows()}
  for lease in ret['data']:
   lease['oui'] = oui_d.get(lease['mac'][0:8].replace(':','').upper())
 return ret

#
#
def server_macs(aCTX, aArgs):
 """Function returns all MACs for ip addresses belonging to networks belonging to particular server.

 Args:
  - id (required)

 Output:
 """
 ret = {'status':'OK'}
 with aCTX.db as db:
  ret['count'] = db.do("SELECT ia.id, LPAD(hex(di.mac),12,0) AS mac, INET_NTOA(ia.ip) AS ip, ia.network_id AS network FROM interfaces AS di LEFT JOIN ipam_addresses AS ia ON di.ipam_id = ia.id LEFT JOIN ipam_networks AS ine ON ia.network_id = ine.id WHERE di.mac > 0 AND ine.server_id = %s"%aArgs['id'])
  ret['data']  = db.get_rows()
  for row in ret['data']:
   row['mac'] = ':'.join(row['mac'][i:i+2] for i in [0,2,4,6,8,10])
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
 ret = {}
 with aCTX.db as db:
  if (db.do("SELECT mask, network, INET_NTOA(network) as netasc, gateway, INET_NTOA(gateway) as gwasc FROM ipam_networks WHERE id = %(network_id)s"%aArgs) == 1):
   network = db.get_row()
   ret['status']  = 'OK'
   ret['start']   = network['network']
   ret['size']    = 2**(32-network['mask'])
   ret['mask']    = network['mask']
   ret['network'] = network['netasc']
   ret['gateway'] = network['gwasc']
   tables = ['ipam_addresses AS ia']
   fields = ['ia.ip AS ip_integer','INET_NTOA(ia.ip) AS ip','ia.id','ia.state']
   for field in aArgs.get('extra',[]):
    if   field == 'device_id':
     fields.append('di.device_id')
     tables.append('interfaces AS di ON ia.id = di.ipam_id')
    elif field == 'a_domain_id':
     fields.extend(['a_domain_id','domains.name AS domain'])
     tables.append('domains ON a_domain_id = domains.id')
    else:
     fields.append(field)
   ret['count']   = db.do("SELECT %s FROM %s WHERE network_id = %s ORDER BY ip_integer"%(",".join(fields)," LEFT JOIN ".join(tables),aArgs['network_id']))
   ret['data'] = db.get_rows() if not 'dict' in aArgs else db.get_dict(aArgs['dict'])
  else:
   ret['status'] = 'NOT_OK'
 return ret

#
#
def address_info(aCTX, aArgs):
 """ Function manages IPAM address instance info, can change IP from here as DNS is consistent

 Args:
  - id (required) <id>/'new'
  - op (optional) 'update'/'update_only'
  - ip (optional)
  - network_id (optional required when ip supplied)
  - a_domain_id (optional)
  - type (optional)
  - hostname (optional)

 Output:
  - same as above + ptr_domain_id
  - A/PTR, from dns as result from DNS operation
  - status, if there has been an operation
 """
 ret = {}
 id = aArgs.pop('id','new')
 op = aArgs.pop('op',None)
 aArgs.pop('ptr_domain_id',None)
 with aCTX.db as db:
  if op:
   if (id != 'new'):
    if (db.do("SELECT INET_NTOA(ip) AS ip, network_id, a_domain_id, type, hostname, reverse_zone_id AS ptr_domain_id FROM ipam_addresses AS ia LEFT JOIN ipam_networks AS ine ON ia.network_id = ine.id WHERE ia.id = %s"%id) > 0):
     old = db.get_row()
    else:
     return {'status':'NOT_OK', 'info':'Illegal id'}
   else:
    old = {'ip':'0.0.0.0','network_id':None,'a_domain_id':None,'type':0,'hostname':'unknown','ptr_domain_id':None}
   ret = {'status':'OK','info':None}
   # Save for DNS
   ip  = aArgs.get('ip',old['ip'])

   if any(i in aArgs for i in ['ip','network_id']):
    from struct import unpack
    from socket import inet_aton
    def GL_ip2int(addr):
     return unpack("!I", inet_aton(addr))[0]
    aArgs['ip'] = GL_ip2int(ip)
    aArgs['network_id'] = aArgs.get('network_id',old['network_id'])
    """ if valid in network range AND available => then go """
    if (db.do("SELECT network FROM ipam_networks WHERE id = %(network_id)s AND %(ip)s > network AND %(ip)s < (network + POW(2,(32-mask))-1)"%aArgs) == 1):
     if (db.do("SELECT id FROM ipam_addresses WHERE ip = %(ip)s AND network_id = %(network_id)s"%aArgs) == 1):
      existing = db.get_val('id')
      if (existing and id == 'new') or (existing != int(id)):
       ret['status'] = 'NOT_OK'
       ret['info'] = 'IP/Network combination in use (%s)'%existing
      else:
       aArgs.pop('ip',None)
       aArgs.pop('network_id',None)
    else:
     ret['status'] = 'NOT_OK'
     ret['info'] = 'IP not in network range'

   if 'hostname' in aArgs:
    # INTERNAL from rims.api.ipam import address_sanitize
    aArgs['hostname'] = address_sanitize(aCTX, aArgs)['sanitized']

   if (len(aArgs) > 0) and ret['status'] == 'OK':
    if not id == 'new':
     try: ret['update'] = (db.update_dict('ipam_addresses',aArgs,'id=%s'%id) == 1)
     except:
      ret['status'] = 'NOT_OK'
      ret['info']   = "IPAM update failed"
    elif 'ip' in aArgs:
     try: ret['insert'] = (db.insert_dict('ipam_addresses',aArgs) == 1)
     except Exception as e:
      ret['status'] = 'NOT_OK'
      ret['info']   = 'IPAM insert failed (%s)'%repr(e)
     else:
      id = db.get_last_id()
    else:
     ret['status'] = 'NOT_OK'
     ret['info'] = 'Illegal address operation'

    # DNS
    if ret['status'] == 'OK' and any(i in aArgs for i in ['a_domain_id','hostname','ip','network_id']):
     from rims.api.dns import record_info, record_delete
     db.do("SELECT id, name FROM domains")
     domains = db.get_dict('id')
     ret.update({'A':{},'PTR':{}})

     # Remove
     if old['a_domain_id']:
      ret['A']['delete']   = record_delete(aCTX, {'domain_id':old['a_domain_id'],'name':'%s.%s'%(old['hostname'],domains[old['a_domain_id']]['name']), 'type':'A'})['status']
     if old['ptr_domain_id']:
      ptr = old['ip'].split('.')
      ptr.reverse()
      ptr.append('in-addr.arpa')
      ret['PTR']['delete'] = record_delete(aCTX, {'domain_id':old['ptr_domain_id'], 'name':'.'.join(ptr), 'type':'PTR'})['status']

     # Create - let record_info handle errors, if we have a domain we can create both A and PTR otherwise none (!)
     if aArgs.get('a_domain_id','NULL') != 'NULL':
      fqdn = '%s.%s'%(aArgs.get('hostname',old['hostname']),domains[int(aArgs['a_domain_id'])]['name'])
      ret['A']['create'] = record_info(aCTX, {'domain_id':aArgs['a_domain_id'], 'name':fqdn, 'type':'A', 'content':ip, 'op':'insert'})['status']
      ptr = ip.split('.')
      ptr.reverse()
      ptr.append('in-addr.arpa')
      if 'network_id' in aArgs and (db.do("SELECT reverse_zone_id FROM ipam_networks WHERE id = %s"%aArgs['network_id']) > 0):
       ret['PTR']['create'] = record_info(aCTX, {'domain_id':db.get_val('reverse_zone_id'), 'name':'.'.join(ptr), 'type':'PTR', 'content':fqdn, 'op':'insert'})['status']
      elif old['ip'] == ip:
       ret['PTR']['create'] = record_info(aCTX, {'domain_id':old['ptr_domain_id'], 'name':'.'.join(ptr), 'type':'PTR', 'content':fqdn, 'op':'insert'})['status']

  if op and op == 'update_only':
   pass
  elif not (id == 'new') and (db.do("SELECT ia.id, INET_NTOA(ip) AS ip, ia.state, network_id, INET_NTOA(ine.network) AS network, a_domain_id, ine.reverse_zone_id AS ptr_domain_id, type, hostname FROM ipam_addresses AS ia LEFT JOIN ipam_networks AS ine ON ia.network_id = ine.id WHERE ia.id = %s"%id) == 1):
   ret['data'] = db.get_row()
   ret['extra']= {'network':ret['data'].pop('network',None), 'ptr_domain_id': ret['data'].pop('ptr_domain_id',None)}
  else:
   if aArgs.get('network_id') and (db.do("SELECT INET_NTOA(network) AS network FROM ipam_networks WHERE id = %s"%aArgs['network_id']) > 0):
    network = db.get_val('network')
    network_id = int(aArgs['network_id'])
   else:
    network,network_id = '0.0.0.0',None
   ret['data'] = {'id':id,'network_id':network_id,'ip':network,'a_domain_id':None, 'type':0,'hostname':'unknown','state':'unknown'}
   ret['extra']= {'network':network, 'ptr_domain_id':None}
 return ret

#
#
def address_sanitize(aCTX, aArgs):
 """ Function sanitize info, e.g. hostnames, so that they will fit into DNS records

 Args:
  - hostname

 Output:
  - status
  - santizie
 """
 ret = {'status':'OK'}
 hostname = aArgs['hostname'].lower()
 if hostname.isalnum():
  ret['sanitized'] = hostname
 else:
  parsed,special = [],True
  for i in range(0,len(hostname)):
   if hostname[i].isalnum():
    special = False
    parsed.append(hostname[i])
   elif hostname[i] in ['-',' '] and not special:
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
  - consecutive (optional)

 Output:
 """
 from struct import pack
 from socket import inet_ntoa
 def GL_int2ip(addr):
  return inet_ntoa(pack("!I", addr))

 ret = {'status':'OK'}
 consecutive = int(aArgs.get('consecutive',1))
 with aCTX.db as db:
  if (db.do("SELECT network, INET_NTOA(network) as netasc, mask FROM ipam_networks WHERE id = %(network_id)s"%aArgs) == 0):
   return {'status':'NOT_OK', 'info':'Network not found'}
  net = db.get_row()
  db.do("SELECT ip FROM ipam_addresses WHERE network_id = %(network_id)s"%aArgs)
  iplist = db.get_dict('ip')
 network = int(net.get('network'))
 start  = None
 ret['network'] = net['netasc']
 for ip in range(network + 1, network + 2**(32-int(net.get('mask')))-1):
  if ip in iplist:
   start = None
  elif not start:
   count = consecutive
   if count > 1:
    start = ip
   else:
    ret['ip'] = GL_int2ip(ip)
    break
  else:
   if count == 2:
    ret['start'] = GL_int2ip(start)
    ret['end'] = GL_int2ip(start + consecutive - 1)
    break
   else:
    count = count - 1
 return ret

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
  if (db.do("SELECT INET_NTOA(ia.ip) AS ip, ia.hostname, a_domain_id, reverse_zone_id AS ptr_domain_id FROM ipam_addresses AS ia LEFT JOIN ipam_networks AS ine ON ia.network_id = ine.id WHERE ia.id = %s"%aArgs['id']) > 0):
   old = db.get_row()
   db.do("SELECT id, name FROM domains")
   domains = db.get_dict('id')
   if old['a_domain_id']:
    ret['A'] = record_delete(aCTX, {'name':'%s.%s'%(old['hostname'],domains[old['a_domain_id']]['name']), 'domain_id':old['a_domain_id'], 'type':'A'})['status']
   if old['ptr_domain_id']:
    ptr = old['ip'].split('.')
    ptr.reverse()
    ptr.append('in-addr.arpa')
    ret['PTR'] = record_delete(aCTX, {'name':'.'.join(ptr), 'domain_id':old['ptr_domain_id'],'type':'PTR'})['status']
  ret['deleted'] = (db.do("DELETE FROM ipam_addresses WHERE id = %(id)s"%aArgs) == 1)
  ret['status'] = 'OK' if ret['deleted'] else 'NOT_OK'
 return ret

#
#
def address_events(aCTX, aArgs):
 """ Function operates on events

 Args:
  - id (optional). find events for id
  - op (optional). 'clear'. clears events (all or for 'id')
  - extra (optional). list of extra fields to add (hostname,ip,ip_state)
  - limit (optional)
  - offset (optional)

 Output:
  - status
  - count (optional)
  - events (optional) list of {'time','state',<extra>} entries
 """
 ret = {'status':'OK'}
 with aCTX.db as db:
  if aArgs.get('op') == 'clear':
   if 'id' in aArgs:
    ret['count'] = db.do("DELETE FROM ipam_events WHERE ipam_id = %s"%aArgs['id'])
   else:
    db.do("TRUNCATE ipam_events")
  else:
   fields = ['DATE_FORMAT(ie.time,"%Y-%m-%d %H:%i") AS time', 'ie.state']
   tables = ['ipam_events AS ie']
   if 'id' in aArgs:
    filter = "ie.ipam_id = %s"%aArgs['id']
   else:
    filter = "TRUE"
    fields.append('ie.ipam_id AS id')
   if 'extra' in aArgs:
    tables.append('ipam_addresses AS ia')
    if 'hostname' in aArgs['extra']:
     fields.append('ia.hostname')
    if 'ip' in aArgs['extra']:
     fields.append('INET_NTOA(ia.ip) AS ip')
    if 'ip_state' in aArgs['extra']:
     fields.append('ia.state AS ip_state')
   ret['count'] = db.do("SELECT {} FROM {} WHERE {} ORDER BY time DESC LIMIT {} OFFSET {}".format(", ".join(fields), " LEFT JOIN ".join(tables), filter, aArgs.get('limit','50'), aArgs.get('offset','0')))
   ret['events']= db.get_rows()
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
   filter = "id IN (SELECT ia.id FROM ipam_addresses AS ia LEFT JOIN interfaces AS di ON di.ipam_id = ia.id LEFT JOIN devices ON devices.id = di.device_id WHERE devices.id = %s)"%aArgs['device_id']
  elif aArgs.get('network_id'):
   filter = "network_id = %s"%aArgs['network_id']
  else:
   filter = 'TRUE'
  ret['count'] = db.do("UPDATE ipam_addresses SET state = 'unknown' WHERE %s"%filter)
 return ret

#
#
def check(aCTX, aArgs):
 """ Initiate a status check for all or a subset of IP:s that belongs to proper interfaces

 Args:
  - networks (optional). List of network ids to check
  - repeat (optional). If declared, it's an integer with frequency.. This is the way to keep status checks 'in-memory'

 """
 with aCTX.db as db:
  db.do("SELECT id FROM ipam_networks" if not 'networks' in aArgs else "SELECT id FROM ipam_networks WHERE ipam_networks.id IN (%s)"%(','.join(str(x) for x in aArgs['networks'])))
  networks = db.get_rows()
  db.do("SELECT ia.id, INET_NTOA(ia.ip) AS ip, ia.state FROM ipam_addresses AS ia LEFT JOIN interfaces AS di ON di.ipam_id = ia.id WHERE network_id IN (%s) AND di.class IN ('wired','optical','virtual','logical') ORDER BY ip"%(','.join(str(x['id']) for x in networks)))
  addresses = db.get_rows()

 if 'repeat' in aArgs:
  # INTERNAL from rims.api.ipam import process
  aCTX.workers.schedule_periodic_function(process,'ipam_process',int(aArgs['repeat']),args = {'addresses':addresses}, output = aCTX.debugging())
  return {'status':'OK','function':'ipam_check','detach_frequency':aArgs['repeat']}
 else:
  # INTERNAL from rims.api.ipam import process
  process(aCTX,{'addresses':addresses})
  return {'status':'OK','function':'ipam_check'}

#
#
def process(aCTX, aArgs):
 """ Function checks all IP addresses

 Args:
  - addresses (required). List of addresses

 Output:
 """
 ret = {'status':'OK','function':'ipam_process'}
 from os import system
 report = aCTX.node_function('master','ipam','report', aHeader= {'X-Log':'false'})

 def __check_ip(aDev):
  aDev['old'] = aDev['state']
  try:    aDev['state'] = 'up' if (system("ping -c 1 -w 1 %s > /dev/null 2>&1"%(aDev['ip'])) == 0) or (system("ping -c 1 -w 1 %s > /dev/null 2>&1"%(aDev['ip'])) == 0) else 'down'
  except: aDev['state'] = 'unknown'
  return True

 aCTX.workers.block_map(__check_ip,aArgs['addresses'])

 changed = [dev for dev in aArgs['addresses'] if (dev['state'] != dev['old'])]
 if changed:
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
    ret[chg] = db.do("UPDATE ipam_addresses SET state = '%s' WHERE id IN (%s)"%(chg,",".join(str(x) for x in change)))
    begin = 0
    final  = len(change)
    while begin < final:
     end = min(final,begin+16)
     db.do("INSERT INTO ipam_events (ipam_id, state) VALUES %s"%(",".join("(%s,'%s')"%(x,chg) for x in change[begin:end])))
     begin = end
 return ret
