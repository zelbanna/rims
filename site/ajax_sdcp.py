"""Module docstring.

Ajax generic SDCP calls module

"""
__author__= "Zacharias El Banna"
__version__ = "17.6.1GA"
__status__= "Production"


############################################ Bookings ##############################################
#
# Examine Logs
#
def examine_logs(aWeb):
 import sdcp.PackageContainer as PC
 from sdcp.site.rest_sdcp import examine_logs
 logs = examine_logs({'count':10,'logs':"{},{}".format(PC.generic['logformat'],PC.sdcp['netlogs'])})
 for file,res in logs.iteritems():
  print "<DIV CLASS='z-logs'><H1>{}</H1><PRE>".format(file)
  for line in res:
   print line
  print "</PRE></DIV>"

def examine_ups(aWeb):
 from sdcp.tools.Grapher import Grapher
 upshost,void,domain = aWeb.get_value('upshost').partition('.')
 graph = Grapher()
 graph.widget_cols([ "{1}/{0}.{1}/hw_apc_power".format(upshost,domain), "{1}/{0}.{1}/hw_apc_time".format(upshost,domain), "{1}/{0}.{1}/hw_apc_temp".format(upshost,domain) ])

def examine_dns(aWeb):
 from sdcp.core.rest import call as rest_call     
 svchost = aWeb.get_value('svchost')

 dnstop = rest_call("http://{}/rest.cgi".format(svchost), "sdcp.site:ddi_dns_top", {'count':20})
 print "<DIV CLASS=z-frame STYLE='float:left; width:48%;'><DIV CLASS=title>Top looked up FQDN ({})</DIV>".format(svchost)
 print "<DIV CLASS=z-table style='padding:5px; width:100%; height:600px'><DIV CLASS=thead><DIV CLASS=th>Count</DIV><DIV CLASS=th>What</DIV></DIV>"
 print "<DIV CLASS=tbody>"       
 for data in dnstop['top']:
  print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV></DIV>".format(data['count'],data['fqdn'])
 print "</DIV></DIV></DIV>"
 print "<DIV CLASS=z-frame STYLE='float:left; width:48%;'><DIV CLASS=title>Top looked up FQDN per Client ({})</DIV>".format(svchost)
 print "<DIV CLASS=z-table style='padding:5px; width:100%; height:600px'><DIV CLASS=thead><DIV CLASS=th>Count</DIV><DIV CLASS=th>What</DIV><DIV CLASS=th>Who</DIV><DIV CLASS=th>Hostname</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for data in dnstop['who']:
  print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV></DIV>".format(data['count'],data['fqdn'],data['who'],data['hostname'])
 print "</DIV></DIV></DIV>"

def examine_dhcp(aWeb):
 from sdcp.core.rest import call as rest_call      
 svchost = aWeb.get_value('svchost')   

 dhcp = rest_call("http://{}/rest.cgi".format(svchost), "sdcp.site:ddi_dhcp_leases")
 print "<DIV CLASS=z-frame STYLE='float:left; width:48%;'><DIV CLASS=title>DHCP Active Leases ({})</DIV>".format(svchost)
 print "<DIV CLASS=z-table style='padding:5px; width:100%; height:auto'><DIV CLASS=thead><DIV CLASS=th>IP</DIV><DIV CLASS=th>MAC</DIV><DIV CLASS=th>Started</DIV><DIV CLASS=th>Ends</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for data in dhcp['active']:
  print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV></DIV>".format(data['ip'],data['mac'],data['starts'],data['ends'])
 print "</DIV></DIV></DIV>"
 print "<DIV CLASS=z-frame STYLE='float:left; width:48%;'><DIV CLASS=title>DHCP Free/Old Leases ({})</DIV>".format(svchost)
 print "<DIV CLASS=z-table style='padding:5px; width:100%; height:auto'><DIV CLASS=thead><DIV CLASS=th>IP</DIV><DIV CLASS=th>MAC</DIV><DIV CLASS=th>Started</DIV><DIV CLASS=th>Ended</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for data in dhcp['free']:
  print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV></DIV>".format(data['ip'],data['mac'],data['starts'],data['ends'])
 print "</DIV></DIV></DIV>"

def examine_svc(aWeb):
 from sdcp.core.rest import call as rest_call      
 import sdcp.PackageContainer as PC
 svchost = aWeb.get_value('svchost')
 logs = rest_call("http://{}/rest.cgi".format(svchost), "sdcp.site:sdcp_examine_logs",{'count':20,'logs':PC.generic['logformat']})
 for file,res in logs.iteritems():
  print "<DIV CLASS='z-logs'><H1>{}</H1><PRE>".format(file)
  for line in res:
   print line
  print "</PRE></DIV>"

