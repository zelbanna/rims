"""Module docstring.

Site view panes module

"""
__author__= "Zacharias El Banna"                     
__version__ = "17.6.1GA"
__status__= "Production"

#################################################################################################################
#
# SDCP "login"
#
# - writes cookies for sdcp_user(name) and sdcp_id
# - if passwords, then do proper checks
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
  aWeb.put_html("SDCP Portal")
  print "<CENTER><H1>Welcome {} - please choose section to continue</H1></CENTER>".format(user)
  return
 
 from sdcp.core.GenLib import DB
 db = DB()
 db.connect()
 db.do("SELECT id,name FROM users ORDER BY name")
 db.close()
 rows = db.get_all_rows()
 aWeb.put_html("SDCP Portal")
 print "<DIV CLASS='z-centered' style='height:100%;'>"
 print "<DIV ID=div_sdcp_login style='background-color:#F3F3F3; display:block; border: solid 1px black; border-radius:8px; width:600px; height:180px;'>"
 print "<CENTER><H1>Welcome to the management portal</H1></CENTER>"
 print "<FORM ACTION=pane.cgi METHOD=POST ID=sdcp_login_form>"
 print "<INPUT TYPE=HIDDEN NAME=view VALUE=login>"
 print "<DIV CLASS=z-table style='display:inline; float:left; margin:0px 0px 0px 30px;'><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Username:</DIV><DIV CLASS=td><SELECT style='border:none; display:inline; color:black' NAME=sdcp_login>"
 for row in rows:
  print "<OPTION VALUE='{0}_{1}' {2}>{1}</OPTION>".format(row['id'],row['name'],'' if str(row['id']) != id else "selected=True")
 print "</SELECT></DIV></DIV>"
 print "</DIV></DIV>"
 print "<A CLASS='z-btn z-op' style='margin:20px 20px 30px 40px;' OP=submit FRM=sdcp_login_form>Enter</A>"
 print "</FORM>"
 print "</DIV></DIV>"


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
  aWeb.put_redirect("pane.cgi?view=openstack_portal")
  return

 aWeb.add_cookie("os_demo_name",name)
 aWeb.add_cookie("os_controller",ctrl)
 aWeb.add_cookie("af_controller",appf)

 if not mtok:
  openstack = OpenstackRPC(ctrl,None)
  res = openstack.auth({'project':PC.openstack_project, 'username':PC.openstack_username,'password':PC.openstack_password })
  aWeb.add_cookie("os_main_token",openstack.get_token())
  PC.log_msg("openstack_login - login result: {}".format(str(res['result'])))
 else:
  PC.log_msg("openstack_login - reusing token: {}".format(mtok))
  openstack = OpenstackRPC(ctrl,mtok)

 ret = openstack.call("5000","v3/projects")
 projects = [] if not ret['code'] == 200 else ret['data']['projects']

 aWeb.put_html("{} 2 Cloud".format(name.capitalize()))
 print "<DIV CLASS='z-centered' style='height:100%;'>"
 print "<DIV ID=div_os_login style='background-color:#F3F3F3; display:block; border: solid 1px black; border-radius:8px; width:600px; height:180px;'>"
 print "<CENTER><H1>Welcome to '{}' Cloud portal</H1></CENTER>".format(name.capitalize())
 print "<FORM ACTION=pane.cgi METHOD=POST ID=openstack_login>"
 print "<INPUT TYPE=HIDDEN NAME=view VALUE=openstack_portal>"
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
 print "<A CLASS='z-btn z-op' OP=logout URL='pane.cgi?view=openstack_login&controller={}&name={}&appformix={}' style='float:right; background-color:red!important; margin-right:20px;'>Log out</A>".format(ctrl,aWeb.cookie.get('os_demo_name'),aWeb.cookie.get('af_controller'))
 print "</DIV>"
 print "<DIV CLASS='z-navbar' style='top:60px; z-index:1001' ID=div_navbar>"
 print "<A CLASS='z-op'           DIV=div_content URL='ajax.cgi?call=heat_list'>Orchestration</A>"
 print "<A CLASS='z-op'           DIV=div_content URL='ajax.cgi?call=neutron_list'>Virtual Networks</A>"
 print "<A CLASS='z-op'           DIV=div_content URL='ajax.cgi?call=nova_list'>Virtual Machines</A>"
 print "<A CLASS='z-op' SPIN=true DIV=div_content URL='ajax.cgi?call=appformix_report'>Usage Report</A>"
 print "<A CLASS='z-reload z-op'  OP=redirect URL='pane.cgi?view=openstack_portal'></A>"
 if username == 'admin':
  print "<A CLASS='z-op z-right'  DIV=div_content URL=ajax.cgi?call=openstack_fqname>FQDN</A>"
  print "<A CLASS='z-op z-right'  DIV=div_content URL=ajax.cgi?call=openstack_api>API Debug</A>"
 print "</DIV>"
 print "</DIV>"
 print "<DIV CLASS=z-content ID=div_content style='top:94px;'></DIV>"

