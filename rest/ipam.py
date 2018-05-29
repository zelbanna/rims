"""IPAM API module. Provides subnet management for devices"""
__author__ = "Zacharias El Banna"
__version__ = "18.04.07GA"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

from sdcp.core.common import DB

#
#
def list(aDict):
 """Function docstring for list: lists subnets

 Args:

 Output:
 """
 ret = {}
 with DB() as db:
  dhcp = db.do("SELECT parameter,value FROM settings WHERE section = 'dhcp'")
  ret['dhcp'] = db.get_dict('parameter') if dhcp > 0 else None
  ret['xist']    = db.do("SELECT id, CONCAT(INET_NTOA(subnet),'/',mask) AS subasc, INET_NTOA(gateway) AS gateway, description, mask, subnet FROM ipam_networks ORDER by subnet")
  ret['subnets'] = db.get_rows()
 return ret

#
#
def info(aDict):
 """Function docstring for info TBD

 Args:
  - id (required)
  - subnet (optional)
  - description (optional)
  - mask (optional)
  - gateway (optional)

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

   # Check gateway
   low   = GL_ip2int(args['subnet'])
   high  = low + 2**(32-int(args['mask'])) - 1
   try:    gwint = GL_ip2int(args['gateway'])
   except: gwint = 0
   if not (low < gwint and gwint < high):
    gwint = low + 1
    ret['info'] = "illegal gateway"
   args['gateway'] = str(gwint)
   args['subnet']  = str(low)
   if id == 'new':
    ret['update'] = db.insert_dict('ipam_networks',args,'ON DUPLICATE KEY UPDATE id = id')
    id = db.get_last_id() if ret['update'] > 0 else 'new'
   else:
    ret['update'] = db.update_dict('ipam_networks',args,'id=%s'%id)

  if not id == 'new':
   ret['xist'] = db.do("SELECT id, mask, description, INET_NTOA(subnet) AS subnet, INET_NTOA(gateway) AS gateway FROM ipam_networks WHERE id = %s"%id)
   ret['data'] = db.get_row()
  else:
   ret['data'] = { 'id':'new', 'subnet':'0.0.0.0', 'mask':'24', 'gateway':'0.0.0.0', 'description':'New' }
 return ret

#
#
def inventory(aDict):
 """Function docstring for inventory: Allocation of IP addresses within a subnet.

 Args:
  - id (required)

 Output:
 """
 ret = {}
 with DB() as db:
  db.do("SELECT mask, subnet, INET_NTOA(subnet) as subasc, gateway, INET_NTOA(gateway) as gwasc FROM ipam_networks WHERE id = {}".format(aDict['id']))
  subnet = db.get_row()
  ret['start']  = subnet['subnet']
  ret['no']     = 2**(32-subnet['mask'])
  ret['mask']   = subnet['mask']
  ret['subnet'] = subnet['subasc']
  ret['gateway']= subnet['gwasc']
  ret['xist_devices'] = db.do("SELECT ip,id,hostname,0 AS gateway FROM devices WHERE subnet_id = {} ORDER BY ip".format(aDict['id']))
  ret['devices'] = db.get_dict('ip')
  gw = ret['devices'].get(subnet['gateway'])
  if gw:
   gw['gateway'] = 1
  else:
   ret['devices'][subnet['gateway']] = {'id':None,'ip':subnet['gateway'],'hostname':'gateway','gateway':1}
 return ret

#
#
def find(aDict):
 """Function docstring for find TBD

 Args:
  - id (required)
  - consecutive (optional)

 Output:
 """
 from struct import pack
 from socket import inet_ntoa
 def GL_int2ip(addr):
  return inet_ntoa(pack("!I", addr))

 with DB() as db:
  db.do("SELECT subnet, INET_NTOA(subnet) as subasc, mask FROM ipam_networks WHERE id = {}".format(aDict['id']))
  sub = db.get_row()
  db.do("SELECT ip FROM devices WHERE subnet_id = {}".format(aDict['id']))
  iplist = db.get_dict('ip')
 subnet = int(sub.get('subnet'))
 start  = None
 ret    = { 'subnet':sub['subasc'] }
 for ip in range(subnet + 1, subnet + 2**(32-int(sub.get('mask')))-1):
  if iplist.get(ip):
   start = None
  elif not start:
   count = int(aDict.get('consecutive',1))
   if count > 1:
    start = ip
   else:
    ret['ip'] = GL_int2ip(ip)
    break
  else:
   if count == 2:
    ret['start'] = GL_int2ip(start)
    ret['end'] = GL_int2ip(start+int(aDict.get('consecutive'))-1)
    break
   else:
    count = count - 1
 return ret

#
#
def delete(aDict):
 """Function docstring for delete TBD

 Args:
  - id (required)

 Output:
 """
 ret = {}
 with DB() as db:
  ret['devices'] = db.do("DELETE FROM devices WHERE subnet_id = " + aDict['id'])
  ret['deleted'] = db.do("DELETE FROM ipam_networks WHERE id = " + aDict['id'])
 return ret
 
