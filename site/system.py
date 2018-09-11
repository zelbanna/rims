"""Module docstring.

HTML5 Ajax SDCP generic module

"""
__author__= "Zacharias El Banna"
__version__ = "4.0GA"
__status__= "Production"
__icon__ = '../images/icon-examine.png'
__type__ = 'menuitem'

#
#
def main(aWeb):
 cookie = aWeb.cookie('system') 
 if not cookie.get('authenticated'):
  aWeb.wr("<SCRIPT>location.replace('system_login')</SCRIPT>")
  return
 data = aWeb.rest_call("system_inventory",{'node':aWeb.node(),'user_id':cookie['id']})
 aWeb.wr("<NAV><UL>")
 if data.get('logs'):
  aWeb.wr("<LI CLASS='dropdown'><A>Logs</A><DIV CLASS='dropdown-content'>")
  for node in data['logs']:
   aWeb.wr("<A CLASS=z-op DIV=div_content URL=tools_logs_show?node=%s>%s</A>"%(node,node))
  aWeb.wr("</DIV></LI>")
 aWeb.wr("<LI><A CLASS=z-op DIV=div_content URL='activities_report'>Activities</A></LI>")
 if data.get('users'):
  aWeb.wr("<LI><A CLASS=z-op DIV=div_content URL='reservations_list'>Reservations</A></LI>")
 aWeb.wr("<LI><A CLASS=z-op TARGET=_blank            HREF='../infra/zdcp.pdf'>ERD</A></LI>")
 aWeb.wr("<LI CLASS=dropdown><A>REST</A><DIV CLASS='dropdown-content'>")
 aWeb.wr("<A CLASS=z-op DIV=div_content URL='tools_rest_main?node=%s'>Debug</A>"%aWeb.node())
 aWeb.wr("<A CLASS=z-op DIV=div_content URL='tools_logs_show?name=rest&node=%s'>Logs</A>"%aWeb.node())
 aWeb.wr("<A CLASS=z-op DIV=div_content URL='tools_rest_explore'>Explore</A>")
 aWeb.wr("</DIV></LI>")
 aWeb.wr("<LI><A CLASS='z-op reload' DIV=main URL='system_main?node=%s'></A></LI>"%aWeb['node'])
 if data.get('navinfo'):
  for info in data['navinfo']:
   aWeb.wr("<LI CLASS='right navinfo'><A>%s</A></LI>"%info)
 aWeb.wr("</UL></NAV>")
 aWeb.wr("<SECTION CLASS=content ID=div_content></SECTION>")


#
# Generic Login - REST based apps required
#
def login(aWeb):
 application = aWeb.get('application','system')
 cookie = aWeb.cookie(application)
 if cookie and cookie.get('authenticated') == 'OK':
  aWeb.wr("<SCRIPT>location.replace('%s_portal')</SCRIPT>"%application)
  return

 args = aWeb.args()
 args['node'] = aWeb.node() if not args.get('node') else args['node']
 data = aWeb.rest_call("%s_application"%(application),args)
 aWeb.put_html(data['title'])
 aWeb.put_cookie(application,data['cookie'],data['expires'])
 aWeb.wr("<DIV CLASS='background overlay'><ARTICLE CLASS='login'><H1 CLASS='centered'>%s</H1>"%data['message'])
 if data.get('exception'):
  aWeb.wr("Error retrieving application info - exception info: %s"%(data['exception']))
 else:
  aWeb.wr("<FORM ACTION='%s_portal' METHOD=POST ID=login_form>"%(application))
  aWeb.wr("<INPUT TYPE=HIDDEN NAME=title VALUE='%s'>"%data['title'])
  aWeb.wr("<DIV CLASS=table STYLE='display:inline; float:left; margin:0px 0px 0px 30px; width:auto;'><DIV CLASS=tbody>")
  for choice in data.get('choices'):
   aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%s:</DIV><DIV CLASS=td><SELECT NAME='%s'>"%(choice['display'],choice['id']))
   for row in choice['data']:
    aWeb.wr("<OPTION VALUE='%s'>%s</OPTION>"%(row['id'],row['name']))
   aWeb.wr("</SELECT></DIV></DIV>")
  for param in data.get('parameters'):
   aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%s:</DIV><DIV CLASS=td><INPUT TYPE=%s NAME='%s'></DIV></DIV>"%(param['display'],param['data'],param['id']))
  aWeb.wr("</DIV></DIV>")
  aWeb.wr("</FORM><BUTTON CLASS='z-op menu' OP=submit STYLE='font-size:18px; margin:20px 20px 30px 40px;' FRM=login_form><IMG SRC='../images/icon-start.png' /></BUTTON>")
  aWeb.wr("</ARTICLE></DIV>")

