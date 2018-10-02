"""IPAM API module. Provides IP network and address management"""
__author__ = "Zacharias El Banna"
__version__ = "4.0GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

#
#
def status(aDict, aCTX):
 """ Initiate a status check for all or a subset of IP:s

 Args:
  - subnets (optional). List of subnet_ids to check

 """
 from zdcp.core.common import rest_call
 ret = {'local':[],'remote':[]}
 with aCTX.db as db:
  trim = "" if not aDict.get('subnets') else "WHERE ipam_networks.id IN (%s)"%(",".join([str(x) for x in aDict['subnets']]))
  db.do("SELECT ipam_networks.id, servers.node, servers.server FROM ipam_networks LEFT JOIN servers ON servers.id = ipam_networks.server_id %s"%trim)
  subnets = db.get_rows()
  for sub in subnets:
   count = db.do("SELECT id,INET_NTOA(ip) AS ip, state FROM ipam_addresses WHERE network_id = %s ORDER BY ip"%sub['id'])
   if count > 0:
    args = {'module':'ipam','func':'address_status_check','args':{'address_list':db.get_rows(),'subnet_id':sub['id']},'output':False}
    if not sub['node'] or sub['node'] == 'master':
     gWorkers.add_task(args)
     ret['local'].append(sub['id'])
    else:
     rest_call("%s/api/system_task_worker?node=%s"%(gSettings['nodes'][sub['node']],sub['node']),args)['data']
     ret['remote'].append(sub['id'])
 return ret

##################################### Networks ####################################
#
#
def network_list(aDict, aCTX):
 """Lists networks

 Args:

 Output:
  - networks. List of:
  -- id
  -- netasc
  -- gateway
  -- description
  -- network
  -- mask
 """
 ret = {}
 with aCTX.db as db:
  ret['count']    = db.do("SELECT ipam_networks.id, CONCAT(INET_NTOA(network),'/',mask) AS netasc, INET_NTOA(gateway) AS gateway, description, mask, network, server FROM ipam_networks LEFT JOIN servers ON ipam_networks.server_id = servers.id ORDER by network")
  ret['networks'] = db.get_rows()
 return ret

#
#
def network_info(aDict, aCTX):
 """Function docstring for info TBD

 Args:
  - id (required)
  - op (optional)
  - network (optional)
  - description (optional)
  - mask (optional)
  - gateway (optional)
  - reverse_zone_id (optional)

 Output:
  - Same as above
 """
 ret = {}
 id = aDict.pop('id','new')
 op = aDict.pop('op',None)
 with aCTX.db as db:
  db.do("SELECT id, server, node FROM servers WHERE type = 'DHCP'")
  ret['servers'] = db.get_rows()
  ret['servers'].append({'id':'NULL','server':None,'node':None})
  if op == 'update':
   from struct import unpack
   from socket import inet_aton
   def GL_ip2int(addr):
    return unpack("!I", inet_aton(addr))[0]

   # Check gateway
   low   = GL_ip2int(aDict['network'])
   high  = low + 2**(32-int(aDict['mask'])) - 1
   try:    gwint = GL_ip2int(aDict['gateway'])
   except: gwint = 0
   if not (low < gwint and gwint < high):
    gwint = low + 1
    ret['info'] = "illegal gateway"
   aDict['gateway'] = str(gwint)
   aDict['network']  = str(low)
   if id == 'new':
    ret['update'] = db.insert_dict('ipam_networks',aDict,'ON DUPLICATE KEY UPDATE id = id')
    id = db.get_last_id() if ret['update'] > 0 else 'new'
   else:
    ret['update'] = db.update_dict('ipam_networks',aDict,'id=%s'%id)

  if not id == 'new':
   ret['found'] = (db.do("SELECT id, mask, description, INET_NTOA(network) AS network, INET_NTOA(gateway) AS gateway, reverse_zone_id, server_id FROM ipam_networks WHERE id = %s"%id) > 0)
   ret['data'] = db.get_row()
  else:
   ret['data'] = { 'id':'new', 'network':'0.0.0.0', 'mask':'24', 'gateway':'0.0.0.0', 'description':'New','reverse_zone_id':None,'server_id':None }
 from zdcp.rest.dns import domain_ptr_list
 ret['domains'] = domain_ptr_list({'prefix':ret['data']['network']}, aCTX)
 ret['domains'].append({'id':'NULL','name':None,'server':None})
 return ret

