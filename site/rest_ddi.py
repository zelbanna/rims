"""Module docstring.

 DDI API module

"""
__author__ = "Zacharias El Banna"                     
__version__ = "10.0GA"
__status__ = "Production"

import sdcp.SettingsContainer as SC
from GenLib import sys_log_msg, sys_ip2ptr, sys_ip2int, DB, rpc_call

################################################# DDI - DNS ##################################################
#
# Lookup a and ptr id for a given ip,hostname and domain, return as dict
#

def ddi_dns_domains(aDict):
 if SC.dnsdb_proxy == 'True':
  return rpc_call(SC.dnsdb_url, "ddi_dns_domains", aDict)
 db = DB()
 db.connect_details('localhost',SC.dnsdb_username, SC.dnsdb_password, SC.dnsdb_dbname)
 res = db.do("SELECT id,name from domains")
 retvals = db.get_all_rows()
 return retvals

def ddi_dns_lookup(aDict):
 if SC.dnsdb_proxy == 'True':
  return rpc_call(SC.dnsdb_url, "ddi_dns_lookup", aDict)
 ptr     = sys_ip2ptr(aDict['ip'])
 fqdn    = aDict['name'] + "." + aDict['domain']
 retvals = {}
 sys_log_msg("DNS  lookup - input:{}, {}, {}".format(aDict['ip'],aDict['name'],aDict['domain']))  
 db = DB()
 db.connect_details('localhost',SC.dnsdb_username, SC.dnsdb_password, SC.dnsdb_dbname)
 res = db.do("SELECT id,name from domains")
 domain_db = db.get_all_dict("name")
 domain_id = [ domain_db.get(aDict['domain'],{ 'id':'0' }), domain_db.get(ptr.partition('.')[2],{ 'id':'0' }) ]
 db.do("SELECT id,content FROM records WHERE type = 'A' and domain_id = '{}' and name = '{}'".format(domain_id[0]['id'],fqdn)) 
 a_record = db.get_row()                       
 db.do("SELECT id,content FROM records WHERE type = 'PTR' and domain_id = '{}' and name = '{}'".format(domain_id[1]['id'],ptr)) 
 p_record = db.get_row()
 if a_record and (a_record.get('content',None) == aDict['ip']):
  retvals['dns_a_id'] = a_record.get('id') 
 if p_record and p_record.get('content',None):
  retvals['dns_ptr_id'] = p_record.get('id')
 db.close() 
 return retvals

def ddi_dns_update(aDict):
 if SC.dnsdb_proxy == 'True':
  return rpc_call(SC.dnsdb_url, "ddi_dns_update", aDict)
 from time import strftime
 serial  = strftime("%Y%m%d01")
 ptr     = sys_ip2ptr(aDict['ip'])
 fqdn    = aDict['name'] + "." + aDict['domain']
 retvals = {}
 sys_log_msg("DNS  update - input:{}".format(", ".join(aDict.values)))
 db = DB()
 db.connect_details('localhost',SC.dnsdb_username, SC.dnsdb_password, SC.dnsdb_dbname)
 db.do("SELECT id,name from domains")
 domain_db = db.get_all_dict("name")
 domain_id = [ domain_db.get(aDict['domain'],{ 'id':'0' }), domain_db.get(ptr.partition('.')[2],{ 'id':'0' }) ]
 # A domain dict, PTR domain dict
 if aDict['a_id'] != '0':
  retvals['a'] = "update"
  db.do("UPDATE records SET name = '{}', content = '{}', change_date='{}' WHERE id ='{}'".format(fqdn,aDict['ip'],serial,aDict['a_id']))
 else:
  retvals['a'] = "insert"
  db.do("INSERT INTO records (domain_id,name,type,content,ttl,change_date) VALUES('{}','{}','A','{}',3600,'{}')".format(str(domain_id[0].get('id')),fqdn,aDict['ip'],serial))
 if aDict['ptr_id'] != '0':
  retvals['ptr'] = "update"
  db.do("UPDATE records SET name = '{}', content = '{}', change_date='{}' WHERE id ='{}'".format(ptr,fqdn,serial,aDict['ptr_id']))
 else:
  retvals['ptr'] = "insert"
  db.do("INSERT INTO records (domain_id,name,type,content,ttl,change_date) VALUES('{}','{}','PTR','{}',3600,'{}')".format(str(domain_id[1].get('id')),ptr,fqdn,serial))
 db.commit()
 db.close()
 sys_log_msg("DNS  update - results: " + str(retvals))
 return retvals

