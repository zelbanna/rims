"""Module docstring.

Ajax generic SDCP calls module

"""
__author__= "Zacharias El Banna"
__version__ = "17.10.4"
__status__= "Production"

############################################ resources ##############################################
#
def navigate(aWeb):
 print "<DIV CLASS=z-navbar  ID=div_navbar>&nbsp;</DIV>"
 print "<DIV CLASS=z-content ID=div_content>"
 list_resource_type(aWeb)
 print "</DIV>"

#
#
#
def list_resources(aWeb):
 from sdcp.core.dbase import DB
 with DB() as db:
  res  = db.do("SELECT id, title, href, type, inline, user_id FROM resources WHERE (user_id = '{}' {}) ORDER BY type,title".format(aWeb.cookie['sdcp_id'],'' if aWeb.cookie['sdcp_view'] == '0' else 'OR private = 0'))
  rows = db.get_rows()
 print "<DIV CLASS=z-content-left ID=div_content_left>"
 print "<DIV CLASS=z-frame><DIV CLASS=title>Resources</DIV>"
 print "<A TITLE='Reload List'  CLASS='z-btn z-small-btn z-op' DIV=div_content       URL='sdcp.cgi?call=base_list_resources'><IMG SRC='images/btn-reboot.png'></A>"
 print "<A TITLE='Add Resource' CLASS='z-btn z-small-btn z-op' DIV=div_content_right URL='sdcp.cgi?call=base_resource_info&id=new'><IMG SRC='images/btn-add.png'></A>"
 print "<DIV CLASS=z-table><DIV CLASS=thead><DIV CLASS=th>Type</DIV><DIV CLASS=th>Title</DIV><DIV CLASS=th>&nbsp;</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for row in rows:
  print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><DIV CLASS=td><A TITLE='{}' ".format(row['type'],row['title'])
  if row['inline'] == 0:
   print "TARGET=_blank HREF='{}'>".format(row['href'])
  else:
   print "CLASS=z-op DIV=div_main_cont URL='{}'>".format(row['href'])
  print "{}</A></DIV><DIV CLASS=td>".format(row['title'])
  print "&nbsp;<A CLASS='z-op z-small-btn z-btn' DIV=div_content_right URL=sdcp.cgi?call=base_resource_info&id={0}><IMG SRC=images/btn-info.png></A>".format(row['id'])
  if aWeb.cookie['sdcp_id'] == str(row['user_id']):
   print "<A CLASS='z-op z-small-btn z-btn' DIV=div_content_right URL=sdcp.cgi?call=base_resource_remove&id={0} MSG='Really remove resource?'><IMG SRC='images/btn-remove.png'></A>".format(row['id'])
  print "</DIV></DIV>"
 print "</DIV></DIV></DIV></DIV>"
 print "<DIV CLASS=z-content-right ID=div_content_right>"

