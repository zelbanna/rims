"""Module docstring.

phpIPAM API module

"""
__author__ = "Zacharias El Banna"                     
__version__ = "17.10.4"
__status__ = "Production"

import sdcp.PackageContainer as PC
import sdcp.core.genlib as GL
from sdcp.core.dbase import DB

#
# Should be subnets(target, arg)
#
def subnets(aDict):
 PC.log_msg("phpipam_subnet({})".format(aDict))
 with DB(PC.ipam['dbname'],'localhost',PC.ipam['username'],PC.ipam['password']) as db:
  db.do("SELECT subnets.id, subnet, mask, subnets.description, name as section_name, sectionId as section_id FROM subnets INNER JOIN sections on subnets.sectionId = sections.id") 
  rows = db.get_rows()
 return rows

#
# lookup(ip,ipam_sub_id)
#
def lookup(aDict):
 PC.log_msg("phpipam_lookup({})".format(aDict))
 ipint   = GL.ip2int(aDict['ip'])
 retvals = { 'ipam_id':'0' }
 with DB(PC.ipam['dbname'],'localhost',PC.ipam['username'],PC.ipam['password']) as db:
  db.do("SELECT id, dns_name, PTR FROM ipaddresses WHERE ip_addr = {0} AND subnetId = {1}".format(ipint,aDict.get('ipam_sub_id')))
  ipam   = db.get_row()
 if ipam:
  retvals['ipam_id'] = ipam.get('id')
  retvals['fqdn']    = ipam.get('dns_name',None)
  retvals['ptr_id']  = ipam.get('PTR',0)
 return retvals

#
# update( ipam_sub_id, ipam_id, ip, fqdn, ptr_id )
#
def update(aDict):
 PC.log_msg("phpipam_update({})".format(aDict))
 ret = {}
 with DB(PC.ipam['dbname'],'localhost',PC.ipam['username'],PC.ipam['password']) as db:
  if aDict.get('ipam_id','0') != '0':
   db.do("UPDATE ipaddresses SET PTR = '{}', dns_name = '{}' WHERE id = '{}'".format(aDict['ptr_id'],aDict['fqdn'],aDict['ipam_id']))
   ret['ipam_op'] = 'update'
   ret['ipam_id'] = aDict['ipam_id']
  else:
   ipint = GL.ip2int(aDict['ip'])
   xist  = db.do("SELECT id FROM ipaddresses WHERE ip_addr = '{0}' AND subnetId = {1}".format(ipint,aDict['ipam_sub_id']))
   if xist > 0:
    entry = db.get_row()
    db.do("UPDATE ipaddresses SET PTR = '{}', dns_name = '{}' WHERE id = '{}'".format(aDict['ptr_id'],aDict['fqdn'],entry['id']))
    ret['ipam_op'] = 'update_existed'
    ret['ipam_id'] = entry['id']
   else:
    db.do("INSERT INTO ipaddresses (subnetId,ip_addr,dns_name,PTR) VALUES('{}','{}','{}','{}')".format(aDict['ipam_sub_id'],ipint,aDict['fqdn'],aDict['ptr_id']))
    ret['ipam_op'] = "insert"
    ret['ipam_id'] = db.get_last_id()
  db.commit()
 return ret

#
# new(ipint, ip, fqdn, ipam_sub_id)
#
def new(aDict):
 PC.log_msg("phpipam_new({})".format(aDict))
 ret = {'res':'NOT_OK'}
 with DB(PC.ipam['dbname'],'localhost',PC.ipam['username'],PC.ipam['password']) as db:
  ret['existed'] = db.do("SELECT id FROM ipaddresses WHERE ip_addr = '{0}' AND subnetId = {1}".format(aDict['ipint'],aDict['ipam_sub_id']))
  if ret['existed'] == 0:
   ret['insert'] = db.do("INSERT INTO ipaddresses (subnetId,ip_addr,dns_name) VALUES('{}','{}','{}')".format(aDict['ipam_sub_id'],aDict['ipint'],aDict['fqdn']))
   ret['id']  = db.get_last_id()
   ret['res'] = 'OK'
   db.commit()
 return ret        

#
# remove(ipam_id)
#
def remove(aDict):
 PC.log_msg("phpipam_remove({})".format(aDict))
 with DB(PC.ipam['dbname'],'localhost',PC.ipam['username'],PC.ipam['password']) as db:
  ires = db.do("DELETE FROM ipaddresses WHERE id = '{}'".format(aDict['ipam_id']))
  db.commit()
 return ires

#
# 
#
def get_addresses(aDict):
 PC.log_msg("phpipam_get_addresses({})".format(aDict))
 with DB(PC.ipam['dbname'],'localhost',PC.ipam['username'],PC.ipam['password']) as db:
  ires  = db.do("SELECT id, ip_addr AS ip, INET_NTOA(ip_addr) as ipasc, subnetId as ipam_sub_id, description, dns_name AS fqdn FROM ipaddresses ORDER BY ip_addr")
  irows = db.get_rows()
 return {'addresses':irows, 'res':'OK', 'info':ires }

#
# find(ipam_sub_id, consecutive)
#
# - Find X consecutive ip from a particular subnet-id
# ipam_sub_id: X
# consecutive: X

def find(aDict):
 PC.log_msg("phpipam_find({})".format(aDict))
 sub_id = aDict.get('ipam_sub_id')
 with DB(PC.ipam['dbname'],'localhost',PC.ipam['username'],PC.ipam['password']) as db:
  db.do("SELECT subnet, INET_NTOA(subnet) as subasc, mask FROM subnets WHERE id = {}".format(sub_id))
  sub = db.get_row()
  db.do("SELECT ip_addr FROM ipaddresses WHERE subnetId = {}".format(sub_id))
  iplist = db.get_rows_dict('ip_addr')
 subnet = int(sub.get('subnet'))
 start  = None
 ret    = { 'subnet':sub['subasc'], 'res':'NOT_OK' }
 for ip in range(subnet + 1, subnet + 2**(32-int(sub.get('mask')))-1):
  if iplist.get(str(ip)):
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
