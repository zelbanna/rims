"""Module docstring.

Site view panes module

"""
__author__= "Zacharias El Banna"                     
__version__ = "17.10.4"
__status__= "Production"


#################################################################################################################
#
# SDCP "login"
#
# - writes cookies for sdcp_user(name) and sdcp_id
# - if passwords, then do proper checks
#
# Now do referrer?
#
def login(aWeb):
 if aWeb.cookie.get('sdcp_id'):
  id,user = aWeb.cookie.get('sdcp_id'),aWeb.cookie.get('sdcp_user')
 else:
  id,user = aWeb.get_value('sdcp_login',"None_None").split('_')
  if id != "None":
   # "Login successful"
   aWeb.add_cookie('sdcp_user', user, 86400)
   aWeb.add_cookie('sdcp_id', id, 86400)

 if id != "None":
  import sdcp.PackageContainer as PC
  PC.log_msg("Entering as [{}-{}]".format(id,user))
  aWeb.put_html(PC.sdcp['name'])
  print """<DIV class='z-main-menu' ID=div_main_menu>
  <A CLASS='z-btn z-menu-btn z-op' DIV=div_main_cont TITLE='General'   URL=ajax.cgi?call=pane_navigate&type=demo><IMG SRC='images/icon-start.png'/></A>
  <A CLASS='z-btn z-menu-btn z-op' DIV=div_main_cont TITLE='Rack'      URL=ajax.cgi?call=pane_rack><IMG SRC='images/icon-rack.png'/></A>
  <A CLASS='z-btn z-menu-btn z-op' DIV=div_main_cont TITLE='Devices'   URL=ajax.cgi?call=pane_devices><IMG SRC='images/icon-network.png'/></A>
  <A CLASS='z-btn z-menu-btn z-op' DIV=div_main_cont TITLE='Examine'   URL=ajax.cgi?call=pane_examine><IMG SRC='images/icon-examine.png'/></A>
  <A CLASS='z-btn z-menu-btn z-op' DIV=div_main_cont TITLE='Users'     URL=ajax.cgi?call=pane_users><IMG SRC='images/icon-users.png'/></A>
  <A CLASS='z-btn z-menu-btn z-op' DIV=div_main_cont TITLE='Documents' URL=ajax.cgi?call=pane_navigate&type=bookmark><IMG SRC='images/icon-docs.png'/></A>
  <A CLASS='z-btn z-menu-btn z-op' DIV=div_main_cont TITLE='ESXi'      URL=ajax.cgi?call=pane_esxi><IMG SRC='images/icon-servers.png'/></A>
  <A CLASS='z-btn z-menu-btn z-op' DIV=div_main_cont TITLE='Tool'      URL=ajax.cgi?call=pane_tools><IMG SRC='images/icon-tools.png'/></A>
  </DIV>
  <DIV CLASS=z-main-content ID=div_main_cont></DIV>"""
  return
 
 from sdcp.core.GenLib import DB
 db = DB()
 db.connect()
 db.do("SELECT id,name FROM users ORDER BY name")
 db.close()
 rows = db.get_rows()
 aWeb.put_html("Login")
 print "<DIV CLASS='z-centered' style='height:100%;'>"
 print "<DIV CLASS='z-frame' ID=div_login style='border: solid 1px black; width:600px; height:180px;'>"
 print "<CENTER><H1>Welcome to the management portal</H1></CENTER>"
 print "<FORM ACTION=index.cgi METHOD=POST ID=sdcp_login_form>"
 print "<INPUT TYPE=HIDDEN NAME=call VALUE=pane_login>"
 print "<DIV CLASS=z-table style='display:inline; float:left; margin:0px 0px 0px 30px;'><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Username:</DIV><DIV CLASS=td><SELECT style='border:none; display:inline; color:black' NAME=sdcp_login>"
 for row in rows:
  print "<OPTION VALUE='{0}_{1}' {2}>{1}</OPTION>".format(row['id'],row['name'],'' if str(row['id']) != id else "selected=True")
 print "</SELECT></DIV></DIV>"
 print "</DIV></DIV>"
 print "<A CLASS='z-btn z-op' OP=submit style='margin:20px 20px 30px 40px;' FRM=sdcp_login_form>Enter</A>"
 print "</FORM>"
 print "</DIV></DIV>"

