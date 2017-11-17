"""Module docstring.

HTML5 Ajax generic SDCP calls module

"""
__author__= "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__= "Production"

from sdcp import PackageContainer as PC

############################################ Examine ##############################################
#
# Examine Logs
#
def main(aWeb):
 if not aWeb.cookie.get('sdcp_id'):
  print "<SCRIPT>location.replace('index.cgi')</SCRIPT>"
  return
 upshost = PC.sdcp['upshost']
 print "<NAV>"
 print "<A CLASS='z-warning z-op' DIV=div_content MSG='Clear Network Logs?' URL='sdcp.cgi?call=examine_clear'>Clear Logs</A>"
 print "<A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=examine_logs&ip=127.0.0.1>Logs</A>"
 if upshost:
  print "<A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=examine_ups>UPS</A>"
 print "<A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=dns_top>DNS</A>"
 print "<A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=dhcp_leases>DHCP</A>"
 print "<A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=examine_logs&ip={}>Services Logs</A>".format(PC.sdcp['svcsrv'])
 print "<A CLASS='z-reload z-op' DIV=main URL=sdcp.cgi?call=examine_main></A>"
 print "</NAV>"
 print "<SECTION CLASS=content ID=div_content></SECTION>"

#
#
#
def clear(aWeb):
 from sdcp.core.rest import call as rest_call
 res_dns  = rest_call(PC.dns['url'],'sdcp.rest.examine_clear_logs',{ 'logs':[PC.generic['logformat']]})
 res_host = rest_call("http://127.0.0.1/rest.cgi",'sdcp.rest.examine_clear_logs',{ 'logs':[PC.generic['logformat'],PC.sdcp['netlogs']]})
 print "<ARTICLE>{}<BR>{}</ARTICLE>".format(res_host,res_dns)

#
# Internal Logs
#
def logs(aWeb):
 from sdcp.core.rest import call as rest_call
 res = rest_call("http://{}/rest.cgi".format(aWeb['ip']),'sdcp.rest.examine_get_logs',{'count':18,'logs':[PC.generic['logformat'],PC.sdcp['netlogs']]})
 for file,logs in res['logs'].iteritems():
  print "<ARTICLE><P>%s</P><P CLASS='machine-text'>%s</P></ARTICLE>"%(file,"<BR>".join(logs))

#
# UPS graphs
#
def ups(aWeb):
 from sdcp.tools.munin import widget_cols
 upshost,void,domain = PC.sdcp['upshost'].partition('.')
 print "<ARTICLE>"
 widget_cols([ "{1}/{0}.{1}/hw_apc_power".format(upshost,domain), "{1}/{0}.{1}/hw_apc_time".format(upshost,domain), "{1}/{0}.{1}/hw_apc_temp".format(upshost,domain) ])
 print "</ARTICLE>"