#
# Console redirect - since ajax not able to do header manipulations 'yet'
#
def openstack_console(aWeb):
 from sdcp.devices.openstack import OpenstackRPC
 token = aWeb.cookie.get('os_user_token')
 if token:
  id   = aWeb.get_value('id')
  name = aWeb.get_value('name')
  controller = OpenstackRPC(aWeb.cookie.get('os_controller'),token)
  data = controller.call(aWeb.cookie.get('os_nova_port'), aWeb.cookie.get('os_nova_url') + "/servers/{}/remote-consoles".format(id), { "remote_console": { "protocol": "vnc", "type": "novnc" } }, header={'X-OpenStack-Nova-API-Version':'2.8'})
  if data['code'] == 200:
   url = data['data']['remote_console']['url']
   # URL is #@?! inline URL.. remove http:// and replace IP (assume there is a port..) with controller IP
   url = "http://" + aWeb.cookie.get('os_controller') + ":" + url[7:].partition(':')[2]
   aWeb.put_redirect("{}&title={}".format(url,name))
 else:
  aWeb.put_html('Openstack Console')
  print "Not logged in "
  
##################################################################################################
#
# Examine pane
#
def examine(aWeb):
 if not aWeb.cookie.get('sdcp_id'):
  aWeb.put_redirect("pane.cgi?view=login")
  return

 aWeb.put_html('Services Pane')
 import sdcp.PackageContainer as PC
 from sdcp.tools.Grapher import Grapher

 domain  = aWeb.get_value('domain')
 upshost = aWeb.get_value('upshost')
 svchost = PC.sdcp_svcsrv
 graph = Grapher()  
 print "<DIV CLASS='z-navbar' ID=div_navbar>"
 print "<A CLASS='z-warning z-op' DIV=div_sys MSG='Clear Network Logs?' URL='rest.cgi?call=sdcp.site:sdcp_clear_logs&logs={},{}'>Clear Logs</A>".format(PC.generic_logformat,PC.sdcp_netlogs)
 print "<A CLASS=z-op OP=single SELECTOR='.z-system' DIV=div_sys URL='.z-system'>Logs</A>"
 if upshost:
  print "<A CLASS=z-op OP=single SELECTOR='.z-system' DIV=div_ups URL='.z-system'>UPS</A>"
 if svchost:
  print "<A CLASS=z-op OP=single SELECTOR='.z-system' DIV=div_dns  URL='.z-system'>DNS</A>"
  print "<A CLASS=z-op OP=single SELECTOR='.z-system' DIV=div_dhcp URL='.z-system'>DHCP</A>"
  print "<A CLASS=z-op OP=single SELECTOR='.z-system' DIV=div_svc URL='.z-system'>Services Logs</A>"
 print "<A CLASS='z-reload z-op' OP=redirect URL='pane.cgi?{}'></A>".format(aWeb.get_args())
 print "</DIV>"
 
 print "<DIV CLASS=z-content ID=div_content>"
 
 print "<DIV CLASS=z-system id=div_sys title='System Logs' style='display:block;'>"
 from sdcp.site.rest_sdcp import examine_logs
 logs = examine_logs({'count':10,'logs':"{},{}".format(PC.generic_logformat,PC.sdcp_netlogs)})
 for file,res in logs.iteritems():
  print "<DIV CLASS='z-logs'><H1>{}</H1><PRE>".format(file)
  for line in res:
   print line
  print "</PRE></DIV>"
 print "</DIV>"
 
 if upshost:
  print "<DIV CLASS=z-system id=div_ups title='UPS info' style='display:none;'>"
  graph.widget_cols([ "{1}/{0}.{1}/hw_apc_power".format(upshost,domain), "{1}/{0}.{1}/hw_apc_time".format(upshost,domain), "{1}/{0}.{1}/hw_apc_temp".format(upshost,domain) ])
  print "</DIV>"
 
 if svchost:
  from sdcp.core.rest import call as rest_call

  print "<DIV CLASS=z-system id=div_dns title='DNS data' style='display:none; width:100%'>"
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
  print "</DIV>"
 
  print "<DIV CLASS=z-system id=div_dhcp title='DHCP leases' style='display:none; width:100%'>"
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
  print "</DIV>"
 
  print "<DIV CLASS=z-system id=div_svc title='System Logs' style='display:none; width:100%;'>"
  logs = rest_call("http://{}/rest.cgi".format(svchost), "sdcp.site:sdcp_examine_logs",{'count':20,'logs':PC.generic_logformat})
  for file,res in logs.iteritems():
   print "<DIV CLASS='z-logs'><H1>{}</H1><PRE>".format(file)
   for line in res:
    print line
   print "</PRE></DIV>"
  print "</DIV>"
 
 print "</DIV>"

