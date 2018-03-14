"""Module docstring.

HTML5 Ajax Tools calls module

"""
__author__= "Zacharias El Banna"
__version__ = "18.03.14GA"
__status__= "Production"
__icon__ = 'images/icon-config.png'
__type__ = 'menuitem'

############################################ Options ##############################################
#
def main(aWeb):
 if not aWeb.cookies.get('sdcp'):
  print "<SCRIPT>location.replace('index.cgi')</SCRIPT>"
  return
 data = aWeb.rest_call("tools_system")
 print "<NAV><UL>"
 print "<LI CLASS='warning dropdown'><A>Clear Logs</A><DIV CLASS='dropdown-content'>"
 for node in data['nodes']:
  print "<A CLASS=z-op DIV=div_content MSG='Clear Network Logs?' URL='sdcp.cgi?call=tools_clear&node=%s'>%s</A>"%(node['node'],node['node'])
 print "<LI CLASS='dropdown'><A>Logs</A><DIV CLASS='dropdown-content'>"
 for node in data['nodes']:
  print "<A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=tools_logs&node=%s>%s</A>"%(node['node'],node['node'])
 print "<LI CLASS='dropdown'><A>Resources</A><DIV CLASS='dropdown-content'>"
 print "<A CLASS=z-op DIV=div_content URL='sdcp.cgi?call=resources_list'><B>- List -</B></A>"
 print "<A CLASS=z-op DIV=div_content URL='sdcp.cgi?call=resources_view&type=tool'>View Tools</A>"
 print "<A CLASS=z-op DIV=div_content URL='sdcp.cgi?call=resources_view&type=demo'>View Demos</A>"
 print "<A CLASS=z-op DIV=div_content URL='sdcp.cgi?call=resources_view&type=bookmark'>View Bookmarks</A>"
 print "</DIV></LI>"
 print "<LI CLASS='dropdown'><A>Tools</A><DIV CLASS='dropdown-content'>"
 if data.get('dhcp_node'):
  print "<A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=dhcp_update&node=%s&type=%s SPIN=true>DHCP - Update Server</A>"%(data['dhcp_node'],data['dhcp_type'])
  print "<A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=dhcp_leases&node=%s&type=%s&lease=active>DHCP - Active</A>"%(data['dhcp_node'],data['dhcp_type'])
  print "<A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=dhcp_leases&node=%s&type=%s&lease=free>DHCP - Free</A>"%(data['dhcp_node'],data['dhcp_type'])
 print "<A CLASS=z-op TARGET=_blank            HREF='sdcp.pdf'>DB - View relational diagram</A>"
 print "<A CLASS=z-op DIV=div_content SPIN=true URL='sdcp.cgi?call=device_mac_sync'>Find MAC Info</A>"
 print "</DIV></LI>"
 print "<LI CLASS='dropdown'><A>Settings</A><DIV CLASS='dropdown-content'>"
 print "<A CLASS=z-op DIV=div_content URL='sdcp.cgi?call=sdcp_node_list'><B>- Nodes -</B></A>"
 for node in data['nodes']:
  print "<A CLASS=z-op DIV=div_content URL='sdcp.cgi?call=settings_list&node=%s'>%s</A>"%(node['node'],node['node'])
 print "</DIV></LI>"
 print "<LI CLASS=dropdown><A>REST</A><DIV CLASS='dropdown-content'>"
 print "<A CLASS=z-op DIV=div_content URL='sdcp.cgi?call=tools_rest_main'>Debug</A>"
 print "<A CLASS=z-op DIV=div_content URL='sdcp.cgi?call=tools_rest_explore'>Explore</A>"
 print "</DIV></LI>"
 for mon in data['monitors']:
  print "<LI><A CLASS=z-op DIV=div_content URL='%s'>%s</A></LI>"%(mon['href'],mon['title'])
 print "<LI><A CLASS='z-op reload' DIV=main URL='sdcp.cgi?{}'></A></LI>".format(aWeb.get_args())
 print "</UL></NAV>"
 print "<SECTION CLASS=content ID=div_content></SECTION>"

#
#
def install(aWeb):
 res = aWeb.rest_call("tools_install&node=%s"%aWeb['node'])
 print "<ARTICLE CLASS='info'><P>Install results</P>"
 print "<DIV CLASS=table><DIV CLASS=tbody>"
 for key,value in res.iteritems():
  print "<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV></DIV>"%(key,value)
 print "</DIV></DIV></ARTICLE>"

