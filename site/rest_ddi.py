"""Module docstring.

 DDI API module

"""
__author__ = "Zacharias El Banna"                     
__version__ = "17.10.4"
__status__ = "Production"

import sdcp.PackageContainer as PC
import sdcp.core.genlib as GL

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
 from sdcp.core.dbase import DB
 with DB() as db:
  for dom in domains:
   db.do("INSERT INTO domains(id,name) VALUES ({0},'{1}') ON DUPLICATE KEY UPDATE name='{1}'".format(dom['id'],dom['name']))
  db.commit()
  for sub in subnets:
   db.do("INSERT INTO subnets(id,subnet,mask,subnet_description,section_id,section_name) VALUES ({0},{1},{2},'{3}',{4},'{5}') ON DUPLICATE KEY UPDATE subnet={1},mask={2}".format(sub['id'],sub['subnet'],sub['mask'],sub['description'],sub['section_id'],sub['section_name']))
  db.commit()
 return { 'domains':len(domains), 'subnets':len(subnets) }

################################################# DDI - DHCP #################################################
#
#
#
def dhcp_leases(aDict):
 if PC.dhcp['proxy'] == 'True':
  from sdcp.core.rest import call as rest_call
  return rest_call(PC.dhcp['url'], "sdcp.site:ddi_dhcp_leases", aDict)
 import sdcp.core.genlib as GL
 active = []
 free   = []
 lease  = {}
 with open(PC.dhcp['leasefile'],'r') as leasefile: 
  for line in leasefile:
   if line == '\n':
    continue
   parts = line.split()
   if   parts[0] == 'lease' and parts[2] == '{':
    lease['ip'] = parts[1]
   elif parts[0] == '}':
    if lease.pop('binding') == "active":
     active.append(lease)
    else:
     free.append(lease)
    lease = {}
   elif parts[0] == 'hardware' and parts[1] == 'ethernet':
    lease['mac'] = parts[2][:-1] 
   elif parts[0] == 'binding':
    lease['binding'] = parts[2][:-1] 
   elif parts[0] == 'starts' or parts[0] == 'ends':
    lease[parts[0]] = " ".join(parts[2:])[:-1]
   elif parts[0] == 'client-hostname':
    lease['hostname'] = parts[1][:-1]
  active.sort(key=lambda d: GL.ip2int(d['ip']))
  free.sort(  key=lambda d: GL.ip2int(d['ip']))
  return {"active":active, "free":free }                                

def dhcp_update(aDict):
 #
 # Update function - reload the DHCP server to use new info
 # - entries is a list of dict objects containing hostname, mac, ip etc
 if PC.dhcp['proxy'] == 'True':
  from sdcp.core.rest import call as rest_call             
  return rest_call(PC.dhcp['url'], "sdcp.site:ddi_dhcp_update", aDict)

 entries = aDict['entries']
 # Create new file
 with open(PC.dhcp['file'],'w') as leasefile:
  for entry in entries:
   leasefile.write("host {0: <30} {{ hardware ethernet {1}; fixed-address {2}; }} # Subnet {3}, Id: {4}\n".format(entry['fqdn'],entry['mac'],entry['ip'],entry['subnet_id'],entry['id'])) 

 # Reload
 from subprocess import check_output, CalledProcessError
 commands = PC.dhcp['reload'].split()
 result = {}
 try:
  status = check_output(commands)
  result['res'] = "OK"
  result['output'] = status
 except CalledProcessError, c:
  result['res'] = "Error"
  result['code'] = c.returncode
  result['output'] = c.output
 return result

################################################# DDI - DNS ##################################################
#
# Call removes name duplicates.. (assume order by name => duplicate names :-))
#
def dns_cleanup(aDict):
 if PC.dnsdb['proxy'] == 'True':
  from sdcp.core.rest import call as rest_call             
  return rest_call(PC.dnsdb['url'], "sdcp.site:ddi_dns_cleanup", aDict)
 from sdcp.core.dbase import DB
 with DB(PC.dnsdb['dbname'],'localhost',PC.dnsdb['username'],PC.dnsdb['password']) as db:
  db.do("SELECT id,name,content FROM records WHERE type = 'A' OR type = 'PTR' ORDER BY name")   
  rows = db.get_rows();
  remove = []
  previous = {'content':None,'name':None}
  for row in rows:
   if previous['content'] == row['content'] and previous['name'] == row['name']:
    db.do("DELETE from records WHERE id = '{}'".format(row['id'] if row['id'] > previous['id'] else previous['id']))
    row.pop('id')
    remove.append(row)
   else:              
    previous = row
  db.commit()
 return {'removed':remove}

