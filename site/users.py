"""Module docstring.

HTML5 Ajax Users calls module


"""
__author__= "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"
__icon__ = 'images/icon-users.png'

############################################ Users ##############################################
def main(aWeb):
 if not aWeb.cookies.get('sdcp_id'):
  print "<SCRIPT>location.replace('index.cgi')</SCRIPT>"
  return
 print "<NAV><UL>"
 print "<LI><A CLASS=z-op DIV=div_content_left URL='sdcp.cgi?call=users_list'>Users</A></LI>"
 print "<LI><A CLASS=z-op DIV=div_content_left URL='sdcp.cgi?call=bookings_list'>Bookings</A></LI>"
 print "<LI CLASS='right navinfo'><A CLASS=z-op DIV=div_content_right URL=sdcp.cgi?call=users_info&id={}>{}</A></LI>".format(aWeb.cookies.get('sdcp_id'),aWeb.cookies.get('sdcp_user'))
 print "</UL></NAV>"
 print "<SECTION CLASS=content       ID=div_content>"
 print "<SECTION CLASS=content-left  ID=div_content_left></SECTION>"
 print "<SECTION CLASS=content-right ID=div_content_right></SECTION>"
 print "</SECTION>"

def user(aWeb):
 if not aWeb.cookies.get('sdcp_id'):
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
 from sdcp.core.dbase import DB
 with DB() as db:
  res  = db.do("SELECT id, alias, name, email FROM users ORDER by name")
  rows = db.get_rows()
 print "<ARTICLE><P>Users</P>"
 print aWeb.button('reload', DIV='div_content_left', URL='sdcp.cgi?call=users_list')
 print aWeb.button('add',    DIV='div_content_right',URL='sdcp.cgi?call=users_info&id=new')
 print "<DIV CLASS=table>"
 print "<DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Alias</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>E-mail</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for row in rows:
  print "<DIV CLASS=tr><DIV CLASS=td>{0}</DIV><DIV CLASS=td><A CLASS='z-op' DIV=div_content_right URL='sdcp.cgi?call=users_info&id={0}'>{1}</A></DIV><DIV CLASS=td>{2}</DIV><DIV CLASS=td>{3}</DIV></DIV>".format(row['id'],row['alias'],row['name'],row['email'])
 print "</DIV></DIV></ARTICLE>"

