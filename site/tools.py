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
 print "<A CLASS='z-op z-right' DIV=div_content URL='sdcp.cgi?call=resources_view&type=bookmark'>Bookmarks</A>"
 print "<A CLASS='z-op z-right' DIV=div_content URL='sdcp.cgi?call=resources_view&type=demo'>Demos</A>"
 print "<A CLASS='z-op z-right' DIV=div_content URL='sdcp.cgi?call=resources_view&type=tool'>Tools</A>"
 print "</DIV>"
 print "<DIV CLASS=z-content ID=div_content></DIV>"

def list(aWeb):
 print "<DIV CLASS=z-content-left ID=div_content_left>"
 print "<DIV CLASS=z-frame><DIV CLASS=title>Tools</DIV>"
 print "<DIV CLASS=z-table><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right SPIN=true URL='sdcp.cgi?call=dhcp_update'>DHCP - Update Server</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right SPIN=true URL='sdcp.cgi?call=dns_load'>DNS - Load Cache</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right SPIN=true URL='sdcp.cgi?call=dns_cleanup'>DNS - Backend Cleanup</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right SPIN=true URL='sdcp.cgi?call=dns_discrepancy'>DNS - Backend Discrepancy</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right SPIN=true URL='sdcp.cgi?call=ipam_load'>Load IPAM - Load Cache</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right SPIN=true URL='sdcp.cgi?call=ipam_discrepancy'>IPAM - Backend Discrepancy</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right SPIN=true URL='sdcp.cgi?call=rack_rackinfo'>Device - View Rackinfo Table</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right           URL='sdcp.cgi?call=tools_sync_devicetypes'>Devices - Load New Types</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right           URL='sdcp.cgi?call=device_mac_sync'>Find MAC Info</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op TARGET=_blank                  HREF='sdcp.cgi?call=tools_db_table'>DB - Dump Device Table to JSON</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right           URL='sdcp.cgi?call=tools_db_structure'>DB - View Structure</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op TARGET=_blank                  HREF='sdcp.pdf'>DB - View relational diagram</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right SPIN=true URL='sdcp.cgi?call=tools_install&host=127.0.0.1'>Reinstall Host</A></DIV></DIV>"
 from sdcp import PackageContainer as PC
 if PC.sdcp['svcsrv']:
  print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right  URL='sdcp.cgi?call=tools_install&host={}'>Reinstall SVC</A></DIV></DIV>".format(PC.sdcp['svcsrv'])
 print "</DIV></DIV></DIV></DIV>"
 print "<DIV CLASS=z-content-right ID=div_content_right></DIV>"

#
#
def db_structure(aWeb):
 from sdcp.core.mysql import dump
 print "<DIV CLASS=z-logs><PRE>"
 print dump({'mode':'structure'})['output']
 print "</PRE></DIV>"

#
#
def db_table(aWeb):
 from json import dumps
 from sdcp.rest.tools import db_table
 print "<PRE>{}</PRE>".format(dumps(db_table({'table':aWeb.get('table','devices'),'columns':aWeb.get('columns','*')})['db'], indent=4, sort_keys=True))

#
#
def sync_devicetypes(aWeb):
 from sdcp.core import extras as EXT
 from sdcp.rest.tools import sync_devicetypes as rest_sync_devicetypes
 res = rest_sync_devicetypes(None)
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
 
