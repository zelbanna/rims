"""Module docstring.

 DDI API module

"""
__author__ = "Zacharias El Banna"                     
__version__ = "10.5GA"
__status__ = "Production"

import sdcp.SettingsContainer as SC
import sdcp.core.GenLib as GL

################################################ DDI - Common ################################################
#
#
#
def load_infra(aDict):
 #
 # Get domains from dns and subnets from ipam
 #
 domains = dns_domains(None) 
 subnets = ipam_subnets(None)
 db = GL.DB()
 db.connect()
 for dom in domains:
  db.do("INSERT INTO domains(id,name) VALUES ({0},'{1}') ON DUPLICATE KEY UPDATE name='{1}'".format(dom['id'],dom['name']))
 db.commit()
 for sub in subnets:
  db.do("INSERT INTO subnets(id,subnet,mask,subnet_description,section_id,section_name) VALUES ({0},{1},{2},'{3}',{4},'{5}') ON DUPLICATE KEY UPDATE subnet={1},mask={2}".format(sub['id'],sub['subnet'],sub['mask'],sub['description'],sub['section_id'],sub['section_name']))
 db.commit()
 db.close()
 return { 'domains':len(domains), 'subnets':len(subnets) }

################################################# DDI - DNS ##################################################
#
# Should be domains(target, arg) to simpler select domain 
#
def dns_domains(aDict):
 if SC.dnsdb_proxy == 'True':
  return GL.rpc_call(SC.dnsdb_url, "ddi_dns_domains", aDict)
 db = GL.DB()
 db.connect_details('localhost',SC.dnsdb_username, SC.dnsdb_password, SC.dnsdb_dbname)
 res = db.do("SELECT id, name FROM domains")
 db.close()
 return db.get_all_rows()