#
#
#
def resource_info(aWeb):
 from sdcp.core.dbase import DB
 from os import listdir, path
 op    = aWeb.get_value('op')
 data  = {}
 data['id'] = aWeb.get_value('id','new')
 if op == 'update' or data['id'] == 'new':
  data['title'] = aWeb.get_value('title',"unknown")
  data['href']  = aWeb.get_value('href',"unknown")
  data['type']  = aWeb.get_value('type')
  data['icon']  = aWeb.get_value('icon')
  data['inline']  = aWeb.get_value('inline',"0")
  data['private'] = aWeb.get_value('private',"0")
  data['user_id'] = aWeb.get_value('user_id',aWeb.cookie['sdcp_id'])
  if op == 'update':
   with DB() as db:   
    if data['id'] == 'new':
     db.do("INSERT INTO resources (title,href,icon,type,inline,private,user_id) VALUES ('{}','{}','{}','{}','{}','{}','{}')".format(data['title'],data['href'],data['icon'],data['type'],data['inline'],data['private'],data['user_id']))
     data['id']  = db.get_last_id()
    else:
     db.do("UPDATE resources SET title='{}',href='{}',icon='{}', type='{}', inline='{}', private='{}' WHERE id = '{}'".format(data['title'],data['href'],data['icon'],data['type'],data['inline'],data['private'],data['id']))
    db.commit()
 else:
  with DB() as db:
   db.do("SELECT id,title,href,icon,type,inline,private,user_id FROM resources WHERE id = '{}'".format(data['id']))
   data = db.get_row()

 print "<DIV CLASS=z-frame>"
 print "<DIV CLASS=title>Resource entity ({})</DIV>".format(data['id'])
 print "<FORM ID=sdcp_resource_info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(data['id'])
 print "<INPUT TYPE=HIDDEN NAME=user_id VALUE={}>".format(data['user_id'])
 print "<DIV CLASS=z-table style='float:left; width:auto;'><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Title:</DIV><DIV    CLASS=td><INPUT NAME=title STYLE='min-width:400px' TYPE=TEXT VALUE='{}'></DIV></DIV>".format(data['title'])
 print "<DIV CLASS=tr><DIV CLASS=td>HREF:</DIV><DIV     CLASS=td><INPUT NAME=href  STYLE='min-width:400px' TYPE=TEXT VALUE='{}'></DIV></DIV>".format(data['href'])
 print "<DIV CLASS=tr><DIV CLASS=td>Icon URL:</DIV><DIV CLASS=td><INPUT NAME=icon  STYLE='min-width:400px' TYPE=TEXT VALUE='{}'></DIV></DIV>".format(data['icon'])
 print "<DIV CLASS=tr><DIV CLASS=td>Inline:</DIV><DIV   CLASS=td><INPUT NAME=inline  {}                TYPE=CHECKBOX VALUE=1   ></DIV></DIV>".format("checked=checked" if data['inline'] == 1 or data['inline'] == "1" else '')
 print "<DIV CLASS=tr><DIV CLASS=td>Private:</DIV><DIV  CLASS=td><INPUT NAME=private {} {}             TYPE=CHECKBOX VALUE=1   ></DIV></DIV>".format("checked=checked" if data['private'] == 1 or data['private'] == "1" else "","disabled" if aWeb.cookie['sdcp_id'] <> str(data['user_id']) else "")
 print "<DIV CLASS=tr><DIV CLASS=td>Type:</DIV><DIV     CLASS=td><SELECT NAME=type STYLE='min-width:400px'>"
 for tp in ['bookmark','demo','tool']:
  print "<OPTION VALUE={} {}>{}</OPTION>".format(tp,"" if data['type'] != tp else 'selected',tp.title())
 print "</SELECT></DIV></DIV>"
 print "</DIV></DIV>"
 print "</FORM>"
 if data['icon'] and data['icon'] != 'NULL':
  print "<A CLASS='z-btn z-menu-btn' style='float:left; min-width:52px; font-size:10px; cursor:default;'><IMG ALT={0} SRC='{0}'></A>".format(data['icon'])
 print "<BR style='clear:left'>"
 if data['id'] != 'new':
  print "<A TITLE='Remove resource' CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=sdcp.cgi?call=base_resource_remove&id={0}  MSG='Really remove resource?'><IMG SRC='images/btn-remove.png'></A>".format(data['id'])
 print "<A TITLE='Update resource'  CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=sdcp.cgi?call=base_resource_info&op=update FRM=sdcp_resource_info_form><IMG SRC='images/btn-save.png'></A>"
 print "</DIV>"

#
#
#
def list_resource_type(aWeb):
 #
 #
 # 
 from sdcp.core.dbase import DB
 with DB() as db:
  db.do("SELECT title,href,icon,inline FROM resources WHERE type = '{}' AND ( user_id = {} {} )".format(aWeb.get_value('type'),aWeb.cookie['sdcp_id'],'' if aWeb.cookie.get('sdcp_view') == '0' else "OR private = 0"))
  rows = db.get_rows()
 index = 0;
 print "<DIV CLASS=z-centered style='align-items:initial'>"
 for row in rows:
  print "<DIV style='float:left; min-width:100px; margin:6px;'><A STYLE='font-size:10px;' TITLE='{}'".format(row['title'])
  if row['inline'] == 0:
   print "CLASS='z-btn z-menu-btn' TARGET=_blank HREF='{}'>".format(row['href'])
  else:
   print "CLASS='z-op z-btn z-menu-btn' DIV=div_main_cont URL='{}'>".format(row['href'])
  print "<IMG ALT='{0}' SRC='{0}'></A>".format(row['icon'])
  print "</A><BR><SPAN style='width:100px; display:block;'>{}</SPAN>".format(row['title'])
  print "</DIV>"
 print "</DIV>"

