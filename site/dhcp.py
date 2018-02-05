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
 dhcp = aWeb.rest_call("settings_type",{'type':'dhcp'})['data']
 args = aWeb.rest_call("device_list_mac")
 print  aWeb.rest_generic(dhcp['url']['value'],"%s_update_server"%(dhcp['type']['value']),{'entries':args,'settings':dhcp})

#
#
def leases(aWeb):
 from ..core import extras as EXT
 dhcp   = aWeb.rest_call("settings_type",{'type':'dhcp'})['data']
 leases = aWeb.rest_generic(dhcp['url']['value'], "{}_leases"%(dhcp['type']['value']),{'type':aWeb['type'],'settings':dhcp})
 print "<ARTICLE><P>%s Leases</P>"%(aWeb['type'].title())
 try: EXT.dict2table(leases['data'])
 except: pass
 print "</ARTICLE>"
