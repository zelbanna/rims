#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Module docstring.

 DNS interworking module

"""
__author__ = "Zacharias El Banna"                     
__version__ = "10.0GA"
__status__ = "Production"

import sdcp.SettingsContainer as SC
from GenLib import sys_log_msg, sys_ip2ptr, sys_ip2int, DB
from subprocess import check_output, check_call
from time import sleep
from socket import gethostbyname

################################ LOOPIA DNS ###################################
#
# Change IP for a domain in loopia DNS
#
loopia_domain_server_url = 'https://api.loopia.se/RPCSERV' 

def set_loopia_ip(subdomain, newip):
 import xmlrpclib
 try:
  client = xmlrpclib.ServerProxy(uri = loopia_domain_server_url, encoding = 'utf-8')
  data = client.getZoneRecords(SC.loopia_username, SC.loopia_password, SC.loopia_domain, subdomain)[0]
  oldip = data['rdata']
  data['rdata'] = newip
  status = client.updateZoneRecord(SC.loopia_username, SC.loopia_password, SC.loopia_domain, subdomain, data)[0]
 except Exception as exmlrpc:
  sys_log_msg("System Error - Loopia set: " + str(exmlrpc))
  return False
 return True

#
# Get Loopia settings for subdomain
#
def get_loopia_ip(subdomain):
 import xmlrpclib
 try:
  client = xmlrpclib.ServerProxy(uri = loopia_domain_server_url, encoding = 'utf-8')
  data = client.getZoneRecords(SC.loopia_username, SC.loopia_password, SC.loopia_domain, subdomain)[0]
  return data['rdata']
 except Exception as exmlrpc:
  sys_log_msg("System Error - Loopia get: " + str(exmlrpc))
  return False

def get_loopia_suffix():
 return "." + SC.loopia_domain

################################# OpenDNS ######################################
#
# Return external IP from opendns
#
def opendns_my_ip():
 from dns import resolver
 try:
  opendns = resolver.Resolver()
  opendns.nameservers = [gethostbyname('resolver1.opendns.com')]
  myiplookup = opendns.query("myip.opendns.com",'A').response.answer[0]
  return str(myiplookup).split()[4]
 except Exception as exresolve:
  sys_log_msg("OpenDNS Error - Resolve: " + str(exresolve))
  return False
 
############################### PDNS SYSTEM FUNCTIONS ##################################
#

def pdns_get():
 recursor = check_output(["sudo","/bin/grep", "^recursor","/etc/powerdns/pdns.conf"])
 return recursor.split('=')[1].split('#')[0].strip()

#
# All-in-one, runs check, verify and (if needed) set and reload pdns service
# - returns True if was in sync and False if modified
# 
def pdns_sync(dnslist):
 from XtraLib import sys_file_replace
 pdns = pdns_get()
 if not pdns in dnslist:
  sys_log_msg("System Info - updating recursor to " + dnslist[0])
  sys_file_replace('/etc/powerdns/pdns.conf', pdns, dnslist[0])
  try:
   check_call(["/usr/sbin/service","pdns","reload"])
   sleep(1)
  except Exception as svcerr:
   sys_log_msg("System Error - Reloading PowerDNS: " + str(svcerr))
  return False
 return True  

################################################# DDI - DNS ##################################################
#
# Lookup a and ptr id for a given ip,hostname and domain, return as dict
#
def ddi_dns_lookup(aIP,aName,aDomain):
 ptr     = sys_ip2ptr(aIP)
 fqdn    = aName + "." + aDomain
 retvals = {}
 sys_log_msg("DNS  lookup - input:{}, {}, {}".format(aIP,aName,aDomain))  
 db = DB()
 db.connect_details('localhost',SC.dnsdb_username, SC.dnsdb_password, SC.dnsdb_dbname)
 res = db.do("SELECT id,name from domains")
 domain_db = db.get_all_dict("name")
 domain_id = [ domain_db.get(aDomain,{ 'id':'0' }), domain_db.get(ptr.partition('.')[2],{ 'id':'0' }) ]
 db.do("SELECT id,content FROM records WHERE type = 'A' and domain_id = '{}' and name = '{}'".format(domain_id[0]['id'],fqdn)) 
 a_record = db.get_row()                       
 db.do("SELECT id,content FROM records WHERE type = 'PTR' and domain_id = '{}' and name = '{}'".format(domain_id[1]['id'],ptr)) 
 p_record = db.get_row()
 if a_record and (a_record.get('content',None) == aIP):
  retvals['dns_a_id'] = a_record.get('id') 
 if p_record and p_record.get('content',None):
  retvals['dns_ptr_id'] = p_record.get('id')
 db.close() 
 return retvals

def ddi_dns_update(aIP,aName,aDomain,aAid,aPid):
 from time import strftime
 serial  = strftime("%Y%m%d01")
 ptr     = sys_ip2ptr(aIP)
 fqdn    = aName + "." + aDomain
 retvals = {}
 sys_log_msg("DNS  update - input:{}, {}, {}, {}, {}".format(aIP,aName,aDomain,aAid,aPid))  
 db = DB()
 db.connect_details('localhost',SC.dnsdb_username, SC.dnsdb_password, SC.dnsdb_dbname)
 db.do("SELECT id,name from domains")
 domain_db = db.get_all_dict("name")
 domain_id = [ domain_db.get(aDomain,{ 'id':'0' }), domain_db.get(ptr.partition('.')[2],{ 'id':'0' }) ]
 # A domain dict, PTR domain dict
 if aAid != '0':
  retvals['a'] = "update"
  db.do("UPDATE records SET name = '{}', content = '{}', change_date='{}' WHERE id ='{}'".format(fqdn,aIP,serial,aAid))
 else:
  retvals['a'] = "insert"
  db.do("INSERT INTO records (domain_id,name,type,content,ttl,change_date) VALUES('{}','{}','A','{}',3600,'{}')".format(str(domain_id[0].get('id')),fqdn,aIP,serial))
 if aPid != '0':
  retvals['ptr'] = "update"
  db.do("UPDATE records SET name = '{}', content = '{}', change_date='{}' WHERE id ='{}'".format(ptr,fqdn,serial,aPid))
 else:
  retvals['ptr'] = "insert"
  db.do("INSERT INTO records (domain_id,name,type,content,ttl,change_date) VALUES('{}','{}','PTR','{}',3600,'{}')".format(str(domain_id[1].get('id')),ptr,fqdn,serial))
 db.commit()
 db.close()
 sys_log_msg("DNS  update - results: " + str(retvals))
 return retvals

def ddi_dns_remove(aAid,aPid):
 db = DB()
 db.connect_details('localhost',SC.dnsdb_username, SC.dnsdb_password, SC.dnsdb_dbname)
 ares = 0
 pres = 0
 if aAid != '0':
  ares = db.do("DELETE FROM records WHERE id = '{}' and type = 'A'".format(aAid))
 if aPid != '0':
  pres = db.do("DELETE FROM records WHERE id = '{}' and type = 'PTR'".format(aPid))
 db.commit()
 sys_log_msg("DNS  remove - A:{} PTR:{}".format(str(ares),str(pres)))
 return { 'a':ares, 'ptr':pres }
 db.close()

################################################# DDI - IPAM ##################################################
#
#
def ddi_ipam_lookup(aIP):
 sys_log_msg("IPAM lookup - input {}".format(aIP))
 ipint   = sys_ip2int(aIP)
 retvals = { 'ipam_id':'0' }
 db = DB()
 db.connect_details('localhost',SC.ipamdb_username, SC.ipamdb_password, SC.ipamdb_dbname)
 db.do("SELECT id, subnet, INET_NTOA(subnet) as subnetasc, mask FROM subnets WHERE vrfId = 0 AND {0} > subnet AND {0} < (subnet + POW(2,(32-mask))-1)".format(ipint))
 subnet = db.get_row()
 retvals['subnet_id'] = subnet.get('id')
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
def ddi_ipam_update(aIP, aIPAMid, aPid, aFQDN):
 retvals = { 'op_result':'done' }
 ipint   = sys_ip2int(aIP)
 sys_log_msg("IPAM update - input:{}, {}, {}, {}".format(aIP,aIPAMid,aPid,aFQDN))
 db = DB()
 db.connect_details('localhost',SC.ipamdb_username, SC.ipamdb_password, SC.ipamdb_dbname)
 if not aIPAMid == '0':
  db.do("UPDATE ipaddresses SET PTR = '{}', dns_name = '{}' WHERE id = '{}'".format(aPid,aFQDN,aIPAMid))
 else:
  db.do("SELECT id, subnet, INET_NTOA(subnet) as subnetasc, mask FROM subnets WHERE vrfId = 0 AND {0} > subnet AND {0} < (subnet + POW(2,(32-mask))-1)".format(ipint))
  subnet = db.get_row()
  subnet_id = subnet.get('id')
  db.do("SELECT id FROM ipaddresses WHERE ip_addr = '{0}' AND subnetId = {1}".format(ipint,subnet_id))
  entry = db.get_row()
  if entry:
   aIPAMid = entry.get('id')
   sys_log_msg("IPAM update - ipam_id 0 -> {}".format(aIPAMid))
   db.do("UPDATE ipaddresses SET PTR = '{}', dns_name = '{}' WHERE id = '{}'".format(aPid,aFQDN,aIPAMid))
  else:
   db.do("INSERT INTO ipaddresses (subnetId,ip_addr,dns_name,PTR) VALUES('{}','{}','{}','{}')".format(subnet_id,ipint,aFQDN,aPid))
 db.commit()
 db.close()
 return retvals

#
#
#
def ddi_ipam_remove(aIPAMid):
 db = DB()
 db.connect_details('localhost',SC.ipamdb_username, SC.ipamdb_password, SC.ipamdb_dbname)
 ires = db.do("DELETE FROM ipaddresses WHERE id = '{}'".format(aIPAMid))
 db.commit()
 sys_log_msg("IPAM remove - I:{}".format(str(ires)))
 return { 'ipam':ires }
 db.close()