#
#
#
def resource_remove(aWeb):
 from sdcp.core.dbase import DB
 with DB() as db:
  id = aWeb.get_value('id')
  res = db.do("DELETE FROM resources WHERE id = '{}'".format(id))
  db.commit()
 print "<DIV CLASS=z-frame>Result: {}</DIV>".format("OK" if res == 1 else "Not OK:{}".format(res))


############################################ Options ##############################################
#
def config(aWeb):
 print "<DIV CLASS=z-navbar ID=div_navbar>"
 print "<A CLASS=z-op           DIV=div_content URL='sdcp.cgi?call=base_list_resources'>Resources</A>"
 print "<A CLASS=z-op           DIV=div_content URL='sdcp.cgi?call=base_list_options'>Options</A>"
 print "<A CLASS='z-op z-right' DIV=div_content URL='sdcp.cgi?call=base_list_resource_type&type=bookmark'>Bookmarks</A>"
 print "<A CLASS='z-op z-right' DIV=div_content URL='sdcp.cgi?call=base_list_resource_type&type=demo'>Demos</A>"
 print "<A CLASS='z-op z-right' DIV=div_content URL='sdcp.cgi?call=base_list_resource_type&type=tool'>Tools</A>"
 print "</DIV>"
 print "<DIV CLASS=z-content ID=div_content>"
 print "</DIV>"

def list_options(aWeb):
 print "<DIV CLASS=z-content-left ID=div_content_left>"
 print "<DIV CLASS=z-frame><DIV CLASS=title>Options</DIV>"
 print "<DIV CLASS=z-table><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right SPIN=true URL='sdcp.cgi?call=ddi_sync'>Synch DDI</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right SPIN=true URL='sdcp.cgi?call=ddi_dhcp_update'>Update DHCP</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right SPIN=true URL='sdcp.cgi?call=ddi_load_infra'>Load DDI Tables</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op TARGET=_blank                  HREF='sdcp.cgi?call=device_dump_db'>Dump DB to JSON</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right SPIN=true URL='sdcp.cgi?call=rack_rackinfo'>Rackinfo Table</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right           URL='sdcp.cgi?call=device_mac_sync'>Sync MAC Info</A></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right           URL='sdcp.cgi?call=base_reload'>Reload App</A></DIV></DIV>"
 print "</DIV></DIV></DIV></DIV>"
 print "<DIV CLASS=z-content-right ID=div_content_right></DIV>"

############################################ Examine ##############################################
#
# Examine Logs
#
def examine(aWeb):
 import sdcp.PackageContainer as PC
 upshost = PC.sdcp['upshost']
 print "<DIV CLASS='z-navbar' ID=div_navbar>"
 print "<A CLASS='z-warning z-op' DIV=div_content MSG='Clear Network Logs?' URL='sdcp.cgi?call=base_examine_clear'>Clear Logs</A>"
 print "<A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=base_examine_logs>Logs</A>"
 if upshost:
  print "<A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=base_examine_ups>UPS</A>"
 print "<A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=base_examine_dns>DNS</A>"
 print "<A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=base_examine_dhcp>DHCP</A>"
 print "<A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=base_examine_svc>Services Logs</A>"
 print "<A CLASS='z-reload z-op' DIV=div_main_cont URL=sdcp.cgi?call=base_examine></A>"
 print "</DIV>"
 print "<DIV CLASS=z-content ID=div_content></DIV>"

#
#
#
def examine_clear(aWeb):
 import sdcp.PackageContainer as PC
 from sdcp.core.rest import call as rest_call
 res_dns  = rest_call(PC.dns['url'],'sdcp.rest.base_clear_logs',{ 'logs':[PC.generic['logformat']]})
 res_host = rest_call("http://127.0.0.1/rest.cgi",'sdcp.rest.base_clear_logs',{ 'logs':[PC.generic['logformat'],PC.sdcp['netlogs']]})
 print "<DIV CLASS=z-frame>{}<BR>{}</DIV>".format(res_host,res_dns)

#
# Internal Logs
#
def examine_logs(aWeb):
 import sdcp.PackageContainer as PC
 from sdcp.core.rest import call as rest_call
 logs = rest_call('http://127.0.0.1/rest.cgi','sdcp.rest.base_examine_logs',{'count':10,'logs':[PC.generic['logformat'],PC.sdcp['netlogs']]})
 for file,res in logs.iteritems():
  print "<DIV CLASS='z-logs'><H1>{}</H1><PRE>".format(file)
  for line in res:
   print line
  print "</PRE></DIV>"

