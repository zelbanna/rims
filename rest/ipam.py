"""IPAM API module. Provides IP network and address management"""
__author__ = "Zacharias El Banna"
__add_globals__ = lambda x: globals().update(x)

#
#
def status(aCTX, aArgs = None):
 """ Initiate a status check for all or a subset of IP:s

 Args:
  - networks (optional). List of network ids to check
  - repeat (optional). If declared, it's an integer with frequency.. This is the way to keep address status checks 'in-memory'

 """
 ret = {}
 ipam_nodes = {}
 with aCTX.db as db:
  trim = "" if not aArgs.get('networks') else "WHERE ipam_networks.id IN (%s)"%(','.join(str(x) for x in aArgs['networks']))
  db.do("SELECT ipam_networks.id, servers.node, servers.service FROM ipam_networks LEFT JOIN servers ON servers.id = ipam_networks.server_id %s"%trim)
  for sub in db.get_rows():
   node = 'master' if not sub['node'] else sub['node']
   node_addresses = ipam_nodes.get(node,[])
   count = db.do("SELECT ia.id, ia.id, INET_NTOA(ip) AS ip, ia.state, devices.notify FROM ipam_addresses AS ia LEFT JOIN devices ON devices.ipam_id = ia.id WHERE network_id = %s ORDER BY ia.ip"%sub['id'])
   if count > 0:
    ret[node] = ret.get(node,[])
    ret[node].append(sub['id'])
    node_addresses.extend(db.get_rows())
    ipam_nodes[node] = node_addresses

 for node,data in ipam_nodes.items():
  args = {'module':'ipam','func':'address_status_check','args':{'addresses':data,'repeat':aArgs.get('repeat')},'output':False}
  if node == 'master':
   aCTX.workers.add_task(args)
  else:
   try: aCTX.rest_call("%s/api/system/task_worker"%(aCTX.nodes[node]['url']),aArgs = args, aHeader = {'X-Log':'false','X-Route':node}, aDataOnly = True)
   except Exception as e:
    aCTX.log("ipam_status REST failure (%s => %s)"%(node,repr(e)))
 return ret

#
#
def events(aCTX, aArgs = None):
 """ Function operates on events

 Args:
  - id (optional). find events for id
  - op (optional). 'clear'. clears events (all or for 'id')
 
 Output:
  - status
  - count (optional)
  - events (optional) list of {'time','state'} entries
 """
 ret = {'status':'OK'}
 with aCTX.db as db:
  if aArgs.get('op') == 'clear':
   if aArgs.get('id'):
    ret['count'] = db.do("DELETE FROM ipam_events WHERE ipam_id = %s"%aArgs['id'])
   else:
    db.do("TRUNCATE ipam_events")
  elif aArgs.get('id'):
   ret['count'] = db.do("SELECT DATE_FORMAT(time,'%%Y-%%m-%%d %%H:%%i') AS time,state FROM ipam_events WHERE ipam_id = %s ORDER BY time DESC"%aArgs['id'])
   ret['events']= db.get_rows()
  else:
   ret['status'] = 'NOT_OK'
 return ret

#

##################################### Networks ####################################
#
#
def network_list(aCTX, aArgs = None):
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
  ret['count']    = db.do("SELECT ipam_networks.id, CONCAT(INET_NTOA(network),'/',mask) AS netasc, INET_NTOA(gateway) AS gateway, description, mask, network, servers.service FROM ipam_networks LEFT JOIN servers ON ipam_networks.server_id = servers.id ORDER by network")
  ret['networks'] = db.get_rows()
 return ret

