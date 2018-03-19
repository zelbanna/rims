"""Module docstring.

HTML5 Ajax Tools calls module

"""
__author__= "Zacharias El Banna"
__version__ = "18.03.16"
__status__= "Production"
__icon__ = 'images/icon-config.png'
__type__ = 'menuitem'

############################################ Options ##############################################
#
def main(aWeb):
 if not aWeb.cookies.get('system'):
  print "<SCRIPT>location.replace('index.cgi')</SCRIPT>"
  return
 cookie = aWeb.cookie_unjar('system')
 data = aWeb.rest_call("system_inventory",{'node':aWeb.id,'user_id':cookie['id']})
 print "<NAV><UL>"
 if data.get('node'):
  print "<LI><A CLASS=z-op DIV=div_content URL='sdcp.cgi?call=system_node_list'>Nodes</A></LI>"
 if data.get('logs'):
  print "<LI CLASS='dropdown'><A>Logs</A><DIV CLASS='dropdown-content'>"
  for node in data['logs']:
   print "<A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=tools_logs_show&node=%s>%s - show</A>"%(node,node)
   print "<A CLASS=z-op DIV=div_content MSG='Clear Network Logs?' URL='sdcp.cgi?call=tools_logs_clear&node=%s'>%s - clear</A>"%(node,node)
  print "</DIV></LI>"
 if data.get('www'):
  print "<LI CLASS='dropdown'><A>Resources</A><DIV CLASS='dropdown-content'>"
  for node in data['www']:
   print "<A CLASS=z-op DIV=div_content URL='sdcp.cgi?call=resources_list&node=%s'>%s</A>"%(node,node)
  print "</DIV></LI>"  
 if data.get('users'):
  print "<LI><A CLASS=z-op DIV=div_content URL='sdcp.cgi?call=users_list'>Users</A></LI>"
  print "<LI><A CLASS=z-op DIV=div_content URL='sdcp.cgi?call=bookings_list'>Booking</A></LI>"
 print "<LI CLASS='dropdown'><A>Tools</A><DIV CLASS='dropdown-content'>"
 for tool in data.get('tools',[]): 
  print "<A CLASS=z-op DIV=div_content URL='%s'>%s</A>"%(tool['href'],tool['title'])
 for svc in data.get('services',[]):
  print "<A CLASS=z-op DIV=div_content URL='sdcp.cgi?call=tools_services_info&node=%s&service=%s'>%s</A>"%(aWeb['node'],svc['service'],svc['name'])
 if data.get('dhcp'):
  dhcp = (data['dhcp']['node'],data['dhcp']['type'])
  print "<A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=dhcp_update&node=%s&type=%s SPIN=true>DHCP - Update Server</A>"%dhcp
  print "<A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=dhcp_leases&node=%s&type=%s&lease=active>DHCP - Active</A>"%dhcp
  print "<A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=dhcp_leases&node=%s&type=%s&lease=free>DHCP - Free</A>"%dhcp
 if data.get('extra'):
  print "<A CLASS=z-op TARGET=_blank            HREF='sdcp.pdf'>DB - View relational diagram</A>"
  print "<A CLASS=z-op DIV=div_content SPIN=true URL='sdcp.cgi?call=device_mac_sync'>Find MAC Info</A>"
 print "</DIV></LI>"
 print "<LI CLASS=dropdown><A>REST</A><DIV CLASS='dropdown-content'>"
 print "<A CLASS=z-op DIV=div_content URL='sdcp.cgi?call=tools_rest_main&node=%s'>Debug</A>"%aWeb['node']
 print "<A CLASS=z-op DIV=div_content URL='sdcp.cgi?call=tools_rest_explore'>Explore</A>"
 print "</DIV></LI>"
 print "<LI><A CLASS='z-op reload' DIV=main URL='sdcp.cgi?call=tools_main&node=%s'></A></LI>"%aWeb['node']
 if data.get('navinfo'):
  for info in data['navinfo']:
   print "<LI CLASS='right navinfo'><A>%s</A></LI>"%info
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