#
# UPS graphs
#
def examine_ups(aWeb):
 import sdcp.PackageContainer as PC
 from sdcp.tools.munin import widget_cols
 upshost,void,domain = PC.sdcp['upshost'].partition('.')
 print "<DIV CLASS=z-frame STYLE='width:auto;'>"
 widget_cols([ "{1}/{0}.{1}/hw_apc_power".format(upshost,domain), "{1}/{0}.{1}/hw_apc_time".format(upshost,domain), "{1}/{0}.{1}/hw_apc_temp".format(upshost,domain) ])
 print "</DIV>"

#
# DNS stats
#
def examine_dns(aWeb):
 import sdcp.PackageContainer as PC
 from sdcp.core.rest import call as rest_call
 dnstop = rest_call(PC.dns['url'], "sdcp.rest.{}_top".format(PC.dns['type']), {'count':20})
 print "<DIV CLASS=z-frame STYLE='float:left; width:49%;'><DIV CLASS=title>Top looked up FQDN</DIV>"
 print "<DIV CLASS=z-table style='padding:5px; height:600px'><DIV CLASS=thead><DIV CLASS=th>Count</DIV><DIV CLASS=th>What</DIV></DIV>"
 print "<DIV CLASS=tbody>"       
 for data in dnstop['top']:
  print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV></DIV>".format(data['count'],data['fqdn'])
 print "</DIV></DIV></DIV>"
 print "<DIV CLASS=z-frame STYLE='float:left; width:49%;'><DIV CLASS=title>Top looked up FQDN per Client</DIV>"
 print "<DIV CLASS=z-table style='padding:5px; height:600px'><DIV CLASS=thead><DIV CLASS=th>Count</DIV><DIV CLASS=th>What</DIV><DIV CLASS=th>Who</DIV><DIV CLASS=th>Hostname</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for data in dnstop['who']:
  print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV></DIV>".format(data['count'],data['fqdn'],data['who'],data['hostname'])
 print "</DIV></DIV></DIV>"

#
# DHCP stats
#
def examine_dhcp(aWeb):
 import sdcp.PackageContainer as PC
 from sdcp.core.rest import call as rest_call
 dhcp = rest_call(PC.dhcp['url'], "sdcp.rest.{}_get_leases".format(PC.dhcp['type']))
 print "<!-- {} -->".format(dhcp)
 print "<DIV CLASS=z-frame STYLE='float:left; width:49%;'><DIV CLASS=title>DHCP Active Leases</DIV>"
 print "<DIV CLASS=z-table style='padding:5px; height:auto'><DIV CLASS=thead><DIV CLASS=th>IP</DIV><DIV CLASS=th>MAC</DIV><DIV CLASS=th>Started</DIV><DIV CLASS=th>Ends</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for data in dhcp['active']:
  print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV></DIV>".format(data['ip'],data['mac'],data['starts'],data['ends'])
 print "</DIV></DIV></DIV>"
 print "<DIV CLASS=z-frame STYLE='float:left; width:49%;'><DIV CLASS=title>DHCP Free/Old Leases</DIV>"
 print "<DIV CLASS=z-table style='padding:5px; height:auto'><DIV CLASS=thead><DIV CLASS=th>IP</DIV><DIV CLASS=th>MAC</DIV><DIV CLASS=th>Started</DIV><DIV CLASS=th>Ended</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for data in dhcp['free']:
  print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV></DIV>".format(data['ip'],data['mac'],data['starts'],data['ends'])
 print "</DIV></DIV></DIV>"

#
# Service logs
#
def examine_svc(aWeb):
 import sdcp.PackageContainer as PC
 from sdcp.core.rest import call as rest_call
 logs = rest_call("http://{}/rest.cgi".format(PC.sdcp['svcsrv']), "sdcp.rest.base_examine_logs",{'count':20,'logs':PC.generic['logformat']})
 for file,res in logs.iteritems():
  print "<DIV CLASS='z-logs'><H1>{}</H1><PRE>".format(file)
  for line in res:
   print line
  print "</PRE></DIV>"

