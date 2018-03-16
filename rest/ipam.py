"""IPAM API module. Provides subnet management for devices"""
__author__ = "Zacharias El Banna"
__version__ = "18.03.16"
__status__ = "Production"
__add_globals__ = lambda x: globals().update(x)

from ..core.common import DB

#
#
def list(aDict):
 """Function docstring for list: lists subnets

 Args:

 Output:
 """
 ret = {}
 with DB() as db:
  ret['xist']    = db.do("SELECT id, CONCAT(INET_NTOA(subnet),'/',mask) AS subasc, INET_NTOA(gateway) AS gateway, description, mask, subnet FROM subnets ORDER by subnet")
  ret['subnets'] = db.get_rows()
 return ret

#
#
def info(aDict):
 """Function docstring for info TBD

 Args:
  - id (required) ('new' / <no>)

 Output:
 """
 ret = {}
 if aDict['id'] == 'new':
  ret['xist'] = 0
  ret['data'] = { 'id':'new', 'subnet':'0.0.0.0', 'mask':'24', 'gateway':'0.0.0.0', 'description':'New' }
 else:
  with DB() as db:
   ret['xist'] = db.do("SELECT id, mask, description, INET_NTOA(subnet) AS subnet, INET_NTOA(gateway) AS gateway FROM subnets WHERE id = '%s'"%aDict['id'])
   ret['data'] = db.get_row()
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
  db.do("SELECT mask, subnet, INET_NTOA(subnet) as subasc, gateway, INET_NTOA(gateway) as gwasc FROM subnets WHERE id = {}".format(aDict['id']))
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
def update(aDict):
 """Function docstring for update TBD

 Args:
  - subnet (required)
  - description (required)
  - mask (required)
  - gateway (required)
  - id (required)

 Output:
 """
 from struct import pack,unpack
 from socket import inet_aton,inet_ntoa

 def GL_ip2int(addr):
  return unpack("!I", inet_aton(addr))[0]
 def GL_int2ip(addr):
  return inet_ntoa(pack("!I", addr))

 ret = {}
 id = aDict.pop('id',None)
 args = aDict

 # Check gateway
 low   = GL_ip2int(args['subnet'])
 high  = low + 2**(32-int(args['mask'])) - 1
 try:    gwint = GL_ip2int(args['gateway'])
 except: gwint = 0
 if (low < gwint and gwint < high):
  ret['gateway'] = args['gateway']
 else:
  gwint = low + 1
  ret['gateway'] = GL_int2ip(gwint)
  ret['info'] = "illegal gateway"
 args['gateway'] = str(gwint)
 args['subnet']  = str(low)
 with DB() as db:
  if id == 'new':
   ret['update'] = db.insert_dict('subnets',args,'ON DUPLICATE KEY UPDATE id = id')
   ret['id'] = db.get_last_id() if ret['update'] > 0 else "new"
  else:
   ret['update'] = db.update_dict('subnets',args,'id=%s'%id)
   ret['id'] = id
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
  db.do("SELECT subnet, INET_NTOA(subnet) as subasc, mask FROM subnets WHERE id = {}".format(aDict['id']))
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
  ret['deleted'] = db.do("DELETE FROM subnets WHERE id = " + aDict['id'])
 return ret
 