#
#
def network_inventory(aDict, aCTX):
 """Allocation of IP addresses within a network.

 Args:
  - id (required)
  - dict(optional)
  - extra (optional) list of extra info

 Output:
 """
 ret = {}
 with aCTX.db as db:
  db.do("SELECT mask, network, INET_NTOA(network) as netasc, gateway, INET_NTOA(gateway) as gwasc FROM ipam_networks WHERE id = %(id)s"%aDict)
  network = db.get_row()
  ret['start']   = network['network']
  ret['size']    = 2**(32-network['mask'])
  ret['mask']    = network['mask']
  ret['network'] = network['netasc']
  ret['gateway'] = network['gwasc']
  fields = ['ip AS ip_integer','INET_NTOA(ip) AS ip','id']
  fields.extend(aDict.get('extra',[]))
  ret['count']   = db.do("SELECT %s FROM ipam_addresses WHERE network_id = %s ORDER BY ip_integer"%(",".join(fields),aDict['id']))
  entries = db.get_rows()
  if 'mac' in aDict.get('extra',[]):
   for ip in entries:
    ip['mac'] = ':'.join(s.encode('hex') for s in str(hex(ip['mac']))[2:].zfill(12).decode('hex')).lower()
  if not aDict.get('dict'):
   ret['entries'] = entries
  else:
   ret['entries'] = {e[aDict['dict']]:e for e in entries}
 return ret

#
#
def network_delete(aDict, aCTX):
 """Function docstring for network_delete TBD.

 Args:
  - id (required)

 Output:
 """
 ret = {}
 with aCTX.db as db:
  ret['addresses'] = db.do("DELETE FROM ipam_addresses WHERE network_id = %s"%aDict['id']) 
  ret['deleted'] = db.do("DELETE FROM ipam_networks WHERE id = " + aDict['id'])
 return ret

#
#
def network_discover(aDict, aCTX):
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
  if system("ping -c 1 -w 1 %s > /dev/null 2>&1"%ip) == 0:
   aIPs.append(ip)
  return True

 addresses = []
 simultaneous = int(aDict.get('simultaneous',20))
 ret = {'addresses':addresses}

 with aCTX.db as db:
  db.do("SELECT network,mask FROM ipam_networks WHERE id = %s"%aDict['id'])
  net = db.get_row()
  ip_start = net['network'] + 1
  ip_end   = net['network'] + 2**(32 - net['mask']) - 1
  ret.update({'start':{'ipint':ip_start,'ip':GL_int2ip(ip_start)},'end':{'ipint':ip_end,'ip':GL_int2ip(ip_end)}})
  db.do("SELECT ip FROM ipam_addresses WHERE network_id = %s"%aDict['id'])
  ip_list = db.get_dict('ip')

 try:
  sema = gWorkers.semaphore(simultaneous)
  for ip in range(ip_start,ip_end):
   if not ip_list.get(ip):
    gWorkers.add_sema(__detect_thread,sema,ip,addresses)
  gWorkers.block(sema,simultaneous)
 except Exception as err:
  ret['error']   = str(err)

 return ret

#
#
def network_discrepancy(aDict, aCTX):
 """Function retrieves orphan entries with no matching device or other use

 Args:

 Output:
  entries. list of ID and IP which are orphan
 """
 ret = {}
 with aCTX.db as db:
  db.do("SELECT id, ip AS ip_integer, INET_NTOA(ip) AS ip FROM ipam_addresses WHERE id NOT IN (SELECT ipam_id FROM devices) ORDER BY ip_integer")
  ret['entries'] = db.get_rows()
 return ret

#################################### DHCP ###############################
#
#
def server_leases(aDict, aCTX):
 """Server_leases returns free or active server leases for DHCP servers

 Args:
  - type (required). active/free

 Output:
 """
 from zdcp.core.common import node_call
 ret = {'data':[]}
 with aCTX.db as db:
  ret['servers'] = db.do("SELECT server,node FROM servers WHERE type = 'DHCP'")
  servers = db.get_rows()
 for srv in servers:
  data = node_call(srv['node'],srv['server'],'leases',{'type':aDict['type']})['data']
  if data:
   ret['data'].extend(data)
 return ret


################################## Addresses #############################
#
#
def address_find(aDict, aCTX):
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

 consecutive = int(aDict.get('consecutive',1))
 with aCTX.db as db:
  db.do("SELECT network, INET_NTOA(network) as netasc, mask FROM ipam_networks WHERE id = %(network_id)s"%aDict)
  net = db.get_row()
  db.do("SELECT ip FROM ipam_addresses WHERE network_id = %(network_id)s"%aDict)
  iplist = db.get_dict('ip')
 network = int(net.get('network'))
 start  = None
 ret    = { 'network':net['netasc'] }
 for ip in range(network + 1, network + 2**(32-int(net.get('mask')))-1):
  if iplist.get(ip):
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
def address_allocate(aDict, aCTX):
 """ Function allocate IP relative a specific network.

 Args:
  - ip (required)
  - network_id (required)
  - mac (optional)

 Output:
  - valid (boolean) Indicates valid within network
  - success (boolean)
  - id. Id of address
 """
 ret = {'success':False}
 try:    mac = int(str(aDict.get('mac','0')).replace(":",""),16)
 except: mac = 0
 with aCTX.db as db:
  ret['valid'] = (db.do("SELECT network FROM ipam_networks WHERE id = %(network_id)s AND INET_ATON('%(ip)s') > network AND INET_ATON('%(ip)s') < (network + POW(2,(32-mask))-1)"%aDict) == 1)
  if ret['valid']:
   try:
    ret['success'] = (db.do("INSERT INTO ipam_addresses(ip,network_id,mac) VALUES(INET_ATON('%s'),%s,%s)"%(aDict['ip'],aDict['network_id'],mac)) == 1)
    ret['id']= db.get_last_id() if ret['success'] else None
   except: pass
 return ret

