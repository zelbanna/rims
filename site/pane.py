"""Module docstring.

Site view panes module

"""
__author__= "Zacharias El Banna"                     
__version__ = "10.5.1GA"
__status__= "Production"

#
# - Divide all panes into pane (nav) and include widget_xyz
#
#
##################################################################################################
#
# Examine pane
#
def examine(aWeb):
 from ajax_examine import clear_logs
 print aWeb.get_header_full('Services Pane')
 domain  = aWeb.get_value('domain')
 upshost = aWeb.get_value('upshost')
 svclist = aWeb.get_list('svchost')
 from sdcp.tools.Grapher import Grapher
 graph = Grapher() 
 
 print aWeb.get_listeners()
 print "<DIV CLASS='z-navframe' ID=div_navframe>"
 
 print "<DIV CLASS='z-navbar' ID=div_navbar>"
 print "<A CLASS='z-warning z-op' OP=confirm DIV=div_examine_log MSG='Clear Network Logs?' LNK='ajax.cgi?call=examine_clear_logs&{}'>Clear Logs</A>".format(aWeb.get_args_except(['pane']))
 print "<A CLASS=z-op OP=single SELECTOR='.z-system' DIV=div_examine_log LNK='.z-system'>Logs</A>"
 if upshost:
  print "<A CLASS=z-op OP=single SELECTOR='.z-system' DIV=div_ups LNK='.z-system'>UPS</A>"
 if svclist:
  print "<A CLASS=z-op OP=single SELECTOR='.z-system' DIV=div_dns  LNK='.z-system'>DNS</A>"
  print "<A CLASS=z-op OP=single SELECTOR='.z-system' DIV=div_dhcp LNK='.z-system'>DHCP</A>"
  print "<A CLASS=z-op OP=single SELECTOR='.z-system' DIV=div_external LNK='.z-system'>External</A>"
 print "<A CLASS='z-reload z-op' OP=reload LNK='pane.cgi?{}'></A>".format(aWeb.get_args_except())
 print "</DIV>"
 
 print "<DIV CLASS='z-navcontent' ID=div_navcont>"
 
 print "<DIV CLASS='z-system' id=div_examine_log title='Network Logs' style='display:block;'>"
 clear_logs(aWeb, False)
 print "</DIV>"
 
 if upshost:
  print "<DIV CLASS='z-system' id=div_ups title='UPS info' style='display:none;'>"
  graph.widget_cols([ "{1}/{0}.{1}/hw_apc_power".format(upshost,domain), "{1}/{0}.{1}/hw_apc_time".format(upshost,domain), "{1}/{0}.{1}/hw_apc_temp".format(upshost,domain) ])
  print "</DIV>"
 
 if svclist:
  print "<DIV CLASS='z-system' id=div_dns title='DNS data' style='display:none;'>"
  graph.widget_rows( ["{1}/{0}.{1}/pdns_queries".format(svclist[0],domain), "{1}/{0}.{1}/dhcpd3".format(svclist[0],domain) ])
  print "<DIV CLASS='z-table' style='width:30%; float:left;'><CENTER>{}</CENTER></DIV>".format(aWeb.get_include("http://"+ svclist[0] +"/dns-top.php?type=sites"))
  print "<DIV CLASS='z-table' style='width:30%; float:left;'><CENTER>{}</CENTER></DIV>".format(aWeb.get_include("http://"+ svclist[0] +"/dns-top.php?type=clients"))
  print "</DIV>"
 
  print "<DIV CLASS='z-system' id=div_dhcp title='DHCP leases' style='display:none;'>"
  print "<DIV CLASS='z-logs'><H1>DHCP Lease List</H1>{}</DIV>".format(aWeb.get_include("http://"+ svclist[0] +"/dhcp-lease-list.php"))
  print "</DIV>"
 
  print "<DIV CLASS='z-system' id=div_external title='System Logs' style='display:none;'>"
  for svc in svclist:
   print "<DIV style='width:" + str(int(100/len(svclist))) + "%; float:left'>"
   print "<DIV CLASS='z-logs'><H1>System Logs for {}.{}</H1>{}</DIV>".format(svc,domain,aWeb.get_include("http://"+ svc +"/ajax.cgi?call=examine_log"))
   print "</DIV>"
  print "</DIV>"
 
 print "</DIV>"
 print "</DIV>"

