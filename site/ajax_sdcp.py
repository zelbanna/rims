"""Module docstring.

Ajax generic SDCP calls module

"""
__author__= "Zacharias El Banna"
__version__ = "17.10.4"
__status__= "Production"

############################################ Options ##############################################
#
def list_options(aWeb):
 print "<DIV CLASS=z-content-left ID=div_content_left>"
 print "<DIV CLASS=z-frame><DIV CLASS=title>Options</DIV>"
 print "<DIV CLASS=z-table style='width:99%'><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right SPIN=true URL='ajax.cgi?call=ddi_sync'>Synch DDI</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right SPIN=true URL='ajax.cgi?call=ddi_dhcp_update'>Update DHCP</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right SPIN=true URL='ajax.cgi?call=ddi_load_infra'>Load DDI Tables</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op TARGET=_blank                  HREF='ajax.cgi?call=device_dump_db'>Dump DB to JSON</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right SPIN=true URL='ajax.cgi?call=device_rack_info'>Device Rackinfo</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right           URL='ajax.cgi?call=device_mac_sync'>Sync MAC Info</A></DIV></DIV>"
 print "</DIV></DIV></DIV></DIV>"
 print "<DIV CLASS=z-content-right ID =div_content_right></DIV>"

############################################ resources ##############################################
#
def list_resources(aWeb):
 import sdcp.core.GenLib as GL
 db   = GL.DB()
 db.connect()
 res  = db.do("SELECT id, title, href,type FROM resources ORDER BY type,title")
 rows = db.get_rows()              
 db.close()               
 print "<DIV CLASS=z-content-left ID=div_content_left>"
 print "<DIV CLASS=z-frame><DIV CLASS=title>Resources</DIV>"
 print "<A TITLE='Reload List'  CLASS='z-btn z-small-btn z-op' DIV=div_content_left  URL='ajax.cgi?call=sdcp_list_resources'><IMG SRC='images/btn-reboot.png'></A>"
 print "<A TITLE='Add Resource' CLASS='z-btn z-small-btn z-op' DIV=div_content_right URL='ajax.cgi?call=sdcp_resource_info&id=new'><IMG SRC='images/btn-add.png'></A>"
 print "<DIV CLASS=z-table style='width:99%'><DIV CLASS=thead><DIV CLASS=th>Type</DIV><DIV CLASS=th>Title</DIV><DIV CLASS=th>&nbsp;</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for row in rows:
  print "<DIV CLASS=tr><DIV CLASS=td>{0}</DIV><DIV CLASS=td><A HREF={1} TARGET=blank_>{2}</A></DIV><DIV CLASS=td>".format(row['type'],row['href'],row['title'])
  print "<A CLASS='z-op z-small-btn z-btn' DIV=div_content_right URL=ajax.cgi?call=sdcp_resource_info&id={0}><IMG SRC=images/btn-info.png></A>".format(row['id'])
  print "<A CLASS='z-op z-small-btn z-btn' DIV=div_content_right URL=ajax.cgi?call=sdcp_resource_remove&id={0} MSG='Really remove resource?'><IMG SRC='images/btn-remove.png'></A>&nbsp;".format(row['id'])
  print "</DIV></DIV>"
 print "</DIV></DIV></DIV></DIV>"
 print "<DIV CLASS=z-content-right ID =div_content_right></DIV>"

