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
# lookup ( name, a_dom_id, ip)
#
def dns_lookup(aDict):
 if SC.dnsdb_proxy == 'True':
  return GL.rpc_call(SC.dnsdb_url, "ddi_dns_lookup", aDict)
 ptr  = GL.sys_ip2arpa(aDict['ip'])
 GL.sys_log_msg("DNS  lookup - input:{}".format(aDict.values()))  
 db = GL.DB()
 db.connect_details('localhost',SC.dnsdb_username, SC.dnsdb_password, SC.dnsdb_dbname)
 res = db.do("SELECT id,name FROM domains WHERE id = {} OR name = '{}'".format(aDict['a_dom_id'],ptr))
 domains = db.get_all_rows()
 if res == 2:
  domain     = domains[0]['name'] if domains[1]['name'] == ptr else domains[1]['name']
  ptr_dom_id = domains[1]['id']   if domains[1]['name'] == ptr else domains[0]['id']
 else:
  domain     = domains[0]['name']
  ptr_dom_id = '0'
 fqdn    = aDict['name'] + "." + domain
 db.do("SELECT id,content FROM records WHERE type = 'A' and domain_id = {} and name = '{}'".format(aDict['a_dom_id'],fqdn))
 a_record = db.get_row()
 db.do("SELECT id,content FROM records WHERE type = 'PTR' and domain_id = {} and name = '{}'".format(ptr_dom_id,GL.sys_ip2ptr(aDict['ip']))) 
 p_record = db.get_row()
 db.close()
 retvals = {}
 if a_record and (a_record.get('content',None) == aDict['ip']):
  retvals['a_id'] = a_record.get('id') 
 if p_record and p_record.get('content',None):
  retvals['ptr_id'] = p_record.get('id')
  retvals['ptr_dom_id'] = ptr_dom_id
 return retvals

#
# update( ip, name, a_dom_id , a_id, ptr_id )
#
def dns_update(aDict):
 if SC.dnsdb_proxy == 'True':
  return GL.rpc_call(SC.dnsdb_url, "ddi_dns_update", aDict)
 GL.sys_log_msg("DNS  update - input:{}".format(aDict.values()))
 from time import strftime
 serial  = strftime("%Y%m%d%H")
 ptr     = GL.sys_ip2ptr(aDict['ip'])
 retvals = {}
 db = GL.DB()
 db.connect_details('localhost',SC.dnsdb_username, SC.dnsdb_password, SC.dnsdb_dbname)
 res = db.do("SELECT id,name FROM domains WHERE id = {} OR name = '{}'".format(aDict['a_dom_id'],ptr.partition('.')[2]))
 domains = db.get_all_rows()
 if res == 2:
  domain     = domains[0]['name'] if domains[1]['name'] == ptr else domains[1]['name']
  ptr_dom_id = domains[1]['id']   if domains[1]['name'] == ptr else domains[0]['id']
 else:
  domain     = domains[0]['name']
  ptr_dom_id = None
 fqdn    = aDict['name'] + "." + domain

 if aDict['a_id'] != '0':
  retvals['a_op'] = "update"
  db.do("UPDATE records SET name = '{}', content = '{}', change_date='{}' WHERE id ='{}'".format(fqdn,aDict['ip'],serial,aDict['a_id']))
 else:
  db.do("INSERT INTO records (domain_id,name,type,content,ttl,change_date) VALUES('{}','{}','A','{}',3600,'{}')".format(aDict['a_dom_id'],fqdn,aDict['ip'],serial))
  retvals['a_op'] = "insert"
  retvals['a_id'] = db.get_last_id()

 if aDict['ptr_id'] != '0':
  retvals['ptr_op'] = "update"
  db.do("UPDATE records SET name = '{}', content = '{}', change_date='{}' WHERE id ='{}'".format(ptr,fqdn,serial,aDict['ptr_id']))
 elif aDict['ptr_id'] == '0' and ptr_dom_id:
  db.do("INSERT INTO records (domain_id,name,type,content,ttl,change_date) VALUES('{}','{}','PTR','{}',3600,'{}')".format(ptr_dom_id,ptr,fqdn,serial))
  retvals['ptr_op'] = "insert"
  retvals['ptr_id'] = db.get_last_id()

 db.commit()
 db.close()
 GL.sys_log_msg("DNS  update - results: " + str(retvals))
 return retvals

