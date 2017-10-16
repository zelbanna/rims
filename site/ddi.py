"""Module docstring.

Ajax DDI calls module

"""
__author__= "Zacharias El Banna"                     
__version__ = "17.10.4"
__status__= "Production"


#
#
#
def dhcp_update(aWeb):
 from sdcp.core.dbase import DB
 import sdcp.core.genlib as GL
 from rest_ddi import dhcp_update as rest_dhcp_update
 with DB() as db:
  db.do("SELECT devices.id, hostname, INET_NTOA(ip) as ipasc, domains.name as domain, mac, ipam_sub_id from devices JOIN domains ON domains.id = devices.a_dom_id WHERE NOT  mac = 0 ORDER BY ip")
  rows = db.get_rows()
 args = []
 for row in rows:
  args.append({'ip':row['ipasc'],'fqdn':"{}.{}".format(row['hostname'],row['domain']),'mac':GL.int2mac(row['mac']),'id':row['id'],'subnet_id':row['ipam_sub_id']})
 res = rest_dhcp_update({'entries':args})
 print res
#
#
#
def sync(aWeb):
 from sdcp.core.dbase import DB
 from rest_ddi import dns_lookup, ipam_lookup, dns_update, ipam_update
 print "<DIV CLASS=z-frame><DIV CLASS=z-table>"
 print "<DIV CLASS=thead style='border: 1px solid grey'><DIV CLASS=th>Id</DIV><DIV CLASS=th>IP</DIV><DIV CLASS=th>Hostname</DIV><DIV CLASS=th>Domain</DIV><DIV CLASS=th>A</DIV><DIV CLASS=th>PTR</DIV><DIV CLASS=th>IPAM</DIV><DIV CLASS=th>Extra</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 with DB() as db:
  db.do("SELECT devices.id, ip, hostname, INET_NTOA(ip) as ipasc, ipam_sub_id, a_dom_id, domains.name as domain FROM devices JOIN domains ON domains.id = devices.a_dom_id WHERE (a_id = 0 or ptr_id = 0 or ipam_id = 0) ORDER BY ip")
  rows = db.get_rows()
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
   print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>".format(row['id'],ip,name,dom,a_id,ptr_id,ipam_id)
   if not name == 'unknown':
    print "updating"
    uargs = { 'ip':ip, 'name':name, 'a_dom_id':dom, 'a_id':a_id, 'ptr_id':ptr_id }
    dns_update(uargs)
    retvals = dns_lookup(dargs)
    uargs = { 'ip':ip, 'ipam_id':ipam_id, 'ipam_sub_id':row['ipam_sub_id'], 'ptr_id':retvals.get('ptr_id','0'), 'fqdn':name + '.' + row['domain'] }
    ipam_update(uargs)
    print str(retvals)
    db.do("UPDATE devices SET ipam_id = {}, a_id = {}, ptr_id = {}, ptr_dom_id = {}  WHERE id = {}".format(ipam_id, retvals.get('a_id','0'),retvals.get('ptr_id','0'), retvals.get('ptr_dom_id','NULL'), row['id']))
   print "</DIV></DIV>"
  db.commit()
 print "</DIV></DIV></DIV>"

#
#
#

def load_infra(aWeb):
 from rest_ddi import load_infra
 print "<PRE>{}</PRE>".format(load_infra(None))