#
# dns top lookups
#
def dns_top(aDict):
 if PC.dnsdb['proxy'] == 'True':
  from sdcp.core.rest import call as rest_call             
  return rest_call(PC.dnsdb['url'], "sdcp.site:ddi_dns_top", aDict)
 import sdcp.core.genlib as GL
 count = int(aDict.get('count',10))
 fqdn_top = {}                
 fqdn_who = {}
 with open(PC.dnsdb['logfile'],'r') as log:
  for line in log:
   parts = line.split()
   fqdn  = parts[8].split('|')[0][1:]
   fqdn_top[fqdn] = fqdn_top.get(fqdn,0)+1     
   fqdn_who[fqdn+"#"+parts[6]] = fqdn_who.get(fqdn+"#"+parts[6],0)+1
 from collections import Counter
 top = map(lambda x: {'fqdn':x[0],'count':x[1]}, Counter(fqdn_top).most_common(count))
 who = []
 for item in  Counter(fqdn_who).most_common(count):
  parts = item[0].split('#')
  who.append({'fqdn':parts[0], 'who':parts[1], 'hostname': GL.get_host_name(parts[1]), 'count':item[1]})
 return {'top':top,'who':who }


#
# Should be domains(target, arg) to simpler select domain 
#
def dns_domains(aDict):
 if PC.dnsdb['proxy'] == 'True':
  from sdcp.core.rest import call as rest_call             
  return rest_call(PC.dnsdb['url'], "sdcp.site:ddi_dns_domains", aDict)
 from sdcp.core.dbase import DB
 with DB(PC.dnsdb['dbname'],'localhost',PC.dnsdb['username'],PC.dnsdb['password']) as db:
  res = db.do("SELECT id, name FROM domains")
  rows = db.get_rows()
 return rows

#
# lookup ( name, a_dom_id, ip)
#
def dns_lookup(aDict):
 if PC.dnsdb['proxy'] == 'True':
  from sdcp.core.rest import call as rest_call             
  return rest_call(PC.dnsdb['url'], "sdcp.site:ddi_dns_lookup", aDict)
 import sdcp.core.genlib as GL
 ptr  = GL.ip2arpa(aDict['ip'])
 PC.log_msg("DNS  lookup - input:{}".format(aDict.values()))  
 from sdcp.core.dbase import DB
 with DB(PC.dnsdb['dbname'],'localhost',PC.dnsdb['username'],PC.dnsdb['password']) as db:
  res = db.do("SELECT id,name FROM domains WHERE id = {} OR name = '{}'".format(aDict['a_dom_id'],ptr))
  domains = db.get_rows()
  if res == 2:
   domain     = domains[0]['name'] if domains[1]['name'] == ptr else domains[1]['name']
   ptr_dom_id = domains[1]['id']   if domains[1]['name'] == ptr else domains[0]['id']
  else:
   domain     = domains[0]['name']
   ptr_dom_id = '0'
  fqdn    = aDict['name'] + "." + domain
  db.do("SELECT id,content FROM records WHERE type = 'A' and domain_id = {} and name = '{}'".format(aDict['a_dom_id'],fqdn))
  a_record = db.get_row()
  db.do("SELECT id,content FROM records WHERE type = 'PTR' and domain_id = {} and name = '{}'".format(ptr_dom_id,GL.ip2ptr(aDict['ip']))) 
  p_record = db.get_row()
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
 if PC.dnsdb['proxy'] == 'True':
  from sdcp.core.rest import call as rest_call             
  return rest_call(PC.dnsdb['url'], "sdcp.site:ddi_dns_update", aDict)
 PC.log_msg("DNS  update - input:{}".format(aDict.values()))
 import sdcp.core.genlib as GL
 from time import strftime
 serial  = strftime("%Y%m%d%H")
 ptr     = GL.ip2ptr(aDict['ip'])
 retvals = {}
 from sdcp.core.dbase import DB
 with DB(PC.dnsdb['dbname'],'localhost',PC.dnsdb['username'],PC.dnsdb['password']) as db:
  res = db.do("SELECT id,name FROM domains WHERE id = {} OR name = '{}'".format(aDict['a_dom_id'],ptr.partition('.')[2]))
  domains = db.get_rows()
  if res == 2:
   domain     = domains[0]['name'] if domains[1]['name'] == ptr else domains[1]['name']
   ptr_dom_id = domains[1]['id']   if domains[1]['name'] == ptr else domains[0]['id']
  else:
   domain     = domains[0]['name']
   ptr_dom_id = None
  fqdn    = aDict['name'] + "." + domain

  if aDict['a_id'] != '0':
   retvals['a_op'] = "update"
   retvals['a_id'] = aDict['a_id']
   db.do("UPDATE records SET name = '{}', content = '{}', change_date='{}' WHERE id ='{}'".format(fqdn,aDict['ip'],serial,aDict['a_id']))
  else:
   db.do("INSERT INTO records (domain_id,name,type,content,ttl,change_date) VALUES('{}','{}','A','{}',3600,'{}')".format(aDict['a_dom_id'],fqdn,aDict['ip'],serial))
   retvals['a_op'] = "insert"
   retvals['a_id'] = db.get_last_id()

  if aDict['ptr_id'] != '0':
   retvals['ptr_id'] = aDict['ptr_id']
   retvals['ptr_op'] = "update"
   db.do("UPDATE records SET name = '{}', content = '{}', change_date='{}' WHERE id ='{}'".format(ptr,fqdn,serial,aDict['ptr_id']))
  elif aDict['ptr_id'] == '0' and ptr_dom_id:
   db.do("INSERT INTO records (domain_id,name,type,content,ttl,change_date) VALUES('{}','{}','PTR','{}',3600,'{}')".format(ptr_dom_id,ptr,fqdn,serial))
   retvals['ptr_op'] = "insert"
   retvals['ptr_id'] = db.get_last_id()

  db.commit()
 PC.log_msg("DNS  update - results: " + str(retvals))
 return retvals