#################################################################################################################
#
# Navigation
#

def navigate(aWeb):
 aWeb.put_headers()

 print "<DIV CLASS=z-navbar  ID=div_navbar>&nbsp;</DIV>"
 print "<DIV CLASS=z-content ID=div_content>"
 from ajax_sdcp import list_resource_type
 list_resource_type(aWeb)
 print "</DIV>"

##################################################################################################
#
# Examine pane
#
def examine(aWeb):
 aWeb.put_headers()
 import sdcp.PackageContainer as PC

 svchost = PC.sdcp['svcsrv']
 upshost = PC.sdcp['upshost']
 print "<DIV CLASS='z-navbar' ID=div_navbar>"
 print "<A CLASS='z-warning z-op' DIV=div_content MSG='Clear Network Logs?' URL='rest.cgi?call=sdcp.site:sdcp_clear_logs&logs={},{}'>Clear Logs</A>".format(PC.generic['logformat'],PC.sdcp['netlogs'])
 print "<A CLASS=z-op DIV=div_content URL='ajax.cgi?call=sdcp_examine_logs'>Logs</A>"
 if upshost:
  print "<A CLASS=z-op DIV=div_content URL='ajax.cgi?call=sdcp_examine_ups&upshost={}'>UPS</A>".format(upshost)
 if svchost:
  print "<A CLASS=z-op DIV=div_content URL='ajax.cgi?call=sdcp_examine_dns&svchost={}'>DNS</A>".format(svchost)
  print "<A CLASS=z-op DIV=div_content URL='ajax.cgi?call=sdcp_examine_dhcp&svchost={}'>DHCP</A>".format(svchost)
  print "<A CLASS=z-op DIV=div_content URL='ajax.cgi?call=sdcp_examine_svc&svchost={}'>Services Logs</A>".format(svchost)
 print "<A CLASS='z-reload z-op' DIV=div_main_cont URL='ajax.cgi?call=pane_examine'></A>"
 print "</DIV>"
 print "<DIV CLASS=z-content ID=div_content></DIV>"

##################################################################################################
#
# Weathermap
#
def weathermap(aWeb):
 aWeb.put_html("Weathermap")
 import sdcp.PackageContainer as PC

 page = aWeb.get_value('page')
 if not page:
  print "<DIV CLASS=z-navbar ID=div_navbar>" 
  for map,entry in PC.weathermap.iteritems():
   print "<A CLASS=z-op OP=iload IFRAME=iframe_wm_cont URL=ajax.cgi?call=pane_weathermap&page={0}>{1}</A>".format(map,entry['name'])
  print "</DIV>"
  print "<DIV CLASS='z-content' ID=div_content NAME='Weathermap Content'>"
  print "<IFRAME ID=iframe_wm_cont src=''></IFRAME>"
  print "</DIV>" 
 else:
  entry  = PC.weathermap[page]
  graphs = entry.get('graphs')
  if graphs:
   from sdcp.tools.munin import widget_rows
   widget_rows(graphs)
  print "<DIV CLASS='z-frame'>"
  print aWeb.get_include('{}.html'.format(page))
  print "</DIV>"

##################################################################################################
#
# Rack
#

def rack(aWeb):
 aWeb.put_headers()

 from sdcp.core.GenLib import DB
 db = DB()
 db.connect()
 db.do("SELECT id,name,image_url from racks")
 db.close()
 racks = db.get_rows()
 print "<CENTER><H1>Rack Overview | <A CLASS=z-op DIV=div_main_cont URL=ajax.cgi?call=pane_devices&target=vm&arg=1>Virtual Machines</A></H1><BR>"
 rackstr = "<A TITLE='{1}' CLASS=z-op DIV=div_main_cont URL=ajax.cgi?call=pane_devices&target=rack_id&arg={0}><IMG ALT='{1} ({2})' SRC='images/{2}'></A>&nbsp;"
 for index, rack in enumerate(racks):
  print rackstr.format(rack['id'], rack['name'], rack['image_url'])
 print "</CENTER></DIV>"

##################################################################################################
#
# Devices view pane
#
# - all devices and all else
#
 
