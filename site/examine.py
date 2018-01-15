"""Module docstring.

HTML5 Ajax generic SDCP calls module

"""
__author__= "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"
__icon__ = 'images/icon-examine.png'

from .. import PackageContainer as PC

############################################ Examine ##############################################
#
# Examine Logs
#
def main(aWeb):
 if not aWeb.cookies.get('sdcp'):
  print "<SCRIPT>location.replace('index.cgi')</SCRIPT>"
  return
 upshost = PC.sdcp['upshost']
 print "<NAV><UL>"
 print "<LI CLASS='warning'><A CLASS=z-op DIV=div_content MSG='Clear Network Logs?' URL='sdcp.cgi?call=examine_clear'>Clear Logs</A></LI>"
 print "<LI><A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=examine_logs&ip=127.0.0.1>Logs</A></LI>"
 if upshost:
  print "<LI><A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=examine_ups>UPS</A></LI>"
 print "<LI><A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=dns_top>DNS</A></LI>"
 print "<LI><A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=dhcp_leases>DHCP</A></LI>"
 print "<LI><A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=examine_logs&ip={}>Services Logs</A></LI>".format(PC.sdcp['svcsrv'])
 print "<LI><A CLASS='z-op reload' DIV=main URL=sdcp.cgi?call=examine_main></A></LI>"
 print "</UL></NAV>"
 print "<SECTION CLASS=content ID=div_content></SECTION>"

#
#
#
def clear(aWeb):
 res_dns  = aWeb.rest_call(PC.dns['url'],'sdcp.rest.examine_clear_logs',{ 'logs':[PC.generic['logformat']]})['data']
 res_host = aWeb.rest_call("http://127.0.0.1/rest.cgi",'sdcp.rest.examine_clear_logs',{ 'logs':[PC.generic['logformat'],PC.sdcp['netlogs']]})['data']
 print "<ARTICLE>%s<BR>%s</ARTICLE>"%(res_host,res_dns)

#
# Internal Logs
#
def logs(aWeb):
 res = aWeb.rest_call("http://{}/rest.cgi".format(aWeb['ip']),'sdcp.rest.examine_get_logs',{'count':18,'logs':[PC.generic['logformat'],PC.sdcp['netlogs']]})['data']
 for file,logs in res['logs'].iteritems():
  print "<ARTICLE><P>%s</P><P CLASS='machine-text'>%s</P></ARTICLE>"%(file,"<BR>".join(logs))

#
# UPS graphs
#
def ups(aWeb):
 from ..tools.munin import widget_cols
 upshost,void,domain = PC.sdcp['upshost'].partition('.')
 print "<ARTICLE>"
 widget_cols([ "{1}/{0}.{1}/hw_apc_power".format(upshost,domain), "{1}/{0}.{1}/hw_apc_time".format(upshost,domain), "{1}/{0}.{1}/hw_apc_temp".format(upshost,domain) ])
 print "</ARTICLE>"