def dns_remove(aDict):
 if PC.dnsdb['proxy'] == 'True':
  from sdcp.core.rest import call as rest_call             
  return rest_call(PC.dnsdb['url'], "sdcp.site:ddi_dns_remove", aDict)
 PC.log_msg("DNS  remove - input:{}".format(aDict.values()))
 ares = 0
 pres = 0
 from sdcp.core.dbase import DB
 with DB(PC.dnsdb['dbname'],'localhost',PC.dnsdb['username'],PC.dnsdb['password']) as db:
  if aDict['a_id'] != '0':
   ares = db.do("DELETE FROM records WHERE id = '{}' and type = 'A'".format(aDict['a_id']))
  if aDict['ptr_id'] != '0':
   pres = db.do("DELETE FROM records WHERE id = '{}' and type = 'PTR'".format(aDict['ptr_id']))
  db.commit()
 PC.log_msg("DNS  remove - A:{} PTR:{}".format(str(ares),str(pres)))
 return { 'a':ares, 'ptr':pres }

################################################# DDI - IPAM ##################################################
#
# Should be subnets(target, arg)
#
def ipam_subnets(aDict):
 if PC.ipamdb['proxy'] == 'True':
  from sdcp.core.rest import call as rest_call             
  return rest_call(PC.ipamdb['url'], "sdcp.site:ddi_ipam_subnets", aDict)
 from sdcp.core.dbase import DB
 with DB(PC.ipamdb['dbname'],'localhost',PC.ipamdb['username'],PC.ipamdb['password']) as db:
  db.do("SELECT subnets.id, subnet, mask, subnets.description, name as section_name, sectionId as section_id FROM subnets INNER JOIN sections on subnets.sectionId = sections.id") 
  rows = db.get_rows()
 return rows

#
# lookup(ip,ipam_sub_id)
#
def ipam_lookup(aDict):
 if PC.ipamdb['proxy'] == 'True':
  from sdcp.core.rest import call as rest_call             
  return rest_call(PC.ipamdb['url'], "sdcp.site:ddi_ipam_lookup", aDict)
 PC.log_msg("IPAM lookup - input {}".format(aDict.values()))
 import sdcp.core.genlib as GL
 ipint   = GL.ip2int(aDict['ip'])
 retvals = { 'ipam_id':'0' }
 from sdcp.core.dbase import DB
 with DB(PC.ipamdb['dbname'],'localhost',PC.ipamdb['username'],PC.ipamdb['password']) as db:
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
def ipam_update(aDict):
 if PC.ipamdb['proxy'] == 'True':
  from sdcp.core.rest import call as rest_call             
  return rest_call(PC.ipamdb['url'], "sdcp.site:ddi_ipam_update", aDict)
 PC.log_msg("IPAM update - input:{}".format(aDict.values()))
 res = {}
 import sdcp.core.genlib as GL
 from sdcp.core.dbase import DB
 with DB(PC.ipamdb['dbname'],'localhost',PC.ipamdb['username'],PC.ipamdb['password']) as db:
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
def ipam_remove(aDict):
 if PC.ipamdb['proxy'] == 'True':
  from sdcp.core.rest import call as rest_call             
  return rest_call(PC.ipamdb['url'], "sdcp.site:ddi_ipam_remove", aDict)
 from sdcp.core.dbase import DB
 with DB(PC.ipamdb['dbname'],'localhost',PC.ipamdb['username'],PC.ipamdb['password']) as db:
  ires = db.do("DELETE FROM ipaddresses WHERE id = '{}'".format(aDict['ipam_id']))
  db.commit()
 PC.log_msg("IPAM remove - {} -> {}".format(aDict,ires))
 return ires

#
# ipam_find(ipam_sub_id, consecutive)
#
def ipam_find(aDict):
 if PC.ipamdb['proxy'] == 'True':
  from sdcp.core.rest import call as rest_call             
  return rest_call(PC.ipamdb['url'], "sdcp.site:ddi_ipam_find", aDict)
 import sdcp.core.genlib as GL
 from sdcp.core.dbase import DB
 with DB(PC.ipamdb['dbname'],'localhost',PC.ipamdb['username'],PC.ipamdb['password']) as db:
  db.do("SELECT subnet, mask FROM subnets WHERE id = {}".format(aDict.get('ipam_sub_id'))) 
  sub = db.get_row()
  db.do("SELECT ip_addr FROM ipaddresses WHERE subnetId = {}".format(aDict.get('ipam_sub_id')))
  iplist = db.get_all_dict('ip_addr')
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
