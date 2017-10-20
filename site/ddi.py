"""Module docstring.

Ajax DDI calls module

"""
__author__= "Zacharias El Banna"                     
__version__ = "17.10.4"
__status__= "Production"

import sdcp.PackageContainer as PC
from sdcp.core.dbase import DB
from sdcp.core.rest import call as rest_call

#
#
#
def dhcp_update(aWeb):
 import sdcp.core.genlib as GL
 with DB() as db:
  db.do("SELECT devices.id, hostname, INET_NTOA(ip) as ipasc, domains.name as domain, mac, ipam_sub_id from devices JOIN domains ON domains.id = devices.a_dom_id WHERE NOT  mac = 0 ORDER BY ip")
  rows = db.get_rows()
 args = []
 for row in rows:
  args.append({'ip':row['ipasc'],'fqdn':"{}.{}".format(row['hostname'],row['domain']),'mac':GL.int2mac(row['mac']),'id':row['id'],'subnet_id':row['ipam_sub_id']})
 
 res = rest_call(PC.dhcp['url'],"sdcp.rest.{}_update".format(PC.dhcp['type']),{'entries':args})
 print res
#
#
#
def sync(aWeb):
 print "<DIV CLASS=z-frame><DIV CLASS=z-table>"
 print "<DIV CLASS=thead style='border:solid 1px grey;'><DIV CLASS=th>Id</DIV><DIV CLASS=th>IP</DIV><DIV CLASS=th>Hostname</DIV><DIV CLASS=th>Domain</DIV><DIV CLASS=th>A</DIV><DIV CLASS=th>PTR</DIV><DIV CLASS=th>IPAM</DIV><DIV CLASS=th>Extra</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 with DB() as db:
  db.do("SELECT devices.id, ip, hostname, INET_NTOA(ip) as ipasc, ipam_sub_id, a_dom_id, domains.name as domain FROM devices JOIN domains ON domains.id = devices.a_dom_id WHERE (a_id = 0 or ptr_id = 0 or ipam_id = 0) ORDER BY ip")
  rows = db.get_rows()
  for row in rows:
   ip   = row['ipasc']
   name = row['hostname']
   dom  = row['a_dom_id'] 
   dargs = { 'ip':ip, 'name':name, 'a_dom_id':dom }
   retvals = rest_call(PC.dnsdb['url'],"sdcp.rest.{}_lookup".format(PC.dnsdb['type']), dargs)
   a_id    = retvals.get('a_id','0')
   ptr_id  = retvals.get('ptr_id','0')

   retvals = rest_call(PC.ipamdb['url'],"sdcp.rest.{}_lookup".format(PC.ipamdb['type']),{'ip':ip, 'ipam_sub_id':row['ipam_sub_id']})
   ipam_id = retvals.get('ipam_id','0')
   print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>".format(row['id'],ip,name,dom,a_id,ptr_id,ipam_id)
   if not name == 'unknown':
    print "updating"
    uargs = { 'ip':ip, 'name':name, 'a_dom_id':dom, 'a_id':a_id, 'ptr_id':ptr_id }
    rest_call(PC.dnsdb['url'],"sdcp.rest.{}_update".format(PC.dnsdb['type']), uargs)
    retvals = rest_call(PC.dnsdb['url'],"sdcp.rest.{}_lookup".format(PC.dnsdb['type']), dargs)
    uargs = { 'ip':ip, 'ipam_id':ipam_id, 'ipam_sub_id':row['ipam_sub_id'], 'ptr_id':retvals.get('ptr_id','0'), 'fqdn':name + '.' + row['domain'] }
    rest_call(PC.ipamdb['url'],"sdcp.rest.{}_update".format(PC.ipamdb['type']),uargs)
    print str(retvals)
    db.do("UPDATE devices SET ipam_id = {}, a_id = {}, ptr_id = {}, ptr_dom_id = {}  WHERE id = {}".format(ipam_id, retvals.get('a_id','0'),retvals.get('ptr_id','0'), retvals.get('ptr_dom_id','NULL'), row['id']))
   print "</DIV></DIV>"
  db.commit()
 print "</DIV></DIV></DIV>"

#
#
#
def load_infra(aWeb):
 domains = rest_call(PC.dnsdb['url'], "sdcp.rest.{}_domains".format(PC.dnsdb['type']))
 subnets = rest_call(PC.ipamdb['url'],"sdcp.rest.{}_subnets".format(PC.ipamdb['type']))
 with DB() as db:
  for dom in domains:
   db.do("INSERT INTO domains(id,name) VALUES ({0},'{1}') ON DUPLICATE KEY UPDATE name='{1}'".format(dom['id'],dom['name']))
  db.commit()
  for sub in subnets:
   db.do("INSERT INTO subnets(id,subnet,mask,subnet_description,section_id,section_name) VALUES ({0},{1},{2},'{3}',{4},'{5}') ON DUPLICATE KEY UPDATE subnet={1},mask={2}".format(sub['id'],sub['subnet'],sub['mask'],sub['description'],sub['section_id'],sub['section_name']))
  db.commit()
 print "<DIV CLASS=z-frame>synced domains:{}, synced subnets:{}</DIV>".format(len(domains), len(subnets))
