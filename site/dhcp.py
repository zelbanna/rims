"""Module docstring.

HTML5 Ajax DHCP calls module

"""
__author__= "Zacharias El Banna"
__version__ = "18.02.09GA"
__status__= "Production"

#
#
def update(aWeb):
 print "<ARTICLE>%s</ARTICLE>"%(aWeb.rest_call("sdcpdhcp_update_server"))

#
#
def leases(aWeb):
 from ..core import extras as EXT
 leases = aWeb.rest_call("sdcpdhcp_leases",{'type':aWeb['type']})
 print "<ARTICLE><P>%s Leases</P>"%(aWeb['type'].title())
 try: EXT.dict2table(leases['data'])
 except: pass
 print "</ARTICLE>"