############################################## SDCP ###############################################
#
#
# Base SDCP Portal, creates DIVs for layout
#
def portal(aWeb):
 aWeb.put_html(aWeb.get('title','Portal'))
 cookie = aWeb.cookie('system')
 id = cookie.get('id','NOID') if cookie else 'NOID'
 if id == 'NOID':
  id,_,username = aWeb.get('system_login',"NOID_NONAME").partition('_')
  res = aWeb.rest_call("system_authenticate",{'id':id,'username':username})
  if not res['authenticated'] == "OK":
   aWeb.wr("<SCRIPT>erase_cookie('system');</SCRIPT>")
   aWeb.put_redirect("system_login")
   return
  else:
   cookie.update({'id':id,'authenticated':'OK'})
   aWeb.put_cookie('system',cookie,res['expires'])

 # proper id here
 menu = aWeb.rest_call("system_menu",{"id":id,'node':aWeb.node()})
 aWeb.wr("<HEADER>")
 for item in menu['menu']:
  if   item['view'] == 0:
   aWeb.wr("<BUTTON CLASS='z-op menu' TITLE='%s' DIV=main URL='%s'><IMG ALT='%s' SRC='%s' /></BUTTON>"%(item['title'],item['href'],item['title'],item['icon']))
  elif item['view'] == 1:
   aWeb.wr("<BUTTON CLASS='z-op menu' TITLE='%s' DIV=main URL='resources_framed?id=%s'><IMG ALT='%s' SRC='%s' /></BUTTON>"%(item['title'],item['id'],item['title'],item['icon']))
  else:
   aWeb.wr("<A CLASS='btn menu' TITLE='%s' TARGET=_blank HREF='%s'><IMG ALT='%s' SRC='%s' /></A>"%(item['title'],item['href'],item['title'],item['icon']))
 aWeb.wr("<BUTTON CLASS='z-op menu right warning' OP=logout COOKIE=system URL=system_login>Log out</BUTTON>")
 aWeb.wr("<BUTTON CLASS='z-op menu right' TITLE='Tools' DIV=main URL='tools_main?node=%s'><IMG SRC='../images/icon-config.png' /></BUTTON>"%aWeb.node())
 aWeb.wr("<BUTTON CLASS='z-op menu right' TITLE='User'  DIV=main URL='users_%s'><IMG SRC='../images/icon-users.png' /></BUTTON>"%("main" if id == '1' else "user?id=%s"%id))
 aWeb.wr("</HEADER>")
 aWeb.wr("<MAIN ID=main></MAIN>")
 if menu['start']:
  aWeb.wr("<SCRIPT>include_html('main','%s')</SCRIPT>"%(menu['menu'][0]['href'] if menu['menu'][0]['view'] == 0 else "resources_framed?id=%s"%menu['menu'][0]['id']))

