"""Moduledocstring.

Site view panes module

"""
__author__= "Zacharias El Banna"                     
__version__= "2.0GA"
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
 from ajax import examine_clear_logs
 print aWeb.get_header_full('Services Pane')
 domain  = aWeb.get_value('domain')
 upshost = aWeb.get_value('upshost')
 svclist = aWeb.get_list('svchost')
 from sdcp.core.Grapher import Grapher
 graph = Grapher() 
 
 print aWeb.get_listeners()
 print "<DIV CLASS='z-navframe' ID=div_navframe>"
 
 print "<DIV CLASS='z-navbar' ID=div_navbar>"
 print "<A CLASS='z-warning z-btnop' OP=confirm DIV=div_examine_log MSG='Clear Network Logs?' LNK='site.cgi?ajax=examine_clear_logs&{}'>Clear Logs</A>".format(aWeb.reload_args_except(['pane']))
 print "<A CLASS=z-btnop OP=single SELECTOR='.z-system' DIV=div_examine_log LNK='.z-system'>Logs</A>"
 if upshost:
  print "<A CLASS=z-btnop OP=single SELECTOR='.z-system' DIV=div_ups LNK='.z-system'>UPS</A>"
 if svclist:
  print "<A CLASS=z-btnop OP=single SELECTOR='.z-system' DIV=div_dns  LNK='.z-system'>DNS</A>"
  print "<A CLASS=z-btnop OP=single SELECTOR='.z-system' DIV=div_dhcp LNK='.z-system'>DHCP</A>"
  print "<A CLASS=z-btnop OP=single SELECTOR='.z-system' DIV=div_external LNK='.z-system'>External</A>"
 print "<A CLASS='z-reload z-btnop' OP=reload LNK='site.cgi?{}'></A>".format(aWeb.reload_args_except([]))
 print "</DIV>"
 
 print "<DIV CLASS='z-navcontent' ID=div_navcont>"
 
 print "<DIV CLASS='z-system' id=div_examine_log title='Network Logs' style='display:block;'>"
 examine_clear_logs(aWeb, False)
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
   print "<DIV CLASS='z-logs'><H1>System Logs for {}.{}</H1>{}</DIV>".format(svc,domain,aWeb.get_include("http://"+ svc +"/systemlog.php"))
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
 <A CLASS='z-reload z-btnop' OP=iload IFRAME=iframe_munin LNK='/munin-cgi/munin-cgi-html/index.html'></A>
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
 view = aWeb.get_value('view')
 json = aWeb.get_value('json')
 
 if view == 'main':
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
      print "<A CLASS='z-btnop' OP=iload IFRAME=iframe_wm_cont LNK=site.cgi?pane=weathermap&json={2}&view={0}>{1}</A>".format(name,name.capitalize(),json)
   except :
    print "<A CLASS='z-warning'>Error loading JSON file</A>"
  else:
   try:
    from os import listdir
    for file in listdir("wm_configs/"):
     if file.startswith("wm_"):
      name= file[3:-5]
      print "<A CLASS='z-btnop' OP=iload IFRAME=iframe_wm_cont LNK=site.cgi?pane=weathermap&view={0}>{1}</A>".format(name,name.capitalize())
   except Exception as err:
    print "weathermap.cgi: error finding config files in 'wm_configs/' [{}]".format(str(err))
  print "</DIV>"
  print "<DIV CLASS='z-navcontent' ID=div_navcont NAME='Weathermap Content'>"
  print "<IFRAME ID=iframe_wm_cont src=''></IFRAME>"
  print "</DIV>"
  print "</DIV>"
 
 elif view:
  print aWeb.get_header_base()
  if json:
   from json import load
   from sdcp.core.Grapher import Grapher
   with open(json) as conffile:
    config = load(conffile)
    entry  = config[view]
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
   print aWeb.get_include('wm_{}.html'.format(view))
   print "</DIV>"
 else:
  print "Weathermap fetches config names from the<PRE> wm_configs/</PRE> directory, all names starting with wm_ and ending with .conf are mapped for navigation bar"

##################################################################################################
#
# Shutdown all
#
def thread_shutdown_host(afqdn, aWeb):
 from sdcp.core.DevESXi import ESXi
 print "<PRE>Shutting down host: {}</PRE>".format(afqdn)
 aWeb.log_msg("shutdownAll: Thread shutting down [{}]".format(afqdn))
 esxi = ESXi(fqdn)
 esxi.shutdown_vms()

def shutdownall(aWeb):
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
 from ajax import rack_info
 print aWeb.get_header_full("Rack")
 domain = aWeb.get_value('domain')
 rack   = aWeb.get_value('rack', 0)
 con    = aWeb.get_value('console')
 pdu    = aWeb.get_value('pdu')
 print aWeb.get_listeners()
 print "<DIV CLASS=z-navframe ID=div_navframe>"
 print "<DIV CLASS=z-navbar ID=div_navbar>"
 print "<A CLASS='z-btnop' OP=load DIV=div_navcont LNK='site.cgi?ajax=rack_info&{}'>Info</A>".format(aWeb.reload_args_except(['pane']))
 print "<A CLASS='z-btnop' OP=load DIV=div_navleft LNK='site.cgi?ajax=device_view_devicelist&domain={0}&target=rack&arg={1}'>Devices</A>".format(domain,rack)
 if con:
  print "<A CLASS='z-btnop' OP=load DIV=div_navleft LNK='site.cgi?ajax=device_view_consolelist&domain={0}&conlist={1}'>Console</A>".format(domain,con)
 if pdu:
  print "<A CLASS='z-btnop' OP=load DIV=div_navleft SPIN=true LNK='site.cgi?ajax=device_view_pdulist&domain={0}&pdu={1}'>Power</A>".format(domain,pdu)
 print "<A CLASS='z-btnop z-reload' OP=reload LNK='site.cgi?{}'></A>".format(aWeb.reload_args_except())
 print "<A CLASS='z-right'></A>".format(rack)
 print "</DIV>"

 print "<DIV CLASS=z-navleft  ID=div_navleft></DIV>"
 print "<DIV CLASS=z-navright ID=div_navcont>"
 rack_info(aWeb)
 print "</DIV>"
 print aWeb.get_listeners('div_navleft')
 print aWeb.get_listeners('div_navcont')
 print "</DIV>"

