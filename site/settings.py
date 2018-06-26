"""Module docstring.

HTML5 Ajax Settings module

"""
__author__= "Zacharias El Banna"
__version__ = "1.0GA"
__status__= "Production"

#
#
def list(aWeb):
 if not aWeb.cookies.get('system'):
  print "<SCRIPT>location.replace('index.cgi')</SCRIPT>"
  return
 cookie = aWeb.cookie_unjar('system')
 res = aWeb.rest_call("system_settings_list",{'node':aWeb['node'],'user_id':cookie['id']})
 print "<SECTION CLASS=content-left ID=div_content_left>"
 print "<ARTICLE><P>Settings</P>"
 print "<DIV CLASS=controls>"
 print aWeb.button('reload',DIV='div_content', URL='zdcp.cgi?settings_list&node=%s'%aWeb['node'])
 print aWeb.button('add',   DIV='div_content_right', URL='zdcp.cgi?settings_info&id=new&node=%s'%aWeb['node'])
 print aWeb.button('info',  DIV='div_content_right', URL='zdcp.cgi?settings_comprehensive&node=%s'%aWeb['node'])
 print aWeb.button('save',  DIV='div_content_right', URL='zdcp.cgi?settings_save&node=%s'%aWeb['node'])
 print aWeb.button('help',  DIV='div_content_right', URL='zdcp.cgi?settings_help')
 print "</DIV>"
 print "<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Section</DIV><DIV CLASS=th>Parameter</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for row in res.get('data'):
  print "<DIV CLASS=tr><DIV CLASS=td>{0}</DIV><DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL='zdcp.cgi?settings_comprehensive&section={1}&node={2}'>{1}</A></DIV><DIV CLASS=td TITLE='{3}'><A CLASS='z-op' DIV=div_content_right URL='zdcp.cgi?settings_info&id={0}&node={2}'>{4}</A></DIV>".format(row['id'],row['section'],aWeb['node'],row['description'],row['parameter'])
  print "</DIV>"
 print "</DIV></DIV></ARTICLE></SECTION>"
 print "<SECTION CLASS=content-right ID=div_content_right></SECTION>"

#
#
def info(aWeb):
 cookie = aWeb.cookie_unjar('system')
 args = aWeb.get_args2dict()
 data = aWeb.rest_call("system_settings_info",args)['data']
 print "<ARTICLE CLASS=info><P>Settings</P>"
 print "<FORM ID=settings_info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(data['id'])
 print "<INPUT TYPE=HIDDEN NAME=node VALUE={}>".format(aWeb['node'])
 print "<DIV CLASS=table STYLE='float:left; width:auto;'><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Section:</DIV><DIV CLASS=td><INPUT  NAME=section VALUE='%s'  TYPE=TEXT REQUIRED STYLE='min-width:400px'></DIV></DIV>"%(data['section'])
 print "<DIV CLASS=tr><DIV CLASS=td>Parameter:</DIV><DIV CLASS=td><INPUT NAME=parameter VALUE='%s' TYPE=TEXT REQUIRED></DIV></DIV>"%(data['parameter'])
 print "<DIV CLASS=tr><DIV CLASS=td>Value:</DIV><DIV CLASS=td><INPUT NAME=value VALUE='%s' TYPE=TEXT REQUIRED></DIV></DIV>"%data['value']
 print "<DIV CLASS=tr><DIV CLASS=td>Description:</DIV><DIV CLASS=td><INPUT NAME=description VALUE='%s' TYPE=TEXT></DIV></DIV>"%(data['description'])
 print "</DIV></DIV>"
 print "</FORM><DIV CLASS=controls>"
 print aWeb.button('save',    DIV='div_content_right', URL='zdcp.cgi?settings_info&op=update', FRM='settings_info_form')
 if data['id'] != 'new':
  print aWeb.button('trash', DIV='div_content_right', URL='zdcp.cgi?settings_delete&id=%s&node=%s'%(data['id'],aWeb['node']), MSG='Delete settings?')
  print aWeb.button('add',   DIV='div_content_right', URL='zdcp.cgi?settings_info&id=new&section=%s&node=%s'%(data['section'],aWeb['node']))
 print "</DIV></ARTICLE>"

#
#
def comprehensive(aWeb):
 settings = aWeb.rest_call("system_settings_comprehensive",{'node':aWeb['node'],'section':aWeb['section']})
 print "<ARTICLE><P>Settings</P>"
 for section,parameters in settings.iteritems():
  print "<P>%s</P>"%section
  print "<DIV CLASS=table STYLE='width:500px;'><DIV CLASS=tbody>"
  for data in parameters:
   print "<DIV CLASS=tr><DIV CLASS=td>%s:</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td STYLE='max-width:300px; overflow-x:hidden; font-style:italic;'>\"%s\"</DIV></DIV>"%(data['parameter'],data['value'],data['description'])
  print "</DIV></DIV>"
 print "</ARTICLE>"

#
#
def delete(aWeb):
 print "<ARTICLE>Delete %s (%s)</ARTICLE>"%(aWeb['id'],aWeb.rest_call("system_settings_delete",{'node':aWeb['node'],'id':aWeb['id']}))

#
#
def save(aWeb):
 print "<ARTICLE>Save: %s</ARTICLE>"%(aWeb.rest_call("system_settings_save&node=%s"%aWeb['node']))

#
#
def help(aWeb):
 print """<ARTICLE CLASS='help' STYLE='overflow:auto'><PRE>
 Settings offers an interface to manipulate different settings for a system (REST) node.

 Settings are applied to sections, typically:
  - matching a specific function (e.g. username/passwords for ESXi, Openstack)
  - indicating on which node a function resides (like DNS server's node and type)

 </PRE></ARTICLE"""