############################################# REST ###############################################
#
#
def rest_main(aWeb):
 nodes = aWeb.rest_call("system_node_list")['data']
 print "<ARTICLE><P>REST API inspection</P>"
 print "<FORM ID=frm_rest>"
 print "Choose host and enter API:<SELECT CLASS=white STYLE='height:22px;' NAME=node>"
 for node in nodes:
  print "<OPTION VALUE='%s' %s>%s</A>"%(node['id'],"selected" if aWeb['node'] == node['node'] else "",node['node'])
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
   url = aWeb.rest_call("system_node_info",{'id':aWeb['node']})['data']['url']
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
 
############################################### Logs ###############################################

#
#
def logs_clear(aWeb):
 res = aWeb.rest_call('tools_logs_clear&node=%s'%aWeb['node'])
 print "<ARTICLE><P>%s</P>"%res['node']
 for k,v in res['file'].iteritems():
  print "%s: %s<BR>"%(k,v)
 print "</ARTICLE>"%(res)

#
#
def logs_show(aWeb):           
 res = aWeb.rest_call('tools_logs_get&node=%s'%aWeb['node'],{'count':18})
 res.pop('xist',None)               
 print "<ARTICLE>"   
 for file,logs in res.iteritems():
  print "<P STYLE='font-weight:bold; text-align:center;'>%s</P><P CLASS='machine-text'>%s</P>"%(file,"<BR>".join(logs))
 print "</ARTICLE>"

############################################# Services ##############################################
#
#
def services_info(aWeb):
 args = {'service':aWeb['service']}
 if aWeb['op']:
  args['operation'] = aWeb['op']
 data  = aWeb.rest_call('tools_service_info&node=%s'%aWeb['node'],args)
 state = 'start' if data['state'] == 'inactive' else 'stop'
 print "<ARTICLE STYLE='display:inline-block;'><B>%s</B>: %s (%s)<DIV CLASS=controls>"%(aWeb['service'],data['state'],data['info'])
 print aWeb.button(state, DIV='div_content', SPIN='true', URL='sdcp.cgi?call=tools_services_info&service=%s&node=%s&op=%s'%(args['service'],aWeb['node'],state))
 print "</DIV></ARTICLE>"

############################################## Files ###############################################
#
#
def files_list(aWeb):
 res = aWeb.rest_call('tools_files_list',{'setting':aWeb['setting']})
 print "<NAV></NAV><SECTION CLASS=content ID=div_content><ARTICLE><P>Files in %s<P>"%res['directory']
 for file in res['files']:
  print "<P CLASS=machine-text>{0}/<A HREF='{0}/{1}' TARGET=_blank>{1}</A></P>".format(res['directory'],file.encode('utf-8'))
 print "</ARTICLE></SECTION>"

#
#
def images(aWeb):
 res = aWeb.rest_call('tools_files_list',{'setting':'images'})
 print "<NAV></NAV><SECTION CLASS=content ID=div_content><ARTICLE><P>Images<P><DIV CLASS=table><DIV CLASS=tbody>"
 for file in res['files']:
  if file[-3:] == 'png':
   print "<DIV CLASS=tr><DIV CLASS=td STYLE='max-width:180px'>{0}</DIV><DIV CLASS=td STYLE='width:100%;'><IMG STYLE='max-height:60px;' SRC='images/{0}' /></DIV></DIV>".format(file)
 print "</DIV></DIV></ARTICLE></SECTION>"

#
# UPS graphs   
#
def ups(aWeb):
 print "<ARTICLE>"
 if aWeb.get('host'):                 
  from sdcp.tools.munin import widget_cols
  upshost,void,domain = aWeb['host'].partition('.')
  widget_cols([ "{1}/{0}.{1}/hw_apc_power".format(upshost,domain), "{1}/{0}.{1}/hw_apc_time".format(upshost,domain), "{1}/{0}.{1}/hw_apc_temp".format(upshost,domain) ])
 else:
  print "Missing 'host' var" 
 print "</ARTICLE>"
