"""Module docstring.

Ajax Users calls module

"""
__author__= "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__= "Production"

############################################ Users ##############################################
def main(aWeb):
 if not aWeb.cookie.get('sdcp_id'):
  print "<SCRIPT>location.replace('index.cgi')</SCRIPT>"
  return
 print "<DIV CLASS=z-navbar ID=div_navbar>"
 print "<A CLASS=z-op DIV=div_content_left URL='sdcp.cgi?call=users_list'>Users</A>"
 print "<A CLASS=z-op DIV=div_content_left URL='sdcp.cgi?call=bookings_list'>Bookings</A>"
 print "<A CLASS='z-right z-op' OP=logout style='background-color:red;' URL=sdcp.cgi>Log out</A>"
 print "<A CLASS='z-right z-op z-navinfo' DIV=div_content_right URL=sdcp.cgi?call=users_info&id={}>{}</A>".format(aWeb.cookie.get('sdcp_id'),aWeb.cookie.get('sdcp_user'))
 print "</DIV>"
 print "<DIV CLASS=z-content ID=div_content>"
 print "<DIV CLASS=z-content-left  ID=div_content_left></DIV>"
 print "<DIV CLASS=z-content-right ID=div_content_right></DIV>"
 print "</DIV>"


def list(aWeb):
 from sdcp.core.dbase import DB
 with DB() as db:
  res  = db.do("SELECT id, alias, name, email FROM users ORDER by name")
  rows = db.get_rows()
 print "<DIV CLASS=z-frame><DIV CLASS=title>Users</DIV>"
 print "<A TITLE='Reload List' CLASS='z-btn z-small-btn z-op' DIV=div_content_left URL='sdcp.cgi?call=users_list'><IMG SRC='images/btn-reload.png'></A>"
 print "<A TITLE='Add User'    CLASS='z-btn z-small-btn z-op' DIV=div_content_right   URL='sdcp.cgi?call=users_info&id=new'><IMG SRC='images/btn-add.png'></A>"
 print "<DIV CLASS=z-table>"
 print "<DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Alias</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>E-mail</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for row in rows:
  print "<DIV CLASS=tr><DIV CLASS=td>{0}</DIV><DIV CLASS=td><A CLASS='z-op' DIV=div_content_right URL='sdcp.cgi?call=users_info&id={0}'>{1}</A></DIV><DIV CLASS=td>{2}</DIV><DIV CLASS=td>{3}</DIV></DIV>".format(row['id'],row['alias'],row['name'],row['email'])
 print "</DIV></DIV></DIV>"

#
#
#
def info(aWeb):
 from sdcp.core.dbase import DB
 data = {}
 data['id'] = aWeb.get('id','new')
 op = aWeb['op']
 with DB() as db:
  db.do("SELECT id,title FROM resources")
  resources = db.get_rows()
  resources.insert(0,{'id':'NULL','title':'default'})
  if op == 'update' or data['id'] == 'new':
   data['name']  = aWeb.get('name',"unknown")
   data['alias'] = aWeb.get('alias',"unknown")
   data['email'] = aWeb.get('email',"unknown")
   data['front'] = aWeb.get('front','NULL')
   data['view']  = aWeb.get('view','1')
   if op == 'update':
    if data['id'] == 'new':
     db.do("INSERT INTO users (alias,name,email,frontpage,view_public) VALUES ('{}','{}','{}','{}',{})".format(data['alias'],data['name'],data['email'],data['front'],data['view']))
     data['id']  = db.get_last_id()
    else:
     db.do("UPDATE users SET alias='{}',name='{}',email='{}',view_public='{}',frontpage={} WHERE id = '{}'".format(data['alias'],data['name'],data['email'],data['view'],data['front'],data['id']))
     if aWeb.cookie['sdcp_id'] == str(data['id']):
      aWeb.add_cookie('sdcp_view',data['view'],86400)
    aWeb.put_headers()
  else:
   db.do("SELECT users.* FROM users WHERE id = '{}'".format(data['id']))
   data = db.get_row()
   data['front'] = str(data['frontpage'])
   data['view']  = str(data['view_public'])

 print "<DIV CLASS=z-frame>"
 print "<DIV CLASS=title>User Info ({})</DIV>".format(data['id'])
 print "<FORM ID=sdcp_user_info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(data['id'])
 print "<DIV CLASS=z-table style='width:auto'><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Alias:</DIV>  <DIV CLASS=td><INPUT NAME=alias  TYPE=TEXT VALUE='{}' STYLE='min-width:400px'></DIV></DIV>".format(data['alias'])
 print "<DIV CLASS=tr><DIV CLASS=td>Name:</DIV>   <DIV CLASS=td><INPUT NAME=name   TYPE=TEXT VALUE='{}' STYLE='min-width:400px'></DIV></DIV>".format(data['name'])
 print "<DIV CLASS=tr><DIV CLASS=td>E-mail:</DIV> <DIV CLASS=td><INPUT NAME=email  TYPE=TEXT VALUE='{}' STYLE='min-width:400px'></DIV></DIV>".format(data['email'])
 print "<DIV CLASS=tr><DIV CLASS=td>View All:</DIV><DIV CLASS=td><INPUT NAME=view  TYPE=CHECKBOX VALUE=1 {}                  {}></DIV></DIV>".format("checked=checked" if data['view'] == 1 or data['view'] == "1" else '',"disabled" if aWeb.cookie['sdcp_id'] <> str(data['id']) else "")
 print "<DIV CLASS=tr><DIV CLASS=td>Front page:</DIV><DIV CLASS=td><SELECT NAME=front STYLE='min-width:400px'>"
 for resource in resources:
  print "<OPTION VALUE='{0}' {2}>{1}</OPTION>".format(resource['id'],resource['title'],"selected" if str(resource['id']) == data['front'] else '')
 print "</SELECT></DIV></DIV>"

 print "</DIV></DIV>"
 if data['id'] != 'new':
  print "<A TITLE='Delete user' CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=sdcp.cgi?call=users_remove&id={0} MSG='Really remove user?'><IMG SRC='images/btn-delete.png'></A>".format(data['id'])
 print "<A TITLE='Update user'  CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=sdcp.cgi?call=users_info&headers=no&op=update FRM=sdcp_user_info_form><IMG SRC='images/btn-save.png'></A>"
 print "</FORM>"
 print "</DIV>"

#
#
#
def remove(aWeb):
 from sdcp.core.dbase import DB
 with DB() as db:
  res = db.do("DELETE FROM users WHERE id = '{}'".format(aWeb['id']))
 print "<DIV CLASS=z-frame>User with id {} removed ({})</DIV>".format(aWeb['id'],"OK" if res == 1 else "NOT_OK")