#
# Lookup a and ptr id for a given ip,hostname and domain, return as dict
# lookup ( name, a_dom_id, ip)
#
def dns_lookup(aDict):
 if SC.dnsdb_proxy == 'True':
  return GL.rpc_call(SC.dnsdb_url, "ddi_dns_lookup", aDict)
 ptr  = GL.sys_ip2arpa(aDict['ip'])
 GL.sys_log_msg("DNS  lookup - input:{}".format(aDict.values()))  
 db = GL.DB()
 db.connect_details('localhost',SC.dnsdb_username, SC.dnsdb_password, SC.dnsdb_dbname)
 res = db.do("SELECT id,name FROM domains WHERE id = {} OR name = {}".format(aDict('a_dom_id'),ptr))
 domains = db.get_all_rows()
 domain  = domains[0]['name'] if domains[1]['name'] == ptr else domains[1]['name']
 fqdn    = aDict['name'] + "." + domain
 ptr_id  = domains[1]['id'] if domains[1]['name'] == ptr else domains[0]['id]
 db.do("SELECT id,content FROM records WHERE type = 'A' and domain_id = {} and name = '{}'".format(aDict('a_dom_id'),fqdn))
 a_record = db.get_row()
 db.do("SELECT id,content FROM records WHERE type = 'PTR' and domain_id = {} and name = '{}'".format(ptr_id,ptr)) 
 p_record = db.get_row()
 db.close()
 retvals = {}
 if a_record and (a_record.get('content',None) == aDict['ip']):
  retvals['a_id'] = a_record.get('id') 
 if p_record and p_record.get('content',None):
  retvals['ptr_id'] = p_record.get('id')
 return retvals

def dns_update(aDict):
 if SC.dnsdb_proxy == 'True':
  return GL.rpc_call(SC.dnsdb_url, "ddi_dns_update", aDict)
 from time import strftime
 serial  = strftime("%Y%m%d01")
 ptr     = GL.sys_ip2ptr(aDict['ip'])
 fqdn    = aDict['name'] + "." + aDict['domain']
 retvals = {}
 GL.sys_log_msg("DNS  update - input:{}".format(", ".join(aDict.values)))
 db = GL.DB()
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
 GL.sys_log_msg("DNS  update - results: " + str(retvals))
 return retvals

def dns_remove(aDict):
 if SC.dnsdb_proxy == 'True':
  return GL.rpc_call(SC.dnsdb_url, "ddi_dns_remove", aDict)
 db = GL.DB()
 db.connect_details('localhost',SC.dnsdb_username, SC.dnsdb_password, SC.dnsdb_dbname)
 ares = 0
 pres = 0
 if aDict['a_id'] != '0':
  ares = db.do("DELETE FROM records WHERE id = '{}' and type = 'A'".format(aDict['a_id']))
 if aDict['ptr_id'] != '0':
  pres = db.do("DELETE FROM records WHERE id = '{}' and type = 'PTR'".format(aDict['ptr_id']))
 db.commit()
 db.close()
 GL.sys_log_msg("DNS  remove - A:{} PTR:{}".format(str(ares),str(pres)))
 return { 'a':ares, 'ptr':pres }

################################################# DDI - IPAM ##################################################
#
# Should be subnets(target, arg)
#
def ipam_subnets(aDict):
 if SC.ipamdb_proxy == 'True':
  return GL.rpc_call(SC.ipamdb_url, "ddi_ipam_subnets", aDict)
 db = GL.DB()
 db.connect_details('localhost',SC.ipamdb_username, SC.ipamdb_password, SC.ipamdb_dbname)
 res = db.do("SELECT subnets.id, subnet, mask, subnets.description, name as section_name, sectionId as section_id FROM subnets INNER JOIN sections on subnets.sectionId = sections.id") 
 db.close()
 return db.get_all_rows()

#
# lookup(ip,ipam_sub_id)
#
def ipam_lookup(aDict):
 if SC.ipamdb_proxy == 'True':
  return GL.rpc_call(SC.ipamdb_url, "ddi_ipam_lookup", aDict)
 GL.sys_log_msg("IPAM lookup - input {}".format(aDict.values()))
 ipint   = GL.sys_ip2int(aDict['ip'])
 retvals = { 'ipam_id':'0' }
 db = GL.DB()
 db.connect_details('localhost',SC.ipamdb_username, SC.ipamdb_password, SC.ipamdb_dbname)
 db.do("SELECT id, dns_name, PTR FROM ipaddresses WHERE ip_addr = {0} AND subnetId = {1}".format(ipint,aDict.get('ipam_sub_id')))
 db.close()
 ipam   = db.get_row()
 if ipam:
  retvals['ipam_id'] = ipam.get('id')
  retvals['a_name']  = ipam.get('dns_name',None)
  retvals['ptr_id']  = ipam.get('PTR',0)
 return retvals

#
# update( ipam_sub_id, ipam_id, ip, fqdn, ptr_id )
#
def ipam_update(aDict):
 if SC.ipamdb_proxy == 'True':
  return GL.rpc_call(SC.ipamdb_url, "ddi_ipam_update", aDict)
 GL.sys_log_msg("IPAM update - input:{}".format(", ".join(aDict.values())))
 db = GL.DB()
 db.connect_details('localhost',SC.ipamdb_username, SC.ipamdb_password, SC.ipamdb_dbname)
 if aDict.get('ipam_id','0') != '0':
  db.do("UPDATE ipaddresses SET PTR = '{}', dns_name = '{}' WHERE id = '{}'".format(aDict['ptr_id'],aDict['fqdn'],aDict['ipam_id']))
 else:
  ipint = GL.sys_ip2int(aDict['ip'])
  db.do("SELECT id FROM ipaddresses WHERE ip_addr = '{0}' AND subnetId = {1}".format(ipint,aDict['ipam_sub_id']))
  entry = db.get_row()
  if entry:
   GL.sys_log_msg("IPAM update - ipam_id 0 -> {}".format(entry.get('id')))
   db.do("UPDATE ipaddresses SET PTR = '{}', dns_name = '{}' WHERE id = '{}'".format(aDict['ptr_id'],aDict['fqdn'],entry.get('id')))
  else:
   db.do("INSERT INTO ipaddresses (subnetId,ip_addr,dns_name,PTR) VALUES('{}','{}','{}','{}')".format(aDict['ipam_sub_id'],ipint,aDict['fqdn'],aDict['ptr_id']))
 db.commit()
 db.close()
 return "done"

#
#
#
def ipam_remove(aDict):
 if SC.ipamdb_proxy == 'True':
  return GL.rpc_call(SC.ipamdb_url, "ddi_ipam_remove", aDict)
 db = GL.DB()
 db.connect_details('localhost',SC.ipamdb_username, SC.ipamdb_password, SC.ipamdb_dbname)
 ires = db.do("DELETE FROM ipaddresses WHERE id = '{}'".format(aDict['ipam_id']))
 db.commit()
 db.close()
 GL.sys_log_msg("IPAM remove - I:{}".format(str(ires)))
 return ires
