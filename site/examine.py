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
 print "<NAV><UL>"
 print "<LI CLASS='warning'><A CLASS=z-op DIV=div_content MSG='Clear Network Logs?' URL='sdcp.cgi?call=examine_clear&ip=%s'>Clear Logs</A></LI>"%",".join(PC.generic['hosts'])
 print "<LI CLASS='dropdown'><A>Logs</A><DIV CLASS='dropdown-content'>"
 for host in PC.generic['hosts']:
  print "<A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=examine_logs&ip=%s>%s</A>"%(host,host)
 print "</DIV></LI>"
 if PC.generic['upshost']:
  print "<LI><A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=examine_ups>UPS</A></LI>"
 print "<LI><A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=dns_top>DNS</A></LI>"
 print "<LI CLASS='dropdown'><A>DHCP</A><DIV CLASS='dropdown-content'>"
 print "<A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=dhcp_leases&type=active>Active</A>"
 print "<A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=dhcp_leases&type=free>Free</A>"
 print "</DIV></LI>"
 print "<LI><A CLASS='z-op reload' DIV=main URL=sdcp.cgi?call=examine_main></A></LI>"
 print "</UL></NAV>"
 print "<SECTION CLASS=content ID=div_content></SECTION>"

#
#
#
def clear(aWeb):
 hosts = aWeb['ip'].split(',')
 print "<ARTICLE>"
 for host in hosts:
  res = aWeb.rest_generic("http://%s/rest.cgi"%host,'sdcp.rest.sdcp_logs_clear',{ 'logs':[PC.generic['logformat'],PC.generic['netlogs']]})
  print "%s: %s<BR>"%(host, res)
 print "</ARTICLE>"

#
# Internal Logs
#
def logs(aWeb):
 res = aWeb.rest_generic("http://%s/rest.cgi"%aWeb['ip'],'sdcp.rest.sdcp_logs_get',{'count':18,'logs':[PC.generic['logformat'],PC.generic['netlogs']]})
 for file,logs in res.iteritems():
  print "<ARTICLE><P>%s</P><P CLASS='machine-text'>%s</P></ARTICLE>"%(file,"<BR>".join(logs))

#
# UPS graphs
#
def ups(aWeb):
 from ..tools.munin import widget_cols
 upshost,void,domain = PC.generic['upshost'].partition('.')
 print "<ARTICLE>"
 widget_cols([ "{1}/{0}.{1}/hw_apc_power".format(upshost,domain), "{1}/{0}.{1}/hw_apc_time".format(upshost,domain), "{1}/{0}.{1}/hw_apc_temp".format(upshost,domain) ])
 print "</ARTICLE>"