def dns_remove(aDict):
 if SC.dnsdb_proxy == 'True':
  return GL.rpc_call(SC.dnsdb_url, "ddi_dns_remove", aDict)
 GL.sys_log_msg("DNS  remove - input:{}".format(aDict.values()))
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
  retvals['fqdn']    = ipam.get('dns_name',None)
  retvals['ptr_id']  = ipam.get('PTR',0)
 return retvals

#
# update( ipam_sub_id, ipam_id, ip, fqdn, ptr_id )
#
def ipam_update(aDict):
 if SC.ipamdb_proxy == 'True':
  return GL.rpc_call(SC.ipamdb_url, "ddi_ipam_update", aDict)
 GL.sys_log_msg("IPAM update - input:{}".format(aDict.values()))
 db = GL.DB()
 db.connect_details('localhost',SC.ipamdb_username, SC.ipamdb_password, SC.ipamdb_dbname)
 res = {}

 if aDict.get('ipam_id','0') != '0':
  res['ipam_op'] = 'update'
  db.do("UPDATE ipaddresses SET PTR = '{}', dns_name = '{}' WHERE id = '{}'".format(aDict['ptr_id'],aDict['fqdn'],aDict['ipam_id']))
 else:
  ipint = GL.sys_ip2int(aDict['ip'])
  db.do("SELECT id FROM ipaddresses WHERE ip_addr = '{0}' AND subnetId = {1}".format(ipint,aDict['ipam_sub_id']))
  entry = db.get_row()
  if entry:
   res['ipam_op'] = 'update_existed'
   db.do("UPDATE ipaddresses SET PTR = '{}', dns_name = '{}' WHERE id = '{}'".format(aDict['ptr_id'],aDict['fqdn'],entry.get('id')))
  else:
   db.do("INSERT INTO ipaddresses (subnetId,ip_addr,dns_name,PTR) VALUES('{}','{}','{}','{}')".format(aDict['ipam_sub_id'],ipint,aDict['fqdn'],aDict['ptr_id']))
   res['ipam_op'] = "insert"
   res['ipam_id'] = db.get_last_id()
 db.commit()
 db.close()
 return res

#
# remove(ipam_id)
#
def ipam_remove(aDict):
 if SC.ipamdb_proxy == 'True':
  return GL.rpc_call(SC.ipamdb_url, "ddi_ipam_remove", aDict)
 db = GL.DB()
 db.connect_details('localhost',SC.ipamdb_username, SC.ipamdb_password, SC.ipamdb_dbname)
 ires = db.do("DELETE FROM ipaddresses WHERE id = '{}'".format(aDict['ipam_id']))
 db.commit()
 db.close()
 GL.sys_log_msg("IPAM remove - {} -> {}".format(aDict,ires))
 return ires

#
# ipam_find(ipam_sub_id, consecutive)
#
def ipam_find(aDict):
 if SC.ipamdb_proxy == 'True':
  return GL.rpc_call(SC.ipamdb_url, "ddi_ipam_find", aDict)
 db = GL.DB()
 db.connect_details('localhost',SC.ipamdb_username, SC.ipamdb_password, SC.ipamdb_dbname)
 db.do("SELECT subnet, mask FROM subnets WHERE id = {}".format(aDict.get('ipam_sub_id'))) 
 sub = db.get_row()
 db.do("SELECT ip_addr FROM ipaddresses WHERE subnetId = {}".format(aDict.get('ipam_sub_id')))
 db.close()
 iplist = db.get_all_dict('ip_addr')
 subnet = int(sub.get('subnet'))
 start  = None
 ret    = { 'subnet':GL.sys_int2ip(subnet) }
 for ip in range(subnet + 1, subnet + 2**(32-int(sub.get('mask')))-1):
  if not iplist.get(str(ip),False):
   if start:
    count = count - 1
    if count == 1:
     ret['start'] = GL.sys_int2ip(start)
     ret['end'] = GL.sys_int2ip(start+int(aDict.get('consecutive'))-1)
     break
   else:
    count = int(aDict.get('consecutive'))          
    start = ip       
  else:     
   start = None           
 return ret                            