#
#
def rest_main(aWeb):
 nodes = aWeb.rest_call("sdcp_node_list")['data']
 print "<ARTICLE><P>REST API inspection</P>"
 print "<FORM ID=frm_rest>"
 print "Choose host and enter API:<SELECT CLASS=white STYLE='height:22px;' NAME=node>"
 for node in nodes:
  print "<OPTION VALUE='%s' %s>%s</A>"%(node['id'],"selected" if aWeb['node'] else "",node['node'])
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
   url = aWeb.rest_call("sdcp_node_info",{'id':aWeb['node']})['data']['url']
  elif aWeb['device'] == 'vera':
   url = "http://%s:3480/data_request"%(aWeb['host'])
  ret = aWeb.rest_full(url,aWeb['api'],arguments,aWeb['method'])
 except Exception,e:
  ret = e[0]
 data = ret.pop('data',None)
 print "<ARTICLE STYLE='width:auto'>"
 print "<DIV CLASS='border'>"
 print "<DIV CLASS=table STYLE='table-layout:fixed; width:100%;'><DIV CLASS=tbody>"
 if ret.get('info'):
  print "<DIV CLASS=tr STYLE=><DIV CLASS=td STYLE='width:100px'>INFO</DIV><DIV CLASS=td STYLE='white-space:normal'>"
  for key,value in ret.pop('info',{}).iteritems():
   print "<DIV CLASS='rest'><DIV>%s</DIV><DIV>%s</DIV></DIV>"%(key,value)
  print "</DIV></DIV>"
 for key,value in ret.iteritems():
  print "<DIV CLASS=tr><DIV CLASS=td STYLE='width:100px'>%s</DIV><DIV CLASS=td STYLE='white-space:normal'>%s</DIV></DIV>"%(key.upper(),value)
 print "</DIV></DIV>"
 print "<PRE CLASS='white'>%s</PRE>"%dumps(data,indent=4, sort_keys=True)
 print "</DIV></ARTICLE>"

#
#
def rest_explore(aWeb):
 res = aWeb.rest_call("tools_rest_explore")
 print "<SECTION CLASS=content-left  ID=div_content_left>"
 print "<ARTICLE><DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>API</DIV><DIV CLASS=th>Function</DIV></DIV><DIV CLASS=tbody>"
 for item in res['data']:
  for fun in item['functions']:
   print "<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL=sdcp.cgi?call=tools_rest_information&api=%s&function=%s>%s</A></DIV></DIV>"%(item['api'],item['api'],fun,fun)
 print "</DIV></DIV></ARTICLE>"
 print "</SECTION>"
 print "<SECTION CLASS=content-right ID=div_content_right></SECTION>"

#
#
def rest_information(aWeb):
 res = aWeb.rest_call("tools_rest_information",{'api':aWeb['api'],'function':aWeb['function']})
 print "<ARTICLE>"
 print "<H1>API: %s</H1>"%(aWeb['api'])
 print "<BR>".join(res['module'])
 print "<H1>Function: %s</H1>"%(aWeb['function'])
 print "<BR>".join(res['information'])
 print "</ARTICLE>"
 
############################################ Monitor #############################################

#
#
def clear(aWeb):
 res = aWeb.rest_call('tools_logs_clear&node=%s'%aWeb['node'])
 print "<ARTICLE>%s</ARTICLE>"%(res)

#
#
def logs(aWeb):           
 res = aWeb.rest_call('tools_logs_get&node=%s'%aWeb['node'],{'count':18})
 res.pop('xist',None)               
 print "<ARTICLE>"   
 for file,logs in res.iteritems():
  print "<P STYLE='font-weight:bold; text-align:center;'>%s</P><P CLASS='machine-text'>%s</P>"%(file,"<BR>".join(logs))
 print "</ARTICLE>"

#
# UPS graphs   
#
def ups(aWeb):
 print "<ARTICLE>"
 if aWeb.get('node'):                 
  from ..tools.munin import widget_cols
  upshost,void,domain = aWeb['node'].partition('.')
  widget_cols([ "{1}/{0}.{1}/hw_apc_power".format(upshost,domain), "{1}/{0}.{1}/hw_apc_time".format(upshost,domain), "{1}/{0}.{1}/hw_apc_temp".format(upshost,domain) ])
 else:
  print "Missing 'node' var" 
 print "</ARTICLE>"
