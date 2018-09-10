"""Module docstring.

HTML5 Ajax Settings module

"""
__author__= "Zacharias El Banna"
__version__ = "1.0GA"
__status__= "Production"

#
#
def list(aWeb):
 if not aWeb.cookie('system'):
  aWeb.wr("<SCRIPT>location.replace('system_login')</SCRIPT>")
  return
 cookie = aWeb.cookie('system')
 res = aWeb.rest_call("system_settings_list",{'node':aWeb['node'],'user_id':cookie['id']})
 aWeb.wr("<SECTION CLASS=content-left ID=div_content_left>")
 aWeb.wr("<ARTICLE><P>Settings</P>")
 aWeb.wr(aWeb.button('reload',DIV='div_content', URL='settings_list?node=%s'%aWeb['node']))
 aWeb.wr(aWeb.button('back',  DIV='div_content', URL='system_node_list'))
 aWeb.wr(aWeb.button('add',   DIV='div_content_right', URL='settings_info?id=new&node=%s'%aWeb['node']))
 aWeb.wr(aWeb.button('info',  DIV='div_content_right', URL='settings_comprehensive?node=%s'%aWeb['node']))
 aWeb.wr(aWeb.button('save',  DIV='div_content_right', URL='settings_save?node=%s'%aWeb['node']))
 aWeb.wr(aWeb.button('help',  DIV='div_content_right', URL='settings_help'))
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Section</DIV><DIV CLASS=th>Parameter</DIV></DIV>")
 aWeb.wr("<DIV CLASS=tbody>")
 for row in res.get('data'):
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>{0}</DIV><DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL='settings_comprehensive?section={1}&node={2}'>{1}</A></DIV><DIV CLASS=td TITLE='{3}'><A CLASS='z-op' DIV=div_content_right URL='settings_info?id={0}&node={2}'>{4}</A></DIV>".format(row['id'],row['section'],aWeb['node'],row['description'],row['parameter']))
  aWeb.wr("</DIV>")
 aWeb.wr("</DIV></DIV></ARTICLE></SECTION>")
 aWeb.wr("<SECTION CLASS=content-right ID=div_content_right></SECTION>")

#
#
def info(aWeb):
 cookie = aWeb.cookie('system')
 args = aWeb.args()
 data = aWeb.rest_call("system_settings_info",args)['data']
 aWeb.wr("<ARTICLE CLASS=info><P>Settings</P>")
 aWeb.wr("<FORM ID=settings_info_form>")
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(data['id']))
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=node VALUE={}>".format(aWeb['node']))
 aWeb.wr("<DIV CLASS=table STYLE='float:left; width:auto;'><DIV CLASS=tbody>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Section:</DIV><DIV CLASS=td><INPUT  NAME=section VALUE='%s'  TYPE=TEXT REQUIRED STYLE='min-width:400px'></DIV></DIV>"%(data['section']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Parameter:</DIV><DIV CLASS=td><INPUT NAME=parameter VALUE='%s' TYPE=TEXT REQUIRED></DIV></DIV>"%(data['parameter']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Value:</DIV><DIV CLASS=td><INPUT NAME=value VALUE='%s' TYPE=TEXT REQUIRED></DIV></DIV>"%data['value'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Description:</DIV><DIV CLASS=td><INPUT NAME=description VALUE='%s' TYPE=TEXT></DIV></DIV>"%(data['description']))
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</FORM>")
 aWeb.wr(aWeb.button('save',    DIV='div_content_right', URL='settings_info?op=update', FRM='settings_info_form'))
 if data['id'] != 'new':
  aWeb.wr(aWeb.button('trash', DIV='div_content_right', URL='settings_delete?id=%s&node=%s'%(data['id'],aWeb['node']), MSG='Delete settings?'))
  aWeb.wr(aWeb.button('add',   DIV='div_content_right', URL='settings_info?id=new&section=%s&node=%s'%(data['section'],aWeb['node'])))
 aWeb.wr("</ARTICLE>")

#
#
def comprehensive(aWeb):
 settings = aWeb.rest_call("system_settings_comprehensive",{'node':aWeb['node'],'section':aWeb['section']})
 aWeb.wr("<ARTICLE><P>Settings</P>")
 for section,parameters in settings.iteritems():
  aWeb.wr("<P>%s</P>"%section)
  aWeb.wr("<DIV CLASS=table STYLE='width:500px;'><DIV CLASS=tbody>")
  for data in parameters:
   aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%s:</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td STYLE='max-width:300px; overflow-x:hidden; font-style:italic;'>\"%s\"</DIV></DIV>"%(data['parameter'],data['value'],data['description']))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</ARTICLE>")

#
#
def delete(aWeb):
 aWeb.wr("<ARTICLE>Delete %s (%s)</ARTICLE>"%(aWeb['id'],aWeb.rest_call("system_settings_delete",{'node':aWeb['node'],'id':aWeb['id']})))

#
#
def save(aWeb):
 aWeb.wr("<ARTICLE>Save: %s</ARTICLE>"%(aWeb.rest_call("system_settings_save&node=%s"%aWeb['node'])))

#
#
def help(aWeb):
 aWeb.wr("""<ARTICLE CLASS='help' STYLE='overflow:auto'><PRE>
 Settings offers an interface to manipulate different settings for a system (REST) node.

 Settings are applied to sections, typically:
  - matching a specific function (e.g. username/passwords for ESXi, Openstack)
  - provides settings for a function like sections: logs -> log x -> location

 </PRE></ARTICLE""")