############################################ Bookings ##############################################
#
#
def list_bookings(aWeb):
 from sdcp.core.dbase import DB
 op = aWeb.get_value('op')
 id = aWeb.get_value('id')
 
 with DB() as db:
  if   op == 'unbook' and id:
   res = db.do("DELETE FROM bookings WHERE device_id = '{}'".format(id))
   db.commit()
  elif op == 'extend' and id:
   res = db.do("UPDATE bookings SET time_start = NOW() WHERE device_id = '{}'".format(id))
   db.commit()
  res  = db.do("SELECT user_id, device_id, time_start, NOW() < ADDTIME(time_start, '30 0:0:0.0') AS valid, ADDTIME(time_start, '30 0:0:0.0') as time_end, devices.hostname, users.alias FROM bookings INNER JOIN devices ON device_id = devices.id INNER JOIN users ON user_id = users.id ORDER by user_id")
  rows = db.get_rows()

 print "<DIV CLASS=z-frame><DIV CLASS=title>Bookings</DIV>"
 print "<A TITLE='Reload List' CLASS='z-btn z-small-btn z-op' DIV=div_content_left URL='sdcp.cgi?call=base_list_bookings'><IMG SRC='images/btn-reboot.png'></A>"
 print "<DIV CLASS=z-table>"
 print "<DIV CLASS=thead><DIV CLASS=th>User (Id)</DIV><DIV CLASS=th>Device</DIV><DIV CLASS=th>Until</DIV><DIV CLASS=th>Op</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for row in rows:
  print "<DIV CLASS=tr><DIV CLASS=td><A CLASS='z-op' DIV=div_content_right URL='sdcp.cgi?call=base_user_info&id={3}'>{0}</A> ({3})</DIV><DIV CLASS=td><A CLASS='z-op' DIV=div_content_right URL='sdcp.cgi?call=device_info&id={4}'>{1}</A></DIV><DIV CLASS=td {5}>{2}</DIV><DIV CLASS=td>".format(row['alias'],row['hostname'],row['time_end'],row['user_id'],row['device_id'],'' if row['valid'] == 1 else "style='background-color:orange;'")
  if int(aWeb.cookie.get('sdcp_id')) == row['user_id'] or row['valid'] == 0:
   print "<A CLASS='z-btn z-small-btn z-op' DIV=div_content_left TITLE='Extend booking' URL='sdcp.cgi?call=base_list_bookings&op=extend&id={0}'><IMG SRC='images/btn-add.png'></A>".format(row['device_id'])
   print "<A CLASS='z-btn z-small-btn z-op' DIV=div_content_left TITLE='Remove booking' URL='sdcp.cgi?call=base_list_bookings&op=unbook&id={0}'><IMG SRC='images/btn-remove.png'></A>".format(row['device_id'])
  print "&nbsp;</DIV></DIV>"
 print "</DIV></DIV></DIV>"

############################################ Users ##############################################
#
#
#
def users(aWeb):
 print "<DIV CLASS=z-navbar ID=div_navbar>"
 print "<A CLASS=z-op DIV=div_content_left URL='sdcp.cgi?call=base_list_users'>Users</A>"
 print "<A CLASS=z-op DIV=div_content_left URL='sdcp.cgi?call=base_list_bookings'>Bookings</A>"
 print "<A CLASS='z-right z-op' OP=logout style='background-color:red;' URL=sdcp.cgi>Log out</A>"
 print "<A CLASS='z-right z-op z-navinfo' DIV=div_content_right URL=sdcp.cgi?call=base_user_info&id={}>{}</A>".format(aWeb.cookie.get('sdcp_id'),aWeb.cookie.get('sdcp_user'))
 print "</DIV>"
 print "<DIV CLASS=z-content ID=div_content>"
 print "<DIV CLASS=z-content-left  ID=div_content_left></DIV>"
 print "<DIV CLASS=z-content-right ID=div_content_right></DIV>"
 print "</DIV>"


def list_users(aWeb):
 from sdcp.core.dbase import DB
 with DB() as db:
  res  = db.do("SELECT id, alias, name, email FROM users ORDER by name")
  rows = db.get_rows()
 print "<DIV CLASS=z-frame><DIV CLASS=title>Users</DIV>"
 print "<A TITLE='Reload List' CLASS='z-btn z-small-btn z-op' DIV=div_content_left URL='sdcp.cgi?call=base_list_users'><IMG SRC='images/btn-reboot.png'></A>"
 print "<A TITLE='Add User'    CLASS='z-btn z-small-btn z-op' DIV=div_content_right   URL='sdcp.cgi?call=base_user_info&id=new'><IMG SRC='images/btn-add.png'></A>"
 print "<DIV CLASS=z-table>"
 print "<DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Alias</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>E-mail</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for row in rows:
  print "<DIV CLASS=tr><DIV CLASS=td>{0}</DIV><DIV CLASS=td><A CLASS='z-op' DIV=div_content_right URL='sdcp.cgi?call=base_user_info&id={0}'>{1}</A></DIV><DIV CLASS=td>{2}</DIV><DIV CLASS=td>{3}</DIV></DIV>".format(row['id'],row['alias'],row['name'],row['email'])
 print "</DIV></DIV></DIV>"