#
#
#
def resource_info(aWeb):
 import sdcp.core.GenLib as GL
 import sdcp.PackageContainer as PC
 from os import listdir, path
 id    = aWeb.get_value('id','new')
 op    = aWeb.get_value('op')
 title = aWeb.get_value('title',"unknown")
 href  = aWeb.get_value('href',"unknown")
 type  = aWeb.get_value('type')
 icon  = aWeb.get_value('icon')
 if op == 'update':
  db = GL.DB()
  db.connect()
  if id == 'new':
   db.do("INSERT INTO resources (title,href,icon,type,user_id) VALUES ('{}','{}','{}','{}','{}')".format(title,href,icon,type,aWeb.cookie.get('sdcp_id')))
   db.commit()
   id  = db.get_last_id()
  else:
   db.do("UPDATE resources SET title='{}',href='{}',icon='{}', type='{}' WHERE id = '{}'".format(title,href,icon,type,id))
   db.commit()
  db.close()
 elif id <> 'new':
  db = GL.DB()
  db.connect()
  db.do("SELECT title,href,icon,type FROM resources WHERE id = '{}'".format(id))
  db.close()
  row = db.get_row()
  title,href,icon,type = row['title'],row['href'],row['icon'],row['type']

 print "<DIV CLASS=z-frame>"
 print "<DIV CLASS=title>Resource entity ({})</DIV>".format(id)
 print "<FORM ID=sdcp_resource_info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(id)
 print "<DIV CLASS=z-table style='float:left;'><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Title:</DIV><DIV CLASS=td><INPUT   NAME=title TYPE=TEXT STYLE='border:1px solid grey; width:400px;' VALUE='{}'></DIV></DIV>".format(title)
 print "<DIV CLASS=tr><DIV CLASS=td>HREF:</DIV><DIV CLASS=td><INPUT     NAME=href TYPE=TEXT STYLE='border:1px solid grey; width:400px;' VALUE='{}'></DIV></DIV>".format(href)
 print "<DIV CLASS=tr><DIV CLASS=td>Icon URL:</DIV><DIV CLASS=td><INPUT NAME=icon TYPE=TEXT STYLE='border:1px solid grey; width:400px;' VALUE='{}'></DIV></DIV>".format(icon)
 print "<DIV CLASS=tr><DIV CLASS=td>Type:</DIV><DIV CLASS=td><SELECT NAME=type>"
 for tp in ['bookmark','demo','tool']:
  print "<OPTION VALUE={} {}>{}</OPTION>".format(tp,"" if type != tp else 'selected',tp.title())
 print "</SELECT></DIV></DIV>"

 print "</DIV></DIV>"
 if icon and icon != 'NULL':
  print "<A CLASS=z-btn style='float:left; padding:6px; cursor:default;'><IMG ALT={0} SRC='{0}'></A>".format(icon)
 print "<BR style='clear:left'>"
 if id != 'new':
  print "<A TITLE='Remove resource' CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=ajax.cgi?call=sdcp_resource_remove&id={0}  MSG='Really remove resource?'><IMG SRC='images/btn-remove.png'></A>".format(id)
 print "<A TITLE='Update resource'  CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=ajax.cgi?call=sdcp_resource_info&op=update FRM=sdcp_resource_info_form><IMG SRC='images/btn-save.png'></A>"
 print "</FORM>"
 print "</DIV>"

#
#
#
def list_resource_type(aWeb):
 import sdcp.core.GenLib as GL
 db = GL.DB()
 db.connect()
 type  = aWeb.get_value('type')
 db.do("SELECT * FROM resources WHERE type = '{}'".format(type))
 rows = db.get_rows() 
 db.close()
 index = 0;
 print "<DIV CLASS=z-centered style='align-items:initial'>"
 for row in rows:
  print "<DIV style='float:left; min-width:100px; margin:6px;'>"
  print "<A CLASS='z-btn z-menu-btn' style='min-width:52px;'; TITLE='{}' TARGET=_blank HREF='{}'>".format(row['title'],row['href'])
  print "<IMG ALT='{0}' SRC='{0}'></A>".format(row['icon'])
  print "</A><BR><SPAN style='width:100px; display:block;'>{}</SPAN>".format(row['title'])
  print "</DIV>"
 print "</DIV>"


############################################ Examine ##############################################
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

#
# UPS graphs
#
def examine_ups(aWeb):
 from sdcp.tools.munin import widget_cols
 upshost,void,domain = aWeb.get_value('upshost').partition('.')
 widget_cols([ "{1}/{0}.{1}/hw_apc_power".format(upshost,domain), "{1}/{0}.{1}/hw_apc_time".format(upshost,domain), "{1}/{0}.{1}/hw_apc_temp".format(upshost,domain) ])

#
# DNS stats
#
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

#
# DHCP stats
#
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

