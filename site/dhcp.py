"""Module docstring.

HTML5 Ajax DHCP calls module

"""
__author__= "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__= "Production"

from .. import PackageContainer as PC
#
#
def update(aWeb):
 args = aWeb.rest("device_list_mac")
 print  aWeb.rest_generic(PC.dhcp['url'],"sdcp.rest.%s_update_server"%(PC.dhcp['type']),{'entries':args})

#
#
def leases(aWeb):
 from ..core import extras as EXT
 dhcp = aWeb.rest_generic(PC.dhcp['url'], "sdcp.rest.{}_leases".format(PC.dhcp['type']),{'type':aWeb['type']})
 print "<ARTICLE><P>%s Leases</P>"%(aWeb['type'].title())
 try: EXT.dict2table(dhcp['data'])
 except: pass
 print "</ARTICLE>"