############################################ Bookings ##############################################
#
#
def list_bookings(aWeb):
 import sdcp.core.GenLib as GL
 op = aWeb.get_value('op')
 id = aWeb.get_value('id')

 db   = GL.DB()
 db.connect()

 if   op == 'unbook' and id:
  res = db.do("DELETE FROM bookings WHERE device_id = '{}'".format(id))
  db.commit()
 elif op == 'extend' and id:
  res = db.do("UPDATE bookings SET time_start = NOW() WHERE device_id = '{}'".format(id))
  db.commit()

 res  = db.do("SELECT user_id, device_id, time_start, ADDTIME(time_start, '30 0:0:0.0') as time_end, devices.hostname, users.alias FROM bookings INNER JOIN devices ON device_id = devices.id INNER JOIN users ON user_id = users.id ORDER by user_id")
 rows = db.get_all_rows()
 db.close()
 print "<DIV CLASS=z-frame><DIV CLASS=title>Bookings</DIV>"
 print "<A TITLE='Reload List' CLASS='z-btn z-small-btn z-op' DIV=div_content_left URL='ajax.cgi?call=sdcp_list_bookings'><IMG SRC='images/btn-reboot.png'></A>"
 print "<DIV CLASS=z-table style='width:99%;'>"
 print "<DIV CLASS=thead><DIV CLASS=th>User (Id)</DIV><DIV CLASS=th>Device</DIV><DIV CLASS=th>Until</DIV><DIV CLASS=th>Op</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for row in rows:
  print "<DIV CLASS=tr><DIV CLASS=td><A CLASS='z-op' DIV=div_content_right URL='ajax.cgi?call=sdcp_user_info&id={3}'>{0}</A> ({3})</DIV><DIV CLASS=td><A CLASS='z-op' DIV=div_content_right URL='ajax.cgi?call=device_info&id={4}'>{1}</A></DIV><DIV CLASS=td>{2}</DIV><DIV CLASS=td>".format(row['alias'],row['hostname'],row['time_end'],row['user_id'],row['device_id'])
  print "<A CLASS='z-btn z-small-btn z-op' DIV=div_content_left TITLE='Remove booking' URL='ajax.cgi?call=sdcp_list_bookings&op=unbook&id={0}'><IMG SRC='images/btn-remove.png'></A>".format(row['device_id'])
  print "<A CLASS='z-btn z-small-btn z-op' DIV=div_content_left TITLE='Extend booking' URL='ajax.cgi?call=sdcp_list_bookings&op=extend&id={0}'><IMG SRC='images/btn-add.png'></A>".format(row['device_id'])
  print "&nbsp;</DIV></DIV>"
 print "</DIV></DIV></DIV>"

############################################ Users ##############################################
#
#
#
def list_users(aWeb):
 import sdcp.core.GenLib as GL
 db   = GL.DB()
 db.connect()
 res  = db.do("SELECT id, alias, name, email FROM users ORDER by name")
 rows = db.get_all_rows()
 db.close()
 print "<DIV CLASS=z-frame><DIV CLASS=title>Users</DIV>"
 print "<A TITLE='Reload List' CLASS='z-btn z-small-btn z-op' DIV=div_content_left URL='ajax.cgi?call=sdcp_list_users'><IMG SRC='images/btn-reboot.png'></A>"
 print "<A TITLE='Add User'    CLASS='z-btn z-small-btn z-op' DIV=div_content_right   URL='ajax.cgi?call=sdcp_user_info&id=new'><IMG SRC='images/btn-add.png'></A>"
 print "<DIV CLASS=z-table style='width:99%'>"
 print "<DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Alias</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>E-mail</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for row in rows:
  print "<DIV CLASS=tr><DIV CLASS=td>{0}</DIV><DIV CLASS=td><A CLASS='z-op' DIV=div_content_right URL='ajax.cgi?call=sdcp_user_info&id={0}'>{1}</A></DIV><DIV CLASS=td>{2}</DIV><DIV CLASS=td>{3}</DIV></DIV>".format(row['id'],row['alias'],row['name'],row['email'])
 print "</DIV></DIV></DIV>"

#
#
#
def user_info(aWeb):
 id = aWeb.get_value('id','new')
 op = aWeb.get_value('op',None)
 name = aWeb.get_value('name',"unknown")
 alias = aWeb.get_value('alias',"unknown")
 email = aWeb.get_value('email',"unknown")
 if op == 'update':
  import sdcp.core.GenLib as GL
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
  import sdcp.core.GenLib as GL
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
 if id != 'new' or op != 'view':
  print "<A TITLE='Remove user' CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=rest.cgi?call=sdcp.site:sdcp_remove_user&id={0}><IMG SRC='images/btn-remove.png'></A>".format(id)
 print "<A TITLE='Update user'  CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=ajax.cgi?call=sdcp_user_info&op=update FRM=sdcp_user_info_form><IMG SRC='images/btn-save.png'></A>"
 print "</FORM>"
 print "</DIV>"