#
# Service logs
#
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

 res  = db.do("SELECT user_id, device_id, time_start, NOW() < ADDTIME(time_start, '30 0:0:0.0') AS valid, ADDTIME(time_start, '30 0:0:0.0') as time_end, devices.hostname, users.alias FROM bookings INNER JOIN devices ON device_id = devices.id INNER JOIN users ON user_id = users.id ORDER by user_id")
 rows = db.get_rows()
 db.close()
 print "<DIV CLASS=z-frame><DIV CLASS=title>Bookings</DIV>"
 print "<A TITLE='Reload List' CLASS='z-btn z-small-btn z-op' DIV=div_content_left URL='ajax.cgi?call=sdcp_list_bookings'><IMG SRC='images/btn-reboot.png'></A>"
 print "<DIV CLASS=z-table style='width:99%;'>"
 print "<DIV CLASS=thead><DIV CLASS=th>User (Id)</DIV><DIV CLASS=th>Device</DIV><DIV CLASS=th>Until</DIV><DIV CLASS=th>Op</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for row in rows:
  print "<DIV CLASS=tr><DIV CLASS=td><A CLASS='z-op' DIV=div_content_right URL='ajax.cgi?call=sdcp_user_info&id={3}'>{0}</A> ({3})</DIV><DIV CLASS=td><A CLASS='z-op' DIV=div_content_right URL='ajax.cgi?call=device_info&id={4}'>{1}</A></DIV><DIV CLASS=td {5}>{2}</DIV><DIV CLASS=td>".format(row['alias'],row['hostname'],row['time_end'],row['user_id'],row['device_id'],'' if row['valid'] == 1 else "style='background-color:orange;'")
  print "<A CLASS='z-btn z-small-btn z-op' DIV=div_content_left TITLE='Remove booking' URL='ajax.cgi?call=sdcp_list_bookings&op=unbook&id={0}'><IMG SRC='images/btn-remove.png'></A>".format(row['device_id'])
  print "<A CLASS='z-btn z-small-btn z-op' DIV=div_content_left TITLE='Extend booking' URL='ajax.cgi?call=sdcp_list_bookings&op=extend&id={0}'><IMG SRC='images/btn-add.png'></A>".format(row['device_id'])
  print "&nbsp;</DIV></DIV>"
 print "</DIV></DIV></DIV>"

#
#
#
def resource_remove(aWeb):
 import sdcp.core.GenLib as GL
 id = aWeb.get_value('id')
 db   = GL.DB()           
 db.connect()             
 res = db.do("DELETE FROM resources WHERE id = '{}'".format(id))
 db.commit()
 db.close()
 print "<DIV CLASS=z-frame>Result: {}</DIV>".format("OK" if res == 1 else "Not OK:{}".format(res))

############################################ Users ##############################################
#
#
#
def list_users(aWeb):
 import sdcp.core.GenLib as GL
 db   = GL.DB()
 db.connect()
 res  = db.do("SELECT id, alias, name, email FROM users ORDER by name")
 rows = db.get_rows()
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
  row = db.get_row()
  alias,name,email = row['alias'],row['name'],row['email']

 print "<DIV CLASS=z-frame>"
 print "<DIV CLASS=title>User Info ({})</DIV>".format(id)
 print "<FORM ID=sdcp_user_info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(id)
 print "<DIV CLASS=z-table><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Alias:</DIV><DIV CLASS=td><INPUT  NAME=alias TYPE=TEXT STYLE='border:1px solid grey; width:400px;' VALUE='{}'></DIV></DIV>".format(alias)
 print "<DIV CLASS=tr><DIV CLASS=td>Name:</DIV><DIV CLASS=td><INPUT    NAME=name TYPE=TEXT STYLE='border:1px solid grey; width:400px;' VALUE='{}'></DIV></DIV>".format(name)
 print "<DIV CLASS=tr><DIV CLASS=td>E-mail:</DIV><DIV CLASS=td><INPUT NAME=email TYPE=TEXT STYLE='border:1px solid grey; width:400px;' VALUE='{}'></DIV></DIV>".format(email)
 print "</DIV></DIV>"
 if id != 'new':
  print "<A TITLE='Remove user' CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=rest.cgi?call=sdcp.site:sdcp_remove_user&id={0} MSG='Really remove user?'><IMG SRC='images/btn-remove.png'></A>".format(id)
 print "<A TITLE='Update user'  CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=ajax.cgi?call=sdcp_user_info&op=update          FRM=sdcp_user_info_form><IMG SRC='images/btn-save.png'></A>"
 print "</FORM>"
 print "</DIV>"
