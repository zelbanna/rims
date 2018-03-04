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
 print "<A CLASS=z-op DIV=div_content SPIN=true URL='sdcp.cgi?call=dns_load_cache'>DNS - Load Cache</A>"
 print "<A CLASS=z-op DIV=div_content SPIN=true URL='sdcp.cgi?call=device_mac_sync'>Find MAC Info</A>"
 print "<A CLASS=z-op TARGET=_blank            HREF='sdcp.pdf'>DB - View relational diagram</A>"
 for host in hosts:
  print "<A CLASS=z-op DIV=div_content SPIN=true URL='sdcp.cgi?call=tools_install&host=%s'>Reinstall %s</A>"%(host['id'],host['parameter'])
 print "</DIV></LI>"
 print "<LI CLASS='dropdown'><A>Settings</A><DIV CLASS='dropdown-content'>"
 for host in hosts:
  print "<A CLASS=z-op DIV=div_content URL='sdcp.cgi?call=settings_list&node=%s'>%s</A>"%(host['parameter'],host['parameter'])
 print "</DIV></LI>"
 print "<LI><A CLASS=z-op DIV=div_content URL='sdcp.cgi?call=tools_rest_main'>REST</A></LI>"
 print "<LI><A CLASS='z-op reload' DIV=main URL='sdcp.cgi?{}'></A></LI>".format(aWeb.get_args())
 print "</UL></NAV>"
 print "<SECTION CLASS=content ID=div_content></SECTION>"

#
#
def install(aWeb):
 dev = aWeb.rest_call("settings_info",{'id':aWeb['host']})['data']
 res = aWeb.rest_generic(dev['value'],"tools_install")
 print "<ARTICLE CLASS='info'><P>Install results</P>"
 print "<DIV CLASS=table><DIV CLASS=tbody>"
 for key,value in res.iteritems():
  print "<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV></DIV>"%(key,value)
 print "</DIV></DIV></ARTICLE>"

#
#
def rest_main(aWeb):
 nodes = aWeb.rest_call("settings_list",{'section':'node'})['data']
 print "<ARTICLE><P>REST API inspection</P>"
 print "<FORM ID=frm_rest>"
 print "Choose host and enter API:<SELECT STYLE='height:22px;' NAME=node>"
 for node in nodes:
  print "<OPTION VALUE='%s'>%s</A>"%(node['id'],node['parameter'])
 print "</SELECT> <INPUT CLASS='white' STYLE='width:500px;' TYPE=TEXT NAME=api><BR>"
 print "Call 'Method': <SELECT CLASS='white' STYLE='width:70px; height:22px;' NAME=method>"
 for method in ['GET','POST','DELETE','PUT']:
  print "<OPTION VALUE={0}>{0}</OPTION>".format(method)
 print "</SELECT>"
 print "<BR>Arguments/Body<BR><TEXTAREA STYLE='width:100%; height:70px;' NAME=arguments></TEXTAREA>"
 print "</FORM><DIV CLASS=controls>"
 print aWeb.button('start',  DIV='div_rest_info', URL='sdcp.cgi?call=tools_rest_execute', FRM='frm_rest')
 print aWeb.button('delete', DIV='div_rest_info', OP='empty', TITLE='Clear results view')
 print "</DIV></ARTICLE>"
 print "<DIV ID=div_rest_info></DIV>"

#
#
def rest_execute(aWeb):
 from json import loads,dumps
 try:    arguments = loads(aWeb['arguments'])
 except: arguments = None
 try:
  if aWeb['node']:
   dev = aWeb.rest_call("settings_info",{'id':aWeb['node']})['data']
   ret = aWeb.rest_full(dev['value'],aWeb['api'],arguments,aWeb['method'])
  elif aWeb['device'] == 'vera':
   from ..devices.vera import Device
   controller = Device(aWeb['host'])
   ret = controller.call(3480,aWeb['api'],arguments,aWeb['method'])
 except Exception,e:
  ret = e[0]
 data = ret.pop('data',None)
 print "<ARTICLE STYLE='width:auto'>"
 print "<DIV CLASS='border'>"
 print "<DIV CLASS=table STYLE='table-layout:fixed; width:100%;'><DIV CLASS=tbody>"
 if ret.get('info'):
  print "<DIV CLASS=tr STYLE=><DIV CLASS=td STYLE='width:100px'>INFO</DIV><DIV CLASS=td STYLE='white-space:normal'>"
  for key,value in ret.pop('info',{}).iteritems():
   print "<DIV CLASS='border-grey' STYLE='float:left; margin:1px;'><DIV CLASS=grey STYLE='min-width:100px; font-weight:bold;'>{}</DIV><DIV CLASS=white STYLE='white-space:normal; min-width:100px;'>{}</DIV></DIV>".format(key,value)
  print "</DIV></DIV>"
 for key,value in ret.iteritems():
  print "<DIV CLASS=tr><DIV CLASS=td STYLE='width:100px'>{}</DIV><DIV CLASS=td STYLE='white-space:normal'>{}</DIV></DIV>".format(key.upper(),value)
 print "</DIV></DIV>"
 print "<PRE CLASS='white'>%s</PRE>"%dumps(data,indent=4, sort_keys=True)
 print "</DIV></ARTICLE>"

#
#
def rest_explore(aWeb):
 pass
