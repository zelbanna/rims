"""Module docstring.

HTML5 Ajax DHCP calls module

"""
__author__= "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__= "Production"

from ..settings.dhcp import data as Settings
#
#
def update(aWeb):
 args = aWeb.rest_call("device_list_mac")
 print  aWeb.rest_generic(Settings['url'],"%s_update_server"%(Settings['type']),{'entries':args})

#
#
def leases(aWeb):
 from ..core import extras as EXT
 leases = aWeb.rest_generic(Settings['url'], "%s_leases"%(Settings['type']),{'type':aWeb['type']})
 print "<ARTICLE><P>%s Leases</P>"%(aWeb['type'].title())
 try: EXT.dict2table(leases['data'])
 except: pass
 print "</ARTICLE>"