#
#
#
def user_info(aWeb):
 from sdcp.core.dbase import DB
 data = {}
 data['id'] = aWeb.get_value('id','new')
 op = aWeb.get_value('op')
 with DB() as db:
  db.do("SELECT id,title FROM resources")
  resources = db.get_rows()
  resources.insert(0,{'id':'NULL','title':'default'})
  if op == 'update' or data['id'] == 'new':
   data['name']  = aWeb.get_value('name',"unknown")
   data['alias'] = aWeb.get_value('alias',"unknown")
   data['email'] = aWeb.get_value('email',"unknown")
   data['front'] = aWeb.get_value('front','NULL')
   data['view']  = aWeb.get_value('view','1')
   if op == 'update':
    if data['id'] == 'new':
     db.do("INSERT INTO users (alias,name,email,frontpage,view_public) VALUES ('{}','{}','{}','{}',{})".format(data['alias'],data['name'],data['email'],data['front'],data['view']))
     data['id']  = db.get_last_id()
    else:
     db.do("UPDATE users SET alias='{}',name='{}',email='{}',view_public='{}',frontpage={} WHERE id = '{}'".format(data['alias'],data['name'],data['email'],data['view'],data['front'],data['id']))
     if aWeb.cookie['sdcp_id'] == str(data['id']):
      aWeb.add_cookie('sdcp_view',data['view'],86400)
    db.commit()
    aWeb.put_headers()
  else:
   db.do("SELECT * FROM users WHERE id = '{}'".format(data['id']))
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
  print "<A TITLE='Remove user' CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=rest.cgi?call=sdcp.rest.base_remove_user&id={0} MSG='Really remove user?'><IMG SRC='images/btn-remove.png'></A>".format(data['id'])
 print "<A TITLE='Update user'  CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=sdcp.cgi?call=base_user_info&headers=no&op=update FRM=sdcp_user_info_form><IMG SRC='images/btn-save.png'></A>"
 print "</FORM>"
 print "</DIV>"

############################################ Configuration ##############################################

def reload(aWeb):
 import sdcp.PackageContainer as PC
 print "<DIV CLASS=z-frame STYLE='width:600px;'>"
 if aWeb.get_value('file'):
  from sdcp.core.rest import call as rest_call
  res = rest_call('http://127.0.0.1/rest.cgi','sdcp.rest.base_reload',{'file':aWeb.get_value('file')})
  print "{}<BR>".format(res)
  if PC.sdcp['svcsrv']:
   res = rest_call("http://{}/rest.cgi".format(PC.sdcp['svcsrv']),'sdcp.rest.base_reload',{'file':aWeb.get_value('file')})
   print "{}<BR>".format(res)
 else:
  from git import Repo
  repo = Repo(PC.repo)
  print "<FORM ID=sdcp_reload>"
  print "Reload: <INPUT NAME=file STYLE='border:none; overflow:visible; background-color: transparent;' TYPE=TEXT VALUE={}>".format(PC.file)
  print "<A CLASS='z-op z-btn z-small-btn' DIV=div_content_right URL=sdcp.cgi?call=base_reload FRM=sdcp_reload><IMG SRC=images/btn-reboot.png></A>"
  if len(repo.index.diff(None)) > 0:
   print "<DIV CLASS=title>Changes</DIV>"
   print "<DIV CLASS=z-table><DIV CLASS=thead><DIV CLASS=th>Old File</DIV><DIV CLASS=th>New File</DIV><DIV CLASS=th>Diff</DIV></DIV><DIV CLASS=tbody>"
   for info in repo.index.diff(None):
    print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV></DIV>".format(info.a_path,info.b_path,info.change_type)
   print "</DIV></DIV>"
  if len(repo.untracked_files) > 0:
   print "<DIV CLASS=title>Untracked files</DIV>"
   print "<DIV CLASS=z-table><DIV CLASS=tbody>"
   for file in repo.untracked_files:
    print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV></DIV>".format(file)
   print "</DIV></DIV>"
  print "</FORM>"
 print "</DIV>"
