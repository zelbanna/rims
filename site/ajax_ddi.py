"""Module docstring.

Ajax DDI calls module

"""
__author__= "Zacharias El Banna"                     
__version__ = "10.5GA"
__status__= "Production"

import sdcp.core.GenLib as GL

#
#
#
def sync(aWeb):
 from rest_ddi import dns_lookup, ipam_lookup, dns_update, ipam_update
 db = GL.DB()
 db.connect()
 db.do("SELECT id, ip, hostname, INET_NTOA(ip) as ipasc, domain FROM devices WHERE (a_id = 0 or ptr_id = 0 or ipam_id = 0 or ipam_mask = 0 or ipam_sub = 0) ORDER BY ip")
 rows = db.get_all_rows()
 print "<DIV CLASS='z-table'>"
 print "<TABLE>"
 print "<TR><TH>Id</TH><TH>IP</TH><TH>Hostname</TH><TH>Domain</TH><TH>A</TH><TH>PTR</TH><TH>IPAM</TH><TH>Subnet</TH><TH>Mask</TH><TH>Extra</TH>"
 for row in rows:
  ip   = row['ipasc']
  name = row['hostname']
  dom  = row['domain'] 
  dargs = { 'ip':ip, 'name':name, 'domain':dom }
  retvals    = dns_lookup( dargs )
  a_id   = retvals.get('a_id','0')
  ptr_id = retvals.get('ptr_id','0')

  retvals    = ipam_lookup({'ip':ip})
  ipam_id    = retvals.get('ipam_id','0')
  ipam_mask  = retvals.get('subnet_mask','24')
  ipam_sub   = retvals.get('subnet_asc','0.0.0.0')
  ipam_subint= GL.sys_ip2int(ipam_sub)
  print "<TR><TD>{}</<TD><TD>{}</TD><TD>{}</TD><TD>{}</TD><TD>{}</TD><TD>{}</TD><TD>{}</TD><TD>{}</TD><TD>{}</TD><TD>".format(row['id'],ip,name,dom,a_id,ptr_id,ipam_id,ipam_sub,ipam_mask)
  if not name == 'unknown':
   print "updating"
   uargs = { 'ip':ip, 'name':name, 'domain':dom, 'a_id':a_id, 'ptr_id':ptr_id }
   dns_update(uargs)
   retvals = dns_lookup(dargs)
   uargs['ipam_id'] = ipam_id
   uargs['ptr_id']  = retvals.get('ptr_id','0')
   del uargs['a_id']
   ipam_update(uargs)
   print str(retvals)
   db.do("UPDATE devices SET ipam_id = {}, a_id = '{}', ptr_id = '{}', ipam_mask = '{}', ipam_sub = '{}' WHERE id = '{}'".format(ipam_id, retvals.get('a_id','0'),retvals.get('ptr_id','0'), ipam_mask, ipam_subint, row['id']))
  print "</TD></TR>"

 db.commit()
 db.close()
 print "</TABLE></DIV>"

#
#
#

def load_infra(aWeb):
 from rest_ddi import load_infra
 print "<PRE>{}</PRE>".format(load_infra(None))
