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
  ret['xist']    = db.do("SELECT id, CONCAT(INET_NTOA(subnet),'/',mask) AS subnet, INET_NTOA(gateway) AS gateway from subnets ORDER by subnet")
  ret['subnets'] = db.get_rows()
 return ret

#
#
def subnet(aDict):
 ret = {'res':'OK'}
 if aDict['id'] == 'new':
   ret['data'] = { 'id':'new', 'subnet':'0.0.0.0', 'mask':'24', 'gateway':'0.0.0.0', 'subnet_description':'New' }
   ret['xist'] = 0
 else:
  with DB() as db:
   ret['xist'] = db.do("SELECT id, mask, subnet_description, INET_NTOA(subnet) AS subnet, INET_NTOA(gateway) AS gateway FROM subnets WHERE id = " + aDict['id'])
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
 except: gwint = 0
 if (low < gwint and gwint < high):
  ret['gateway'] = aDict['gateway']
 else:
  ret['gateway'] = GL.int2ip(low + 1)
  gwint = low + 1
  ret['info'] = "defaulted illegal gateway"
 with DB() as db:
  if aDict['id'] == 'new':
   ret['xist'] = db.do("INSERT INTO subnets(subnet,mask,gateway,subnet_description) VALUES (INET_ATON('{}'),{},{},'{}') ON DUPLICATE KEY UPDATE id = id".format(aDict['subnet'],aDict['mask'],gwint,aDict['subnet_description']))
   ret['id']   = db.get_last_id() if ret['xist'] > 0 else "new"
  else:
   ret['xist'] = db.do("UPDATE subnets SET subnet = INET_ATON('{}'), mask = {}, gateway = {}, subnet_description = '{}' WHERE id = {}".format(aDict['subnet'],aDict['mask'],gwint,aDict['subnet_description'],aDict['id']))
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
 