##################################################################################################
#
# Munin
#
def munin(aWeb):
 if not aWeb.cookie.get('sdcp_id'):
  aWeb.put_redirect("pane.cgi?view=login")
  return

 aWeb.put_html('Munin')
 print """
 <SCRIPT>
 function toggleMuninNavigation(){
  var iframe = document.getElementById('iframe_munin');
  var innerDoc = iframe.contentDocument || iframe.contentWindow.document;
  var nav = innerDoc.getElementById('nav');
  var cont = innerDoc.getElementById('content');
  if (nav.style.display == 'block') {
   nav.style.display = 'none';
   cont.style.marginLeft = '0px'
  } else {
   nav.style.display = 'block'; 
   cont.style.marginLeft = '180px'
  }
 }
 </SCRIPT>
 <DIV CLASS=z-navbar ID=div_navbar>
 <A onclick=toggleMuninNavigation()>Navigation</A>
 <A CLASS='z-reload z-op' OP=iload IFRAME=iframe_munin URL='/munin-cgi/munin-cgi-html/index.html'></A>
 </DIV>
 <DIV CLASS='z-content' ID=div_content>
 <IFRAME ID=iframe_munin src='/munin-cgi/munin-cgi-html/index.html'></IFRAME>
 </DIV>
 """

##################################################################################################
#
# Weathermap
#
def weathermap(aWeb):
 if not aWeb.cookie.get('sdcp_id'):
  aWeb.put_redirect("pane.cgi?view=login")
  return

 page = aWeb.get_value('page')
 json = aWeb.get_value('json')
 
 if page == 'main':
  aWeb.put_html('Weathermap')
  print "<DIV CLASS=z-navbar ID=div_navbar>"
 
  wmlist = []
  if json:
   try:
    from json import load
    with open(json) as conffile:
     config = load(conffile)
     for entry in config.keys():
      name= config[entry]['map'][3:]
      print "<A CLASS='z-op' OP=iload IFRAME=iframe_wm_cont URL=pane.cgi?view=weathermap&json={2}&page={0}>{1}</A>".format(name,name.capitalize(),json)
   except :
    print "<A CLASS='z-warning'>Error loading JSON file</A>"
  else:
   try:
    from os import listdir
    for file in listdir("wm_configs/"):
     if file.startswith("wm_"):
      name= file[3:-5]
      print "<A CLASS='z-op' OP=iload IFRAME=iframe_wm_cont URL=pane.cgi?view=weathermap&page={0}>{1}</A>".format(name,name.capitalize())
   except Exception as err:
    print "weathermap.cgi: error finding config files in 'wm_configs/' [{}]".format(str(err))
  print "</DIV>"
  print "<DIV CLASS='z-content' ID=div_content NAME='Weathermap Content'>"
  print "<IFRAME ID=iframe_wm_cont src=''></IFRAME>"
  print "</DIV>"
 
 elif page:
  aWeb.put_html("Weathermap")
  if json:
   from json import load
   from sdcp.tools.Grapher import Grapher
   with open(json) as conffile:
    config = load(conffile)
    entry  = config[page]
    map    = entry['map']
    graphs = entry.get('graphs',None)
    graph  = Grapher()
    if graphs:
     graph.widget_rows(graphs)
    print "<DIV CLASS='z-frame'>"
    print aWeb.get_include('{}.html'.format(map))
    print "</DIV>"
  else:
   print "<DIV CLASS='z-frame'>"
   print aWeb.get_include('wm_{}.html'.format(page))
   print "</DIV>"
 else:
  print "Weathermap fetches config names from the<PRE> wm_configs/</PRE> directory, all names starting with wm_ and ending with .conf are mapped for navigation bar"

##################################################################################################
#
# Rack
#

