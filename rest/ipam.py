"""IPAM API module. Provides IP network and address management"""
__author__ = "Zacharias El Banna"
__version__ = "1.0GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

from zdcp.core.common import DB

############################################## Networks ##################################################
#
#
def network_list(aDict):
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
 with DB() as db:
  dhcp = db.do("SELECT parameter,value FROM settings WHERE section = 'dhcp'")
  ret['dhcp'] = db.get_dict('parameter') if dhcp > 0 else None
  ret['xist']    = db.do("SELECT id, CONCAT(INET_NTOA(network),'/',mask) AS netasc, INET_NTOA(gateway) AS gateway, description, mask, network FROM ipam_networks ORDER by network")
  ret['networks'] = db.get_rows()
 return ret

#
#
def network_info(aDict):
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
 args = aDict
 id = args.pop('id','new')
 op = args.pop('op',None)
 with DB() as db:
  if op == 'update':
   from struct import unpack
   from socket import inet_aton
   def GL_ip2int(addr):
    return unpack("!I", inet_aton(addr))[0]

   # Check gateway
   low   = GL_ip2int(args['network'])
   high  = low + 2**(32-int(args['mask'])) - 1
   try:    gwint = GL_ip2int(args['gateway'])
   except: gwint = 0
   if not (low < gwint and gwint < high):
    gwint = low + 1
    ret['info'] = "illegal gateway"
   args['gateway'] = str(gwint)
   args['network']  = str(low)
   if id == 'new':
    ret['update'] = db.insert_dict('ipam_networks',args,'ON DUPLICATE KEY UPDATE id = id')
    id = db.get_last_id() if ret['update'] > 0 else 'new'
   else:
    ret['update'] = db.update_dict('ipam_networks',args,'id=%s'%id)

  if not id == 'new':
   ret['xist'] = db.do("SELECT id, mask, description, INET_NTOA(network) AS network, INET_NTOA(gateway) AS gateway, reverse_zone_id FROM ipam_networks WHERE id = %s"%id)
   ret['data'] = db.get_row()
  else:
   ret['data'] = { 'id':'new', 'network':'0.0.0.0', 'mask':'24', 'gateway':'0.0.0.0', 'description':'New','reverse_zone_id':None }
 from zdcp.rest.dns import domain_ptr_list
 ret['domains'] = domain_ptr_list({'prefix':ret['data']['network']})
 ret['domains'].append({'id':'NULL','name':None,'server':None})
 return ret

#
#
def network_inventory(aDict):
 """Allocation of IP addresses within a network.

 Args:
  - id (required)

 Output:
 """
 ret = {}
 with DB() as db:
  db.do("SELECT mask, network, INET_NTOA(network) as netasc, gateway, INET_NTOA(gateway) as gwasc FROM ipam_networks WHERE id = %s"%(aDict['id']))
  network = db.get_row()
  ret['start']  = network['network']
  ret['no']     = 2**(32-network['mask'])
  ret['mask']   = network['mask']
  ret['network'] = network['netasc']
  ret['gateway']= network['gwasc']
  ret['xist_addresses'] = db.do("SELECT ip,id,0 AS gateway FROM ipam_addresses WHERE network_id = %s ORDER BY ip"%(aDict['id']))
  ret['addresses'] = db.get_dict('ip')
  gw = ret['addresses'].get(network['gateway'])
  if gw:
   gw['gateway'] = 1
  else:
   ret['addresses'][network['gateway']] = {'id':None,'ip':network['gateway'],'gateway':1}
 return ret

#
#
def network_delete(aDict):
 """Function docstring for network_delete TBD.

 Args:
  - id (required)

 Output:
 """
 ret = {}
 with DB() as db:
  ret['addresses'] = db.do("DELETE FROM ipam_addresses WHERE network_id = %s"%aDict['id']) 
  ret['deleted'] = db.do("DELETE FROM ipam_networks WHERE id = " + aDict['id'])
 return ret