def devices(aWeb):
 aWeb.put_headers()

 from sdcp.core.GenLib import DB
 # target = column name and arg = value, i.e. select all devices where vm = 1, rack_id = 5 :-)
 target = aWeb.get_value('target')
 arg    = aWeb.get_value('arg')
 
 print "<DIV CLASS=z-navbar ID=div_navbar>"
 print "<A CLASS=z-op DIV=div_content_left URL='ajax.cgi?call=device_view_devicelist{0}'>Devices</A>".format('' if (not target or not arg) else "&target="+target+"&arg="+arg)
 print "<A CLASS=z-op DIV=div_content_left URL=ajax.cgi?call=graph_list>Graphing</A>"

 db = DB() 
 db.connect()
 if target == 'rack_id':
  db.do("SELECT racks.name, fk_pdu_1, fk_pdu_2, INET_NTOA(consoles.ip) as con_ip FROM racks LEFT JOIN consoles ON consoles.id = racks.fk_console WHERE racks.id = '{}'".format(arg))
  data = db.get_row()
  if data.get('con_ip'):
   print "<A CLASS=z-op DIV=div_content_left SPIN=true URL='ajax.cgi?call=console_inventory&consolelist={0}'>Console</A>".format(data['con_ip'])
  if (data.get('fk_pdu_1') or data.get('fk_pdu_2')):
   res = db.do("SELECT INET_NTOA(ip) as ip, id FROM pdus WHERE (pdus.id = {0}) OR (pdus.id = {1})".format(data.get('fk_pdu_1','0'),data.get('fk_pdu_2','0')))
   rows = db.get_rows()
   pdus = ""
   for row in rows:
    pdus = pdus + "&pdulist=" + row.get('ip')
   print "<A CLASS=z-op DIV=div_content_left SPIN=true URL='ajax.cgi?call=pdu_inventory{0}'>Pdu</A>".format(pdus)
  print "<A CLASS=z-op DIV=div_content_right URL='ajax.cgi?call=rack_inventory&rack={0}'>'{1}' info</A>".format(arg,data['name'])
 else: 
  for type in ['pdu','console']:
   db.do("SELECT id, INET_NTOA(ip) as ip FROM {}s".format(type))
   tprows = db.get_rows()
   if len(tprows) > 0:
    arglist = "call={}_list".format(type)
    for row in tprows:
     arglist = arglist + "&{}list=".format(type) + row['ip']
    print "<A CLASS=z-op DIV=div_content_left SPIN=true URL='ajax.cgi?call={0}_inventory&{1}'>{2}</A>".format(type,arglist,type.title())
 db.close()
 print "<A CLASS='z-reload z-op' DIV=div_main_cont URL='ajax.cgi?{}'></A>".format(aWeb.get_args())
 print "<A CLASS='z-right z-op' DIV=div_content_right MSG='Discover devices?' URL='ajax.cgi?call=device_discover'>Device Discovery</A>"
 print "<A CLASS='z-right z-op' DIV=div_content_left URL='ajax.cgi?call=pdu_list_pdus'>PDUs</A>"
 print "<A CLASS='z-right z-op' DIV=div_content_left URL='ajax.cgi?call=console_list_consoles'>Consoles</A>"
 print "<A CLASS='z-right z-op' DIV=div_content_left URL='ajax.cgi?call=rack_list_racks'>Racks</A>"
 print "<SPAN STYLE='padding: 6px; height:34px; font-size:16px; font-weight:bold; background-color:green; color:white; float:right;'>Configuration:</SPAN>"
 print "</DIV>"
 print "<DIV CLASS=z-content       ID=div_content>"
 print "<DIV CLASS=z-content-left  ID=div_content_left></DIV>"
 print "<DIV CLASS=z-content-right ID=div_content_right>" 
 print aWeb.get_include('README.devices.html')
 print "</DIV></DIV>"

##################################################################################################
#
# ESXi
#

