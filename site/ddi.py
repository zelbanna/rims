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
 
 res = rest_call(PC.dhcp['url'],"sdcp.rest.{}_update_server".format(PC.dhcp['type']),{'entries':args})
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
   retvals = rest_call(PC.dns['url'],"sdcp.rest.{}_lookup".format(PC.dns['type']), dargs)
   a_id    = retvals.get('a_id','0')
   ptr_id  = retvals.get('ptr_id','0')

   retvals = rest_call(PC.ipam['url'],"sdcp.rest.{}_lookup".format(PC.ipam['type']),{'ip':ip, 'ipam_sub_id':row['ipam_sub_id']})
   ipam_id = retvals.get('ipam_id','0')
   print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>".format(row['id'],ip,name,dom,a_id,ptr_id,ipam_id)
   if not name == 'unknown':
    print "updating"
    uargs = { 'ip':ip, 'name':name, 'a_dom_id':dom, 'a_id':a_id, 'ptr_id':ptr_id }
    rest_call(PC.dns['url'],"sdcp.rest.{}_update".format(PC.dns['type']), uargs)
    retvals = rest_call(PC.dns['url'],"sdcp.rest.{}_lookup".format(PC.dns['type']), dargs)
    uargs = { 'ip':ip, 'ipam_id':ipam_id, 'ipam_sub_id':row['ipam_sub_id'], 'ptr_id':retvals.get('ptr_id','0'), 'fqdn':name + '.' + row['domain'] }
    rest_call(PC.ipam['url'],"sdcp.rest.{}_update".format(PC.ipam['type']),uargs)
    print str(retvals)
    db.do("UPDATE devices SET ipam_id = {}, a_id = {}, ptr_id = {}, ptr_dom_id = {}  WHERE id = {}".format(ipam_id, retvals.get('a_id','0'),retvals.get('ptr_id','0'), retvals.get('ptr_dom_id','NULL'), row['id']))
   print "</DIV></DIV>"
  db.commit()
 print "</DIV></DIV></DIV>"

#
#
#
def load_infra(aWeb):
 dns_domains  = rest_call(PC.dns['url'], "sdcp.rest.{}_domains".format(PC.dns['type']))
 ipam_subnets = rest_call(PC.ipam['url'],"sdcp.rest.{}_subnets".format(PC.ipam['type']))
 print "<DIV CLASS=z-frame>"
 with DB() as db:
  db.do("SELECT id,name FROM domains")
  sdcp_domains = db.get_rows_dict('id')
  for dom in dns_domains:
   add = sdcp_domains.pop(dom['id'],None)
   if not add:
    print "Added: {}".format(dom)
   db.do("INSERT INTO domains(id,name) VALUES ({0},'{1}') ON DUPLICATE KEY UPDATE name='{1}'".format(dom['id'],dom['name']))
  print "<SPAN>Domains - Inserted:{}, Remaining old:{}</SPAN><BR>".format(len(dns_domains),len(sdcp_domains))
  for dom,entry in sdcp_domains.iteritems():
   print "Delete {} -> {}<BR>".format(dom,entry)
   db.do("DELETE FROM domains WHERE id = '{}'".format(dom))
  db.do("SELECT id,subnet,section_name FROM subnets")
  sdcp_subnets = db.get_rows_dict('id')
  for sub in ipam_subnets:
   add = sdcp_subnets.pop(sub['id'],None)
   if not add:
    print "Added: {}".format(sub)
   db.do("INSERT INTO subnets(id,subnet,mask,subnet_description,section_id,section_name) VALUES ({0},{1},{2},'{3}',{4},'{5}') ON DUPLICATE KEY UPDATE subnet={1},mask={2}".format(sub['id'],sub['subnet'],sub['mask'],sub['description'],sub['section_id'],sub['section_name']))
  print "<SPAN>Subnets - Inserted:{}, Remaining old:{}</SPAN><BR>".format(len(ipam_subnets),len(sdcp_subnets))
  for sub,entry in sdcp_subnets.iteritems():
   print "Delete {} -> {}<BR>".format(sub,entry)
   db.do("DELETE FROM subnets WHERE id = '{}'".format(sub))
  db.commit()
 print "</DIV>"
#
#
#
def ipam_discrepancy(aWeb):
 ipam = rest_call(PC.ipam['url'],"sdcp.rest.{}_get_addresses".format(PC.ipam['type']))
 with DB() as db:
  db.do("SELECT devices.id, ip, INET_NTOA(ip) as ipasc, CONCAT(hostname,'.',domains.name) AS fqdn FROM devices LEFT JOIN domains ON domains.id = devices.a_dom_id ORDER BY ip")
  devs = db.get_rows_dict('ip')
 print "<DIV CLASS=z-frame>"
 print "<DIV CLASS=title>IPAM consistency</DIV>"
 print "<SPAN ID=span_ipam STYLE='font-size:9px;'>&nbsp;</SPAN>"
 print "<DIV CLASS=z-table STYLE='width:auto;'>"
 print "<DIV CLASS=tbody>"
 for row in ipam['addresses']:
  dev = devs.pop(int(row['ip']),None)
  if not dev or dev.get('fqdn') != row['fqdn']:
   print "<DIV CLASS=tr>"
   print "<!-- {} -->".format(row)
   print "<DIV CLASS=td>{}</DIV>".format(row['ipasc'])
   print "<DIV CLASS=td>{}</DIV>".format(row['fqdn'])
   print "<DIV CLASS=td>{}</DIV>".format(row['id'])
   print "<DIV CLASS=td>{}</DIV>".format(row['ipam_sub_id'])
   print "<DIV CLASS=td>{}</DIV>".format(row['description'])
   print "<DIV CLASS=td>&nbsp;"
   print "<A CLASS='z-op z-btn z-small-btn' DIV=span_ipam MSG='Are you sure?' URL='sdcp.cgi?call=ddi_ipam_remove&id={}'><IMG SRC=images/btn-remove.png></A>".format(row['id'])
   if row['fqdn']:
    hostname,_,domain = row['fqdn'].partition('.')
    print "<!-- {} -->".format(domain)
    print "<A CLASS='z-op z-btn z-small-btn' DIV=div_content_right URL='sdcp.cgi?call=device_new&ip={}&hostname={}&ipam_id={}&ipam_sub_id={}{}'><IMG SRC=images/btn-add.png></A>".format(row['ipasc'],hostname,row['id'],row['ipam_sub_id'],"&domain={}".format(domain) if domain else "")
   print "</DIV></DIV>"
 print "</DIV></DIV>"
 if len(devs) > 0:
  print "<DIV CLASS=title>Extra only in SDCP</DIV>"
  import sdcp.core.extras as EXT
  EXT.dict2table(devs)
 print "</DIV>"
 
#
#
#
def ipam_remove(aWeb):
 id = aWeb.get_value('id')
 res = rest_call(PC.ipam['url'],"sdcp.rest.{}_remove".format(PC.ipam['type']),{'ipam_id':id})
 print "Remove {} - Results:{}".format(id,res)
