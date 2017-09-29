"""Module docstring.

Ajax generic SDCP calls module

"""
__author__= "Zacharias El Banna"
__version__ = "17.6.1GA"
__status__= "Production"

import sdcp.core.GenLib as GL

def list_bookings(aWeb):
 op = aWeb.get_value('op')
 id = aWeb.get_value('id')

 db   = GL.DB()
 db.connect()

 if op == 'unbook' and id:
  res = db.do("DELETE FROM bookings WHERE device_id = '{}'".format(id))
  db.commit()

 res  = db.do("SELECT device_id, time_start, devices.hostname, users.name FROM bookings INNER JOIN devices ON device_id = devices.id INNER JOIN users ON user_id = users.id ORDER by user_id")
 rows = db.get_all_rows()
 db.close()
 print "<DIV CLASS=z-os-left ID=div_left>"
 print "<DIV CLASS=z-frame><DIV CLASS=title>Bookings</DIV>"
 print "<A TITLE='Reload List' CLASS='z-btn z-small-btn z-op' DIV=div_content URL='ajax.cgi?call=sdcp_list_bookings'><IMG SRC='images/btn-reboot.png'></A>"
 print "<DIV CLASS=z-table style='width:99%'>"
 print "<DIV CLASS=thead><DIV CLASS=th>User</DIV><DIV CLASS=th>Device</DIV><DIV CLASS=th>Timestamp</DIV><DIV CLASS=th>Op</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for row in rows:
  print "<DIV CLASS=tr><DIV CLASS=td>{0}</A></DIV><DIV CLASS=td>{1}</DIV><DIV CLASS=td>{2}</DIV><DIV CLASS=td><A CLASS='z-btn z-small-btn z-op' DIV=div_content URL='ajax.cgi?call=sdcp_list_bookings&op=unbook&id={3}'><IMG SRC='images/btn-remove.png'></A>&nbsp;</DIV></DIV>".format(row['name'],row['hostname'],row['time_start'],row['device_id'])
 print "</DIV></DIV></DIV></DIV>"
 print "<DIV CLASS=z-os-right ID=div_right></DIV>"

def list_users(aWeb):
 db   = GL.DB()
 db.connect()
 res  = db.do("SELECT id, alias, name, email FROM users ORDER by name")
 rows = db.get_all_rows()
 db.close()
 print "<DIV CLASS=z-os-left ID=div_left>"
 print "<DIV CLASS=z-frame><DIV CLASS=title>Users</DIV>"
 print "<A TITLE='Reload List' CLASS='z-btn z-small-btn z-op' DIV=div_content URL='ajax.cgi?call=sdcp_list_users'><IMG SRC='images/btn-reboot.png'></A>"
 print "<A TITLE='Add User'    CLASS='z-btn z-small-btn z-op' DIV=div_right   URL='ajax.cgi?call=sdcp_user_info&id=new'><IMG SRC='images/btn-add.png'></A>"
 print "<DIV CLASS=z-table style='width:99%'>"
 print "<DIV CLASS=thead><DIV CLASS=th>Alias</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>E-mail</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for row in rows:
  print "<DIV CLASS=tr><DIV CLASS=td><A CLASS='z-op' DIV=div_right URL='ajax.cgi?call=sdcp_user_info&id={0}'>{1}</A></DIV><DIV CLASS=td>{2}</DIV><DIV CLASS=td>{3}</DIV></DIV>".format(row['id'],row['alias'],row['name'],row['email'])
 print "</DIV></DIV></DIV></DIV>"
 print "<DIV CLASS=z-os-right ID=div_right></DIV>"

def user_info(aWeb):
 id = aWeb.get_value('id','new')
 op = aWeb.get_value('op',None)
 name = aWeb.get_value('name',"unknown")
 alias = aWeb.get_value('alias',"unknown")
 email = aWeb.get_value('email',"unknown")
 if op == 'update':
  db = GL.DB()
  db.connect()
  if id == 'new':
   db.do("INSERT INTO users (alias,name,email) VALUES ('{}','{}','{}')".format(alias,name,email))
   db.commit()
   id  = db.get_last_id()
  else:
   db.do("UPDATE users SET alias='{}',name='{}',email='{}' WHERE id = '{}'".format(alias,name,email,id))
   db.commit()
  db.close()
 elif id <> 'new':
  db = GL.DB()
  db.connect()
  db.do("SELECT alias,name,email FROM users WHERE id = '{}'".format(id))
  db.close()
  row = db.get_all_rows()
  alias,name,email = row[0]['alias'],row[0]['name'],row[0]['email']

 print "<DIV CLASS=z-frame>"
 print "<DIV CLASS=title>User Info ({})</DIV>".format(id)
 print "<FORM ID=sdcp_user_info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(id)
 print "<DIV CLASS=z-table><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Alias:</DIV><DIV CLASS=td><INPUT  NAME=alias TYPE=TEXT STYLE='border:1px solid grey; width:200px;' VALUE='{}'></DIV></DIV>".format(alias)
 print "<DIV CLASS=tr><DIV CLASS=td>Name:</DIV><DIV CLASS=td><INPUT    NAME=name TYPE=TEXT STYLE='border:1px solid grey; width:200px;' VALUE='{}'></DIV></DIV>".format(name)
 print "<DIV CLASS=tr><DIV CLASS=td>E-mail:</DIV><DIV CLASS=td><INPUT NAME=email TYPE=TEXT STYLE='border:1px solid grey; width:200px;' VALUE='{}'></DIV></DIV>".format(email)
 print "</DIV></DIV>"
 if id != 'new':
  print "<A TITLE='Remove user' CLASS='z-btn z-op z-small-btn' DIV=div_right URL=rest.cgi?call=sdcp.site:sdcp_remove_user&id={0}><IMG SRC='images/btn-remove.png'></A>".format(id)
 print "<A TITLE='Update user'  CLASS='z-btn z-op z-small-btn' DIV=div_right URL=ajax.cgi?call=sdcp_user_info&op=update FRM=sdcp_user_info_form OP=load><IMG SRC='images/btn-save.png'></A>"
 print "</FORM>"
 print "</DIV>"