##################################################################################################
#
# Munin
#
def munin(aWeb):
 print aWeb.get_header_full('Munin')
 print aWeb.get_listeners()
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
 <DIV CLASS=z-navframe ID=div_navframe>
 <DIV CLASS=z-navbar ID=div_navbar>
 <A onclick=toggleMuninNavigation()>Navigation</A>
 <A CLASS='z-reload z-op' OP=iload IFRAME=iframe_munin LNK='/munin-cgi/munin-cgi-html/index.html'></A>
 </DIV>
 <DIV CLASS='z-navcontent' ID=div_navcont>
 <IFRAME ID=iframe_munin src='/munin-cgi/munin-cgi-html/index.html'></IFRAME>
 </DIV>
 </DIV>
 """

##################################################################################################
#
# Weathermap
#
def weathermap(aWeb):
 page = aWeb.get_value('page')
 json = aWeb.get_value('json')
 
 if page == 'main':
  print aWeb.get_header_full('Weathermap')
  print aWeb.get_listeners()
  print "<DIV CLASS=z-navframe ID=div_navframe>"
  print "<DIV CLASS=z-navbar ID=div_navbar>"
 
  wmlist = []
  if json:
   try:
    from json import load
    with open(json) as conffile:
     config = load(conffile)
     for entry in config.keys():
      name= config[entry]['map'][3:]
      print "<A CLASS='z-op' OP=iload IFRAME=iframe_wm_cont LNK=pane.cgi?view=weathermap&json={2}&page={0}>{1}</A>".format(name,name.capitalize(),json)
   except :
    print "<A CLASS='z-warning'>Error loading JSON file</A>"
  else:
   try:
    from os import listdir
    for file in listdir("wm_configs/"):
     if file.startswith("wm_"):
      name= file[3:-5]
      print "<A CLASS='z-op' OP=iload IFRAME=iframe_wm_cont LNK=pane.cgi?view=weathermap&page={0}>{1}</A>".format(name,name.capitalize())
   except Exception as err:
    print "weathermap.cgi: error finding config files in 'wm_configs/' [{}]".format(str(err))
  print "</DIV>"
  print "<DIV CLASS='z-navcontent' ID=div_navcont NAME='Weathermap Content'>"
  print "<IFRAME ID=iframe_wm_cont src=''></IFRAME>"
  print "</DIV>"
  print "</DIV>"
 
 elif page:
  print aWeb.get_header_base()
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
    print "<DIV CLASS='z-graph'>"
    print aWeb.get_include('{}.html'.format(map))
    print "</DIV>"
  else:
   print "<DIV CLASS='z-graph'>"
   print aWeb.get_include('wm_{}.html'.format(page))
   print "</DIV>"
 else:
  print "Weathermap fetches config names from the<PRE> wm_configs/</PRE> directory, all names starting with wm_ and ending with .conf are mapped for navigation bar"

##################################################################################################
#
# Shutdown all
#

def shutdownall(aWeb):
 from sdcp.devices.ESXi import thread_shutdown_host
 from threading import Thread 
 domain    = aWeb.get_value('domain',None)
 srvlist   = aWeb.get_list('srvhost')
  
 if domain and srvlist:
  for host in srvlist:
   fqdn = host+"."+domain
   t = Thread(target = thread_shutdown_host, args=[fqdn, aWeb])
   t.start()
 else:
  print "<PRE>Shutdown system not starting</PRE>"

##################################################################################################
#
# Rack
#

def rack(aWeb):
 print aWeb.get_header_full("Racks")
 from sdcp.core.GenLib import DB
 db = DB()
 db.connect()
 db.do("SELECT * from racks")
 racks = db.get_all_rows()
 print "<DIV>"
 print "<CENTER><H1>Rack Overview | <A HREF=pane.cgi?view=devices&target=vm&arg=1>Virtual Machines</A> <A TITLE='Non-racked devices' HREF=pane.cgi?view=rack_info&rack=NULL>*</A></H1><BR>"
 rackstr = "<A TARGET=main_cont TITLE='{0}' HREF=pane.cgi?view=rack_info&name={0}&{2}><IMG ALT='{0} ({1})' SRC='images/{1}'></A>&nbsp;"
 for index, rack in enumerate(racks):
  rackargs = "rack=" + str(rack['id'])
  if rack.get('fk_console'):
   res = db.do("SELECT INET_NTOA(ip) as ip, id FROM consoles WHERE consoles.id = {}".format(rack.get('fk_console')))
   row = db.get_row()
   rackargs = rackargs + "&console=" + row.get('ip')
  if (rack.get('fk_pdu_1') or rack.get('fk_pdu_2')):
   res = db.do("SELECT INET_NTOA(ip) as ip, id FROM pdus WHERE (pdus.id = {0}) OR (pdus.id = {1})".format(rack.get('fk_pdu_1','0'),rack.get('fk_pdu_2','0')))
   rows = db.get_all_rows()
   for row in rows:
    rackargs = rackargs + "&pdulist=" + row.get('ip')
  print rackstr.format(rack['name'], rack['image_url'], rackargs)
 db.close()
 print "</CENTER></DIV>"

def rack_info(aWeb):
 from sdcp.site.ajax_rack import info as ajax_info
 print aWeb.get_header_full("Rack Info")
 rack = aWeb.get_value('rack')
 con  = aWeb.get_value('console')
 pdus = aWeb.get_list('pdulist')
 name = aWeb.get_value('name')
 print aWeb.get_listeners()
 print "<DIV CLASS=z-navframe ID=div_navframe>"
 print "<DIV CLASS=z-navbar ID=div_navbar>"
 if rack and name:
  print "<A CLASS='z-op' OP=load DIV=div_navcont LNK='ajax.cgi?call=rack_info&rack={0}'>'{1}' info</A>".format(rack,name)
 print "<A CLASS='z-op' OP=load DIV=div_navleft LNK='ajax.cgi?call=device_view_devicelist&target=rack_id&arg={0}'>Devices</A>".format(rack)
 if con:
  print "<A CLASS='z-op' OP=load DIV=div_navleft LNK='ajax.cgi?call=console_list&consolelist={}'>Console</A>".format(con)
 if len(pdus) > 0:
  pdustring = "&pdulist=".join(pdus)
  print "<A CLASS='z-op' OP=load DIV=div_navleft SPIN=true LNK='ajax.cgi?call=pdu_list_units&pdulist={}'>PDU</A>".format(pdustring)
 print "<A CLASS='z-op z-reload' OP=reload LNK='pane.cgi?{}'></A>".format(aWeb.get_args_except())
 print "<A CLASS='z-op' style='float:right;' OP=load DIV=div_navleft LNK='ajax.cgi?call=pdu_list_pdus'>PDUs</A>"
 print "<A CLASS='z-op' style='float:right;' OP=load DIV=div_navleft LNK='ajax.cgi?call=console_list_consoles'>Consoles</A>"
 print "<A CLASS='z-op' style='float:right;' OP=load DIV=div_navleft LNK='ajax.cgi?call=rack_list_racks'>Racks</A>"
 print "<SPAN STYLE='padding: 6px 4px; font-size:16px; font-weight:bold; background-color:green; color:white; float:right;'>Configuration:</SPAN>"
 print "</DIV>"
 print "<DIV CLASS=z-navleft  ID=div_navleft></DIV>"
 print "<DIV CLASS=z-navright ID=div_navcont>"
 if rack and name:
  ajax_info(aWeb)
 print "</DIV>"
 print aWeb.get_listeners('div_navleft')
 print aWeb.get_listeners('div_navcont')
 print "</DIV>"

##################################################################################################
#
# ESXi
#
def esxi(aWeb):
 from ajax_esxi import op as esxi_op
 from sdcp.devices.ESXi import ESXi
 from sdcp.tools.Grapher import Grapher
 host   = aWeb.get_value('host')
 domain = aWeb.get_value('domain')
 esxi   = ESXi(host,domain)
 
 print aWeb.get_header_full("ESXi Operations")
 print aWeb.get_listeners()
 print "<DIV CLASS='z-navframe' ID=div_navframe>"
 print "<DIV CLASS='z-navbar' ID=div_navbar>"
 print "<A CLASS='z-warning z-op' OP=confirm DIV=div_esxi_op MSG='Really shut down?' LNK='ajax.cgi?call=esxi_op&nstate=poweroff&{}'>Shutdown</A>".format(aWeb.get_args_except(['pane']))
 print "<A CLASS=z-op OP=toggle DIV=div_esxi_pic   HREF='#'>Picture</A>"
 print "<A CLASS=z-op OP=toggle DIV=div_esxi_stats HREF='#'>Stats</A>"
 print "<A CLASS=z-op OP=toggle DIV=div_esxi_op   HREF='#'>VM OPs</A>"
 print "<A HREF=https://{0}/ui target=_blank>UI</A>".format(esxi._ip)
 print "<A HREF=http://{0}/index.html target=_blank>IPMI</A>".format(esxi.get_kvm_ip('ipmi'))
 print "<A CLASS='z-op z-reload' OP=reload LNK='pane.cgi?{}'></A>".format(aWeb.get_args_except())
 print "</DIV>"
 
 print aWeb.get_listeners("div_navcont")
 print "<DIV CLASS='z-navcontent' ID=div_navcont>"
 print "<DIV CLASS='z-system' id=div_esxi_stats title='Device stats' style='display:none;'>"
 graph  = Grapher()
 graph.widget_cols([ "{1}/{0}/esxi_vm_info".format(esxi._fqdn,domain), "{1}/{0}/esxi_cpu_info".format(esxi._fqdn,domain), "{1}/{0}/esxi_mem_info".format(esxi._fqdn,domain) ])
 print "</DIV>"
 
 print "<DIV CLASS=z-table ID=div_esxi_op style='float:left; display:block'>"
 esxi_op(aWeb,esxi)
 print "</DIV>"

 print "<DIV CLASS='z-system' id=div_esxi_pic title='Device picture' style='display:none;'>"
 print "<CENTER><IMG ALT='Image of "+ host +"' SRC='images/" + host + ".jpg'></CENTER>"
 print "</DIV>"
 
 try:
  from subprocess import check_output
  logs = check_output("tail -n 10 /var/log/network/"+ host +".operations.log | tac", shell=True)
  print "<DIV CLASS='z-logs' ID=div_esxi_log><H1>{} operation logs</H1>{}</DIV>".format(esxi._fqdn,logs.replace('\n','<BR>'))
 except:
  pass
 
 print "</DIV>"
 print "</DIV>"

##################################################################################################
#
# Devices view pane
#
# - all devices and all else
#
 
def devices(aWeb):
 from sdcp.core.GenLib import DB
 op     = aWeb.get_value('op')
 domain = aWeb.get_value('domain')
 target = aWeb.get_value('target')
 arg    = aWeb.get_value('arg')
 
 db = DB() 
 db.connect()
 argdict = {}
 for type in ['pdu','console']:
  db.do("SELECT id, INET_NTOA(ip) as ip FROM {}s".format(type))
  tprows = db.get_all_rows()
  if len(tprows) > 0:
   arglist = "call={}_list".format(type)
   for row in tprows:
    arglist = arglist + "&{}list=".format(type) + row['ip']
   argdict[type] = arglist

 print aWeb.get_header_full("Device View")
 print aWeb.get_listeners()
 print "<DIV CLASS=z-navframe ID=div_navframe>"
 print "<DIV CLASS=z-navbar ID=div_navbar>"
 print "<A CLASS='z-op' OP=load DIV=div_navleft LNK='ajax.cgi?call=device_view_devicelist{0}'>Devices</A>".format('' if (not target or not arg) else "&target="+target+"&arg="+arg)
 print "<A CLASS='z-op' OP=load DIV=div_navleft LNK='ajax.cgi?call=graph_list&domain={}'>Graphing</A>".format(domain)
 if argdict.get('console',None):
  print "<A CLASS='z-op' OP=load DIV=div_navleft LNK='ajax.cgi?call=console_list&{}'>Console</A>".format(argdict.get('console'))
 if argdict.get('pdu',None):
  print "<A CLASS='z-op' OP=load DIV=div_navleft SPIN=true LNK='ajax.cgi?call=pdu_list_units&{}'>PDU</A>".format(argdict.get('pdu'))
 print "<A CLASS='z-reload z-op' OP=reload LNK='pane.cgi?{}'></A>".format(aWeb.get_args_except())
 print "<A CLASS='z-right z-op'  OP=load   DIV=div_navcont MSG='Discover devices?' LNK='ajax.cgi?call=device_discover&domain={0}'>Device Discovery</A>".format(domain)
 print "</DIV>"
 print aWeb.get_listeners("div_navleft")
 print aWeb.get_listeners("div_navcont")
 print "<DIV CLASS=z-navleft  ID=div_navleft></DIV>"
 print "<DIV CLASS=z-navright ID=div_navcont>" 
 print aWeb.get_include('README.devices.html')
 print "</DIV>"
 print "</DIV>" 
 db.close() 

##################################################################################################
#
# Settings/System pane
#

def config(aWeb):
 domain    = aWeb.get_value('domain', None)
 print aWeb.get_header_full("Config and Settings")
 print aWeb.get_listeners("div_config_menu")
 print "<DIV CLASS='z-table' ID=div_config_menu style='width:200px; float:left; min-height:300px;'>"
 print "<A CLASS='z-btn z-warning z-op' OP=confirm DIV=div_config SPIN=true MSG='Clear DB?' LNK='ajax.cgi?call=device_clear_db'>Clear Database</A>"
 print "<A CLASS='z-btn z-op' OP=load DIV=div_config SPIN=true LNK='ajax.cgi?call=graph_find&domain={0}'>Graph Discovery</A>".format(domain)
 print "<A CLASS='z-btn z-op' OP=load DIV=div_config           LNK='ajax.cgi?call=graph_sync&domain={0}'>Synch Graphing</A>".format(domain)
 print "<A CLASS='z-btn z-op' OP=load DIV=div_config SPIN=true LNK='ajax.cgi?call=ddi_sync'>Synch DDI</A>"
 print "<A CLASS='z-btn z-op' OP=load DIV=div_config SPIN=true LNK='ajax.cgi?call=ddi_load_infra'>Load DDI Tables</A>"
 print "<A CLASS='z-btn' TARGET=_blank HREF='ajax.cgi?call=device_dump_db'>Dump DB to JSON</A>"
 print "<A CLASS='z-btn z-op' OP=load DIV=div_config SPIN=true LNK='ajax.cgi?call=device_rack_info'>Device Rackinfo</A>"
 print "<A CLASS='z-btn z-op' OP=load DIV=div_config           LNK='ajax.cgi?call=device_mac_sync'>Sync MAC Info</A>"
 print "</DIV>"
 print "<DIV ID=div_config style='min-width:600px; min-height:300px; display:inline;'></DIV>"

##################################################################################################
#
# Openstack
#

def openstack_login(aWeb):
 from sdcp.devices.openstack import OpenstackRPC
 import sdcp.SettingsContainer as SC
 name = aWeb.get_value('name')
 ctrl_ip = aWeb.get_value('controller',"127.0.0.1")
 openstack = OpenstackRPC(ctrl_ip)
 if not openstack.load(SC.openstack_cookietemplate.format(SC.openstack_project)):
  catalog = openstack.auth({'project':SC.openstack_project, 'username':SC.openstack_username,'password':SC.openstack_password })
  # Forget about catalog - let user decide what we can do ..
 print aWeb.get_header_full("{} 2 Cloud".format(name.capitalize()))
 print aWeb.get_listeners("div_navframe")
 print "<DIV CLASS='z-navframe' ID=div_navframe>"
 print "<DIV CLASS='z-centered' style='height:100%;'>"
 print "<DIV ID=div_openstack_login style='background-color:#F3F3F3; display:block; border: solid 1px black; border-radius:8px; width:600px; height:180px;'>"
 print "<CENTER><H1>Welcome to {} 2 Cloud portal</H1></CENTER>".format(name.capitalize())
 print "<FORM ID=openstack_login>"
 print "<INPUT TYPE=hidden NAME=name VALUE={0}>".format(name)
 print "<INPUT TYPE=hidden NAME=controller VALUE={0}>".format(ctrl_ip)
 print "<TABLE style='display:inline; float:left; margin:0px 0px 0px 30px;'>"
 print "<TR><TD>Customer:</TD><TD><SELECT style='border:none; width:100px; display:inline; color:black' NAME=project>"
 projects =  openstack.call("5000","v3/projects")['data']['projects']
 for p in projects:
  print "<OPTION VALUE={0}_{1}>{1}</OPTION>".format(p['id'],p['name'])
 print "</SELECT></TD></TR>"
 print "<TR><TD>Username:</TD><TD>[<INPUT style='z-input' TYPE=text NAME=username>]</TD></TR>"
 print "<TR><TD>Password:</TD><TD>[<INPUT style='z-input' TYPE=password NAME=password>]</TD></TR>"
 print "</TABLE>"
 print "</FORM>"
 print "<A CLASS='z-btn z-op' style='margin:20px 20px 30px 40px;' OP=post FRM=openstack_login LNK='pane.cgi?view=openstack_portal' DIV=div_navframe>Login</A>"
 print "</DIV></DIV>"
 print "</DIV>"  

def openstack_portal(aWeb):
 from json import dumps
 from sdcp.devices.openstack import OpenstackRPC
 import sdcp.SettingsContainer as SC
 (pid,pname) = aWeb.get_value('project').split('_')
 username = aWeb.get_value('username')
 password = aWeb.get_value('password')
 ctrl_ip  = aWeb.get_value('controller')
 #
 # Verify login name, create simple "project + username" cookie
 # 
 openstack = OpenstackRPC(ctrl_ip)
 if not openstack.load(SC.openstack_cookietemplate.format(pname)):
  catalog = openstack.auth({'project':pname, 'username':username,'password':password })
  if catalog:
   openstack.dump(SC.openstack_cookietemplate.format(pname))
  else:
   print "Error login in - please try again"
   return
 else:
  catalog = openstack.get_catalog()
 print "<DIV style='height:60px; position:fixed; top:0px; left:0px; right:0px; display:block; z-index:101; border-bottom: 1px solid black;' >"
 print "<TABLE style='display:inline; float:left; margin:5px 100px 0px 10px;'>"
 print "<TR><TD><B>Identity:</B></TD><TD><I>{}</I></TD><TD>&nbsp;<B>Id:</B></TD><TD><I>{}</I></TD></TR>".format(pname,openstack.get_id())
 print "<TR><TD><B>Username:</B></TD><TD><I>{}</I></TD><TD>&nbsp;<B>Token:</B></TD><TD><I>{}</I></TD></TR>".format(username,openstack.get_auth_token())
 print "</TABLE>"
 print "</DIV>"
 print "<DIV CLASS='z-navbar' style='top:60px;' ID=div_navbar>"
 print "<A CLASS='z-op'          OP=load           DIV=div_navleft  LNK='ajax.cgi?call=openstack_heat_list&project={}'>Orchestration</A>".format(aWeb.get_value('project'))
 print "<A CLASS='z-op'          OP=load           DIV=div_navleft  LNK='ajax.cgi?call=openstack_contrail_list&project={}'>Virtual Networks</A>".format(aWeb.get_value('project'))
 print "<A CLASS='z-op'          OP=load           DIV=div_navleft  LNK='ajax.cgi?call=openstack_nova_list&project={}'>Virtual Machines</A>".format(aWeb.get_value('project'))
 print "<A CLASS='z-reload z-op' OP=load           DIV=div_navframe LNK='pane.cgi?{}'></A>".format(aWeb.get_args_except())
 print "</DIV>"
 print "<DIV CLASS=z-navleft  ID=div_navleft style='position:absolute; top:94px;'></DIV>"
 print "<DIV CLASS=z-navright ID=div_navcont style='position:absolute; top:94px; overflow-x:auto'>"
 print openstack
 print "</DIV>"