def rack(aWeb):
 if not aWeb.cookie.get('sdcp_id'):
  aWeb.put_redirect("pane.cgi?view=login")
  return

 aWeb.put_html("Racks")
 from sdcp.core.GenLib import DB
 db = DB()
 db.connect()
 db.do("SELECT id,name,image_url from racks")
 db.close()
 racks = db.get_all_rows()
 print "<CENTER><H1>Rack Overview | <A HREF=pane.cgi?view=devices&target=vm&arg=1>Virtual Machines</A> <A TITLE='Non-racked devices' HREF=pane.cgi?view=rack_info&rack=NULL>*</A></H1><BR>"
 rackstr = "<A TARGET=main_cont TITLE='{1}' HREF=pane.cgi?view=devices&target=rack_id&arg={0}><IMG ALT='{1} ({2})' SRC='images/{2}'></A>&nbsp;"
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
 if not aWeb.cookie.get('sdcp_id'):
  aWeb.put_redirect("pane.cgi?view=login")
  return

 aWeb.put_html("Device View")

 from sdcp.core.GenLib import DB
 op     = aWeb.get_value('op')
 domain = aWeb.get_value('domain')
 # target = column name and arg = value, i.e. select all devices where vm = 1, rack_id = 5 :-)
 target = aWeb.get_value('target')
 arg    = aWeb.get_value('arg')
 
 print "<DIV CLASS=z-navbar ID=div_navbar>"
 print "<A CLASS='z-op' DIV=div_content_left URL='ajax.cgi?call=device_view_devicelist{0}'>Devices</A>".format('' if (not target or not arg) else "&target="+target+"&arg="+arg)
 print "<A CLASS='z-op' DIV=div_content_left URL='ajax.cgi?call=graph_list&domain={}'>Graphing</A>".format(domain)

 db = DB() 
 db.connect()
 if target == 'rack_id':
  db.do("SELECT racks.name, fk_pdu_1, fk_pdu_2, INET_NTOA(consoles.ip) as con_ip FROM racks LEFT JOIN consoles ON consoles.id = racks.fk_console WHERE racks.id = '{}'".format(arg))
  data = db.get_row()
  if data.get('con_ip'):
   print "<A CLASS='z-op' DIV=div_content_left SPIN=true URL='ajax.cgi?call=console_inventory&consolelist={0}'>Console</A>".format(data['con_ip'])
  if (data.get('fk_pdu_1') or data.get('fk_pdu_2')):
   res = db.do("SELECT INET_NTOA(ip) as ip, id FROM pdus WHERE (pdus.id = {0}) OR (pdus.id = {1})".format(data.get('fk_pdu_1','0'),data.get('fk_pdu_2','0')))
   rows = db.get_all_rows()
   pdus = ""
   for row in rows:
    pdus = pdus + "&pdulist=" + row.get('ip')
   print "<A CLASS='z-op' DIV=div_content_left SPIN=true URL='ajax.cgi?call=pdu_inventory{0}'>Pdu</A>".format(pdus)
  print "<A CLASS='z-op' DIV=div_content_right URL='ajax.cgi?call=rack_info&rack={0}'>'{1}' info</A>".format(arg,data['name'])
 else: 
  for type in ['pdu','console']:
   db.do("SELECT id, INET_NTOA(ip) as ip FROM {}s".format(type))
   tprows = db.get_all_rows()
   if len(tprows) > 0:
    arglist = "call={}_list".format(type)
    for row in tprows:
     arglist = arglist + "&{}list=".format(type) + row['ip']
    print "<A CLASS='z-op' DIV=div_content_left SPIN=true URL='ajax.cgi?call={0}_inventory&{1}'>{2}</A>".format(type,arglist,type.title())
 db.close() 
 print "<A CLASS='z-reload z-op' OP=redirect URL='pane.cgi?{}'></A>".format(aWeb.get_args())
 print "<A CLASS='z-right z-op' DIV=div_content_right MSG='Discover devices?' URL='ajax.cgi?call=device_discover&domain={0}'>Device Discovery</A>".format(domain)
 print "<A CLASS='z-right z-op' DIV=div_content_left URL='ajax.cgi?call=pdu_list_pdus'>PDUs</A>"
 print "<A CLASS='z-right z-op' DIV=div_content_left URL='ajax.cgi?call=console_list_consoles'>Consoles</A>"
 print "<A CLASS='z-right z-op' DIV=div_content_left URL='ajax.cgi?call=rack_list_racks'>Racks</A>"
 print "<SPAN STYLE='padding: 6px 4px; font-size:16px; font-weight:bold; background-color:green; color:white; float:right;'>Configuration:</SPAN>"
 print "</DIV>"
 print "<DIV CLASS=z-content-left  ID=div_content_left></DIV>"
 print "<DIV CLASS=z-content-right ID=div_content_right>" 
 print aWeb.get_include('README.devices.html')
 print "</DIV>"

