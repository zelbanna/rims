"""Module docstring.

HTML5 Ajax resources calls module

"""
__author__= "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"
__icon__ = 'images/icon-tools.png'

############################################ resources ##############################################
#
def main(aWeb):
 if not aWeb.cookies.get('sdcp'):
  print "<SCRIPT>location.replace('index.cgi')</SCRIPT>"
  return
 print "<NAV><UL>&nbsp;</UL></NAV>"
 print "<SECTION CLASS=content ID=div_content>"
 view(aWeb)
 print "</SECTION>"

#
#
def view(aWeb):
 cookie = aWeb.cookie_unjar('sdcp')
 res = aWeb.rest_call("resources_list",{'type':aWeb.get('type','tool'),'user_id':cookie['id']})
 index = 0;
 print "<DIV CLASS=centered STYLE='align-items:initial'>"
 for row in res['data']:
  print "<DIV STYLE='float:left; min-width:100px; margin:6px;'><A STYLE='font-size:10px;' TITLE='{}'".format(row['title'])
  if row['inline'] == 0:
   print "CLASS='btn menu-btn' TARGET=_blank HREF='{}'>".format(row['href'])
  else:
   print "CLASS='z-op btn menu-btn' DIV=main URL='{}'>".format(row['href'])
  print "<IMG ALT='{0}' SRC='{0}'></A>".format(row['icon'])
  print "</A><BR><SPAN STYLE='width:100px; display:block;'>{}</SPAN>".format(row['title'])
  print "</DIV>"
 print "</DIV>"

#
#
def list(aWeb):
 if not aWeb.cookies.get('sdcp'):
  print "<SCRIPT>location.replace('index.cgi')</SCRIPT>"
  return
 cookie = aWeb.cookie_unjar('sdcp')
 res = aWeb.rest_call("resources_list",{'user_id':cookie['id']})
 print "<SECTION CLASS=content-left ID=div_content_left>"
 print "<ARTICLE><P>Resources</P>"
 print aWeb.button('reload',DIV='div_content', URL='sdcp.cgi?call=resources_list')
 print aWeb.button('add', DIV='div_content_right', URL='sdcp.cgi?call=resources_info&id=new')
 print "<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Type</DIV><DIV CLASS=th>Title</DIV><DIV CLASS=th>&nbsp;</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for row in res['data']:
  print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><DIV CLASS=td><A TITLE='{}' ".format(row['type'],row['title'])
  if row['inline'] == 0:
   print "TARGET=_blank HREF='{}'>".format(row['href'])
  else:
   print "CLASS=z-op DIV=main URL='{}'>".format(row['href'])
  print "{}</A></DIV><DIV CLASS=td>&nbsp;".format(row['title'])
  print aWeb.button('info', DIV='div_content_right', URL='sdcp.cgi?call=resources_info&id=%i'%row['id'])
  if cookie['id'] == str(row['user_id']):
   print aWeb.button('delete', DIV='div_content_right', URL='sdcp.cgi?call=resources_delete&id=%i'%row['id'], MSG='Delete resource?')
  print "</DIV></DIV>"
 print "</DIV></DIV></ARTICLE></SECTION>"
 print "<SECTION CLASS=content-right ID=div_content_right></SECTION>"


#
#
def info(aWeb):
 cookie = aWeb.cookie_unjar('sdcp')
 data  = {'id':aWeb.get('id','new'),'op':aWeb['op']}
 if aWeb['op'] == 'update' or data['id'] == 'new':
  data['title'] = aWeb.get('title','Not set')
  data['href']  = aWeb.get('href','Not set')
  data['type']  = aWeb['type']
  data['icon']  = aWeb['icon']
  data['inline']  = aWeb.get('inline',"0")
  data['private'] = aWeb.get('private',"0")
  data['user_id'] = aWeb.get('user_id',cookie['id'])
  if aWeb['op'] == 'update':
   res = aWeb.rest_call("resources_info",data)
   data['id'] = res['id']
 else:
  data = aWeb.rest_call("resources_info",data)['data']

 print "<ARTICLE><P>Resource entity ({})</P>".format(data['id'])
 print "<FORM ID=sdcp_resource_info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(data['id'])
 print "<INPUT TYPE=HIDDEN NAME=user_id VALUE={}>".format(data['user_id'])
 print "<DIV CLASS=table STYLE='float:left; width:auto;'><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Title:</DIV><DIV    CLASS=td><INPUT NAME=title TYPE=TEXT VALUE='%s' REQUIRED STYLE='min-width:400px'></DIV></DIV>"%data['title']
 print "<DIV CLASS=tr><DIV CLASS=td>HREF:</DIV><DIV     CLASS=td><INPUT NAME=href  TYPE=URL  VALUE='%s' REQUIRED></DIV></DIV>"%data['href']
 print "<DIV CLASS=tr><DIV CLASS=td>Icon URL:</DIV><DIV CLASS=td><INPUT NAME=icon  TYPE=URL  VALUE='%s'></DIV></DIV>"%data['icon']
 print "<DIV CLASS=tr><DIV CLASS=td>Inline:</DIV><DIV   CLASS=td><INPUT NAME=inline  {}                TYPE=CHECKBOX VALUE=1   ></DIV></DIV>".format("checked=checked" if data['inline'] == 1 or data['inline'] == "1" else '')
 print "<DIV CLASS=tr><DIV CLASS=td>Private:</DIV><DIV  CLASS=td><INPUT NAME=private {} {}             TYPE=CHECKBOX VALUE=1   ></DIV></DIV>".format("checked=checked" if data['private'] == 1 or data['private'] == "1" else "","disabled" if cookie['id'] <> str(data['user_id']) else "")
 print "<DIV CLASS=tr><DIV CLASS=td>Type:</DIV>"
 if data['type'] == 'menuitem':
  print "<DIV CLASS=td><INPUT  NAME=type TYPE=TEXT VALUE='menuitem' STYLE='font-style:italic' readonly></DIV>"
 else:
  print "<DIV CLASS=td><SELECT NAME=type>"
  for tp in ['bookmark','demo','tool','menuitem','monitor']:
   print "<OPTION VALUE={} {}>{}</OPTION>".format(tp,"" if data['type'] != tp else 'selected',tp.title())
  print "</SELECT></DIV>"
 print "</DIV></DIV></DIV>"
 print "</FORM>"
 if data['icon'] and data['icon'] != 'NULL':
  print "<A CLASS='btn menu-btn' STYLE='float:left; min-width:52px; font-size:10px; cursor:default;'><IMG ALT={0} SRC='{0}'></A>".format(data['icon'])
 print "<BR>"
 if cookie['id'] == str(data['user_id']):
  if data['id'] != 'new':
   print aWeb.button('delete', DIV='div_content_right', URL='sdcp.cgi?call=resources_delete&id=%s'%data['id'], MSG='Delete resource?')
  print aWeb.button('save',    DIV='div_content_right', URL='sdcp.cgi?call=resources_info&op=update', FRM='sdcp_resource_info_form')
 print "</ARTICLE>"

#
#
def delete(aWeb):
 res = aWeb.rest_call("resources_delete",{'id':aWeb['id']})
 print "<ARTICLE>Result: %s</ARTICLE>"%(res)
