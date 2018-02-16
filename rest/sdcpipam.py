"""Module docstring.

sdcpIPAM API module

"""
__author__ = "Zacharias El Banna"
__version__ = "18.02.09GA"
__status__ = "Production"

from ..core.dbase import DB

#
#
def list(aDict):
 """Function description for list: lists subnets

 Args:

 Extra:
 """
 ret = {}
 with DB() as db:
  ret['xist']    = db.do("SELECT id, CONCAT(INET_NTOA(subnet),'/',mask) AS subasc, INET_NTOA(gateway) AS gateway, description, mask, subnet FROM subnets ORDER by subnet")
  ret['subnets'] = db.get_rows()
 return ret

#
#
def info(aDict):
 """Function description for info TBD

 Args:
  - id (required) ('new' / <no>)

 Extra:
 """
 ret = {}
 if aDict['id'] == 'new':
   ret['data'] = { 'id':'new', 'subnet':'0.0.0.0', 'mask':'24', 'gateway':'0.0.0.0', 'description':'New' }
   ret['xist'] = 0
 else:
  with DB() as db:
   ret['xist'] = db.do("SELECT id, mask, description, INET_NTOA(subnet) AS subnet, INET_NTOA(gateway) AS gateway FROM subnets WHERE id = " + aDict['id'])
   ret['data'] = db.get_row()
 return ret

#
#
def allocation(aDict):
 """Function description for allocation: Allocation of IP addresses within a subnet

 Args:
  - id (required)

 Extra:
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
 """Function description for update TBD

 Args:
  - subnet (required)
  - description (required)
  - mask (required)
  - gateway (required)
  - id (required)

 Extra:
 """
 from ..core import genlib as GL
 ret = {}
 # Check gateway
 low   = GL.ip2int(aDict['subnet'])
 high  = low + 2**(32-int(aDict['mask'])) - 1
 try:    gwint = GL.ip2int(aDict['gateway'])
 except: gwint = 0
 if (low < gwint and gwint < high):
  ret['gateway'] = aDict['gateway']
 else:
  gwint = low + 1
  ret['gateway'] = GL.int2ip(gwint)
  ret['info'] = "illegal gateway"
 with DB() as db:
  if aDict['id'] == 'new':
   ret['xist'] = db.do("INSERT INTO subnets(subnet,mask,gateway,description) VALUES (INET_ATON('{}'),{},{},'{}') ON DUPLICATE KEY UPDATE id = id".format(aDict['subnet'],aDict['mask'],gwint,aDict['description']))
   ret['id']   = db.get_last_id() if ret['xist'] > 0 else "new"
  else:
   ret['xist'] = db.do("UPDATE subnets SET subnet = INET_ATON('{}'), mask = {}, gateway = {}, description = '{}' WHERE id = {}".format(aDict['subnet'],aDict['mask'],gwint,aDict['description'],aDict['id']))
   ret['id']   = aDict['id']
 return ret

#
#
def remove(aDict):
 """Function description for remove TBD

 Args:
  - id (required)

 Extra:
 """
 ret = {}
 with DB() as db:
  ret['devices'] = db.do("DELETE FROM devices WHERE subnet_id = " + aDict['id'])
  ret['xist']    = db.do("DELETE FROM subnets WHERE id = " + aDict['id'])
 return ret
 
#
#
def find(aDict):
 """Function description for find TBD

 Args:
  - id (required)
  - consecutive (optional)

 Extra:
 """
 from ..core import genlib as GL
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
    ret['ip'] = GL.int2ip(ip)
    break
  else:
   if count == 2:
    ret['start'] = GL.int2ip(start)
    ret['end'] = GL.int2ip(start+int(aDict.get('consecutive'))-1)
    break
   else:
    count = count - 1
 return ret
