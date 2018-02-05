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
 res = aWeb.rest_call("settings_list",{'user_id':cookie['id']})
 print "<SECTION CLASS=content-left ID=div_content_left>"
 print "<ARTICLE><P>Settings</P>"
 print aWeb.button('reload',DIV='div_content', URL='sdcp.cgi?call=settings_list')
 print aWeb.button('add', DIV='div_content_right', URL='sdcp.cgi?call=settings_info&id=new')
 print "<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Type</DIV><DIV CLASS=th>Parameter</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for row in res['data']:
  print "<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td TITLE='%s'>%s</DIV>"%(row['id'],row['type'],row['description'],row['parameter'])
  print "</DIV>"
 print "</DIV></DIV></ARTICLE></SECTION>"
 print "<SECTION CLASS=content-right ID=div_content_right></SECTION>"

#
#
def info(aWeb):
 from os import listdir, path
 cookie = aWeb.cookie_unjar('sdcp')
 data  = {'id':aWeb.get('id','new'),'op':aWeb['op']}
 if aWeb['op'] == 'update' or data['id'] == 'new':
  data['type']        = aWeb.get('type','Not set')
  data['parameter']   = aWeb.get('parameter','Not set')
  data['value']       = aWeb.get('value','Not set')
  data['description'] = aWeb.get('description','Not set') 
  if aWeb['op'] == 'update':
   res = aWeb.rest_call("settings_info",data)
   data['id'] = res['id']
 else:
  data = aWeb.rest_call("settings_info",data)['data']
 print "<ARTICLE CLASS=info><P>Settings ({})</P>".format(data['id'])
 print "<FORM ID=sdcp_settings_info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(data['id'])
 print "<DIV CLASS=table STYLE='float:left; width:auto;'><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Type:</DIV><DIV CLASS=td><INPUT  NAME=type VALUE='%s'  TYPE=TEXT REQUIRED STYLE='min-width:400px'></DIV></DIV>"%data['type']
 print "<DIV CLASS=tr><DIV CLASS=td>Parameter:</DIV><DIV CLASS=td><INPUT NAME=parameter VALUE='%s' TYPE=TEXT REQUIRED></DIV></DIV>"%data['parameter']
 print "<DIV CLASS=tr><DIV CLASS=td>Value:</DIV><DIV CLASS=td><INPUT NAME=value VALUE='%s' TYPE=TEXT REQUIRED></DIV></DIV>"%data['value']
 print "<DIV CLASS=tr><DIV CLASS=td>Value:</DIV><DIV CLASS=td><INPUT NAME=description VALUE='%s' TYPE=TEXT></DIV></DIV>"%data['description']
 print "</DIV></DIV>"
 print "</FORM><BR>"
 if data['id'] != 'new':
  print aWeb.button('delete', DIV='div_content_right', URL='sdcp.cgi?call=settings_delete&id=%s'%data['id'], MSG='Delete settings?')
 print aWeb.button('save',    DIV='div_content_right', URL='sdcp.cgi?call=settings_info&op=update', FRM='sdcp_settings_info_form')
 print "</ARTICLE>"

#
