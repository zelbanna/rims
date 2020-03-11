"""IPAM API module. Provides IP network and address management"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)


##################################### Networks ####################################
#
#
def network_list(aCTX, aArgs = None):
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
def network_info(aCTX, aArgs = None):
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
  ret['servers'] = [{'id':'NULL','service':None,'node':None}]
  ret['servers'].extend([{'id':k,'service':v['service'],'node':v['node']} for k,v in aCTX.services.items() if v['type'] == 'DHCP'])
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
 from rims.rest.dns import domain_ptr_list
 ret['domains'] = [{'id':'NULL','name':None,'server':None}]
 ret['domains'].extend(domain_ptr_list(aCTX, {'prefix':ret['data']['network']}))
 return ret


#
#
def network_delete(aCTX, aArgs = None):
 """Function docstring for network_delete TBD.

 Args:
  - id (required)

 Output:
 """
 ret = {}
 with aCTX.db as db:
  db.do("SELECT id, ptr_id, a_id, a_domain_id FROM ipam_addresses WHERE network_id = %s AND (ptr_id > 0 OR a_id > 0)"%aArgs['id'])
  for address in db.get_rows():
   address_delete(aCTX, address)
  ret['deleted'] = db.do("DELETE FROM ipam_networks WHERE id = %s"%aArgs['id'])
 return ret

#
#
def network_discover(aCTX, aArgs = None):
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
    aCTX.workers.add_semaphore(__detect_thread,sema,ip,addresses)
  aCTX.workers.block(sema,simultaneous)
 except Exception as err:
  ret['status'] = 'NOT_OK'
  ret['info']   = repr(err)
 else:
  ret['status'] = 'OK'
 return ret

#
#
def network_discrepancy(aCTX, aArgs = None):
 """Function retrieves orphan entries with no matching device or other use

 Args:

 Output:
  entries. list of ID and IP which are orphan
 """
 ret = {}
 with aCTX.db as db:
  db.do("SELECT id, ip AS ip_integer, INET_NTOA(ip) AS ip FROM ipam_addresses WHERE id NOT IN (SELECT ipam_id FROM devices_interfaces) AND type = 0 ORDER BY ip_integer")
  ret['entries'] = db.get_rows()
 return ret

#################################### DHCP ###############################
#
#
def server_leases(aCTX, aArgs = None):
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
def server_macs(aCTX, aArgs = None):
 """Function returns all MACs for ip addresses belonging to networks belonging to particular server.

 Args:
  - id (required)

 Output:
 """
 ret = {'status':'OK'}
 with aCTX.db as db:
  ret['count'] = db.do("SELECT ia.id, LPAD(hex(di.mac),12,0) AS mac, INET_NTOA(ia.ip) AS ip, ia.network_id AS network FROM device_interfaces AS di LEFT JOIN ipam_addresses AS ia ON di.ipam_id = ia.id LEFT JOIN ipam_networks AS ine ON ia.network_id = ine.id WHERE di.mac > 0 AND ine.server_id = %s"%aArgs['id'])
  ret['data']  = db.get_rows()
  for row in ret['data']:
   row['mac'] = ':'.join(row['mac'][i:i+2] for i in [0,2,4,6,8,10])
 return ret

################################## Addresses #############################
#
# Addresses contains types, IP (v4 for now), mac (for now until device has proper management-interface connecting to it), DNS connectors (A,PTR,Domain)
#

#
#
def address_list(aCTX, aArgs = None):
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
     tables.append('device_interfaces AS di ON ia.id = di.ipam_id')
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
def address_info(aCTX, aArgs = None):
 """ Function manages IPAM address instance info, can change IP from here as DNS is consistent

 Args:
  - id (required) <id>/'new'
  - op (optional) 'update'/'update_only'
  - ip (optional)
  - network_id (optional required when ip supplied)
  - a_domain_id (optional)
  - type (optional)
  - hostname (optional)

 Warning: these should not be altered in general, let system do it for you (!)
  - a_id (optional).
  - ptr_id (optional).

 Output:
  - same as above + ptr_domain_id
  - dns as result from DNS operation if ip, hostname or a_domain_id has changed.

 """
 ret = {'status':'OK','info':None}
 id = aArgs.pop('id','new')
 op = aArgs.pop('op',None)
 aArgs.pop('ptr_domain_id',None)
 with aCTX.db as db:
  if op:
   if (id != 'new'):
    if (db.do("SELECT INET_NTOA(ip) AS ip, network_id, a_id, a_domain_id, ptr_id, type, hostname, reverse_zone_id AS ptr_domain_id FROM ipam_addresses AS ia LEFT JOIN ipam_networks AS ine ON ia.network_id = ine.id WHERE ia.id = %s"%id) > 0):
     old = db.get_row()
     for k,v in old.items():
      if str(v) == str(aArgs.get(k)):
       aArgs.pop(k,None)
    else:
     return {'status':'NOT_OK', 'info':'Illegal id'}
   else:
    old = {'ip':'0.0.0.0','network_id':None,'a_id':0,'ptr_id':0,'a_domain_id':None,'type':0,'hostname':'unknown','ptr_domain_id':None}

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

    # Now there is an id with either default or updated values, correct them  with new a/ptr id or restore a_domain_id
    if ret['status'] == 'OK' and any(i in aArgs for i in ['a_domain_id','hostname','ip','network_id']):
     from rims.rest.dns import record_info, record_delete

     if 'a_domain_id' in aArgs and aArgs['a_domain_id'] in [None,'NULL'] and old['a_domain_id'] and (old['a_id'] > 0 or old['ptr_id'] > 0):
      dns_args   = {'a_id':0,'ptr_id':0}
      ret['A']   = {'delete':record_delete(aCTX, {'id':old['a_id'],   'domain_id':old['a_domain_id'],  'type':'A'})['status']}
      ret['PTR'] = {'delete':record_delete(aCTX, {'id':old['ptr_id'], 'domain_id':old['ptr_domain_id'],'type':'PTR'})['status']}
     else:
      dns_args = {}
      a_domain_id = aArgs.get('a_domain_id',old['a_domain_id'])
      db.do("SELECT name FROM domains WHERE id = %s"%a_domain_id)
      fqdn = '.'.join([aArgs.get('hostname',old['hostname']),db.get_val('name')])
      ret['A'] = {'delete':record_delete(aCTX, {'id':old['a_id'], 'domain_id':old['a_domain_id'],'type':'A'})['status'] if old['a_id'] > 0 and (old['a_domain_id'] is not None) else 'OK_NONE'}
      res = record_info(aCTX, {'id':'new','domain_id':a_domain_id,'name':fqdn,'content':ip,'type':'A','op':'insert'})
      if res['status'] == 'OK':
       dns_args['a_id'] = res['data']['id']
       dns_args['a_domain_id'] = res['data']['domain_id']
      else:
       dns_args['a_domain_id'] = old['a_domain_id']
      ret['A']['create'] = res['status']
      if 'network_id' in aArgs:
       db.do("SELECT reverse_zone_id FROM ipam_networks WHERE id = %s"%aArgs['network_id'])
       ptr_domain_id = db.get_val('reverse_zone_id')
      else:
       ptr_domain_id = old['ptr_domain_id']
      ptr = ip.split('.')
      ptr.reverse()
      ptr.append('in-addr.arpa')
      ret['PTR'] = {'delete':record_delete(aCTX, {'id':old['ptr_id'], 'domain_id':old['ptr_domain_id'],'type':'PTR'})['status'] if old['ptr_id'] > 0 else 'OK_NONE'}
      res = record_info(aCTX,   {'id':'new','domain_id':ptr_domain_id,'name':'.'.join(ptr),'content':fqdn,'type':'PTR','op':'insert'})
      if res['status'] == 'OK':
       dns_args['ptr_id'] = res['data']['id']
      ret['PTR']['create'] = res['status']
     if dns_args:
      ret['DNS'] = (db.update_dict('ipam_addresses',dns_args,'id=%s'%id) == 1)

  if op and op == 'update_only':
   pass
  elif not (id == 'new') and (db.do("SELECT ia.id, INET_NTOA(ip) AS ip, ia.state, network_id, INET_NTOA(ine.network) AS network, a_id, ptr_id, a_domain_id, ine.reverse_zone_id AS ptr_domain_id, type, hostname FROM ipam_addresses AS ia LEFT JOIN ipam_networks AS ine ON ia.network_id = ine.id WHERE ia.id = %s"%id) == 1):
   ret['data'] = db.get_row()
   ret['extra']= {'network':ret['data'].pop('network',None), 'ptr_domain_id': ret['data'].pop('ptr_domain_id',None)}
  else:
   if aArgs.get('network_id') and (db.do("SELECT INET_NTOA(network) AS network FROM ipam_networks WHERE id = %s"%aArgs['network_id']) > 0):
    network = db.get_val('network')
    network_id = int(aArgs['network_id'])
   else:
    network,network_id = '0.0.0.0',None
   ret['data'] = {'id':id,'network_id':network_id,'ip':network,'a_id':0,'ptr_id':0,'a_domain_id':None, 'type':0,'hostname':'unknown','state':'unknown'}
   ret['extra']= {'network':network, 'ptr_domain_id':None}
 return ret

#
#
def address_sanitize(aCTX, aArgs = None):
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
def address_find(aCTX, aArgs = None):
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

 consecutive = int(aArgs.get('consecutive',1))
 with aCTX.db as db:
  db.do("SELECT network, INET_NTOA(network) as netasc, mask FROM ipam_networks WHERE id = %(network_id)s"%aArgs)
  net = db.get_row()
  db.do("SELECT ip FROM ipam_addresses WHERE network_id = %(network_id)s"%aArgs)
  iplist = db.get_dict('ip')
 network = int(net.get('network'))
 start  = None
 ret    = { 'network':net['netasc'] }
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
def address_delete(aCTX, aArgs = None):
 """Function deletes an IP id

 Args:
  - id (required)

 Output:
  - status.
 """
 ret = {}
 from rims.rest.dns import record_delete
 with aCTX.db as db:
  if (db.do("SELECT a_id, a_domain_id, ptr_id, reverse_zone_id AS ptr_domain_id FROM ipam_addresses AS ia LEFT JOIN ipam_networks AS ine ON ia.network_id = ine.id WHERE ia.id = %s"%aArgs['id']) > 0):
   dns = db.get_row()
   for tp in ['a','ptr']:
    id,domain = '%s_id'%tp, '%s_domain_id'%tp
    ret[tp.upper()] = record_delete(aCTX, {'id':dns[id],'domain_id':dns[domain],'type':tp.upper()})['status'] if (dns[id] > 0 and dns[domain] is not None) else "OK_NONE"
  ret['deleted'] = (db.do("DELETE FROM ipam_addresses WHERE id = %(id)s"%aArgs) == 1)
  ret['status'] = 'OK' if ret['deleted'] else 'NOT_OK'
 return ret

#
#
def address_events(aCTX, aArgs = None):
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