##################################################################################################
#
# ESXi
#
def esxi(aWeb):
 from ajax import esxi_op
 from sdcp.devices.ESXi import ESXi
 from sdcp.core.Grapher import Grapher
 host   = aWeb.get_value('host')
 domain = aWeb.get_value('domain')
 esxi   = ESXi(host,domain)
 
 print aWeb.get_header_full("ESXi Operations")
 print aWeb.get_listeners()
 print "<DIV CLASS='z-navframe' ID=div_navframe>"
 print "<DIV CLASS='z-navbar' ID=div_navbar>"
 print "<A CLASS='z-warning z-btnop' OP=confirm DIV=div_esxi_op MSG='Really shut down?' LNK='site.cgi?ajax=esxi_op&nstate=poweroff&{}'>Shutdown</A>".format(aWeb.reload_args_except(['pane']))
 print "<A CLASS=z-btnop OP=toggle DIV=div_esxi_pic   HREF='#'>Picture</A>"
 print "<A CLASS=z-btnop OP=toggle DIV=div_esxi_stats HREF='#'>Stats</A>"
 print "<A CLASS=z-btnop OP=toggle DIV=div_esxi_op   HREF='#'>VM OPs</A>"
 print "<A HREF=https://{0}/ui target=_blank>UI</A>".format(esxi._ip)
 print "<A HREF=http://{0}/index.html target=_blank>IPMI</A>".format(esxi.get_kvm_ip('ipmi'))
 print "<A CLASS='z-btnop z-reload' OP=reload LNK='site.cgi?{}'></A>".format(aWeb.reload_args_except([]))
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
 
def devices(aWeb):
 op        = aWeb.get_value('op', None)
 domain    = aWeb.get_value('domain', None)
 discstart = aWeb.get_value('discstart',None)
 discstop  = aWeb.get_value('discstop', None)
 conlist   = aWeb.get_list('conlist')
 pdulist   = aWeb.get_list('pdulist')
 
 print aWeb.get_header_full("Device View")
 print aWeb.get_listeners()
 print "<DIV CLASS=z-navframe ID=div_navframe>"
 print "<DIV CLASS=z-navbar ID=div_navbar>"
 print "<A CLASS='z-warning z-btnop' OP=confirm DIV=div_device_frame MSG='Clear DB?' LNK='site.cgi?ajax=device_op_finddevices&clear=true&domain={}'>Reset DB</A>".format(domain)
 print "<A CLASS='z-btnop' OP=load DIV=div_navleft LNK='site.cgi?ajax=device_view_devicelist&domain={}'>Devices</A>".format(domain)
 print "<A CLASS='z-btnop' OP=load DIV=div_navleft LNK='site.cgi?ajax=device_view_graphlist&domain={}'>Graphing</A>".format(domain)
 if conlist:
  print "<A CLASS='z-btnop' OP=load DIV=div_navleft LNK='site.cgi?ajax=device_view_consolelist&{}'>Console</A>".format(aWeb.reload_args_except(['discstart','discstop','pdu','pane']))
 if pdulist:
  print "<A CLASS='z-btnop' OP=load DIV=div_navleft SPIN=true LNK='site.cgi?ajax=device_view_pdulist&{}'>PDU</A>".format(aWeb.reload_args_except(['discstart','discstop','console','pane']))
 print "<A CLASS='z-reload z-btnop' OP=reload LNK='site.cgi?{}'></A>".format(aWeb.reload_args_except([]))
 print "<A CLASS='z-right z-btnop' OP=confirm DIV=div_navcont MSG='Start Device Discovery?' SPIN=true LNK='site.cgi?ajax=device_op_finddevices&domain={0}&discstart={1}&discstop={2}'>Device Discovery</A>".format(domain,discstart,discstop)
 print "<A CLASS='z-right z-btnop' OP=confirm DIV=div_navcont MSG='Start Graph Discovery?'  SPIN=true LNK='site.cgi?ajax=device_op_findgraphs&domain={0}'>Graph Discovery</A>".format(domain)
 print "<A CLASS='z-right z-btnop' OP=confirm DIV=div_navcont MSG='Sync Devices/Graphs?'    LNK='site.cgi?ajax=device_op_syncgraphs&domain={0}'>Sync Graphing</A>".format(domain)
 print "</DIV>"
 print aWeb.get_listeners("div_navleft")
 print aWeb.get_listeners("div_navcont")
 print "<DIV CLASS=z-navleft  ID=div_navleft></DIV>"
 print "<DIV CLASS=z-navright ID=div_navcont>" 
 print aWeb.get_include('README.devices.html')
 print "</DIV>"
 print "</DIV>" 