############################# NODE ###########################
#
#
def node_list(aWeb):
 nodes = aWeb.rest_call("system_node_list")['data']
 aWeb.wr("<SECTION CLASS=content-left ID=div_content_left>")
 aWeb.wr("<ARTICLE><P>Nodes</P>")
 aWeb.wr(aWeb.button('reload',DIV='div_content', URL='system_node_list'))
 aWeb.wr(aWeb.button('add', DIV='div_content_right', URL='system_node_info?id=new'))
 aWeb.wr(aWeb.button('help', DIV='div_content_right', URL='system_node_help'))
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Node</DIV><DIV CLASS=th>URL</DIV><DIV CLASS=th>&nbsp;</DIV></DIV><DIV CLASS=tbody>")
 for row in nodes:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td STYLE='max-width:190px; overflow-x:hidden'>%s</DIV><DIV CLASS=td>"%(row['node'],row['url']))
  aWeb.wr(aWeb.button('info',DIV='div_content_right', URL='system_node_info?id=%s'%row['id'], TITLE='Node info'))
  if row['system']:
   aWeb.wr(aWeb.button('configure',DIV='div_content', URL='settings_list?node=%s'%row['node'], TITLE='Node settings'))
   aWeb.wr(aWeb.button('logs',DIV='div_content_right', URL='tools_logs_show?node=%s'%row['node'], TITLE='Show Logs'))
   aWeb.wr(aWeb.button('trash',DIV='div_content_right', URL='tools_logs_clear?node=%s'%row['node'], TITLE='Clear Logs', MSG='Really clear node logs?'))
   aWeb.wr(aWeb.button('items',DIV='div_content', URL='resources_list?node=%s'%row['node'], TITLE='Node resources'))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</DIV></DIV></ARTICLE></SECTION>")
 aWeb.wr("<SECTION CLASS=content-right ID=div_content_right></SECTION>")

#
#
def node_info(aWeb):
 args = aWeb.args()
 data = aWeb.rest_call("system_node_info",args)['data']
 aWeb.wr("<ARTICLE CLASS='info'><P>Node Info</DIV>")
 aWeb.wr("<FORM ID=system_node_form>")
 aWeb.wr("<DIV CLASS=table STYLE='width:auto'><DIV CLASS=tbody>")
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=id VALUE='%s'>"%(aWeb['id']))
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=device_id ID=device_id VALUE='%s'>"%(data['device_id']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Node:</DIV><DIV CLASS=td><INPUT   TYPE=TEXT NAME=node STYLE='min-width:200px;' VALUE='%s'></DIV></DIV>"%(data['node']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>URL:</DIV><DIV CLASS=td><INPUT    TYPE=URL  NAME=url  STYLE='min-width:200px;' VALUE='%s'></DIV></DIV>"%(data['url']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Device:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=hostname STYLE='min-width:200px;' VALUE='%s'></DIV></DIV>"%(data['hostname'])) 
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</FORM>") 
 aWeb.wr(aWeb.button('search', DIV='device_id', INPUT='true', URL='system_node_device_id',      FRM='system_node_form', TITLE='Find matching device id using hostname'))
 aWeb.wr(aWeb.button('save',   DIV='div_content_right',       URL='system_node_info?op=update', FRM='system_node_form'))
 aWeb.wr(aWeb.button('trash',  DIV='div_content_right',       URL='system_node_delete',         FRM='system_node_form', MSG='Are you really sure you want to delete node?'))
 aWeb.wr("</ARTICLE>")

#
#
def node_delete(aWeb):
 res = aWeb.rest_call("system_node_delete",{'id':aWeb['id']})
 aWeb.wr("<ARTICLE>Result: %s</ARTICLE>"%(res))

#
#
def node_device_id(aWeb):
 res = aWeb.rest_call("device_search",{'device':aWeb['hostname']})
 aWeb.wr(res['device']['id'] if res['found'] > 0 else 'NULL')

def node_help(aWeb):
 aWeb.wr("""<ARTICLE CLASS='help' STYLE='overflow:auto'><PRE>
 Nodes offers an interface to add and delete nodes for the system

 There are two types of nodes, system generated and user inserted:
  - system generated are created during install phase for that node. These can have settings
  - user generated are for nodes that serves a particular funtion (i.e. a mapping between a name 'node' and the REST URL)

 </PRE></ARTICLE""")

