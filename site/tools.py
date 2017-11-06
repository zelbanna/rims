"""Module docstring.

Ajax Tools calls module

"""
__author__= "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__= "Production"

############################################ Options ##############################################
#
def main(aWeb):
 if not aWeb.cookie.get('sdcp_id'):
  print "<SCRIPT>location.replace('index.cgi')</SCRIPT>"
  return
 print "<DIV CLASS=z-navbar ID=div_navbar>"
 print "<A CLASS=z-op           DIV=div_content URL='sdcp.cgi?call=resources_list'>Resources</A>"
 print "<A CLASS=z-op           DIV=div_content URL='sdcp.cgi?call=tools_list'>Options</A>"
 print "<A CLASS='z-op z-right' DIV=div_content URL='sdcp.cgi?call=resources_list_type&type=bookmark'>Bookmarks</A>"
 print "<A CLASS='z-op z-right' DIV=div_content URL='sdcp.cgi?call=resources_list_type&type=demo'>Demos</A>"
 print "<A CLASS='z-op z-right' DIV=div_content URL='sdcp.cgi?call=resources_list_type&type=tool'>Tools</A>"
 print "</DIV>"
 print "<DIV CLASS=z-content ID=div_content></DIV>"

def list(aWeb):
 print "<DIV CLASS=z-content-left ID=div_content_left>"
 print "<DIV CLASS=z-frame><DIV CLASS=title>Tools</DIV>"
 print "<DIV CLASS=z-table><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right SPIN=true URL='sdcp.cgi?call=dhcp_update'>Update DHCP Server</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right SPIN=true URL='sdcp.cgi?call=dns_load'>Load DNS Cache</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right SPIN=true URL='sdcp.cgi?call=dns_cleanup'>DNS Backend Cleanup</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right           URL='sdcp.cgi?call=dns_discrepancy'>DNS  Backend Discrepancy</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right SPIN=true URL='sdcp.cgi?call=ipam_load'>Load IPAM Cache</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right           URL='sdcp.cgi?call=ipam_discrepancy'>IPAM Backend Discrepancy</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op TARGET=_blank                  HREF='sdcp.cgi?call=device_dump_db'>Dump Device Table to JSON</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right SPIN=true URL='sdcp.cgi?call=rack_rackinfo'>View Rackinfo Table</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right           URL='sdcp.cgi?call=device_mac_sync'>Find MAC Info</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right           URL='sdcp.cgi?call=tools_mysql'>Dump DB Structure</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right           URL='sdcp.cgi?call=tools_sync_types'>Load New Types</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right           URL='sdcp.cgi?call=tools_install&host=127.0.0.1'>Reinstall Host</A></DIV></DIV>"
 from sdcp import PackageContainer as PC
 if PC.sdcp['svcsrv']:
  print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right  URL='sdcp.cgi?call=tools_install&host={}'>Reinstall SVC</A></DIV></DIV>".format(PC.sdcp['svcsrv'])
 print "</DIV></DIV></DIV></DIV>"
 print "<DIV CLASS=z-content-right ID=div_content_right></DIV>"

#
#
def mysql(aWeb):
 from sdcp.tools.mysql_dump import dump
 print "<DIV CLASS=z-logs>"
 for line in dump().split('\n'):
  if not line[:2] in [ '/*','--']:
   print line + "<BR>"
 print "</DIV>"

#
#
def sync_types(aWeb):
 from sdcp.core import extras as EXT
 from sdcp.rest.device import sync_types as rest_sync_types
 res = rest_sync_types(None)
 print "<DIV CLASS=z-frame>"
 EXT.dict2table(res['types'])
 print "</DIV>"
#
#
def install(aWeb):
 from sdcp.core.rest import call as rest_call
 from json import dumps
 print "<DIV CLASS=z-frame><PRE>"
 res = rest_call("http://{}/rest.cgi".format(aWeb['host']),"sdcp.rest.tools_installation")
 print dumps(res,indent=4)
 print "</PRE></DIV>"
