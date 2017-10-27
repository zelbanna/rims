"""Module docstring.

Ajax DHCP calls module

"""
__author__= "Zacharias El Banna"                     
__version__ = "17.10.4"
__status__= "Production"

import sdcp.PackageContainer as PC
from sdcp.core.dbase import DB
from sdcp.core.rest import call as rest_call
import sdcp.core.genlib as GL

#
#
#
def update(aWeb):
 with DB() as db:
  db.do("SELECT devices.id, hostname, INET_NTOA(ip) as ipasc, domains.name as domain, mac, ipam_sub_id from devices JOIN domains ON domains.id = devices.a_dom_id WHERE NOT  mac = 0 ORDER BY ip")
  rows = db.get_rows()
 args = []
 for row in rows:
  args.append({'ip':row['ipasc'],'fqdn':"{}.{}".format(row['hostname'],row['domain']),'mac':GL.int2mac(row['mac']),'id':row['id'],'subnet_id':row['ipam_sub_id']})
 
 res = rest_call(PC.dhcp['url'],"sdcp.rest.{}_update_server".format(PC.dhcp['type']),{'entries':args})
 print res
