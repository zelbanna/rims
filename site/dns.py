"""Module docstring.

Ajax DNS calls module

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
 dns_domains  = rest_call(PC.dns['url'], "sdcp.rest.{}_domains".format(PC.dns['type']))
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
  db.commit()
 print "</DIV>"

#
#
#
def discrepancy(aWeb):
 dns = rest_call(PC.dns['url'],"sdcp.rest.{}_get_records".format(PC.dns['type']),{'type':'A'})
 with DB() as db:
  db.do("SELECT devices.id, ip, INET_NTOA(ip) as ipasc, hostname, domains.name as domain AS fqdn FROM devices LEFT JOIN domains ON domains.id = devices.a_dom_id ORDER BY ip")
  devs = db.get_rows()
 print "<DIV CLASS=z-frame>DIV CLASS=title>DNS consistency</DIV>SPAN ID=span_dns STYLE='font-size:9px;'>&nbsp;</SPAN>"
 # print "<DIV CLASS=z-table STYLE='width:auto;'><DIV CLASS=tbody>"
 import sdcp.core.extras as EXT
 EXT.dict2table(devs)
 print "</DIV>"

#
# DNS top
#
def top(aWeb):
 import sdcp.core.extras as EXT
 dnstop = rest_call(PC.dns['url'], "sdcp.rest.{}_top".format(PC.dns['type']), {'count':20})
 print "<DIV CLASS=z-frame STYLE='float:left; width:49%;'><DIV CLASS=title>Top looked up FQDN</DIV>"
 EXT.dict2table(dnstop['top'])
 print "</DIV>"
 print "<DIV CLASS=z-frame STYLE='float:left; width:49%;'><DIV CLASS=title>Top looked up FQDN per Client</DIV>"
 EXT.dict2table(dnstop['who'])
 print "</DIV>"

#
# Cleanup duplicate entries
#
def cleanup(aWeb):
 dnsclean = rest_call(PC.dns['url'], "sdcp.rest.{}_cleanup".format(PC.dns['type']))
 print "<DIV CLASS=z-frame><DIV CLASS=title>Cleanup</DIV>"
 xist = len(dnsclean['removed'])
 if xist > 0:
  import sdcp.core.extras as EXT
  EXT.dict2table(dnsclean['removed'])
 print "</DIV>"
