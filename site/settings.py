"""Module docstring.

HTML5 Ajax Settings calls module

"""
__author__= "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__= "Production"

#
#
def list(aWeb):
 if not aWeb.cookies.get('sdcp'):
  print "<SCRIPT>location.replace('index.cgi')</SCRIPT>"
  return
 cookie = aWeb.cookie_unjar('sdcp')
 host = aWeb.rest_call("settings_info",{'id':aWeb['host']})['data']
 res = aWeb.rest_generic(host['value'],"settings_list",{'user_id':cookie['id']})
 print "<SECTION CLASS=content-left ID=div_content_left>"
 print "<ARTICLE><P>Settings</P>"
 print aWeb.button('reload',DIV='div_content', URL='sdcp.cgi?call=settings_list&host=%s'%aWeb['host'])
 print aWeb.button('add', DIV='div_content_right', URL='sdcp.cgi?call=settings_info&id=new&host=%s'%aWeb['host'])
 print aWeb.button('document', DIV='div_content_right', URL='sdcp.cgi?call=settings_view&host=%s'%aWeb['host'])
 print aWeb.button('save', DIV='div_content_right', URL='sdcp.cgi?call=settings_save&host=%s'%aWeb['host'])
 print "<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Section</DIV><DIV CLASS=th>Parameter</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for row in res['data']:
  print "<DIV CLASS=tr><DIV CLASS=td>{0}</DIV><DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL='sdcp.cgi?call=settings_view&section={1}&host={2}'>{1}</A></DIV><DIV CLASS=td TITLE='{3}'><A CLASS='z-op' DIV=div_content_right URL='sdcp.cgi?call=settings_info&id={0}&host={2}'>{4}</A></DIV>".format(row['id'],row['section'],aWeb['host'],row['description'],row['parameter'])
  print "</DIV>"
 print "</DIV></DIV></ARTICLE></SECTION>"
 print "<SECTION CLASS=content-right ID=div_content_right></SECTION>"

#
#
def info(aWeb):
 cookie = aWeb.cookie_unjar('sdcp')
 host   = aWeb.rest_call("settings_info",{'id':aWeb['host']})['data']
 data  = {'id':aWeb.get('id','new')}
 if aWeb['op'] == 'update' or aWeb['id'] == 'new':
  data['required'] = aWeb.get('required','0')
  data['op']       = aWeb['op']
  data['value']    = aWeb.get('value','Not set')
  data['section']  = aWeb.get('section','Not set')
  data['parameter'] = aWeb.get('parameter','Not set')
  data['description'] = aWeb.get('description','Not set') 
  if aWeb['op'] == 'update':
   data = aWeb.rest_generic(host['value'],"settings_info",data)['data']
 else:
  data = aWeb.rest_generic(host['value'],"settings_info",data)['data']
 readonly = "readonly" if str(data['required']) == '1' else ""
 print "<ARTICLE CLASS=info><P>Settings</P>"
 print "<FORM ID=sdcp_settings_info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(data['id'])
 print "<INPUT TYPE=HIDDEN NAME=required VALUE={}>".format(data['required'])
 print "<INPUT TYPE=HIDDEN NAME=host VALUE={}>".format(aWeb['host'])
 print "<DIV CLASS=table STYLE='float:left; width:auto;'><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Section:</DIV><DIV CLASS=td><INPUT  NAME=section VALUE='%s'  TYPE=TEXT REQUIRED %s STYLE='min-width:400px'></DIV></DIV>"%(data['section'],readonly)
 print "<DIV CLASS=tr><DIV CLASS=td>Parameter:</DIV><DIV CLASS=td><INPUT NAME=parameter VALUE='%s' TYPE=TEXT REQUIRED %s></DIV></DIV>"%(data['parameter'],readonly)
 print "<DIV CLASS=tr><DIV CLASS=td>Value:</DIV><DIV CLASS=td><INPUT NAME=value VALUE='%s' TYPE=TEXT REQUIRED></DIV></DIV>"%data['value']
 print "<DIV CLASS=tr><DIV CLASS=td>Description:</DIV><DIV CLASS=td><INPUT NAME=description VALUE='%s' TYPE=TEXT %s></DIV></DIV>"%(data['description'],readonly)
 print "</DIV></DIV>"
 print "</FORM><BR><DIV CLASS=controls>"
 print aWeb.button('save',    DIV='div_content_right', URL='sdcp.cgi?call=settings_info&op=update', FRM='sdcp_settings_info_form')
 if data['id'] != 'new':
  print aWeb.button('delete', DIV='div_content_right', URL='sdcp.cgi?call=settings_delete&id=%s&host=%s'%(data['id'],aWeb['host']), MSG='Delete settings?')
  print aWeb.button('add',    DIV='div_content_right', URL='sdcp.cgi?call=settings_info&id=new&section=%s&host=%s'%(data['section'],aWeb['host']))
 print "</DIV></ARTICLE>"

#
#
def view(aWeb):
 host     = aWeb.rest_call("settings_info",{'id':aWeb['host']})['data']
 settings = aWeb.rest_generic(host['value'],"settings_all",{'section':aWeb['section']})
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
 host   = aWeb.rest_call("settings_info",{'id':aWeb['host']})['data']
 print "<ARTICLE>Delete %s (%s)</ARTICLE>"%(aWeb['id'],aWeb.rest_generic(host['value'],"settings_delete",{'id':aWeb['id']}))

#
#
def save(aWeb):
 host   = aWeb.rest_call("settings_info",{'id':aWeb['host']})['data']
 print "<ARTICLE>Save: %s</ARTICLE>"%(aWeb.rest_generic(host['value'],"settings_save"))
