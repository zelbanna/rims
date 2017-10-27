"""Module docstring.

Ajax Tools calls module

"""
__author__= "Zacharias El Banna"
__version__ = "17.10.4"
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
 print "<DIV CLASS=z-content ID=div_content>"
 print "</DIV>"

def list(aWeb):
 print "<DIV CLASS=z-content-left ID=div_content_left>"
 print "<DIV CLASS=z-frame><DIV CLASS=title>Tools</DIV>"
 print "<DIV CLASS=z-table><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right SPIN=true URL='sdcp.cgi?call=dhcp_update'>Update DHCP Server</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right SPIN=true URL='sdcp.cgi?call=dns_load'>Load DNS Cache</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right           URL='sdcp.cgi?call=dns_discrepancy'>DNS  Backend Discrepancy</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right SPIN=true URL='sdcp.cgi?call=ipam_load'>Load IPAM Cache</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right           URL='sdcp.cgi?call=ipam_discrepancy'>IPAM Backend Discrepancy</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op TARGET=_blank                  HREF='sdcp.cgi?call=device_dump_db'>Dump Device Table to JSON</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right SPIN=true URL='sdcp.cgi?call=rack_rackinfo'>View Rackinfo Table</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right           URL='sdcp.cgi?call=device_mac_sync'>Find MAC Info</A></DIV></DIV>"
 print "</DIV></DIV></DIV></DIV>"
 print "<DIV CLASS=z-content-right ID=div_content_right></DIV>"
