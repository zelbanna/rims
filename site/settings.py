"""Module docstring.

HTML5 Ajax Settings calls module

"""
__author__= "Zacharias El Banna"
__version__ = "18.03.14GA"
__status__= "Production"

#
#
def list(aWeb):
 if not aWeb.cookies.get('sdcp'):
  print "<SCRIPT>location.replace('index.cgi')</SCRIPT>"
  return
 cookie = aWeb.cookie_unjar('sdcp')
 res = aWeb.rest_call("settings_list",{'node':aWeb['node'],'user_id':cookie['id']})
 print "<SECTION CLASS=content-left ID=div_content_left>"
 print "<ARTICLE><P>Settings</P>"
 print "<DIV CLASS=controls>"
 print aWeb.button('reload',DIV='div_content', URL='sdcp.cgi?call=settings_list&node=%s'%aWeb['node'])
 print aWeb.button('add', DIV='div_content_right', URL='sdcp.cgi?call=settings_info&id=new&node=%s'%aWeb['node'])
 print aWeb.button('document', DIV='div_content_right', URL='sdcp.cgi?call=settings_view&node=%s'%aWeb['node'])
 print aWeb.button('save', DIV='div_content_right', URL='sdcp.cgi?call=settings_save&node=%s'%aWeb['node'])
 print "</DIV>"
 print "<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Section</DIV><DIV CLASS=th>Parameter</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for row in res.get('data'):
  print "<DIV CLASS=tr><DIV CLASS=td>{0}</DIV><DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL='sdcp.cgi?call=settings_view&section={1}&node={2}'>{1}</A></DIV><DIV CLASS=td TITLE='{3}'><A CLASS='z-op' DIV=div_content_right URL='sdcp.cgi?call=settings_info&id={0}&node={2}'>{4}</A></DIV>".format(row['id'],row['section'],aWeb['node'],row['description'],row['parameter'])
  print "</DIV>"
 print "</DIV></DIV></ARTICLE></SECTION>"
 print "<SECTION CLASS=content-right ID=div_content_right></SECTION>"

#
#
def info(aWeb):
 cookie = aWeb.cookie_unjar('sdcp')
 data = {'id':aWeb.get('id','new'),'node':aWeb['node']}
 if aWeb['op'] == 'update' or aWeb['id'] == 'new':
  data['op']       = aWeb['op']
  data['value']    = aWeb.get('value','Not set')
  data['section']  = aWeb.get('section','Not set')
  data['parameter'] = aWeb.get('parameter','Not set')
  data['description'] = aWeb.get('description','Not set') 
  if aWeb['op'] == 'update':
   data = aWeb.rest_call("settings_info",data)['data']
 else:
  data = aWeb.rest_call("settings_info",data)['data']
 print "<ARTICLE CLASS=info><P>Settings</P>"
 print "<FORM ID=sdcp_settings_info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(data['id'])
 print "<INPUT TYPE=HIDDEN NAME=node VALUE={}>".format(aWeb['node'])
 print "<DIV CLASS=table STYLE='float:left; width:auto;'><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Section:</DIV><DIV CLASS=td><INPUT  NAME=section VALUE='%s'  TYPE=TEXT REQUIRED STYLE='min-width:400px'></DIV></DIV>"%(data['section'])
 print "<DIV CLASS=tr><DIV CLASS=td>Parameter:</DIV><DIV CLASS=td><INPUT NAME=parameter VALUE='%s' TYPE=TEXT REQUIRED></DIV></DIV>"%(data['parameter'])
 print "<DIV CLASS=tr><DIV CLASS=td>Value:</DIV><DIV CLASS=td><INPUT NAME=value VALUE='%s' TYPE=TEXT REQUIRED></DIV></DIV>"%data['value']
 print "<DIV CLASS=tr><DIV CLASS=td>Description:</DIV><DIV CLASS=td><INPUT NAME=description VALUE='%s' TYPE=TEXT></DIV></DIV>"%(data['description'])
 print "</DIV></DIV>"
 print "</FORM><DIV CLASS=controls>"
 print aWeb.button('save',    DIV='div_content_right', URL='sdcp.cgi?call=settings_info&op=update', FRM='sdcp_settings_info_form')
 if data['id'] != 'new':
  print aWeb.button('delete', DIV='div_content_right', URL='sdcp.cgi?call=settings_delete&id=%s&node=%s'%(data['id'],aWeb['node']), MSG='Delete settings?')
  print aWeb.button('add',    DIV='div_content_right', URL='sdcp.cgi?call=settings_info&id=new&section=%s&node=%s'%(data['section'],aWeb['node']))
 print "</DIV></ARTICLE>"

#
#
def view(aWeb):
 settings = aWeb.rest_call("settings_all",{'node':aWeb['node'],'section':aWeb['section']})
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
 print "<ARTICLE>Delete %s (%s)</ARTICLE>"%(aWeb['id'],aWeb.rest_call("settings_delete",{'node':aWeb['node'],'id':aWeb['id']}))

#
#
def save(aWeb):
 print "<ARTICLE>Save: %s</ARTICLE>"%(aWeb.rest_call("tools_settings_save&node=%s"%aWeb['node']))
