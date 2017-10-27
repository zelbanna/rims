"""Module docstring.

Ajax IPAM calls module

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
def load(aWeb):
 ipam_subnets = rest_call(PC.ipam['url'],"sdcp.rest.{}_subnets".format(PC.ipam['type']))
 print "<DIV CLASS=z-frame>"
 with DB() as db:
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
def discrepancy(aWeb):
 ipam = rest_call(PC.ipam['url'],"sdcp.rest.{}_get_addresses".format(PC.ipam['type']))
 with DB() as db:
  db.do("SELECT devices.id, ip, INET_NTOA(ip) as ipasc, CONCAT(hostname,'.',domains.name) AS fqdn FROM devices LEFT JOIN domains ON domains.id = devices.a_dom_id ORDER BY ip")
  devs = db.get_rows_dict('ip')
 print "<DIV CLASS=z-frame><DIV CLASS=title>IPAM consistency</DIV><SPAN ID=span_ipam STYLE='font-size:9px;'>&nbsp;</SPAN><DIV CLASS=z-table STYLE='width:auto;'><DIV CLASS=tbody>"
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
   print "<A CLASS='z-op z-btn z-small-btn' DIV=span_ipam MSG='Are you sure?' URL='sdcp.cgi?call=ipam_remove&id={}'><IMG SRC=images/btn-remove.png></A>".format(row['id'])
   if row['fqdn']:
    hostname,_,domain = row['fqdn'].partition('.')
    print "<!-- {} -->".format(domain)
    print "<A CLASS='z-op z-btn z-small-btn' DIV=div_content_right URL='sdcp.cgi?call=device_new&ip={}&hostname={}&ipam_id={}&ipam_sub_id={}{}'><IMG SRC=images/btn-add.png></A>".format(row['ipasc'],hostname,row['id'],row['ipam_sub_id'],"&domain={}".format(domain) if domain else "")
   print "</DIV></DIV>"
 print "</DIV></DIV>"
 if len(devs) > 0:
  print "<DIV CLASS=title>Extra only in SDCP ({})</DIV>".format(len(devs))
 print "</DIV>"


#
#
#
def remove(aWeb):
 id = aWeb.get_value('id')
 res = rest_call(PC.ipam['url'],"sdcp.rest.{}_remove".format(PC.ipam['type']),{'ipam_id':id})
 print "Remove {} - Results:{}".format(id,res)