def esxi(aWeb):
 aWeb.put_headers()

 import sdcp.core.GenLib as GL                   
 db = GL.DB()
 db.connect()
 id = aWeb.get_value('id')
 print "<DIV CLASS=z-navbar ID=div_navbar>"
 if id:
  db.do("SELECT hostname, INET_NTOA(ip) as ipasc, domains.name AS domain FROM devices INNER JOIN domains ON domains.id = devices.a_dom_id WHERE devices.id = '{}'".format(id))
  data = db.get_row() 
  print "<A CLASS='z-warning z-op' DIV=div_esxi_op MSG='Really shut down?' URL='ajax.cgi?call=esxi_op&nstate=poweroff&id={}'>Shutdown</A>".format(id)
  print "<A CLASS=z-op DIV=div_content_right  URL=ajax.cgi?call=esxi_graph&hostname={0}&domain={1}>Stats</A>".format(data['hostname'],data['domain'])
  print "<A CLASS=z-op DIV=div_content_right  URL=ajax.cgi?call=esxi_logs&hostname={0}&domain={1}>Logs</A>".format(data['hostname'],data['domain'])
  print "<A CLASS=z-op HREF=https://{0}/ui     target=_blank>UI</A>".format(data['ipasc'])
  print "<A CLASS='z-op z-reload' DIV=div_main_cont URL='ajax.cgi?{}'></A>".format(aWeb.get_args())
  print "</DIV>"
  print "<DIV CLASS=z-content ID=div_content>"
  print "<DIV CLASS=z-content-left ID=div_content_left>"
  from ajax_esxi import op
  op(aWeb,data['ipasc'],data['hostname'])
 else:
  db.do("SELECT id, INET_NTOA(ip) AS ipasc, hostname, type FROM devices WHERE type = 'esxi' OR type = 'vcenter' ORDER BY type,hostname")
  rows = db.get_rows() 
  print "&nbsp;</DIV>"
  print "<DIV CLASS=z-content ID=div_content>"
  print "<DIV CLASS=z-content-left ID=div_content_left>"
  print "<DIV CLASS=z-frame><DIV CLASS=z-table style='width:99%'>"
  print "<DIV CLASS=thead><DIV CLASS=th>Type</DIV><DIV CLASS=th>Hostname</DIV></DIV>"        
  print "<DIV CLASS=tbody>"
  for row in rows:
   print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><DIV CLASS=td>".format(row['type'])
   if row['type'] == 'esxi':                  
    print "<A CLASS=z-op DIV=div_main_cont URL='ajax.cgi?call=pane_esxi&id={}'>{}</A>".format(row['id'],row['hostname'])
   else:
    print "<A TARGET=_blank HREF='https://{}:9443/vsphere-client/'>{}</A>".format(row['ipasc'],row['hostname'])
   print "</DIV></DIV>"
  print "</DIV></DIV></DIV>"
 db.close()
 print "</DIV>" 
 print "<DIV CLASS=z-content-right ID=div_content_right></DIV>"
 print "</DIV>"

##################################################################################################
#
# Users pane
#
def users(aWeb):
 aWeb.put_headers()

 print "<DIV CLASS=z-navbar ID=div_navbar>"
 print "<A CLASS=z-op DIV=div_content_left URL='ajax.cgi?call=sdcp_list_users'>Users</A>"
 print "<A CLASS=z-op DIV=div_content_left URL='ajax.cgi?call=sdcp_list_bookings'>Bookings</A>"
 print "<A CLASS='z-op z-right' OP=logout DIV=div_main_cont style='background-color:red;'>Log out</A>"
 print "</DIV>"
 print "<DIV CLASS=z-content ID=div_content>"
 print "<DIV CLASS=z-content-left  ID=div_content_left></DIV>"
 print "<DIV CLASS=z-content-right ID=div_content_right></DIV>"
 print "</DIV>"

##################################################################################################
#
# Tools pane
#
def tools(aWeb):
 aWeb.put_headers()

 print "<DIV CLASS=z-navbar ID=div_navbar>"
 print "<A CLASS=z-op           DIV=div_content URL='ajax.cgi?call=sdcp_list_resources'>Resources</A>"
 print "<A CLASS=z-op           DIV=div_content URL='ajax.cgi?call=sdcp_list_options'>Options</A>"
 print "<A CLASS='z-op z-right' DIV=div_content URL='ajax.cgi?call=sdcp_list_resource_type&type=bookmark'>Bookmarks</A>"
 print "<A CLASS='z-op z-right' DIV=div_content URL='ajax.cgi?call=sdcp_list_resource_type&type=demo'>Demos</A>"
 print "<A CLASS='z-op z-right' DIV=div_content URL='ajax.cgi?call=sdcp_list_resource_type&type=tool'>Tools</A>"
 print "</DIV>"
 print "<DIV CLASS=z-content ID=div_content>"
 print "</DIV>"