#
#
#
def info(aWeb):
 from sdcp.core.dbase import DB
 data = {}
 data['id'] = aWeb.get('id','new')
 op = aWeb['op']
 from sdcp.rest.resources import list as resource_list
 with DB() as db:
  if op == 'update' or data['id'] == 'new':
   data['name']  = aWeb.get('name',"unknown")
   data['alias'] = aWeb.get('alias',"unknown")
   data['email'] = aWeb.get('email',"unknown")
   data['view']  = aWeb.get('view','0')
   data['menulist'] = aWeb.get('menulist','default')
   if op == 'update':
    if data['id'] == 'new':
     db.do("INSERT INTO users (alias,name,email,menulist,view_public) VALUES ('{}','{}','{}','{}',{})".format(data['alias'],data['name'],data['email'],data['menulist'],data['view']))
     data['id']  = db.get_last_id()
    else:
     db.do("UPDATE users SET alias='{}',name='{}',email='{}',view_public='{}',menulist='{}' WHERE id = '{}'".format(data['alias'],data['name'],data['email'],data['view'],data['menulist'],data['id']))
     if aWeb.cookies['sdcp_id'] == str(data['id']):
      aWeb.cookie_add('sdcp_view',data['view'],86400)
    aWeb.put_headers()
  else:
   db.do("SELECT users.* FROM users WHERE id = '{}'".format(data['id']))
   data = db.get_row()
   data['view']  = str(data['view_public'])

 resources = resource_list({'id':aWeb.cookies['sdcp_id'], 'dict':'id'})['data']
 print "<!-- %s -->"%(aWeb.cookies['sdcp_id'])
 print aWeb.dragndrop()
 print "<ARTICLE CLASS='info'><P>User Info ({})</P>".format(data['id'])
 print "<FORM ID=sdcp_user_info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(data['id'])
 print "<INPUT TYPE=HIDDEN NAME=menulist ID=menulist VALUE='{}'>".format(data['menulist'])
 print "<DIV CLASS=table><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Alias:</DIV>  <DIV CLASS=td><INPUT NAME=alias  TYPE=TEXT  VALUE='{}' STYLE='min-width:400px'></DIV></DIV>".format(data['alias'])
 print "<DIV CLASS=tr><DIV CLASS=td>Name:</DIV>   <DIV CLASS=td><INPUT NAME=name   TYPE=TEXT  VALUE='{}' STYLE='min-width:400px'></DIV></DIV>".format(data['name'])
 print "<DIV CLASS=tr><DIV CLASS=td>E-mail:</DIV> <DIV CLASS=td><INPUT NAME=email  TYPE=email VALUE='{}' STYLE='min-width:400px'></DIV></DIV>".format(data['email'])
 print "<DIV CLASS=tr><DIV CLASS=td>View All:</DIV><DIV CLASS=td><INPUT NAME=view  TYPE=CHECKBOX VALUE=1 {}                  {}></DIV></DIV>".format("checked=checked" if str(data['view']) == "1" else "","disabled" if aWeb.cookies['sdcp_id'] <> str(data['id']) else "")
 print "</DIV></DIV>"
 print "<SPAN>Menu list</SPAN>"
 print "<DIV CLASS='border' STYLE='display:flex; flex-wrap:wrap; min-height:100px;'><UL STYLE='width:100%' ID=ul_menu DEST=menulist CLASS='drop'>"
 if not data.get('menulist') == 'default':
  for key in data['menulist'].split(','):
   try: 
    resource = resources.pop(int(key),None)
    print "<LI CLASS='drag' ID=%s><A CLASS='btn menu-btn' STYLE='font-size:10px;' TITLE='%s'><IMG SRC='%s'></A></LI>"%(key,resource['title'],resource['icon'])
   except: pass
 else:
  for key in resources.keys():
   if resources[key]['type'] == 'menuitem':
    resource = resources.pop(key,None)
    print "<LI CLASS='drag' ID=%s><A CLASS='btn menu-btn' STYLE='font-size:10px;' TITLE='%s'><IMG SRC='%s'></A></LI>"%(key,resource['title'],resource['icon'])    
 print "</UL></DIV>"
 print "<DIV CLASS='controls'>"
 if data['id'] != 'new' and ((aWeb.cookies.get('sdcp_id') == str(data['id']) or aWeb.cookies.get('sdcp_id') == "1")):
  print aWeb.button('delete',DIV='div_content_right',URL='sdcp.cgi?call=users_remove&id={0}'.format(data['id']), MSG='Really remove user?')
 print aWeb.button('save',DIV='div_content_right', URL='sdcp.cgi?call=users_info&headers=no&op=update', FRM='sdcp_user_info_form')
 print "</DIV>"
 print "</FORM>"
 print "<DIV STYLE='display:flex; flex-wrap:wrap;'><UL STYLE='width:100%' ID=ul_avail CLASS='drop'>"
 for id,resource in resources.iteritems():
  print "<LI CLASS='drag' ID=%s><A CLASS='btn menu-btn' STYLE='font-size:10px;' TITLE='%s'><IMG SRC='%s'></A></LI>"%(id,resource['title'],resource['icon'])
 print "</UL></DIV>"
 print "</ARTICLE>"

#
#
def remove(aWeb):
 from sdcp.core.dbase import DB
 with DB() as db:
  res = db.do("DELETE FROM users WHERE id = '{}'".format(aWeb['id']))
 print "<ARTICLE>User with id {} removed ({})</ARTICLE>".format(aWeb['id'],"OK" if res == 1 else "NOT_OK")
