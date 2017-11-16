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
 print "<nav>"
 print "<A CLASS=z-op           DIV=div_content URL='sdcp.cgi?call=resources_list'>Resources</A>"
 print "<A CLASS=z-op           DIV=div_content URL='sdcp.cgi?call=tools_list'>Options</A>"
 print "<A CLASS='z-op z-right' DIV=div_content URL='sdcp.cgi?call=tools_rest_main'>REST</A>"
 print "<A CLASS='z-op z-right' DIV=div_content URL='sdcp.cgi?call=resources_view&type=tool'>Tools</A>"
 print "<A CLASS='z-op z-right' DIV=div_content URL='sdcp.cgi?call=resources_view&type=demo'>Demos</A>"
 print "<A CLASS='z-op z-right' DIV=div_content URL='sdcp.cgi?call=resources_view&type=bookmark'>Bookmarks</A>"
 print "</nav>"
 print "<DIV CLASS=z-content ID=div_content></DIV>"

def list(aWeb):
 from sdcp import PackageContainer as PC
 print "<DIV CLASS=z-content-left ID=div_content_left>"
 print "<DIV CLASS=z-frame><DIV CLASS=title>Tools</DIV>"
 print "<DIV CLASS=z-table><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right SPIN=true URL='sdcp.cgi?call=dhcp_update'>DHCP - Update Server</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right SPIN=true URL='sdcp.cgi?call=dns_load'>DNS - Load Cache</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right SPIN=true URL='sdcp.cgi?call=rack_rackinfo'>Device - View Rackinfo Table</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right           URL='sdcp.cgi?call=tools_sync_devicetypes'>Devices - Load New Types</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right           URL='sdcp.cgi?call=device_mac_sync'>Find MAC Info</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op TARGET=_blank                  HREF='sdcp.cgi?call=tools_db_table'>DB - Dump Device Table to JSON</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right           URL='sdcp.cgi?call=tools_db_structure'>DB - View Structure</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op TARGET=_blank                  HREF='sdcp.pdf'>DB - View relational diagram</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right SPIN=true URL='sdcp.cgi?call=tools_install&host=127.0.0.1'>Reinstall Host</A></DIV></DIV>"
 if PC.sdcp['svcsrv']:
  print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right  URL='sdcp.cgi?call=tools_install&host={}'>Reinstall SVC</A></DIV></DIV>".format(PC.sdcp['svcsrv'])
 print "</DIV></DIV></DIV></DIV>"
 print "<DIV CLASS=z-content-right ID=div_content_right></DIV>"

#
#
def db_structure(aWeb):
 from sdcp.core.mysql import dump
 print "<DIV CLASS=z-logs>"
 print "<BR>".join(dump({'mode':'structure'})['output'])
 print "</DIV>"

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

#
#
def test_sleep(aWeb):
 from time import sleep
 sleep(int(aWeb['time']))
 print "Done"

#
#
def rest_main(aWeb):
 from sdcp import PackageContainer as PC
 print "<DIV CLASS=z-frame><FORM ID=frm_sdcp_rest>"
 print "<H3> REST API inspection</H3>"
 print "Choose host and enter API:<SELECT style='overflow: visible; width:auto; height:22px;' NAME=sdcp_host>"
 print "<OPTION VALUE=127.0.0.1>Local Host</A>"
 if PC.sdcp['svcsrv']:
  print "<OPTION VALUE={0}>Service Host</OPTION>".format(PC.sdcp['svcsrv'])
 print "</SELECT> <INPUT style='width:520px;' TYPE=TEXT NAME=sdcp_api><BR>"
 print "Call 'Method': <SELECT style='overflow: visible; width:70px; height:22px;' NAME=sdcp_method>"
 for method in ['GET','POST','DELETE','PUT']:
  print "<OPTION VALUE={0}>{0}</OPTION>".format(method)
 print "</SELECT>"
 print aWeb.button('start',  DIV='div_rest_info', URL='sdcp.cgi?call=tools_rest_execute', FRM='frm_sdcp_rest')
 print aWeb.button('remove', DIV='div_rest_info', OP='empty', TITLE='Clear results view')
 print "<BR>Arguments/Body<BR><TEXTAREA style='width:100%; height:100px;' NAME=sdcp_args></TEXTAREA>"
 print "</FORM>"
 print "</DIV>"
 print "<DIV ID=div_rest_info></DIV>"

#
#
def rest_execute(aWeb):
 from sdcp.core.rest import call as rest_call, RestException
 from json import loads,dumps
 try:    arguments = loads(aWeb['sdcp_args'])
 except: arguments = None
 print "<DIV CLASS=z-frame>"
 try:
  ret = rest_call("http://{}/rest.cgi".format(aWeb['sdcp_host']),aWeb['sdcp_api'],arguments,aWeb['sdcp_method'])
  print "<DIV CLASS=z-border>"
  output = dumps(ret,indent=4, sort_keys=True)
  print "<PRE style='margin:0px;'>{}</PRE>".format(output)
 except RestException,re:
  data = re.get()
  data.pop('res',None)
  print "<DIV CLASS=z-table style='width:100%;'><DIV CLASS=tbody>"
  for key in data.keys():
   print "<DIV CLASS=tr><DIV CLASS=td style='width:100px'>{}</DIV><DIV CLASS=td>{}</DIV></DIV>".format(key.upper(),data[key])
  print "</DIV></DIV>"
 print "</DIV>"