###################################################################################################################################
#
# Openstack
#
# Cookies:
# af_controller   = appformix controller ip
# os_controller   = openstack controller ip
# os_demo_name    = Name of Customer demoing for
# os_main_token   = auth token for project recovery
# os_project_id   = id for selected project
# os_project_name = name for selected project
# os_user_name    = username last used
# os_user_token   = token for user
# os_xyz_port     = port for service xyz
# os_xyz_url      = url  for service xyz
# os_xyz_id       = id   for service xyz
#

def openstack_login(aWeb):
 from sdcp.devices.openstack import OpenstackRPC
 import sdcp.PackageContainer as PC
 name = aWeb.get_value('name',"iaas")
 ctrl = aWeb.get_value('controller',"127.0.0.1")
 appf = aWeb.get_value('appformix',"127.0.0.1")
 user = aWeb.cookie.get("os_user_name")
 utok = aWeb.cookie.get("os_user_token")
 mtok = aWeb.cookie.get("os_main_token")
 prev = aWeb.cookie.get("os_project_id")
 if utok:
  aWeb.put_redirect("ajax.cgi?call=pane_openstack_portal")
  return

 aWeb.add_cookie("os_demo_name",name)
 aWeb.add_cookie("os_controller",ctrl)
 aWeb.add_cookie("af_controller",appf)

 if not mtok:
  openstack = OpenstackRPC(ctrl,None)
  res = openstack.auth({'project':PC.openstack['project'], 'username':PC.openstack['username'],'password':PC.openstack['password']})
  aWeb.add_cookie("os_main_token",openstack.get_token())
  PC.log_msg("openstack_login - login result: {}".format(str(res['result'])))
 else:
  PC.log_msg("openstack_login - reusing token: {}".format(mtok))
  openstack = OpenstackRPC(ctrl,mtok)

 ret = openstack.call("5000","v3/projects")
 projects = [] if not ret['code'] == 200 else ret['data']['projects']

 aWeb.put_html("{} 2 Cloud".format(name.capitalize()))
 print "<DIV CLASS='z-centered' style='height:100%;'>"
 print "<DIV CLASS='z-frame' ID=div_login style='border: solid 1px black; width:600px; height:180px;'>"
 print "<CENTER><H1>Welcome to '{}' Cloud portal</H1></CENTER>".format(name.capitalize())
 print "<FORM ACTION=ajax.cgi METHOD=POST ID=openstack_login>"
 print "<INPUT TYPE=HIDDEN NAME=call VALUE=pane_openstack_portal>"
 print "<INPUT TYPE=HIDDEN NAME=headers VALUE=no>"
 print "<DIV CLASS=z-table style='display:inline; float:left; margin:0px 0px 0px 30px;'><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Customer:</DIV><DIV CLASS=td><SELECT style='border:none; display:inline; color:black' NAME=project>"
 for p in projects:
  print "<OPTION VALUE={0}_{1} {2}>{1}</OPTION>".format(p['id'],p['name'],'' if not p['id'] == prev else "selected")
 print "</SELECT></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td>Username:</DIV><DIV CLASS=td><INPUT TYPE=text NAME=username {}></DIV></DIV>".format('' if not user else "VALUE={}".format(user))
 print "<DIV CLASS=tr><DIV CLASS=td>Password:</DIV><DIV CLASS=td><INPUT TYPE=password NAME=password></DIV></DIV>"
 print "</DIV></DIV>"
 print "<A CLASS='z-btn z-op' style='margin:20px 20px 30px 40px;' OP=submit FRM=openstack_login>Login</A>"
 print "</FORM>"
 print "</DIV></DIV>"

