"""Module docstring.

HTML5 Ajax SDCP generic module

"""
__author__= "Zacharias El Banna"
__version__ = "1.0GA"
__status__= "Production"
__icon__ = 'images/icon-examine.png'
__type__ = 'menuitem'

#
#
def main(aWeb):
 if not aWeb.cookies.get('system'):
  print "<SCRIPT>location.replace('index.cgi')</SCRIPT>"
  return
 cookie = aWeb.cookie_unjar('system')
 data = aWeb.rest_call("system_inventory",{'node':aWeb.id,'user_id':cookie['id']})
 print "<NAV><UL>"
 if data.get('logs'):
  print "<LI CLASS='dropdown'><A>Logs</A><DIV CLASS='dropdown-content'>"
  for node in data['logs']:
   print "<A CLASS=z-op DIV=div_content URL=zdcp.cgi?tools_logs_show&node=%s>%s - show</A>"%(node,node)
   print "<A CLASS=z-op DIV=div_content MSG='Clear Network Logs?' URL='zdcp.cgi?tools_logs_clear&node=%s'>%s - clear</A>"%(node,node)
  print "</DIV></LI>"
 print "<LI><A CLASS=z-op DIV=div_content URL='zdcp.cgi?activities_report'>Activities</A></LI>"
 if data.get('users'):
  print "<LI><A CLASS=z-op DIV=div_content URL='zdcp.cgi?bookings_list'>Bookings</A></LI>"
 print "<LI><A CLASS=z-op TARGET=_blank            HREF='zdcp.pdf'>DB</A></LI>"
 print "<LI CLASS=dropdown><A>REST</A><DIV CLASS='dropdown-content'>"
 print "<A CLASS=z-op DIV=div_content URL='zdcp.cgi?tools_rest_main&node=%s'>Debug</A>"%aWeb.id
 print "<A CLASS=z-op DIV=div_content URL='zdcp.cgi?tools_logs_show&name=rest&node=%s'>Logs</A>"%aWeb.id
 print "<A CLASS=z-op DIV=div_content URL='zdcp.cgi?tools_rest_explore'>Explore</A>"
 print "</DIV></LI>"
 print "<LI><A CLASS='z-op reload' DIV=main URL='zdcp.cgi?system_main&node=%s'></A></LI>"%aWeb['node']
 if data.get('navinfo'):
  for info in data['navinfo']:
   print "<LI CLASS='right navinfo'><A>%s</A></LI>"%info
 print "</UL></NAV>"
 print "<SECTION CLASS=content ID=div_content></SECTION>"


#
# Generic Login - REST based apps required
#
def login(aWeb):
 application = aWeb.get('application','system')
 cookie = aWeb.cookie_unjar(application)
 if cookie.get('authenticated') == 'OK':
  aWeb.put_redirect("zdcp.cgi?%s_portal"%application)
  return

 args = aWeb.get_args2dict()
 args['node'] = aWeb.id if not args.get('node') else args['node']
 data = aWeb.rest_call("%s_application"%(application),args)
 aWeb.put_html(data['title'])
 aWeb.put_cookie(application,data['cookie'],data['expires'])
 print "<DIV CLASS='background overlay'><ARTICLE CLASS='login'><H1 CLASS='centered'>%s</H1>"%data['message']
 if data.get('exception'):
  print "Error retrieving application info - exception info: %s"%(data['exception'])
 else:
  print "<FORM ACTION='zdcp.cgi?%s_portal' METHOD=POST ID=login_form>"%(application)
  print "<INPUT TYPE=HIDDEN NAME=title VALUE='%s'>"%data['title']
  print "<DIV CLASS=table STYLE='display:inline; float:left; margin:0px 0px 0px 30px; width:auto;'><DIV CLASS=tbody>"
  for choice in data.get('choices'):
   print "<DIV CLASS=tr><DIV CLASS=td>%s:</DIV><DIV CLASS=td><SELECT NAME='%s'>"%(choice['display'],choice['id'])
   for row in choice['data']:
    print "<OPTION VALUE='%s'>%s</OPTION>"%(row['id'],row['name'])
   print "</SELECT></DIV></DIV>"
  for param in data.get('parameters'):
   print "<DIV CLASS=tr><DIV CLASS=td>%s:</DIV><DIV CLASS=td><INPUT TYPE=%s NAME='%s'></DIV></DIV>"%(param['display'],param['data'],param['id'])
  print "</DIV></DIV>"
  print "</FORM><DIV CLASS=controls><BUTTON CLASS='z-op menu' OP=submit STYLE='font-size:18px; margin:20px 20px 30px 40px;' FRM=login_form><IMG SRC='images/icon-start.png'</BUTTON></DIV>"
  print "</ARTICLE></DIV>"

