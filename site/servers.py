"""HTML5 Ajax Server module"""
__author__= "Zacharias El Banna"

#
#
def list(aWeb):
 res  = aWeb.rest_call("master/server_list",aWeb.args())
 type = "type=%s"%aWeb['type'] if aWeb.get('type') else "dummy"
 aWeb.wr("<SECTION CLASS=content-left ID=div_content_left>")
 aWeb.wr("<ARTICLE><P>Servers</P>")
 aWeb.wr(aWeb.button('reload',DIV='div_content',URL='servers_list?%s'%type))
 aWeb.wr(aWeb.button('add', DIV='div_content_right',URL='servers_info?id=new&%s'%type,TITLE='Add server'))
 aWeb.wr(aWeb.button('help',DIV='div_content_right',URL='servers_help'))
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Node</DIV><DIV CLASS=th>Service</DIV><DIV CLASS=th>Type</DIV><DIV CLASS=th>&nbsp;</DIV></DIV><DIV CLASS=tbody>")
 for srv in res['services']:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>"%(srv['node'],srv['service'],srv['type']))
  aWeb.wr(aWeb.button('info',DIV='div_content_right',URL='servers_info?id=%s'%(srv['id'])))
  if srv['system']:
   aWeb.wr(aWeb.button('sync',DIV='div_content_right',URL='servers_sync?id=%s'%(srv['id']), SPIN='true', TITLE='Sync server'))
   aWeb.wr(aWeb.button('items',DIV='div_content_right',URL='servers_status?id=%s'%(srv['id']), SPIN='true', TITLE='Server status'))
   aWeb.wr(aWeb.button('reload',DIV='div_content_right',URL='servers_restart?id=%s'%(srv['id']), SPIN='true', TITLE='Server restart'))
  else:
   aWeb.wr(aWeb.button('forward',DIV='main', URL='%s_manage?node=%s'%(srv['service'],srv['node']), TITLE='Server pane'))
  if srv['ui']:
   aWeb.wr(aWeb.button('ui', HREF=srv['ui'], target='blank_', TITLE='Server UI'))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</DIV></DIV></ARTICLE></SECTION>")
 aWeb.wr("<SECTION CLASS=content-right ID=div_content_right></SECTION>")

#
#
def info(aWeb):
 aWeb.wr("<ARTICLE CLASS=info><P>Server</P>")
 args = aWeb.args()
 res  = aWeb.rest_call("master/server_info",args)
 data = res['data']
 aWeb.wr("<FORM ID=servers_info_form>")
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=id VALUE=%s>"%(data['id']))
 aWeb.wr("<DIV CLASS=table STYLE='float:left; width:auto;'><DIV CLASS=tbody>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Id:</DIV><DIV CLASS='td readonly'>%s</DIV></DIV>"%data['id'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Node:</DIV><DIV CLASS=td><SELECT NAME=node>")
 for node in res['nodes']:
  extra = " selected" if (data['node'] == node) else ""
  aWeb.wr("<OPTION VALUE=%s %s>%s</OPTION>"%(node,extra,node))
 aWeb.wr("</SELECT></DIV></DIV>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Server:</DIV><DIV CLASS=td><SELECT NAME=type_id>")
 for srv in res['services']:
  extra = " selected" if (data['type_id'] == srv['id']) else ""
  aWeb.wr("<OPTION VALUE=%s %s>%s (%s)</OPTION>"%(srv['id'],extra,srv['service'],srv['type']))
 aWeb.wr("</SELECT></DIV></DIV>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>UI:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=ui VALUE='%s'></DIV></DIV>"%(data['ui']))
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</FORM>")
 aWeb.wr(aWeb.button('save',    DIV='div_content_right', URL='servers_info?op=update', FRM='servers_info_form'))
 if data['id'] != 'new':
  aWeb.wr(aWeb.button('trash', DIV='div_content_right', URL='servers_delete?id=%s'%(data['id']), MSG='Really delete server?'))
 aWeb.wr("</ARTICLE>")

#
#
def status(aWeb):
 from json import dumps
 res = aWeb.rest_call("master/server_status",{'id':aWeb['id']})
 aWeb.wr("<ARTICLE><PRE>%s<PRE></ARTICLE>"%dumps(res,indent=2,sort_keys=True))

#
#
def restart(aWeb):
 from json import dumps
 res = aWeb.rest_call("master/server_restart",{'id':aWeb['id']})
 aWeb.wr("<ARTICLE><PRE>%s<PRE></ARTICLE>"%dumps(res,indent=2,sort_keys=True))

#
#
def sync(aWeb):
 res = aWeb.rest_call("master/server_sync",{'id':aWeb['id']})
 aWeb.wr("<ARTICLE><PRE>%s</PRE></ARTICLE>"%str(res))


#
#
def delete(aWeb):
 res = aWeb.rest_call("master/server_delete",{'id':aWeb['id']})
 aWeb.wr("<ARTICLE><PRE>%s</PRE></ARTICLE>"%str(res))

#
#
def help(aWeb):
 aWeb.wr("""<ARTICLE CLASS='help' STYLE='overflow:auto'><PRE>
 servers manages the location of various services on nodes => servers (e.g. DNS and DHCP servers). That is the system (!) REST nodes where they offer a service interface

 This is helpful in case:
  - the server doesn't offer a good REST API - then other tools can be used directly on that server
  - there are multiple DNS servers serving different zones
  - there are multiple DHCP servers serving different subnets

 </PRE></ARTICLE""")