############################################ Servers ###########################################

def server_list(aWeb):
 res = aWeb.rest_call("system_server_list",{'type':aWeb['type']})
 aWeb.wr("<ARTICLE><P>Servers</P>")
 aWeb.wr(aWeb.button('reload',DIV='div_content_left',URL='system_server_list?type=%s'%aWeb['type']))
 aWeb.wr(aWeb.button('add', DIV='div_content_right',URL='system_server_info?id=new&type=%s'%aWeb['type'],TITLE='Add server'))
 aWeb.wr(aWeb.button('help',DIV='div_content_right',URL='system_server_help'))
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Node</DIV><DIV CLASS=th>Server</DIV><DIV CLASS=th>Type</DIV><DIV CLASS=th>&nbsp;</DIV></DIV><DIV CLASS=tbody>")
 for srv in res['servers']:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>"%(srv['id'],srv['node'],srv['server'],srv['type']))
  aWeb.wr(aWeb.button('info',DIV='div_content_right',URL='system_server_info?id=%s'%(srv['id'])))
  aWeb.wr(aWeb.button('sync',DIV='div_content_right',URL='system_server_sync?id=%s'%(srv['id']), SPIN='true', TITLE='Sync server'))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</ARTICLE>")

#
#
def server_info(aWeb):
 args = aWeb.args()
 res  = aWeb.rest_call("system_server_info",args)
 data = res['data']
 aWeb.wr("<ARTICLE CLASS=info><P>Server</P>")
 aWeb.wr("<FORM ID=server_info_form>")
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=id VALUE=%s>"%(data['id']))
 aWeb.wr("<DIV CLASS=table STYLE='float:left; width:auto;'><DIV CLASS=tbody>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Node:</DIV><DIV CLASS=td><SELECT NAME=node>")
 for node in res['nodes']:
  extra = " selected" if (data['node'] == node['node']) else ""
  aWeb.wr("<OPTION VALUE=%s %s>%s</OPTION>"%(node['node'],extra,node['node']))
 aWeb.wr("</SELECT></DIV></DIV>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Type:</DIV><DIV CLASS=td><INPUT TYPE=TEXT READONLY NAME=type VALUE='%s'></DIV></DIV>"%data['type'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Server:</DIV><DIV CLASS=td><SELECT NAME=server>")
 for srv in res['servers']:
  extra = " selected" if (data['server'] == srv['server']) else ""
  aWeb.wr("<OPTION VALUE=%s %s>%s</OPTION>"%(srv['server'],extra,srv['server']))
 aWeb.wr("</SELECT></DIV></DIV>")
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</FORM>")
 aWeb.wr(aWeb.button('save',    DIV='div_content_right', URL='system_server_info?op=update', FRM='server_info_form'))
 if data['id'] != 'new':
  aWeb.wr(aWeb.button('trash', DIV='div_content_right', URL='system_server_delete?id=%s'%(data['id']), MSG='Delete server?'))
 aWeb.wr("</ARTICLE>")

#
#
def server_sync(aWeb):
 res = aWeb.rest_call("system_server_sync",{'id':aWeb['id']})
 aWeb.wr("<ARTICLE>%s</ARTICLE>"%str(res))

#
#
def server_delete(aWeb):
 res = aWeb.rest_call("system_server_delete",{'id':aWeb['id']})
 aWeb.wr("<ARTICLE>%s</ARTICLE>"%str(res))

#
#
def server_help(aWeb):
 aWeb.wr("""<ARTICLE CLASS='help' STYLE='overflow:auto'><PRE>
 servers manages the location of DNS and DHCP servers, i.e. the system (!) REST nodes where they offer an interface

 This is helpful in case:
  - the server doesn't offer a good REST API - then other tools can be used directly on that server
  - there are multiple DNS servers serving different zones
  - there are multiple DHCP servers serving different subnets

 </PRE></ARTICLE""")           

