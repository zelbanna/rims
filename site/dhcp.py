"""Module docstring.

HTML5 Ajax DHCP calls module

"""
__author__= "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__= "Production"

from .. import SettingsContainer as SC
#
#
def update(aWeb):
 args = aWeb.rest_call("device_list_mac")
 print  aWeb.rest_generic(SC.dhcp['url'],"%s_update_server"%(SC.dhcp['type']),{'entries':args})

#
#
def leases(aWeb):
 from ..core import extras as EXT
 leases = aWeb.rest_generic(SC.dhcp['url'], "%s_leases"%(SC.dhcp['type']),{'type':aWeb['type']})
 print "<ARTICLE><P>%s Leases</P>"%(aWeb['type'].title())
 try: EXT.dict2table(leases['data'])
 except: pass
 print "</ARTICLE>"
