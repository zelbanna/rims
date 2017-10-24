"""Module docstring.

phpIPAM API module

"""
__author__ = "Zacharias El Banna"                     
__version__ = "17.10.4"
__status__ = "Production"

import sdcp.PackageContainer as PC

#
# Should be subnets(target, arg)
#
def subnets(aDict):
 from sdcp.core.dbase import DB
 with DB(PC.ipam['dbname'],'localhost',PC.ipam['username'],PC.ipam['password']) as db:
  db.do("SELECT subnets.id, subnet, mask, subnets.description, name as section_name, sectionId as section_id FROM subnets INNER JOIN sections on subnets.sectionId = sections.id") 
  rows = db.get_rows()
 return rows

#
# lookup(ip,ipam_sub_id)
#
def lookup(aDict):
 PC.log_msg("IPAM lookup - input {}".format(aDict.values()))
 import sdcp.core.genlib as GL
 ipint   = GL.ip2int(aDict['ip'])
 retvals = { 'ipam_id':'0' }
 from sdcp.core.dbase import DB
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
 PC.log_msg("IPAM update - input:{}".format(aDict.values()))
 import sdcp.core.genlib as GL
 from sdcp.core.dbase import DB
 res = {}
 with DB(PC.ipam['dbname'],'localhost',PC.ipam['username'],PC.ipam['password']) as db:
  if aDict.get('ipam_id','0') != '0':
   db.do("UPDATE ipaddresses SET PTR = '{}', dns_name = '{}' WHERE id = '{}'".format(aDict['ptr_id'],aDict['fqdn'],aDict['ipam_id']))
   res['ipam_op'] = 'update'
   res['ipam_id'] = aDict['ipam_id']
  else:
   ipint = GL.ip2int(aDict['ip'])
   db.do("SELECT id FROM ipaddresses WHERE ip_addr = '{0}' AND subnetId = {1}".format(ipint,aDict['ipam_sub_id']))
   entry = db.get_row()
   if entry:
    db.do("UPDATE ipaddresses SET PTR = '{}', dns_name = '{}' WHERE id = '{}'".format(aDict['ptr_id'],aDict['fqdn'],entry['id']))
    res['ipam_op'] = 'update_existed'
    res['ipam_id'] = entry['id']
   else:
    db.do("INSERT INTO ipaddresses (subnetId,ip_addr,dns_name,PTR) VALUES('{}','{}','{}','{}')".format(aDict['ipam_sub_id'],ipint,aDict['fqdn'],aDict['ptr_id']))
    res['ipam_op'] = "insert"
    res['ipam_id'] = db.get_last_id()
  db.commit()
 return res

#
# remove(ipam_id)
#
def remove(aDict):
 from sdcp.core.dbase import DB
 with DB(PC.ipam['dbname'],'localhost',PC.ipam['username'],PC.ipam['password']) as db:
  ires = db.do("DELETE FROM ipaddresses WHERE id = '{}'".format(aDict['ipam_id']))
  db.commit()
 PC.log_msg("IPAM remove - {} -> {}".format(aDict,ires))
 return ires

#
# 
#
def get_addresses(aDict):
 from sdcp.core.dbase import DB
 with DB(PC.ipam['dbname'],'localhost',PC.ipam['username'],PC.ipam['password']) as db:
  ires  = db.do("SELECT id, ip_addr, INET_NTOA(ip_addr) as ipasc, description, dns_name FROM ipaddresses")
  irows = db.get_rows()
 return {'addresses':irows, 'res':'OK', 'info':ires }

#
# find(ipam_sub_id, consecutive)
#
# - Find X consecutive ip from a particular subnet-id
#
def find(aDict):
 import sdcp.core.genlib as GL
 from sdcp.core.dbase import DB
 with DB(PC.ipam['dbname'],'localhost',PC.ipam['username'],PC.ipam['password']) as db:
  db.do("SELECT subnet, mask FROM subnets WHERE id = {}".format(aDict.get('ipam_sub_id'))) 
  sub = db.get_row()
  db.do("SELECT ip_addr FROM ipaddresses WHERE subnetId = {}".format(aDict.get('ipam_sub_id')))
  iplist = db.get_rows_dict('ip_addr')
 subnet = int(sub.get('subnet'))
 start  = None
 ret    = { 'subnet':GL.int2ip(subnet) }
 for ip in range(subnet + 1, subnet + 2**(32-int(sub.get('mask')))-1):
  if not iplist.get(str(ip),False):
   if start:
    count = count - 1
    if count == 1:
     ret['start'] = GL.int2ip(start)
     ret['end'] = GL.int2ip(start+int(aDict.get('consecutive'))-1)
     break
   else:
    count = int(aDict.get('consecutive'))          
    start = ip       
  else:     
   start = None           
 return ret                            
