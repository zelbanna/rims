"""Module docstring.

HTML5 Ajax Tools calls module

"""
__author__= "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__= "Production"
__icon__ = 'images/icon-config.png'

############################################ Options ##############################################
#
def main(aWeb):
 if not aWeb.cookies.get('sdcp'):
  print "<SCRIPT>location.replace('index.cgi')</SCRIPT>"
  return
 from .. import PackageContainer as PC
 print "<NAV><UL>"
 print "<LI><A CLASS=z-op           DIV=div_content URL='sdcp.cgi?call=resources_list'>Resources</A></LI>"
 print "<LI CLASS='dropdown'><A>Options</A><DIV CLASS='dropdown-content'>"
 print "<A CLASS=z-op DIV=div_content SPIN=true URL='sdcp.cgi?call=dhcp_update'>DHCP - Update Server</A>"
 print "<A CLASS=z-op DIV=div_content SPIN=true URL='sdcp.cgi?call=dns_load'>DNS - Load Cache</A>"
 print "<A CLASS=z-op DIV=div_content SPIN=true URL='sdcp.cgi?call=device_mac_sync'>Find MAC Info</A>"
 print "<A CLASS=z-op TARGET=_blank            HREF='sdcp.cgi?call=tools_db_table'>DB - Dump Device Table to JSON</A>"
 print "<A CLASS=z-op DIV=div_content           URL='sdcp.cgi?call=tools_db_structure'>DB - View Structure</A>"
 print "<A CLASS=z-op TARGET=_blank            HREF='sdcp.pdf'>DB - View relational diagram</A>"
 print "<A CLASS=z-op DIV=div_content SPIN=true URL='sdcp.cgi?call=tools_install&host=127.0.0.1'>Reinstall Host</A>"
 if PC.sdcp['svcsrv']:
  print "<A CLASS=z-op DIV=div_content SPIN=true URL='sdcp.cgi?call=tools_install&host={}'>Reinstall SVC</A>".format(PC.sdcp['svcsrv'])
 print "<A CLASS=z-op DIV=div_content            URL='sdcp.cgi?call=tools_test_rest'>Test</A>"
 print "</DIV></LI>"
 print "<LI CLASS='right'><A CLASS='z-op' DIV=div_content URL='sdcp.cgi?call=tools_rest_main'>REST</A></LI>"
 print "<LI CLASS='right'><A CLASS='z-op' DIV=div_content URL='sdcp.cgi?call=resources_view&type=tool'>Tools</A></LI>"
 print "<LI CLASS='right'><A CLASS='z-op' DIV=div_content URL='sdcp.cgi?call=resources_view&type=demo'>Demos</A></LI>"
 print "<LI CLASS='right'><A CLASS='z-op' DIV=div_content URL='sdcp.cgi?call=resources_view&type=bookmark'>Bookmarks</A></LI>"
 print "</UL></NAV>"
 print "<SECTION CLASS=content ID=div_content></SECTION>"

#
#
def db_structure(aWeb):
 from ..core.mysql import dump
 print "<ARTICLE><P>Database Structure</A>"
 print "<P CLASS='machine-text'>"
 print "<BR>".join(dump({'mode':'structure'})['output'])
 print "</P></ARTICLE>"

#
#
def db_table(aWeb):
 from json import dumps
 from ..rest.tools import db_table
 print "<PRE>{}</PRE>".format(dumps(db_table({'table':aWeb.get('table','devices'),'columns':aWeb.get('columns','*')})['db'], indent=4, sort_keys=True))

#
#
def install(aWeb):
 from json import dumps
 print "<ARTICLE><PRE>%s</PRE></ARTICLE"%dumps(aWeb.rest_call("http://{}/rest.cgi".format(aWeb['host']),"sdcp.rest.tools_installation")['data'],indent = 4)

#
#
def test_sleep(aWeb):
 from time import sleep
 sleep(int(aWeb['time']))
 print "Done"

#
#
def test_rest(aWeb):
 res = aWeb.rest_call("http://127.0.0.1/rest.cgi","tools_test")
 print res

#
#
def rest_main(aWeb):
 from .. import PackageContainer as PC
 print "<ARTICLE><P>REST API inspection</P>"
 print "<FORM ID=frm_rest>"
 print "Choose host and enter API:<SELECT STYLE='height:22px;' NAME=host>"
 print "<OPTION VALUE=127.0.0.1>Local Host</A>"
 if PC.sdcp['svcsrv']:
  print "<OPTION VALUE={0}>Service Host</OPTION>".format(PC.sdcp['svcsrv'])
 print "</SELECT> <INPUT CLASS='white' STYLE='width:500px;' TYPE=TEXT NAME=api><BR>"
 print "Call 'Method': <SELECT STYLE='width:70px; height:22px;' NAME=method>"
 for method in ['GET','POST','DELETE','PUT']:
  print "<OPTION VALUE={0}>{0}</OPTION>".format(method)
 print "</SELECT>"
 print aWeb.button('start',  DIV='div_rest_info', URL='sdcp.cgi?call=tools_rest_execute', FRM='frm_rest')
 print aWeb.button('remove', DIV='div_rest_info', OP='empty', TITLE='Clear results view')
 print "<BR>Arguments/Body<BR><TEXTAREA STYLE='width:100%; height:100px;' NAME=args></TEXTAREA>"
 print "</FORM>"
 print "</ARTICLE>"
 print "<DIV ID=div_rest_info></DIV>"

#
#
def rest_execute(aWeb):
 from json import loads,dumps
 try:    arguments = loads(aWeb['args'])
 except: arguments = None
 try:
  ret = aWeb.rest_call("http://{}/rest.cgi".format(aWeb['host']),aWeb['api'],arguments,aWeb['method'])
 except Exception,e:
  ret = e[0]
 data = ret.pop('data',None)
 print "<ARTICLE STYLE='width:auto'>"
 print "<DIV CLASS='border'>"
 print "<!-- %s -->"%(ret.keys())
 print "<DIV CLASS=table STYLE='table-layout:fixed; width:100%; '><DIV CLASS=tbody>"
 for key,value in ret.iteritems():
  print "<DIV CLASS=tr><DIV CLASS=td STYLE='width:100px'>{}</DIV><DIV CLASS=td STYLE='white-space:normal'>{}</DIV></DIV>".format(key.upper(),value)
 print "</DIV></DIV>"
 print "<PRE CLASS='white'>%s</PRE>"%dumps(data,indent=4, sort_keys=True)
 print "</DIV></ARTICLE>"
