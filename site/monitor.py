"""Module docstring.

HTML5 Ajax generic SDCP calls module

"""
__author__= "Zacharias El Banna"
__version__ = "18.03.07GA"
__status__ = "Production"
__icon__ = 'images/icon-examine.png'
__type__ = 'menuitem'

############################################ Monitor ##############################################
#
# Monitor
#
def main(aWeb):
 if not aWeb.cookies.get('sdcp'):
  print "<SCRIPT>location.replace('index.cgi')</SCRIPT>"
  return
 monitors = aWeb.rest_call("resources_list",{'type':'monitor','view_public':True})['data']
 hosts    = aWeb.rest_call("settings_list",{'section':'node'})['data']
 print "<NAV><UL>"
 print "<LI CLASS='warning'><A CLASS=z-op DIV=div_content MSG='Clear Network Logs?' URL='sdcp.cgi?call=monitor_clear&ip=%s'>Clear Logs</A></LI>"
 print "<LI CLASS='dropdown'><A>Logs</A><DIV CLASS='dropdown-content'>"
 for host in hosts:
  print "<A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=monitor_logs&host=%s>%s</A>"%(host['parameter'],host['parameter'])
 print "</DIV></LI>"
 print "<LI><A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=dns_top>DNS</A></LI>"
 print "<LI CLASS='dropdown'><A>DHCP</A><DIV CLASS='dropdown-content'>"
 print "<A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=dhcp_leases&type=active>Active</A>"
 print "<A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=dhcp_leases&type=free>Free</A>"
 print "</DIV></LI>"
 for mon in monitors:
  print "<LI><A CLASS=z-op DIV=div_content URL='%s'>%s</A></LI>"%(mon['href'],mon['title'])
 print "<LI><A CLASS='z-op reload' DIV=main URL=sdcp.cgi?call=monitor_main></A></LI>"
 print "</UL></NAV>"
 print "<SECTION CLASS=content ID=div_content></SECTION>"

#
#
#
def clear(aWeb):
 hosts = aWeb.rest_call("settings_list",{'section':'node'})['data']
 print "<ARTICLE>"
 for host in hosts:
  output = aWeb.rest_full(host['value'],'tools_logs_clear')
  print "%s: %s<BR>"%(host['parameter'], output['data'])
 print "</ARTICLE>"

#
# Internal Logs
#
def logs(aWeb):
 res = aWeb.rest_call('tools_logs_get',{'node':aWeb['host'],'count':18})
 res.pop('xist',None)
 print "<ARTICLE>"
 for file,logs in res.iteritems():
  print "<P>%s</P><P CLASS='machine-text'>%s</P>"%(file,"<BR>".join(logs))
 print "</ARTICLE>"

#
# UPS graphs
#
def ups(aWeb):
 print "<ARTICLE>"
 if aWeb.get('host'):
  from ..tools.munin import widget_cols
  upshost,void,domain = aWeb['host'].partition('.')
  widget_cols([ "{1}/{0}.{1}/hw_apc_power".format(upshost,domain), "{1}/{0}.{1}/hw_apc_time".format(upshost,domain), "{1}/{0}.{1}/hw_apc_temp".format(upshost,domain) ])
 else:
  print "Missing 'host' var" 
 print "</ARTICLE>"
