"""HTML5 Ajax System function module"""
__author__= "Zacharias El Banna"
__icon__ = 'icon-examine.png'
__type__ = 'menuitem'

#
#
def main(aWeb):
 cookie = aWeb.cookie('rims')
 data = aWeb.rest_call("system/inventory",{'node':aWeb.node(),'user_id':cookie['id']})
 aWeb.wr("<NAV><UL>")
 if data.get('logs'):
  aWeb.wr("<LI CLASS='dropdown'><A>Logs</A><DIV CLASS='dropdown-content'>")
  for node in data['logs']:
   aWeb.wr("<A CLASS=z-op DIV=div_content URL=tools_logs_show?node=%s>%s</A>"%(node,node))
  aWeb.wr("</DIV></LI>")
 aWeb.wr("<LI CLASS='dropdown'><A>Reports</A><DIV CLASS='dropdown-content'>")
 if aWeb.node() == 'master':
  aWeb.wr("<A CLASS=z-op DIV=div_content URL='activities_report'>Activities</A>")
  aWeb.wr("<A CLASS=z-op DIV=div_content URL='reservations_report?node=master'>Reservations</A>")
  aWeb.wr("<A CLASS=z-op DIV=div_content URL='device_report?node=master'>Devices</A>")
 aWeb.wr("<A CLASS=z-op DIV=div_content URL='system_task_report'>Tasks</A>")
 aWeb.wr("<A CLASS=z-op DIV=div_content URL='system_report'>System</A>")
 aWeb.wr("</DIV></LI>")
 if aWeb.node() == 'master':
  aWeb.wr("<LI><A CLASS=z-op TARGET=_blank            HREF='../infra/erd.pdf'>ERD</A></LI>")
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
#
def portal(aWeb):
 cookie = aWeb.cookie('rims')
 auth,data,args = {},{},aWeb.args()
 if not cookie.get('token') and (args.get('username') and args.get('password')):
  try:  auth = aWeb.rest_full("%s/auth"%aWeb.url(), aArgs = args, aDataOnly = True)
  except Exception as e:
   auth = e.args[0].get('data',{})
  else:
   cookie = {'node':auth['node'],'id':auth['id'],'token':auth['token'],'theme':auth['theme']}
 if cookie.get('token'):
  id = cookie['id']
  menu = aWeb.rest_call("system/menu",{"id":id,'node':aWeb.node()})
  aWeb.put_html(aTitle = menu.get('title','Portal'), aTheme = cookie['theme'])
  """ If just auth:ed """
  if auth.get('token'):
   aWeb.wr("<SCRIPT>set_cookie('rims','%s','%s');</SCRIPT>"%(",".join("%s=%s"%i for i in cookie.items()),auth['expires']))
  aWeb.wr("<HEADER>")
  for item in menu['menu']:
   if   item['view'] == 0:
    aWeb.wr("<BUTTON CLASS='z-op menu' TITLE='%s' DIV=main URL='%s'><IMG ALT='%s' SRC='%s' /></BUTTON>"%(item['title'],item['href'],item['title'],item['icon']))
   elif item['view'] == 1:
    aWeb.wr("<BUTTON CLASS='z-op menu' TITLE='%s' DIV=main URL='resources_framed?id=%s'><IMG ALT='%s' SRC='%s' /></BUTTON>"%(item['title'],item['id'],item['title'],item['icon']))
   else:
    aWeb.wr("<A CLASS='btn menu' TITLE='%s' TARGET=_blank HREF='%s'><IMG ALT='%s' SRC='%s' /></A>"%(item['title'],item['href'],item['title'],item['icon']))
  aWeb.wr("<BUTTON CLASS='z-op menu right warning' OP=logout COOKIE=system URL=system_portal>Log out</BUTTON>")
  aWeb.wr("<BUTTON CLASS='z-op menu right' TITLE='Tools' DIV=main URL='tools_main?node=%s'><IMG SRC='../images/icon-config.png' /></BUTTON>"%aWeb.node())
  aWeb.wr("<BUTTON CLASS='z-op menu right' TITLE='User'  DIV=main URL='users_%s'><IMG SRC='../images/icon-users.png' /></BUTTON>"%("main" if id == '1' else "user?id=%s"%id))
  aWeb.wr("</HEADER>")
  aWeb.wr("<MAIN ID=main></MAIN>")
  if menu['start']:
   aWeb.wr("<SCRIPT>include_html('main','%s')</SCRIPT>"%(menu['menu'][0]['href'] if menu['menu'][0]['view'] == 0 else "resources_framed?id=%s"%menu['menu'][0]['id']))
 else:
  data = aWeb.rest_call("system/application",{'node':aWeb.node()})
  aWeb.put_html(aTitle = data['title'])
  aWeb.wr("<DIV CLASS='background overlay'><ARTICLE CLASS='login'><H1 CLASS='centered'>%s</H1>"%data['message'])
  if data.get('exception'):
   aWeb.wr("Error retrieving application info - exception info: %s"%(data['exception']))
  else:
   error = auth.get('error',{})
   aWeb.wr("<FORM ACTION='system_portal' METHOD=POST ID=login_form>")
   aWeb.wr("<DIV CLASS=table STYLE='display:inline; float:left; margin:0px 0px 0px 30px; width:auto;'><DIV CLASS=tbody>")
   aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Username:</DIV><DIV CLASS=td><SELECT NAME=username>")
   for row in data['usernames']:
    aWeb.wr("<OPTION VALUE='%s' %s>%s</OPTION>"%(row['id'],"selected=selected" if row['id'] == error.get('username','admin') else "",row['name']))
   aWeb.wr("</SELECT></DIV></DIV>")
   aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Password:</DIV><DIV CLASS=td><INPUT TYPE=password NAME='password' PLACEHOLDER='******'></DIV></DIV>")
   aWeb.wr("</DIV></DIV>")
   aWeb.wr("</FORM><BUTTON CLASS='z-op menu' OP=submit STYLE='font-size:18px; margin:20px 20px 30px 40px;' FRM=login_form><IMG SRC='../images/icon-start.png' /></BUTTON>")
  aWeb.wr("<!-- %s -->"%auth.get('error'))
  aWeb.wr("</ARTICLE></DIV>")