#
#
def network_discover(aDict):
 """ Function discovers _new_ IP:s that answer to ping within a certain network. A list of such IP:s are returned

 Args:
  - id (required)
  - simultaneous (optional). Simultaneouse threads

 Output:
  - addresses. list of ip:s and ip_int pairs that answer to ping
 """
 from threading import Thread, BoundedSemaphore
 from struct import pack
 from socket import inet_ntoa
 from os import system
 def GL_int2ip(addr):
  return inet_ntoa(pack("!I", addr))

 def __detect_thread(aIPint,aIPs,aSema):
  __ip = GL_int2ip(aIPint)
  if system("ping -c 1 -w 1 %s > /dev/null 2>&1"%(__ip)) == 0:
   aIPs.append({'ip':aIPint,'ipasc':__ip})
  aSema.release()
  return True

 addresses = []
 simultaneous = int(aDict.get('simultaneous',20))
 ret = {'addresses':addresses}

 with DB() as db:
  db.do("SELECT network,mask FROM ipam_networks WHERE id = %s"%aDict['id'])
  net = db.get_row()
  ip_start = net['network'] + 1
  ip_end   = net['network'] + 2**(32 - net['mask']) - 1
  ret.update({'start':{'ip':ip_start,'ipasc':GL_int2ip(ip_start)},'end':{'ip':ip_end,'ipasc':GL_int2ip(ip_end)}})
  db.do("SELECT ip FROM ipam_addresses WHERE network_id = %s"%aDict['id'])
  ip_list = db.get_dict('ip')

 try:
  sema = BoundedSemaphore(simultaneous)
  for ip in range(ip_start,ip_end):
   if not ip_list.get(ip):
    sema.acquire()
    t = Thread(target = __detect_thread, args=[ip, addresses, sema])
    t.name = "Detect %s"%ip
    t.start()
  for i in range(simultaneous):
   sema.acquire()
 except Exception as err:
  ret['error']   = str(err)

 return ret

############################################## Addresses ##################################################
#
#
def ip_find(aDict):
 """Function docstring for ip_find TBD

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
 with DB() as db:
  db.do("SELECT network, INET_NTOA(network) as netasc, mask FROM ipam_networks WHERE id = %s"%(aDict['network_id']))
  net = db.get_row()
  db.do("SELECT ip FROM ipam_addresses WHERE network_id = %s"%(aDict['network_id']))
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
def ip_allocate(aDict):
 """ Function allocate IP relative a specific network.

 Args:
  - ip (required)
  - network_id (required)

 Output:
  - valid (boolean) Indicates valid within network
  - success (boolean)
  - id. Id of address
 """
 ret = {'success':False}
 with DB() as db:
  ret['valid'] = (db.do("SELECT network FROM ipam_networks WHERE id = {0} AND INET_ATON('{1}') > network AND INET_ATON('{1}') < (network + POW(2,(32-mask))-1)".format(aDict['network_id'],aDict['ip'])) == 1)
  if ret['valid']:
   try:
    ret['success'] = (db.do("INSERT INTO ipam_addresses(ip,network_id) VALUES(INET_ATON('%s'),%s)"%(aDict['ip'],aDict['network_id'])) == 1)
    ret['id']= db.get_last_id() if ret['success'] else None
   except: pass
 return ret

#
#
def ip_realloc(aDict):
 """ Function re allocate address ID to a new IP within the same or a new network.

 Args:
  - id (required)
  - ip (required)
  - network_id (optional)

 Output:
  - valid (boolean)
  - available (boolean)
  - success (boolean)
 """
 ret = {'success':False,'valid':False,'available':False}
 with DB() as db:
  id_match = "id = %s"%aDict['network_id'] if aDict.get('network_id') else "id IN (SELECT network_id FROM ipam_addresses WHERE id = %s)"%aDict['id']
  ret['valid'] = (db.do("SELECT network FROM ipam_networks WHERE {0} AND INET_ATON('{1}') > network AND INET_ATON('{1}') < (network + POW(2,(32-mask))-1)".format(id_match,aDict['ip'])) == 1)

  if ret['valid']:
   ret['available'] = (db.do("SELECT id FROM ipam_addresses WHERE ip = INET_ATON('%s') AND network_%s"%(aDict['ip'],id_match)) == 0)
   if ret['available']:
    ret['success'] = (db.do("UPDATE ipam_addresses SET ip = INET_ATON('%s'), network_id = %s WHERE id = %s"%(aDict['ip'],aDict['network_id'],aDict['id'])) == 1)
 return ret


#
#
def ip_delete(aDict):
 """Function deletes an IP id

 Args:
  - id (required)

 Output:
  - result
 """
 ret = {}
 with DB() as db:
  ret['result'] = db.do("DELETE FROM ipam_addresses WHERE id = %s"%aDict['id'])
 return ret

#
#
def ip_from_id(aDict):
 """ Funtion returns mapping between IPAM id and ip,network_id

 Args:
  - id (required)

 Output:
  - ip
  - ipasc
  - network
  - netasc
 """
 with DB() as db:
  db.do("SELECT ip, INET_NTOA(ip) AS ipasc, network_id, INET_NTOA(network) AS netasc, mask FROM ipam_addresses LEFT JOIN ipam_networks ON ipam_networks.id = ipam_addresses.network_id WHERE ipam_addresses.id = %s"%aDict['id'])
  ret = db.get_row()
 return ret
