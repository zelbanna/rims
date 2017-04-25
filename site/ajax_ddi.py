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
 db.do("SELECT devices.id, ip, hostname, INET_NTOA(ip) as ipasc, ipam_sub_id, a_dom_id, domains.name as domain FROM devices JOIN domains ON domains.id = devices.a_dom_id WHERE (a_id = 0 or ptr_id = 0 or ipam_id = 0) ORDER BY ip")
 rows = db.get_all_rows()
 print "<DIV CLASS='z-table'>"
 print "<TABLE>"
 print "<TR><TH>Id</TH><TH>IP</TH><TH>Hostname</TH><TH>Domain</TH><TH>A</TH><TH>PTR</TH><TH>IPAM</TH><TH>Extra</TH>"
 for row in rows:
  ip   = row['ipasc']
  name = row['hostname']
  dom  = row['a_dom_id'] 
  dargs = { 'ip':ip, 'name':name, 'a_dom_id':dom }
  retvals = dns_lookup( dargs )
  a_id    = retvals.get('a_id','0')
  ptr_id  = retvals.get('ptr_id','0')

  retvals = ipam_lookup({'ip':ip, 'ipam_sub_id':row['ipam_sub_id']})
  ipam_id = retvals.get('ipam_id','0')
  print "<TR><TD>{}</<TD><TD>{}</TD><TD>{}</TD><TD>{}</TD><TD>{}</TD><TD>{}</TD><TD>{}</TD><TD>".format(row['id'],ip,name,dom,a_id,ptr_id,ipam_id)
  if not name == 'unknown':
   print "updating"
   uargs = { 'ip':ip, 'name':name, 'a_dom_id':dom, 'a_id':a_id, 'ptr_id':ptr_id }
   dns_update(uargs)
   retvals = dns_lookup(dargs)
   uargs = { 'ip':ip, 'ipam_id':ipam_id, 'ipam_sub_id':row['ipam_sub_id'], 'ptr_id':retvals.get('ptr_id','0'), 'fqdn':name + '.' + row['domain'] }
   ipam_update(uargs)
   print str(retvals)
   db.do("UPDATE devices SET ipam_id = {}, a_id = {}, ptr_id = {}, ptr_dom_id = {}  WHERE id = {}".format(ipam_id, retvals.get('a_id','0'),retvals.get('ptr_id','0'), retvals.get('ptr_dom_id','NULL'), row['id']))
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
