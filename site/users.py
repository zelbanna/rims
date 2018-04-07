"""Module docstring.

HTML5 Ajax Users calls module


"""
__author__= "Zacharias El Banna"
__version__ = "18.04.07GA"
__status__ = "Production"
__icon__ = 'images/icon-users.png'
__type__ = 'menuitem'

############################################ Users ##############################################
def main(aWeb):
 if not aWeb.cookies.get('system'):
  print "<SCRIPT>location.replace('index.cgi')</SCRIPT>"
  return
 cookie = aWeb.cookie_unjar('system')
 info = aWeb.rest_call("system_users_info",{'id':cookie['id']})
 print "<NAV><UL>"
 print "<LI><A CLASS=z-op DIV=div_content URL='sdcp.cgi?call=users_list'>Users</A></LI>"
 print "<LI><A CLASS=z-op DIV=div_content URL='sdcp.cgi?call=bookings_list'>Bookings</A></LI>"
 print "<LI CLASS='right navinfo'><A>%s</A></LI>"%info['data']['name']
 print "</UL></NAV>"
 print "<SECTION CLASS=content       ID=div_content></SECTION>"

def user(aWeb):
 if not aWeb.cookies.get('system'):
  print "<SCRIPT>location.replace('index.cgi')</SCRIPT>"
  return
 print "<NAV><UL></UL></NAV>"
 print "<SECTION CLASS=content       ID=div_content>"
 print "<SECTION CLASS=content-left  ID=div_content_left></SECTION>"
 print "<SECTION CLASS=content-right ID=div_content_right>"
 info(aWeb)
 print "</SECTION>"
 print "</SECTION>"

def list(aWeb):
 rows = aWeb.rest_call("system_users_list")['data']
 print "<SECTION CLASS=content-left  ID=div_content_left>"
 print "<ARTICLE><P>Users</P><DIV CLASS=controls>"
 print aWeb.button('reload', DIV='div_content', URL='sdcp.cgi?call=users_list')
 print aWeb.button('add',    DIV='div_content_right',URL='sdcp.cgi?call=users_info&id=new')
 print "</DIV><DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Alias</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>E-mail</DIV></DIV><DIV CLASS=tbody>"
 for row in rows:
  print "<DIV CLASS=tr><DIV CLASS=td>{0}</DIV><DIV CLASS=td><A CLASS='z-op' DIV=div_content_right URL='sdcp.cgi?call=users_info&id={0}'>{1}</A></DIV><DIV CLASS=td>{2}</DIV><DIV CLASS=td>{3}</DIV></DIV>".format(row['id'],row['alias'],row['name'],row['email'])
 print "</DIV></DIV></ARTICLE></SECTION>"
 print "<SECTION CLASS=content-right ID=div_content_right></SECTION>"

#
#
def info(aWeb):
 cookie = aWeb.cookie_unjar('system')
 args = aWeb.get_args2dict(['call'])
 data = aWeb.rest_call("system_users_info",args)['data']
 resources = aWeb.rest_call("system_resources_list",{'user_id':cookie['id'], 'dict':'id','view_public':True,'node':aWeb.id})['data']
 print aWeb.dragndrop()
 print "<ARTICLE CLASS='info'><P>User Info (%s)</P>"%(data['id'])
 print "<FORM ID=user_info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(data['id'])
 print "<INPUT TYPE=HIDDEN NAME=menulist ID=menulist VALUE='{}'>".format(data['menulist'])
 print "<DIV CLASS=table><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Alias:</DIV>  <DIV CLASS=td><INPUT NAME=alias  TYPE=TEXT  VALUE='{}' STYLE='min-width:400px'></DIV></DIV>".format(data['alias'])
 print "<DIV CLASS=tr><DIV CLASS=td>Name:</DIV>   <DIV CLASS=td><INPUT NAME=name   TYPE=TEXT  VALUE='{}' STYLE='min-width:400px'></DIV></DIV>".format(data['name'])
 print "<DIV CLASS=tr><DIV CLASS=td>E-mail:</DIV> <DIV CLASS=td><INPUT NAME=email  TYPE=email VALUE='{}' STYLE='min-width:400px'></DIV></DIV>".format(data['email'])
 print "<DIV CLASS=tr><DIV CLASS=td>View All:</DIV><DIV CLASS=td><INPUT NAME=view_public TYPE=CHECKBOX VALUE=1 {}             {}></DIV></DIV>".format("checked=checked" if str(data['view_public']) == "1" else "","disabled" if cookie['id'] <> str(data['id']) else "")
 print "<DIV CLASS=tr><DIV CLASS=td>Cookie:</DIV><DIV CLASS='td small-text'>%s</DIV></DIV>"%",".join(['%s=%s'%(k,v) for k,v in cookie.iteritems()])
 print "</DIV></DIV><SPAN>Menu list</SPAN>"
 print "<DIV CLASS='border' STYLE='display:flex; flex-wrap:wrap; min-height:100px;'><UL STYLE='width:100%' ID=ul_menu DEST=menulist CLASS='drop'>"
 menulist = data['menulist'].split(',') if not data.get('menulist') == 'default' else [ value['id'] for key,value in resources.iteritems() if value['type'] == 'menuitem']
 for key in menulist:
  try: 
   resource = resources.pop(key,None)
   print "<LI CLASS='drag' ID={0}><BUTTON CLASS='menu' STYLE='font-size:10px;' TITLE='{1}'><IMG SRC='{2}' ALT='{1}'></BUTTON></LI>".format(key,resource['title'],resource['icon'])
  except: pass
 print "</UL></DIV>"
 print "</FORM><DIV CLASS=controls>"
 print aWeb.button('save',DIV='div_content_right', URL='sdcp.cgi?call=users_info&op=update', FRM='user_info_form')
 if data['id'] != 'new' and ((cookie['id'] == str(data['id']) or cookie['id'] == "1")):
  print aWeb.button('trash',DIV='div_content_right',URL='sdcp.cgi?call=users_delete&id={0}'.format(data['id']), MSG='Really remove user?')
 print "</DIV>"
 print "<DIV STYLE='display:flex; flex-wrap:wrap;'><UL STYLE='width:100%' ID=ul_avail CLASS='drop'>"
 for id,resource in resources.iteritems():
  print "<LI CLASS='drag' ID={0}><BUTTON CLASS='menu' STYLE='font-size:10px;' TITLE='{1}'><IMG SRC='{2}' ALT='{1}'></BUTTON></LI>".format(id,resource['title'],resource['icon'])
 print "</UL></DIV>"
 print "</ARTICLE>"

#
#
def delete(aWeb):
 res = aWeb.rest_call("system_users_delete",{'id':aWeb['id']})
 print "<ARTICLE>User with id %s removed(%s)</ARTICLE>"%(aWeb['id'],res)
