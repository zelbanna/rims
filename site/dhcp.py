"""Module docstring.

HTML5 Ajax DHCP calls module

"""
__author__= "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__= "Production"

from .. import PackageContainer as PC

#
#
#
def update(aWeb):
 from ..core.dbase import DB
 from ..core import genlib as GL
 with DB() as db:
  db.do("SELECT devices.id, hostname, INET_NTOA(ip) as ipasc, domains.name as domain, mac, subnet_id from devices JOIN domains ON domains.id = devices.a_dom_id WHERE NOT  mac = 0 ORDER BY ip")
  rows = db.get_rows()
 args = []
 for row in rows:
  args.append({'ip':row['ipasc'],'fqdn':"{}.{}".format(row['hostname'],row['domain']),'mac':GL.int2mac(row['mac']),'id':row['id'],'subnet_id':row['subnet_id']})
 print aWeb.rest_call(PC.dhcp['url'],"sdcp.rest.{}_update_server".format(PC.dhcp['type']),{'entries':args})['data']

#
#
#
def leases(aWeb):
 from ..core import extras as EXT
 dhcp = aWeb.rest_call(PC.dhcp['url'], "sdcp.rest.{}_leases".format(PC.dhcp['type']),{'type':aWeb['type']})['data']
 print "<ARTICLE><P>%s Leases</P>"%(aWeb['type'].title())
 try: EXT.dict2table(dhcp['data'])
 except: pass
 print "</ARTICLE>"
