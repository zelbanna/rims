"""HTML5 Ajax Node function module"""
__author__= "Zacharias El Banna"

#
#
def list(aWeb):
 nodes = aWeb.rest_call("system/node_list")['data']
 aWeb.wr("<SECTION CLASS=content-left ID=div_content_left>")
 aWeb.wr("<ARTICLE><P>Nodes</P>")
 aWeb.wr(aWeb.button('reload',DIV='div_content', URL='node_list'))
 aWeb.wr(aWeb.button('add', DIV='div_content_right', URL='node_info?id=new'))
 aWeb.wr(aWeb.button('help', DIV='div_content_right', URL='node_help'))
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Node</DIV><DIV CLASS=th>URL</DIV><DIV CLASS=th>&nbsp;</DIV></DIV><DIV CLASS=tbody>")
 for row in nodes:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td STYLE='max-width:55px; overflow-x:hidden'>%s</DIV><DIV CLASS=td STYLE='max-width:190px; overflow-x:hidden'>%s</DIV><DIV CLASS=td>"%(row['node'],row['url']))
  aWeb.wr(aWeb.button('info',DIV='div_content_right', URL='node_info?id=%s'%row['id'], TITLE='Node info'))
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
def info(aWeb):
 args = aWeb.args()
 data = aWeb.rest_call("system/node_info",args)['data']
 aWeb.wr("<ARTICLE CLASS='info'><P>Node Info</DIV>")
 aWeb.wr("<FORM ID=node_form>")
 aWeb.wr("<DIV CLASS=table STYLE='width:auto'><DIV CLASS=tbody>")
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=id VALUE='%s'>"%(data['id']))
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=device_id ID=device_id VALUE='%s'>"%(data['device_id']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Node:</DIV><DIV CLASS=td><INPUT   TYPE=TEXT NAME=node STYLE='min-width:200px;' VALUE='%s'></DIV></DIV>"%(data['node']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>URL:</DIV><DIV CLASS=td><INPUT    TYPE=URL  NAME=url  STYLE='min-width:200px;' VALUE='%s'></DIV></DIV>"%(data['url']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Device:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=hostname STYLE='min-width:200px;' VALUE='%s'></DIV></DIV>"%(data['hostname']))
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</FORM>")
 aWeb.wr(aWeb.button('search', DIV='device_id', INPUT='true', URL='node_device_id',      FRM='node_form', TITLE='Find matching device id using hostname'))
 aWeb.wr(aWeb.button('save',   DIV='div_content_right',       URL='node_info?op=update', FRM='node_form'))
 if data['id'] != 'new':
  aWeb.wr(aWeb.button('trash',  DIV='div_content_right',       URL='node_delete',         FRM='node_form', MSG='Are you really sure you want to delete node?'))
 aWeb.wr("</ARTICLE>")

#
#
def delete(aWeb):
 res = aWeb.rest_call("system/node_delete",{'id':aWeb['id']})
 aWeb.wr("<ARTICLE>Result: %s</ARTICLE>"%(res))

#
#
def device_id(aWeb):
 res = aWeb.rest_call("device/search",{'node':aWeb['node']})
 aWeb.wr(str(res['device']['id']) if res['found'] > 0 else "NULL")

#
#
def help(aWeb):
 aWeb.wr("""<ARTICLE CLASS='help' STYLE='overflow:auto'><PRE>
 Nodes offers an interface to add and delete nodes for the system

 There are two types of nodes, system generated and user inserted:
  - system generated are created during install phase for that node. These can have settings
  - user generated are for nodes that serves a particular funtion (i.e. a mapping between a name 'node' and the REST URL)

 </PRE></ARTICLE""")
