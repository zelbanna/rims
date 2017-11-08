"""Module docstring.

sdcpIPAM API module

"""
__author__ = "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"

from sdcp import PackageContainer as PC
from sdcp.core.dbase import DB

#
#
def list(aDict):
 ret = {'res':'OK'}
 with DB() as db:
  ret['xist']    = db.do("SELECT id, CONCAT(INET_NTOA(subnet),'/',mask) AS subnet, INET_NTOA(gateway) AS gateway, description from subnets ORDER by subnet")
  ret['subnets'] = db.get_rows()
 return ret

#
#
def subnet(aDict):
 ret = {'res':'OK'}
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
def update(aDict):
 ret = {'res':'OK'}
 from sdcp.core import genlib as GL

 # Check gateway
 low   = GL.ip2int(aDict['subnet'])
 high  = low + 2**(32-int(aDict['mask'])) - 1
 try:    gwint = GL.ip2int(aDict['gateway'])
 except: gwint = low + 1
 if (low < gwint and gwint < high):
  ret['gateway'] = aDict['gateway']
 else:
  ret['gateway'] = GL.int2ip(low + 1)
  gwint = low + 1
  ret['info'] = "defaulted illegal gateway"
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
 ret = {'res':'OK'}
 with DB() as db:
  ret['devices'] = db.do("DELETE FROM devices WHERE ipam_sub_id = " + aDict['id'])
  ret['xist']    = db.do("DELETE FROM subnets WHERE id = " + aDict['id'])
 return ret
 
#
# find(subnet_id, consecutive)
def find(aDict):   
 from sdcp.core import genlib as GL
 with DB() as db:
  db.do("SELECT subnet, INET_NTOA(subnet) as subasc, mask FROM subnets WHERE id = {}".format(aDict['id']))
  sub = db.get_row()
  db.do("SELECT ip FROM devices WHERE ipam_sub_id = {}".format(aDict['id']))
  iplist = db.get_dict('ip')
 subnet = int(sub.get('subnet'))
 start  = None           
 ret    = { 'subnet':sub['subasc'], 'res':'NOT_OK' }
 for ip in range(subnet + 1, subnet + 2**(32-int(sub.get('mask')))-1):
  if iplist.get(ip):       
   start = None
  elif not start:
   count = int(aDict.get('consecutive',1))
   if count > 1:
    start = ip
   else:
    ret['ip'] = GL.int2ip(ip)
    ret['res'] = 'OK'
    break
  else:
   if count == 2:
    ret['start'] = GL.int2ip(start)
    ret['end'] = GL.int2ip(start+int(aDict.get('consecutive'))-1)
    ret['res'] = 'OK'
    break
   else:
    count = count - 1
 return ret