#
#
def address_reallocate(aDict, aCTX):
 """ Function re allocate address ID to a new IP within the same or a new network.

 Args:
  - id (required)
  - ip (required)
  - network_id (required)

 Output:
  - valid (boolean)
  - available (boolean)
  - success (boolean)
 """
 ret = {'success':False,'valid':False,'available':False}
 with aCTX.db as db:
  ret['valid'] = (db.do("SELECT network FROM ipam_networks WHERE id = '%(network_id)s AND INET_ATON('%(ip)s') > network AND INET_ATON('%(ip)s') < (network + POW(2,(32-mask))-1)"%aDict) == 1)
  if ret['valid']:
   ret['available'] = (db.do("SELECT id FROM ipam_addresses WHERE ip = INET_ATON('%(ip)s') AND network_id = %(network_id)s"%aDict) == 0)
   if ret['available']:
    ret['success'] = (db.do("UPDATE ipam_addresses SET ip = INET_ATON('%(ip)s'), network_id = %(network_id)s WHERE id = %(id)s"%aDict) == 1)
 return ret


#
#
def address_delete(aDict, aCTX):
 """Function deletes an IP id

 Args:
  - id (required)

 Output:
  - result (always) boolean
 """
 ret = {}
 with aCTX.db as db:
  ret['result'] = (db.do("DELETE FROM ipam_addresses WHERE id = %(id)s"%aDict) > 0)
 return ret

#
#
def address_from_id(aDict, aCTX):
 """ Funtion returns mapping between IPAM id and ip,network_id

 Args:
  - id (required)

 Output:
  - ip
  - network
  - network_id
 """
 with aCTX.db as db:
  db.do("SELECT INET_NTOA(ip) AS ip, network_id, INET_NTOA(network) AS network, mask FROM ipam_addresses LEFT JOIN ipam_networks ON ipam_networks.id = ipam_addresses.network_id WHERE ipam_addresses.id = %(id)s"%aDict)
  ret = db.get_row()
 return ret

#
#
def address_status_check(aDict, aCTX):
 """ Process a list of IDs, IP addresses and states {id,'ip',state} and perform a ping. State values are: 0 (not seen), 1(up), 2(down).
  If state has changed this will be reported back. This function is node independent.

 Args:
  - subnet_id
  - address_list (required)

 Output:
 """
 from os import system

 def __pinger(aArgs):
  try:    aArgs['dev']['new'] = 1 if (system("ping -c 1 -w 1 %s > /dev/null 2>&1"%(aArgs['dev']['ip'])) == 0) else 2
  except: aArgs['dev']['new'] = None
  return True

 sema = gWorkers.semaphore(20)  
 for dev in aDict['address_list']:
  gWorkers.add_sema(__pinger,sema, {'dev':dev})
 gWorkers.block(sema,20)

 args = {}
 for n in [1,2]:
  changed = list(dev['id'] for dev in aDict['address_list'] if (dev['new'] != dev['state'] and dev['new'] == n))
  if len(changed) > 0:
   args['up' if n == 1 else 'down'] = changed
 if len(args.keys()) > 0:
  if gSettings['system']['id'] == 'master':
   address_status_report(args, aCTX)
  else:
   from zdcp.core.common import rest_call
   rest_call("%s/api/ipam_address_status_report?log=false"%gSettings['system']['master'],args)
  return {'result':'CHECK_COMPLETED'}

#
#
def address_status_report(aDict, aCTX):
 """ Updates IP addresses' status

 Args:
  - up (optional).   list of id that changed to up
  - down (optional). list of id that changed to down

 Output:
  - result
 """
 ret = {}
 with aCTX.db as db:
  for chg in [('up',1),('down',2)]:
   change = aDict.get(chg[0])
   if change:
    changed = ",".join(map(str,change))
    ret[chg[0]] = db.do("UPDATE ipam_addresses SET state = %s WHERE ID IN (%s)"%(chg[1],changed))
 return ret