#
#
def network_info(aCTX, aArgs = None):
 """Function docstring for info TBD

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
  ret['servers'] = [{'id':k,'service':v['service'],'node':v['node']} for k,v in aCTX.servers.items() if v['type'] == 'DHCP']
  ret['servers'].append({'id':'NULL','service':None,'node':None})
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
    ret['update'] = (db.insert_dict('ipam_networks',aArgs,'ON DUPLICATE KEY UPDATE id = id') == 1)
    id = db.get_last_id() if ret['update'] > 0 else 'new'
   else:
    ret['update'] = (db.update_dict('ipam_networks',aArgs,'id=%s'%id) == 1)

  if not id == 'new':
   ret['found'] = (db.do("SELECT id, mask, description, INET_NTOA(network) AS network, INET_NTOA(gateway) AS gateway, reverse_zone_id, server_id FROM ipam_networks WHERE id = %s"%id) > 0)
   ret['data'] = db.get_row()
  else:
   ret['data'] = { 'id':'new', 'network':'0.0.0.0', 'mask':'24', 'gateway':'0.0.0.0', 'description':'New','reverse_zone_id':None,'server_id':None }
 from rims.rest.dns import domain_ptr_list
 ret['domains'] = domain_ptr_list(aCTX, {'prefix':ret['data']['network']})
 ret['domains'].append({'id':'NULL','name':None,'server':None})
 return ret

#
#
def network_inventory(aCTX, aArgs = None):
 """Allocation of IP addresses within a network.

 Args:
  - id (required)
  - dict(optional)
  - extra (optional) list of extra info

 Output:
 """
 ret = {}
 with aCTX.db as db:
  db.do("SELECT mask, network, INET_NTOA(network) as netasc, gateway, INET_NTOA(gateway) as gwasc FROM ipam_networks WHERE id = %(id)s"%aArgs)
  network = db.get_row()
  ret['start']   = network['network']
  ret['size']    = 2**(32-network['mask'])
  ret['mask']    = network['mask']
  ret['network'] = network['netasc']
  ret['gateway'] = network['gwasc']
  fields = ['ip AS ip_integer','INET_NTOA(ip) AS ip','id']
  fields.extend(aArgs.get('extra',[]))
  ret['count']   = db.do("SELECT %s FROM ipam_addresses WHERE network_id = %s ORDER BY ip_integer"%(",".join(fields),aArgs['id']))
  entries = db.get_rows()
  if 'mac' in aArgs.get('extra',[]):
   for ip in entries:
    ip['mac'] = ':'.join("%s%s"%x for x in zip(*[iter("{:012x}".format(ip['mac']))]*2))
  if not aArgs.get('dict'):
   ret['entries'] = entries
  else:
   ret['entries'] = {e[aArgs['dict']]:e for e in entries}
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
  ret['addresses'] = db.do("DELETE FROM ipam_addresses WHERE network_id = %s"%aArgs['id']) 
  ret['deleted'] = db.do("DELETE FROM ipam_networks WHERE id = " + aArgs['id'])
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
  if system("ping -c 1 -w 1 %s > /dev/null 2>&1"%ip) == 0:
   aIPs.append(ip)
  return True

 addresses = []
 simultaneous = int(aArgs.get('simultaneous',20))
 ret = {'addresses':addresses}

 with aCTX.db as db:
  db.do("SELECT network,mask FROM ipam_networks WHERE id = %s"%aArgs['id'])
  net = db.get_row()
  ip_start = net['network'] + 1
  ip_end   = net['network'] + 2**(32 - net['mask']) - 1
  ret.update({'start':{'ipint':ip_start,'ip':GL_int2ip(ip_start)},'end':{'ipint':ip_end,'ip':GL_int2ip(ip_end)}})
  db.do("SELECT ip FROM ipam_addresses WHERE network_id = %s"%aArgs['id'])
  ip_list = db.get_dict('ip')

 try:
  sema = aCTX.workers.semaphore(simultaneous)
  for ip in range(ip_start,ip_end):
   if not ip_list.get(ip):
    aCTX.workers.add_semaphore(__detect_thread,sema,ip,addresses)
  aCTX.workers.block(sema,simultaneous)
 except Exception as err:
  ret['error']   = repr(err)

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
  db.do("SELECT id, ip AS ip_integer, INET_NTOA(ip) AS ip FROM ipam_addresses WHERE id NOT IN (SELECT ipam_id FROM devices) ORDER BY ip_integer")
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
 servers = [{'service':v['service'],'node':v['node']} for v in aCTX.servers.values() if v['type'] == 'DHCP']
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

################################## Addresses #############################
#
#
def address_info(aCTX, aArgs = None):
 """ Function manages IPAM address instance info, address can not be changed from here as

 Args:
  - id (required)
  - network_id (optional required)
  - mac (optional)
  - ip (optional)
  - state (optional)

 Output:

 """
 ret ={}
 id = aArgs.pop('id','new')
 op = aArgs.pop('op',None)
 with aCTX.db as db:
  if op == 'update':
   network = aArgs.pop('network_id',None)
   if aArgs.get('mac'):
    try:    aArgs['mac'] = int(str(aArgs.get('mac','0')).replace(":",""),16)
    except: aArgs['mac'] = 0
   if aArgs.get('state'):
    try:    state = int(aArgs['state'])
    except: state = 0
    aArgs['state'] = state if state >= 0 and state <= 2 else 0
   if aArgs.get('ip'):
    from struct import unpack
    from socket import inet_aton
    def GL_ip2int(addr):
     return unpack("!I", inet_aton(addr))[0]
    ip = GL_ip2int(aArgs.pop('ip',None))
    """ valid in network range AND available => then add back """
    if (db.do("SELECT network FROM ipam_networks WHERE id = %s AND %s > network AND %s < (network + POW(2,(32-mask))-1)"%(network,ip,ip)) == 1) and (db.do("SELECT id FROM ipam_addresses WHERE ip = %s AND network_id = %s"%(ip,network)) == 0):
     aArgs['ip'] = ip
   if not id == 'new':
    ret['update'] = db.update_dict('ipam_addresses',aArgs,'id=%s'%id)
   elif aArgs.get('ip'):
    ret['update'] = db.insert_dict('ipam_addresses',aArgs)
    id = db.get_last_id() if ret['update'] > 0 else 'new'
  if not id == 'new':
   ret['found'] = (db.do("SELECT id, INET_NTOA(ip) AS ip, state, network_id, LPAD(hex(mac),12,0) AS mac FROM ipam_addresses WHERE id = %s"%id) == 1)
   ret['data'] = db.get_row()
   ret['data']['mac'] = ':'.join(ret['data']['mac'][i:i+2] for i in [0,2,4,6,8,10]) 
  else:
   ret['data'] = {'id':'new','ip':'127.0.0.1','network_id':None,'mac':'00:00:00:00:00:00','state':0}
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
def address_allocate(aCTX, aArgs = None):
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
 try:    mac = int(str(aArgs.get('mac','0')).replace(":",""),16)
 except: mac = 0
 with aCTX.db as db:
  ret['valid'] = (db.do("SELECT network FROM ipam_networks WHERE id = %(network_id)s AND INET_ATON('%(ip)s') > network AND INET_ATON('%(ip)s') < (network + POW(2,(32-mask))-1)"%aArgs) == 1)
  if ret['valid']:
   try:
    ret['success'] = (db.do("INSERT INTO ipam_addresses(ip,network_id,mac) VALUES(INET_ATON('%s'),%s,%s)"%(aArgs['ip'],aArgs['network_id'],mac)) == 1)
    ret['id']= db.get_last_id() if ret['success'] else None
   except: pass
 return ret

#
#
def address_reallocate(aCTX, aArgs = None):
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
  ret['valid'] = (db.do("SELECT network FROM ipam_networks WHERE id = '%(network_id)s AND INET_ATON('%(ip)s') > network AND INET_ATON('%(ip)s') < (network + POW(2,(32-mask))-1)"%aArgs) == 1)
  if ret['valid']:
   ret['available'] = (db.do("SELECT id FROM ipam_addresses WHERE ip = INET_ATON('%(ip)s') AND network_id = %(network_id)s"%aArgs) == 0)
   if ret['available']:
    ret['success'] = (db.do("UPDATE ipam_addresses SET ip = INET_ATON('%(ip)s'), network_id = %(network_id)s WHERE id = %(id)s"%aArgs) == 1)
 return ret


#
#
def address_delete(aCTX, aArgs = None):
 """Function deletes an IP id

 Args:
  - id (required)

 Output:
  - result (always) boolean
 """
 ret = {}
 with aCTX.db as db:
  ret['status'] = (db.do("DELETE FROM ipam_addresses WHERE id = %(id)s"%aArgs) > 0)
 return ret

#
#
def address_status_fetch(aCTX, aArgs = None):
 """ Function fetch a list of addresses and states {id,'ip',state} for a list of networks

 Args:
  - networks

 Output:
  - addresses
 """
 ret = {}
 with aCTX.db as db:
  ret['count'] = db.do("SELECT ia.id, INET_NTOA(ip) AS ip, devices.notify, ia.state FROM ipam_addresses AS ia LEFT JOIN devices ON devices.ipam_id = ia.id WHERE network_id IN (%s) ORDER BY ia.ip"%(','.join(str(x) for x in aArgs['networks'])))
  if ret['count'] > 0:
   ret['addresses'] = db.get_rows()
 return ret

#
#
def address_status_check(aCTX, aArgs = None):
 """ Function processes a list of IDs, IP addresses and states {id,'ip',state} and perform a ping. State values are: 0 (not seen), 1(up), 2(down).
  If state has changed this will be reported back.
  This function is node independent.

 Args:
  - addresses (optional required). If supplied the list is processed
  - networks  (optional required). If not (!) address list is supplied addresses will be fetched for the network id:s in this list
  - repeat (optional). Describes frequency for repeated checks' interval

 Output:
 """

 addresses = aArgs['addresses'] if aArgs.get('addresses') else aCTX.node_function('master','ipam','address_status_fetch', aHeader = {'X-Log':'false'})(aArgs = {'networks':aArgs['networks']})['addresses']

 if aArgs.get('repeat'):
  freq = aArgs.pop('repeat')
  aCTX.workers.add_task({'id':'address_status_check', 'module':'ipam','func':'address_status_check','output':False,'args':{'addresses':addresses}},freq)
  return {'status':'CONTINUOUS_INITIATED_%s'%freq}

 from os import system
 def __liveness_check(aDev):
  aDev['old'] = aDev['state']
  try:    aDev['state'] = 1 if (system("ping -c 1 -w 1 %s > /dev/null 2>&1"%(aDev['ip'])) == 0) else 2
  except: pass
  return True

 nworkers = max(20,int(aCTX.config['workers']) - 5)
 sema = aCTX.workers.semaphore(nworkers)
 for dev in addresses:
  aCTX.workers.add_semaphore(__liveness_check, sema, dev)
 aCTX.workers.block(sema,nworkers)

 changed = [dev for dev in addresses if (dev['state'] != dev['old'])]
 args = {'up':[(dev['id'],dev['notify']) for dev in changed if dev['state'] == 1], 'down':[(dev['id'],dev['notify']) for dev in changed if dev['state'] == 2]}
 up   = len(args['up'])
 down = len(args['down'])
 if up > 0 or down > 0:
  aCTX.node_function('master','ipam','address_status_report', aHeader = {'X-Log':'false'})(aArgs = args)
 return {'status':'CHECK_COMPLETED_%s_%s'%(up,down)}

#
#
def address_status_report(aCTX, aArgs = None):
 """ Updates IP addresses' status

 Args:
  - up (optional).   List of id,notify tuples (x,[0,1]) that changed to up
  - down (optional). List of id,notify tuples that changed to down

 Output:
  - up (number of updated up state)
  - down (number of updated down state)
 """
 ret = {}
 notifications = []
 notifier = aCTX.settings.get('notifier')
 with aCTX.db as db:
  for chg in [('up',1),('down',2)]:
   change = aArgs.get(chg[0])
   if change and len(change) > 0:
    ret[chg[0]] = db.do("UPDATE ipam_addresses SET state = %s WHERE ID IN (%s)"%(chg[1],",".join(str(x[0]) for x in change)))
    begin = 0
    final  = len(change)
    while begin < final:
     end = min(final,begin+16)
     if aCTX.config.get('events'):
      db.do("INSERT INTO ipam_events (ipam_id, state) VALUES %s"%(",".join("(%s,%s)"%(x[0],chg[1]) for x in change[begin:end])))
     else:
      aCTX.log("IPAM Event %s => %s"%(chg[0].ljust(4), ",".join( str(x[0]) for x in change[begin:end])))
     begin = end
    if notifier:
     notify = ",".join([str(x[0]) for x in change if x[1] == chg[1]])
     if len(notify) > 0:
      db.do("SELECT hostname FROM devices WHERE ipam_id IN (%s)"%notify)
      notifications.append((chg[0].upper(),", ".join(dev['hostname'] for dev in db.get_rows()) ))

 if len(notifications) > 0:
  func = aCTX.node_function(notifier.get('proxy','master'),notifier['service'],"notify", aHeader = {'X-Log':'true'})
  for notification in notifications:
   aCTX.workers.add_function(func,aArgs = {'node':notifier['node'],'message':"Device status changed to %s:%s"%notification})
 return ret