#
#
def report(aWeb):
 info = aWeb.rest_full("%s/system/report"%aWeb.url(), aDataOnly = True)
 analytics = info.pop('analytics',{})
 keys = sorted(info.keys())
 aWeb.wr("<ARTICLE CLASS=info STYLE='width:100%'><P>System</P>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Information</DIV><DIV CLASS=th>Value</DIV></DIV><DIV CLASS=tbody>")
 for i in keys:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV></DIV>"%(i,info[i]))
 for x in ['modules','files']:
  for k,v in analytics.get(x,{}).items():
   aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%s: %s</DIV><DIV CLASS=td>%s</DIV></DIV>"%(x.title(),k,v))
 aWeb.wr("</DIV></DIV></ARTICLE>")

#
#
def reload(aWeb):
 """ Map node to URL and call reload """
 api = aWeb.rest_call("system/node_to_api",{'node':aWeb['node']})['url']
 res = aWeb.rest_full("%s/system/reload"%api, aDataOnly = True)
 aWeb.wr("<ARTICLE CLASS=info STYLE='width:100%'><P>Module</P>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=tbody>")
 for x in res['modules']:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%s</DIV></DIV>"%x)
 aWeb.wr("</DIV></DIV></ARTICLE>")

############################# NODE ###########################
#
#
def node_list(aWeb):
 nodes = aWeb.rest_call("system/node_list")['data']
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
   aWeb.wr(aWeb.button('configure',DIV='div_content',    URL='settings_list?node=%s'%row['node'],    TITLE='Node settings'))
   aWeb.wr(aWeb.button('logs',DIV='div_content_right',   URL='tools_logs_show?node=%s'%row['node'],  TITLE='Show Logs'))
   aWeb.wr(aWeb.button('trash',DIV='div_content_right',  URL='tools_logs_clear?node=%s'%row['node'], TITLE='Clear Logs', MSG='Really clear node logs?'))
   aWeb.wr(aWeb.button('items',DIV='div_content',        URL='resources_list?node=%s'%row['node'],   TITLE='Node resources'))
   aWeb.wr(aWeb.button('reload',DIV='div_content_right', URL='system_reload?node=%s'%row['node'],    TITLE='Reload Engine'))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</DIV></DIV></ARTICLE></SECTION>")
 aWeb.wr("<SECTION CLASS=content-right ID=div_content_right></SECTION>")

#
#
def node_info(aWeb):
 args = aWeb.args()
 data = aWeb.rest_call("system/node_info",args)['data']
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
 res = aWeb.rest_call("system/node_delete",{'id':aWeb['id']})
 aWeb.wr("<ARTICLE>Result: %s</ARTICLE>"%(res))

#
#
def node_device_id(aWeb):
 res = aWeb.rest_call("device/search",{'device':aWeb['hostname']})
 aWeb.wr(res['device']['id'] if res['found'] > 0 else 'NULL')

#
#
def node_help(aWeb):
 aWeb.wr("""<ARTICLE CLASS='help' STYLE='overflow:auto'><PRE>
 Nodes offers an interface to add and delete nodes for the system

 There are two types of nodes, system generated and user inserted:
  - system generated are created during install phase for that node. These can have settings
  - user generated are for nodes that serves a particular funtion (i.e. a mapping between a name 'node' and the REST URL)

 </PRE></ARTICLE""")

######################################### Tasks ######################################
#
#
def task_report(aWeb):
 res = aWeb.rest_call("system/task_list",{'node':aWeb.node()})
 aWeb.wr("<ARTICLE><P>Tasks</P>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Id</DIV><DIV CLASS=th>Node</DIV><DIV CLASS=th>Frequency</DIV><DIV CLASS=th>Module</DIV><DIV CLASS=th>Function</DIV><DIV CLASS=th>Args</DIV></DIV><DIV CLASS=tbody>")
 for task in res['tasks']:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%(id)s</DIV><DIV CLASS=td>%(node)s</DIV><DIV CLASS=td>%(frequency)s</DIV><DIV CLASS=td>%(module)s</DIV><DIV CLASS=td>%(func)s</DIV><DIV CLASS=td>%(args)s</DIV></DIV>"%task)
 aWeb.wr("</DIV></DIV></ARTICLE>")