#
# Openstack Portal - New "Window"/Pane
#
def openstack_portal(aWeb):
 from json import dumps
 from sdcp.devices.openstack import OpenstackRPC
 import sdcp.PackageContainer as PC
 ctrl = aWeb.cookie.get('os_controller')
 utok = aWeb.cookie.get('os_user_token')

 if not utok:
  username = aWeb.get_value('username')
  password = aWeb.get_value('password')
  project  = aWeb.get_value('project','none_none')
  (pid,pname) = project.split('_')
  openstack = OpenstackRPC(ctrl,None)
  res = openstack.auth({'project':pname, 'username':username,'password':password })
  if not res['result'] == "OK":
   aWeb.put_html("Openstack Portal")
   PC.log_msg("openstack_portal - error during login for {}@{}".format(username,ctrl))
   print "Error logging in - please try login again"
   return
  utok = openstack.get_token()
  aWeb.add_cookie('os_user_token',utok)
  aWeb.add_cookie('os_user_name',username)
  aWeb.add_cookie("os_project_id",pid)
  aWeb.add_cookie("os_project_name",pname)
  aWeb.add_cookie("os_services",",".join(['heat','nova','neutron','glance']))
  for service in ['heat','nova','neutron','glance']:
   base = "os_" + service
   port,url,id = openstack.get_service(service,'public')
   aWeb.add_cookie(base + "_port",port)
   aWeb.add_cookie(base + "_url",url)
   aWeb.add_cookie(base + "_id",id)

  PC.log_msg("openstack_portal - successful login and catalog init for {}@{}".format(username,ctrl))
 else:
  username = aWeb.cookie.get("os_user_name")
  pid      = aWeb.cookie.get("os_project_id")
  pname    = aWeb.cookie.get("os_project_name")
  PC.log_msg("openstack_portal - using existing token for {}@{}".format(username,ctrl))
  openstack = OpenstackRPC(ctrl,utok)

 aWeb.put_html("Openstack Portal")
 print "<DIV CLASS=z-content-head ID=div_content_head>"
 print "<DIV CLASS=z-content-head-info ID=div_content_head_info>"
 print "<DIV CLASS=z-table style='display:inline; float:left; margin:5px 100px 0px 10px;'><DIV CLASS=tbody>"
 print "<DIV CLASS=tr style='background:transparent'><DIV CLASS=td><B>Identity:</B></DIV><DIV CLASS=td><I>{}</I></DIV><DIV CLASS=td>&nbsp;<B>Id:</B></DIV><DIV CLASS=td><I>{}</I></DIV></DIV>".format(pname,pid)
 print "<DIV CLASS=tr style='background:transparent'><DIV CLASS=td><B>Username:</B></DIV><DIV CLASS=td><I>{}</I></DIV><DIV CLASS=td>&nbsp;<B>Token:</B></DIV><DIV CLASS=td><I>{}</I></DIV></DIV>".format(username,utok)
 print "</DIV></DIV>"
 print "<A CLASS='z-btn z-op' OP=logout URL='ajax.cgi?call=pane_openstack_login&headers=no&controller={}&name={}&appformix={}' style='float:right; background-color:red!important; margin-right:20px;'>Log out</A>".format(ctrl,aWeb.cookie.get('os_demo_name'),aWeb.cookie.get('af_controller'))
 print "</DIV>"
 print "<DIV CLASS='z-navbar' style='top:60px; z-index:1001' ID=div_navbar>"
 print "<A CLASS=z-op           DIV=div_content URL='ajax.cgi?call=heat_list'>Orchestration</A>"
 print "<A CLASS=z-op           DIV=div_content URL='ajax.cgi?call=neutron_list'>Virtual Networks</A>"
 print "<A CLASS=z-op           DIV=div_content URL='ajax.cgi?call=nova_list'>Virtual Machines</A>"
 print "<A CLASS=z-op SPIN=true DIV=div_content URL='ajax.cgi?call=appformix_report'>Usage Report</A>"
 print "<A CLASS='z-reload z-op'  OP=redirect URL='ajax.cgi?call=pane_openstack_portal&headers=no'></A>"
 if username == 'admin':
  print "<A CLASS='z-op z-right'  DIV=div_content URL=ajax.cgi?call=openstack_fqname>FQDN</A>"
  print "<A CLASS='z-op z-right'  DIV=div_content URL=ajax.cgi?call=openstack_api>API Debug</A>"
 print "</DIV>"
 print "</DIV>"
 print "<DIV CLASS=z-content ID=div_content style='top:94px;'></DIV>"