############################################## SDCP ###############################################
#
#
# Base SDCP Portal, creates DIVs for layout
#
def portal(aWeb):
 aWeb.put_html(aWeb.get('title','Portal'))
 cookie = aWeb.cookie_unjar('system')
 id = cookie.get('id','NOID')
 if id == 'NOID':
  id,_,username = aWeb.get('system_login',"NOID_NONAME").partition('_')
  res = aWeb.rest_call("system_authenticate",{'id':id,'username':username})
  if not res['authenticated'] == "OK":
   print "<SCRIPT>erase_cookie('system');</SCRIPT>"
   aWeb.put_redirect("index.cgi")
   return
  else:
   cookie.update({'id':id,'authenticated':'OK'})
   aWeb.put_cookie('system',cookie,res['expires'])

 # proper id here
 menu = aWeb.rest_call("system_menu",{"id":id,'node':aWeb.id})
 print "<HEADER>"
 for item in menu['menu']:
  if   item['view'] == 0:
   print "<BUTTON CLASS='z-op menu' TITLE='%s' DIV=main URL='%s'><IMG ALT='%s' SRC='%s'/></BUTTON>"%(item['title'],item['href'],item['title'],item['icon'])
  elif item['view'] == 1:
   print "<BUTTON CLASS='z-op menu' TITLE='%s' DIV=main URL='zdcp.cgi?resources_framed&id=%s'><IMG ALT='%s' SRC='%s'/></BUTTON>"%(item['title'],item['id'],item['title'],item['icon'])
  else:
   print "<A CLASS='btn menu' TITLE='%s' TARGET=_blank HREF='%s'><IMG ALT='%s' SRC='%s'/></A>"%(item['title'],item['href'],item['title'],item['icon'])
 print "<BUTTON CLASS='z-op menu right warning' OP=logout COOKIE=system URL=zdcp.cgi?system_login>Log out</BUTTON>"
 print "<BUTTON CLASS='z-op menu right' TITLE='Tools' DIV=main URL='zdcp.cgi?tools_main&node=%s'><IMG SRC='images/icon-config'/></BUTTON>"%aWeb.id
 print "<BUTTON CLASS='z-op menu right' TITLE='User'  DIV=main URL='zdcp.cgi?users_%s'><IMG SRC='images/icon-users.png'></BUTTON>"%("main" if id == '1' else "user&id=%s"%id)
 print "</HEADER>"
 print "<MAIN ID=main></MAIN>"
 if menu['start']:
  print "<SCRIPT>include_html('main','%s')</SCRIPT>"%(menu['menu'][0]['href'] if menu['menu'][0]['view'] == 0 else "zdcp.cgi?resources_framed&id=%s"%menu['menu'][0]['id'])

############################# NODE ###########################
#
#
def node_list(aWeb):
 nodes = aWeb.rest_call("system_node_list")['data']
 print "<SECTION CLASS=content-left ID=div_content_left>"
 print "<ARTICLE><P>Nodes</P><DIV CLASS=controls>"
 print aWeb.button('reload',DIV='div_content', URL='zdcp.cgi?system_node_list')
 print aWeb.button('add', DIV='div_content_right', URL='zdcp.cgi?system_node_info&id=new')
 print aWeb.button('help', DIV='div_content_right', URL='zdcp.cgi?system_node_help')
 print "</DIV><DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Node</DIV><DIV CLASS=th>URL</DIV><DIV CLASS=th>&nbsp;</DIV></DIV><DIV CLASS=tbody>"
 for row in nodes:
  print "<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td STYLE='max-width:190px; overflow-x:hidden'>%s</DIV><DIV CLASS=td><DIV CLASS=controls>"%(row['node'],row['url'])
  print aWeb.button('info',DIV='div_content_right', URL='zdcp.cgi?system_node_info&id=%s'%row['id'])
  if row['system']:
   print aWeb.button('items',DIV='div_content', URL='zdcp.cgi?settings_list&node=%s'%row['node']) 
  print "</DIV></DIV></DIV>"
 print "</DIV></DIV></ARTICLE></SECTION>"
 print "<SECTION CLASS=content-right ID=div_content_right></SECTION>"

#
#
def node_info(aWeb):
 args = aWeb.get_args2dict()
 data = aWeb.rest_call("system_node_info",args)['data']
 print "<ARTICLE CLASS='info'><P>Node Info</DIV>"
 print "<FORM ID=system_node_form>"
 print "<DIV CLASS=table STYLE='width:auto'><DIV CLASS=tbody>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE='%s'>"%(aWeb['id'])
 print "<INPUT TYPE=HIDDEN NAME=device_id ID=device_id VALUE='%s'>"%(data['device_id'])
 print "<DIV CLASS=tr><DIV CLASS=td>Node:</DIV><DIV CLASS=td><INPUT   TYPE=TEXT NAME=node STYLE='min-width:200px;' VALUE='%s'></DIV></DIV>"%(data['node'])
 print "<DIV CLASS=tr><DIV CLASS=td>URL:</DIV><DIV CLASS=td><INPUT    TYPE=URL  NAME=url  STYLE='min-width:200px;' VALUE='%s'></DIV></DIV>"%(data['url'])
 print "<DIV CLASS=tr><DIV CLASS=td>Device:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=hostname STYLE='min-width:200px;' VALUE='%s'></DIV></DIV>"%(data['hostname']) 
 print "</DIV></DIV>"
 print "</FORM>" 
 print "<DIV CLASS=controls>"
 print aWeb.button('search', DIV='device_id', INPUT='true', URL='zdcp.cgi?system_node_device_id',      FRM='system_node_form')
 print aWeb.button('save',   DIV='div_content_right',       URL='zdcp.cgi?system_node_info&op=update', FRM='system_node_form')
 print aWeb.button('trash',  DIV='div_content_right',       URL='zdcp.cgi?system_node_delete',         FRM='system_node_form', MSG='Are you really sure you want to delete node?')
 print "</DIV></ARTICLE>"