##################################################################################################
#
# ESXi
#
def esxi(aWeb):
 if not aWeb.cookie.get('sdcp_id'):
  aWeb.put_redirect("pane.cgi?view=login")
  return

 aWeb.put_html("ESXi Operations")
 from ajax_esxi import op as esxi_op
 from sdcp.devices.ESXi import ESXi
 host   = aWeb.get_value('host')
 domain = aWeb.get_value('domain')
 esxi   = ESXi(host,domain)
 print "<DIV CLASS=z-navbar ID=div_navbar>"
 print "<A CLASS='z-warning z-op' DIV=div_esxi_op MSG='Really shut down?' URL='ajax.cgi?call=esxi_op&nstate=poweroff&{}'>Shutdown</A>".format(aWeb.get_args())
 print "<A CLASS=z-op DIV=div_content_right URL=ajax.cgi?call=esxi_graph&{}>Stats</A>".format(aWeb.get_args())
 print "<A CLASS=z-op DIV=div_content_right URL=ajax.cgi?call=esxi_logs&{}>Logs</A>".format(aWeb.get_args())
 print "<A CLASS=z-op HREF=https://{0}/ui        target=_blank>UI</A>".format(esxi._ip)
 print "<A CLASS=z-op HREF=http://{0}/index.html target=_blank>IPMI</A>".format(esxi.get_kvm_ip('ipmi'))
 print "<A CLASS='z-op z-reload' OP=redirect URL='pane.cgi?{}'></A>".format(aWeb.get_args())
 print "</DIV>"
 print "<DIV CLASS=z-content ID=div_content>"
 print "<DIV CLASS=z-content-left ID=div_content_left>"
 esxi_op(aWeb)
 print "</DIV>" 
 print "<DIV CLASS=z-content-right ID=div_content_right style='top:0px;'></DIV>"

##################################################################################################
#
# Settings/System pane
#

def config(aWeb):
 if not aWeb.cookie.get('sdcp_id'):
  aWeb.put_redirect("pane.cgi?view=login")
  return

 aWeb.put_html("Config and Settings")
 domain    = aWeb.get_value('domain', None)
 print "<DIV CLASS=z-content style='top:0px;' ID=div_content>"
 print "<DIV CLASS=z-frame ID=div_config_menu style='width:200px; float:left; min-height:300px;'>"
 print "<A STYLE='width:192px; text-align:left' CLASS='z-btn z-warning z-op' DIV=div_config SPIN=true MSG='Clear DB?' URL='ajax.cgi?call=device_clear_db'>Clear Database</A>"
 print "<A STYLE='width:192px; text-align:left' CLASS='z-btn z-op' DIV=div_config SPIN=true URL='ajax.cgi?call=graph_find&domain={0}'>Graph Discovery</A>".format(domain)
 print "<A STYLE='width:192px; text-align:left' CLASS='z-btn z-op' DIV=div_config           URL='ajax.cgi?call=graph_sync&domain={0}'>Synch Graphing</A>".format(domain)
 print "<A STYLE='width:192px; text-align:left' CLASS='z-btn z-op' DIV=div_config SPIN=true URL='ajax.cgi?call=ddi_sync'>Synch DDI</A>"
 print "<A STYLE='width:192px; text-align:left' CLASS='z-btn z-op' DIV=div_config SPIN=true URL='ajax.cgi?call=ddi_dhcp_update'>Update DHCP</A>"
 print "<A STYLE='width:192px; text-align:left' CLASS='z-btn z-op' DIV=div_config SPIN=true URL='ajax.cgi?call=ddi_load_infra'>Load DDI Tables</A>"
 print "<A STYLE='width:192px; text-align:left' CLASS='z-btn' TARGET=_blank HREF='ajax.cgi?call=device_dump_db'>Dump DB to JSON</A>"
 print "<A STYLE='width:192px; text-align:left' CLASS='z-btn z-op' DIV=div_config SPIN=true URL='ajax.cgi?call=device_rack_info'>Device Rackinfo</A>"
 print "<A STYLE='width:192px; text-align:left' CLASS='z-btn z-op' DIV=div_config           URL='ajax.cgi?call=device_mac_sync'>Sync MAC Info</A>"
 print "<A STYLE='width:192px; text-align:left' CLASS='z-btn z-op' DIV=div_content          URL='ajax.cgi?call=sdcp_list_users'>Users</A>"
 print "<A STYLE='width:192px; text-align:left' CLASS='z-btn z-op' DIV=div_content          URL='ajax.cgi?call=sdcp_list_bookings'>Bookings</A>"
 print "</DIV>"
 print "<DIV ID=div_config style='min-width:600px; min-height:300px; display:inline;'></DIV>"
 print "</DIV>"