def ddi_dns_remove(aDict):
 if SC.dnsdb_proxy == 'True':
  return rpc_call(SC.dnsdb_url, "ddi_dns_remove", aDict)
 db = DB()
 db.connect_details('localhost',SC.dnsdb_username, SC.dnsdb_password, SC.dnsdb_dbname)
 ares = 0
 pres = 0
 if aDict['a_id'] != '0':
  ares = db.do("DELETE FROM records WHERE id = '{}' and type = 'A'".format(aDict['a_id']))
 if aDict['ptr_id'] != '0':
  pres = db.do("DELETE FROM records WHERE id = '{}' and type = 'PTR'".format(aDict['ptr_id']))
 db.commit()
 sys_log_msg("DNS  remove - A:{} PTR:{}".format(str(ares),str(pres)))
 return { 'a':ares, 'ptr':pres }
 db.close()

################################################# DDI - IPAM ##################################################
#
#
def ddi_ipam_subnets(aDict):
 if SC.ipamdb_proxy == 'True':
  return rpc_call(SC.ipamdb_url, "ddi_ipam_subnets", aDict)
 db = DB()
 db.connect_details('localhost',SC.ipamdb_username, SC.ipamdb_password, SC.ipamdb_dbname)
 db.do("SELECT subnets.id, subnet, mask, subnets.description, name, sectionId FROM subnets INNER JOIN sections on subnets.sectionId = sections.id") 
 res = db.get_all_dict('id')
 db.close()
 return res

def ddi_ipam_lookup(aDict):
 if SC.ipamdb_proxy == 'True':
  return rpc_call(SC.ipamdb_url, "ddi_ipam_lookup", aDict)
 sys_log_msg("IPAM lookup - input {}".format(aDict['ip']))
 ipint   = sys_ip2int(aDict['ip'])
 retvals = { 'ipam_id':'0' }
 db = DB()
 db.connect_details('localhost',SC.ipamdb_username, SC.ipamdb_password, SC.ipamdb_dbname)
 db.do("SELECT id, subnet, INET_NTOA(subnet) as subnetasc, mask FROM subnets WHERE vrfId = 0 AND {0} > subnet AND {0} < (subnet + POW(2,(32-mask))-1)".format(ipint))
 subnet = db.get_row()
 retvals['subnet_id']   = subnet.get('id')
 retvals['subnet_asc']  = subnet.get('subnetasc')
 retvals['subnet_mask'] = subnet.get('mask')
 db.do("SELECT id, dns_name, PTR FROM ipaddresses WHERE ip_addr = {0} AND subnetId = {1}".format(ipint,subnet['id']))
 ipam   = db.get_row()
 if ipam:
  retvals['ipam_id']    = ipam.get('id')
  retvals['dns_a_name'] = ipam.get('dns_name',None)
  retvals['dns_ptr_id'] = ipam.get('PTR',0)
 return retvals

#
#
#
def ddi_ipam_update(aDict):
 if SC.ipamdb_proxy == 'True':
  return rpc_call(SC.ipamdb_url, "ddi_ipam_update", aDict)
 ipint = sys_ip2int(aDict['ip'])
 fqdn  = aDict['name'] + "." + aDict['domain']
 sys_log_msg("IPAM update - input:{}".format(", ".join(aDict.values())))
 db = DB()
 db.connect_details('localhost',SC.ipamdb_username, SC.ipamdb_password, SC.ipamdb_dbname)
 if aDict['ipam_id'] != '0':
  db.do("UPDATE ipaddresses SET PTR = '{}', dns_name = '{}' WHERE id = '{}'".format(aDict['ptr_id'],fqdn,aDict['ipam_id']))
 else:
  db.do("SELECT id, subnet, INET_NTOA(subnet) as subnetasc, mask FROM subnets WHERE vrfId = 0 AND {0} > subnet AND {0} < (subnet + POW(2,(32-mask))-1)".format(ipint))
  subnet = db.get_row()
  subnet_id = subnet.get('id')
  db.do("SELECT id FROM ipaddresses WHERE ip_addr = '{0}' AND subnetId = {1}".format(ipint,subnet_id))
  entry = db.get_row()
  if entry:
   sys_log_msg("IPAM update - ipam_id 0 -> {}".format(entry.get('id')))
   db.do("UPDATE ipaddresses SET PTR = '{}', dns_name = '{}' WHERE id = '{}'".format(aDict['ptr_id'],fqdn,entry.get('id')))
  else:
   db.do("INSERT INTO ipaddresses (subnetId,ip_addr,dns_name,PTR) VALUES('{}','{}','{}','{}')".format(subnet_id,ipint,fqdn,aDict['ptr_id']))
 db.commit()
 db.close()
 return { 'op_result':'done' }

#
#
#
def ddi_ipam_remove(aDict):
 if SC.ipamdb_proxy == 'True':
  return rpc_call(SC.ipamdb_url, "ddi_ipam_remove", aDict)
 db = DB()
 db.connect_details('localhost',SC.ipamdb_username, SC.ipamdb_password, SC.ipamdb_dbname)
 ires = db.do("DELETE FROM ipaddresses WHERE id = '{}'".format(aDict['ipam_id']))
 db.commit()
 sys_log_msg("IPAM remove - I:{}".format(str(ires)))
 return { 'ipam':ires }
 db.close()