#
#
def node_delete(aWeb):
 res = aWeb.rest_call("system_node_delete",{'id':aWeb['id']})
 print "<ARTICLE>Result: %s</ARTICLE>"%(res)

#
#
def node_device_id(aWeb):
 res = aWeb.rest_call("device_search",{'device':aWeb['hostname']})
 print res['device']['id'] if res['found'] > 0 else 'NULL'

def node_help(aWeb):
 print """<ARTICLE CLASS='help' STYLE='overflow:auto'><PRE>
 Nodes offers an interface to add and delete nodes for the system

 There are two types of nodes, system generated and user inserted:
  - system generated are created during install phase for that node. These can have settings
  - user generated are for nodes that serves a particular funtion (i.e. a mapping between a name 'node' and the REST URL)

 </PRE></ARTICLE"""

############################################ Servers ###########################################

def server_list(aWeb):
 res = aWeb.rest_call("system_server_list",{'type':aWeb['type']})
 print "<ARTICLE><P>Domains</P><DIV CLASS='controls'>"
 print aWeb.button('reload',DIV='div_content_left',URL='zdcp.cgi?system_server_list&type=%s'%aWeb['type'])
 print aWeb.button('add', DIV='div_content_right',URL='zdcp.cgi?system_server_info&id=new&type=%s'%aWeb['type'],TITLE='Add server')
 print aWeb.button('help',DIV='div_content_right',URL='zdcp.cgi?system_server_help')
 print "</DIV><DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Node</DIV><DIV CLASS=th>Server</DIV><DIV CLASS=th>Type</DIV><DIV CLASS=th>&nbsp;</DIV></DIV><DIV CLASS=tbody>"
 for srv in res['servers']:
  print "<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td><DIV CLASS=controls>"%(srv['id'],srv['node'],srv['server'],srv['type'])
  print aWeb.button('info',DIV='div_content_right',URL='zdcp.cgi?system_server_info&id=%s'%(srv['id']))
  print "</DIV></DIV></DIV>"
 print "</DIV></DIV>"
 print "</ARTICLE>"

#
#
def server_info(aWeb):
 args = aWeb.get_args2dict()
 res  = aWeb.rest_call("system_server_info",args)
 data = res['data']
 print "<ARTICLE CLASS=info><P>Server</P>"
 print "<FORM ID=server_info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE=%s>"%(data['id'])
 print "<DIV CLASS=table STYLE='float:left; width:auto;'><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Node:</DIV><DIV CLASS=td><SELECT NAME=node>"
 for node in res['nodes']:
  extra = " selected" if (data['node'] == node['node']) else ""
  print "<OPTION VALUE=%s %s>%s</OPTION>"%(node['node'],extra,node['node'])
 print "</SELECT></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td>Type:</DIV><DIV CLASS=td>%s</DIV></DIV>"%data['type']
 print "<DIV CLASS=tr><DIV CLASS=td>Server:</DIV><DIV CLASS=td><SELECT NAME=server>"
 for srv in res['servers']:
  extra = " selected" if (data['server'] == srv['server']) else ""
  print "<OPTION VALUE=%s %s>%s</OPTION>"%(srv['server'],extra,srv['server'])
 print "</SELECT></DIV></DIV>"
 print "</DIV></DIV>"
 print "</FORM><DIV CLASS=controls>"
 print aWeb.button('save',    DIV='div_content_right', URL='zdcp.cgi?system_server_info&op=update', FRM='server_info_form')
 if data['id'] != 'new':
  print aWeb.button('trash', DIV='div_content_right', URL='zdcp.cgi?system_server_delete&id=%s'%(data['id']), MSG='Delete server?')
 print "</DIV></ARTICLE>"

#
#
def server_delete(aWeb):
 res = aWeb.rest_call("system_server_delete",{'id':aWeb['id']})
 print "<ARTICLE>%s</ARTICLE>"%str(res)

#
#
def server_help(aWeb):
 print """<ARTICLE CLASS='help' STYLE='overflow:auto'><PRE>
 servers manages the location of DNS and DHCP servers, i.e. the system (!) REST nodes where they offer an interface

 This is helpful in case:
  - the server doesn't offer a good REST API - then other tools can be used directly on that server
  - there are multiple DNS servers serving different zones
  - there are multiple DHCP servers serving different subnets

 </PRE></ARTICLE"""           

