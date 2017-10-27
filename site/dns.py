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
def dns_discrepancy(aWeb):
 dns = rest_call(PC.dns['url'],"sdcp.rest.{}_get_records".format(PC.dns['type']),{'type':'A'})
 # print "<DIV CLASS=z-frame><DIV CLASS=title>IPAM consistency</DIV><SPAN ID=span_ipam STYLE='font-size:9px;'>&nbsp;</SPAN><DIV CLASS=z-table STYLE='width:auto;'><DIV CLASS=tbody>"

 print "<DIV CLASS=z-frame>"
 import sdcp.core.extras as EXT
 EXT.dict2table(dns['records'])
 print "</DIV>"
