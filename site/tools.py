"""Module docstring.

HTML5 Ajax Tools calls module

"""
__author__= "Zacharias El Banna"
__version__ = "18.02.09GA"
__status__= "Production"
__icon__ = 'images/icon-config.png'

############################################ Options ##############################################
#
def main(aWeb):
 if not aWeb.cookies.get('sdcp'):
  print "<SCRIPT>location.replace('index.cgi')</SCRIPT>"
  return
 hosts = aWeb.rest_call("settings_list",{'section':'node'})['data']
 print "<NAV><UL>"
 print "<LI CLASS='dropdown'><A>Resources</A><DIV CLASS='dropdown-content'>"
 print "<A CLASS=z-op DIV=div_content URL='sdcp.cgi?call=resources_list'>List resources</A>"
 print "<A CLASS=z-op DIV=div_content URL='sdcp.cgi?call=resources_view&type=tool'>View Tools</A>"
 print "<A CLASS=z-op DIV=div_content URL='sdcp.cgi?call=resources_view&type=demo'>View Demos</A>"
 print "<A CLASS=z-op DIV=div_content URL='sdcp.cgi?call=resources_view&type=bookmark'>View Bookmarks</A>"
 print "</DIV></LI>"
 print "<LI CLASS='dropdown'><A>Tools</A><DIV CLASS='dropdown-content'>"
 print "<A CLASS=z-op DIV=div_content SPIN=true URL='sdcp.cgi?call=dhcp_update'>DHCP - Update Server</A>"
 print "<A CLASS=z-op DIV=div_content SPIN=true URL='sdcp.cgi?call=dns_load'>DNS - Load Cache</A>"
 print "<A CLASS=z-op DIV=div_content SPIN=true URL='sdcp.cgi?call=device_mac_sync'>Find MAC Info</A>"
 print "<A CLASS=z-op TARGET=_blank            HREF='sdcp.cgi?call=tools_db_table'>DB - Dump Device Table to JSON</A>"
 print "<A CLASS=z-op DIV=div_content           URL='sdcp.cgi?call=tools_db_structure'>DB - View Structure</A>"
 print "<A CLASS=z-op TARGET=_blank            HREF='sdcp.pdf'>DB - View relational diagram</A>"
 for host in hosts:
  print "<A CLASS=z-op DIV=div_content SPIN=true URL='sdcp.cgi?call=tools_install&host=%s'>Reinstall %s</A>"%(host['id'],host['parameter'])
 print "</DIV></LI>"
 print "<LI CLASS='dropdown'><A>Settings</A><DIV CLASS='dropdown-content'>"
 for host in hosts:
  print "<A CLASS=z-op DIV=div_content URL='sdcp.cgi?call=settings_list&host=%s'>%s</A>"%(host['id'],host['parameter'])
 print "</DIV></LI>"
 print "<LI><A CLASS=z-op DIV=div_content URL='sdcp.cgi?call=tools_rest_main'>REST</A></LI>"
 print "<LI><A CLASS='z-op reload' DIV=main URL='sdcp.cgi?{}'></A></LI>".format(aWeb.get_args())
 print "</UL></NAV>"
 print "<SECTION CLASS=content ID=div_content></SECTION>"

#
#
def db_structure(aWeb):
 res = aWeb.rest_call("sdcp_db_dump",{'mode':'structure'})
 print "<ARTICLE><P>Database Structure</A>"
 print "<P CLASS='machine-text'>"
 print "<BR>".join(res['output'])
 print "</P></ARTICLE>"

#
#
def db_table(aWeb):
 from json import dumps
 db = aWeb.rest_call("sdcp_db_table",{'table':aWeb.get('table','devices'),'columns':aWeb.get('columns','*')})['db']
 print "<PRE>{}</PRE>".format(dumps(db, indent=4, sort_keys=True))

#
#
def install(aWeb):
 from json import dumps
 dev = aWeb.rest_call("settings_info",{'id':aWeb['host']})['data']
 print "<ARTICLE><PRE>%s</PRE></ARTICLE"%dumps(aWeb.rest_generic(dev['value'],"sdcp_install"),indent = 4)

#
#
def rest_main(aWeb):
 devices = aWeb.rest_call("settings_list",{'section':'node'})['data']
 print "<ARTICLE><P>REST API inspection</P>"
 print "<FORM ID=frm_rest>"
 print "Choose host and enter API:<SELECT STYLE='height:22px;' NAME=host>"
 for host in devices:
  print "<OPTION VALUE='%s'>%s</A>"%(host['id'],host['parameter'])
 print "</SELECT> <INPUT CLASS='white' STYLE='width:500px;' TYPE=TEXT NAME=api><BR>"
 print "Call 'Method': <SELECT STYLE='width:70px; height:22px;' NAME=method>"
 for method in ['GET','POST','DELETE','PUT']:
  print "<OPTION VALUE={0}>{0}</OPTION>".format(method)
 print "</SELECT>"
 print aWeb.button('start',  DIV='div_rest_info', URL='sdcp.cgi?call=tools_rest_execute', FRM='frm_rest')
 print aWeb.button('delete', DIV='div_rest_info', OP='empty', TITLE='Clear results view')
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
  dev = aWeb.rest_call("settings_info",{'id':aWeb['host']})['data']
  ret = aWeb.rest_full(dev['value'],aWeb['api'],arguments,aWeb['method'])
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
