"""Moduledocstring.

Ajax calls module

"""
__author__= "Zacharias El Banna"                     
__version__= "2.2GA"
__status__= "Production"


######################################## Examine pane - logs ########################################
#
#
#

def examine_clear_logs(aWeb, aClear = True):
 domain  = aWeb.get_value('domain')
 try:
  from subprocess import check_output
  import sdcp.SettingsContainer as SC
  if aClear:
   open("/var/log/network/"+ domain +".log",'w').close()
   open(SC.sdcp_logformat,'w').close()
   aWeb.log_msg("Emptied logs")
  netlogs = check_output("tail -n 15 /var/log/network/{}.log | tac".format(domain), shell=True)
  print "<DIV CLASS='z-logs'><H1>Network Logs</H1><PRE>{}</PRE></DIV>".format(netlogs)
  print "<BR>"
  syslogs = check_output("tail -n 15 " + SC.sdcp_logformat + " | tac", shell=True)
  print "<DIV CLASS='z-logs'><H1>System Logs</H1><PRE>{}</PRE></DIV>".format(syslogs)
 except Exception as err:
  print "<DIV CLASS='z-error'>{}</DIV>".format(str(err))

def examine_log(aWeb):
 try:
  from subprocess import check_output
  import sdcp.SettingsContainer as SC
  logfile = aWeb.get_value('logfile',SC.sdcp_logformat)
  syslogs = check_output("tail -n 15 " + logfile + " | tac", shell=True)
  print "<PRE>{}</PRE>".format(syslogs)
 except Exception as err:
  print "<PRE>{}</PRE>".format(str(err))      

########################################## ESXi Operations ##########################################
#
# ESXi operations
#
def esxi_op(aWeb, aEsxi = None):
 excpt  = aWeb.get_value('except','-1')
 nstate = aWeb.get_value('nstate')
 vmid   = aWeb.get_value('vmid','-1')

 if not aEsxi:
  from sdcp.devices.ESXi import ESXi
  host   = aWeb.get_value('host')
  domain = aWeb.get_value('domain')
  aEsxi   = ESXi(host,domain)

 if nstate:
  from subprocess import check_call, check_output
  try:
   aWeb.log_msg("ESXi: {} got command {}".format(aEsxi._fqdn,nstate))
   if "vm-" in nstate:
    vmop = nstate.split('-')[1]
    with aEsxi:
     aEsxi.ssh_send("vim-cmd vmsvc/power." + vmop + " " + vmid)
   elif nstate == 'poweroff':
    with aEsxi:
     aEsxi.ssh_send("poweroff")
   elif nstate == 'vmsoff':
    excpt = "" if vmid == '-1' else vmid
    check_call("/usr/local/sbin/ups-operations shutdown " + aEsxi._hostname + " " + excpt + " &", shell=True)
  except Exception as err:
   aWeb.log_msg("ESXi: nstate error [{}]".format(str(err)))

 print "<TABLE>"
 template="<A CLASS='z-btn z-small-btn z-btnop' TITLE='{3}' OP=load DIV=div_esxi_op LNK='ajax.cgi?call=esxi_op&domain=" +  aEsxi._domain + "&host="+ aEsxi._hostname + "&nstate={0}&vmid={2}'><IMG SRC=images/btn-{1}.png></A>"
 statelist = aEsxi.get_vms()
 if not nstate:
  print "<TR><TH CLASS='z-header' COLSPAN=2>{}</TH></TR>".format(aEsxi._fqdn)
 else:
  print "<TR><TH CLASS='z-header' COLSPAN=2>{} - {}:{}</TH></TR>".format(aEsxi._fqdn,vmid, nstate.split('-')[1])
 print "<TR><TH>VM</TH><TH>Operations</TH></TR><TR>"
 if nstate and nstate == 'vmsoff':
  print "<TD><B>SHUTDOWN ALL VMs!</B></TD>"
 else:
  print "<TD>SHUTDOWN ALL VMs!</TD>"
 print "<TD><CENTER>" + template.format('vmsoff','shutdown',excpt, "Shutdown all VMs") + "</CENTER></TD></TR>"
 for vm in statelist:
  if vm[0] == vmid:
   print "<TR><TD><B>" + vm[1] + "</B></TD>"
  else:
   print "<TR><TD>" + vm[1] + "</TD>"
  print "<TD><CENTER>"
  if vm[2] == "1":
   print template.format('vm-shutdown','shutdown', vm[0], "Soft shutdown")
   print template.format('vm-reboot','reboot', vm[0], "Soft reboot")
   print template.format('vm-suspend','suspend', vm[0], "Suspend")
   print template.format('vm-off','off', vm[0], "Hard power off")
  elif vm[2] == "3":
   print template.format('vm-on','start', vm[0], "Start")
   print template.format('vm-off','off', vm[0], "Hard power off")
  else:
   print template.format('vm-on','start', vm[0], "Start")
  print "</CENTER></TD></TR>"
 print "</TABLE>"

########################################## Device Operations ##########################################
#
#
#
def device_view_devicelist(aWeb):
 from sdcp.devices.DevHandler import Devices, sys_int2ip
 target = aWeb.get_value('target')
 arg    = aWeb.get_value('arg')
 devs = Devices()
 db   = devs.connect_db()
 if target and arg:
  db.do("SELECT * FROM devices WHERE {0}='{1}' ORDER BY ip".format(target,arg))
 else:
  db.do("SELECT * FROM devices ORDER BY ip")
 print "<DIV CLASS='z-framed' ID=div_device_devicelist><DIV CLASS='z-table'>"
 print "<CENTER><TABLE WIDTH=330>"
 print "<TR><TH>IP</TH><TH>FQDN</TH><TH>Model</TH></TR>"
 rows = db.get_all_rows()
 for row in rows:
  print "<TR><TD><A CLASS=z-btnop TITLE='Show device info for {0}' OP=load DIV=div_navcont LNK='ajax.cgi?call=device_view_devinfo&node={3}'>{0}</A></TD><TD>{1}</TD><TD>{2}</TD></TR>".format(sys_int2ip(row['ip']), row['dns']+"."+row['domain'], row['model'],row['id'])
 print "</TABLE></CENTER>"
 print "</DIV></DIV>"

#
# View graphs
#
def device_view_graphlist(aWeb):
 from sdcp.core.Grapher import Grapher
 node  = aWeb.get_value('node')
 state = aWeb.get_value('state')
 graph = Grapher()
 graph.load_conf()
 if node and state:
  nstate = "yes" if state == "no" else "no"
  graph.update_entry(node, nstate)
 print "<DIV CLASS='z-framed'><DIV CLASS='z-table'>"
 print "<CENTER><TABLE WIDTH=330><TR><TH>Node</TH><TH>Handler</TH><TH TITLE='Include in graphing?'>Include</TH></TR>"
 keys = graph.get_keys()
 for key in keys:
  entry = graph.get_entry(key)
  gdomain = key.partition(".")[2]
  print "<TR>"
  if entry['update'] == 'yes':
   print "<TD><A CLASS=z-btnop TITLE='Show graphs for {1}' OP=load DIV=div_navcont LNK='/munin-cgi/munin-cgi-html/{0}/{1}/index.html'>{1}</A></TD>".format(gdomain,key)
  else:
   print "<TD>{0}</TD>".format(key)
  print "<TD>"+ entry['handler'] +"</TD>"
  print "<TD TITLE='Include in graphing?'><CENTER><A CLASS='z-btn z-small-btn z-btnop' OP=load DIV=div_navleft LNK='ajax.cgi?call=device_view_graphlist&node=" + key + "&state=" + entry['update'] + "'><IMG SRC=images/btn-{}.png></A></CENTER></TD>".format("start" if entry['update'] == "no" else "shutdown")
  print "</TR>"
 print "</TABLE></CENTER></DIV></DIV>"

#
# View PDUs
#
def device_view_pdulist(aWeb):
 from sdcp.devices.RackUtils import Avocent
 domain  = aWeb.get_value('domain')
 slot    = aWeb.get_value('slot')
 nstate  = aWeb.get_value('nstate')
 pdulist = aWeb.get_list('pdulist')
 pduop   = aWeb.get_value('pdu')
 if len(pdulist) == 0:
  pdulist.append(pduop)
 print "<DIV CLASS='z-framed'><DIV CLASS='z-table'><TABLE WIDTH=330>"
 print "<TR><TH>PDU</TH><TH>Entry</TH><TH>Device</TH><TH style='width:63px;'>State</TH></TR>"
 optemplate = "<A CLASS='z-btn z-small-btn z-btnop' OP=load SPIN=true DIV=div_navleft LNK='ajax.cgi?call=device_view_pdulist&pdu={0}&nstate={1}&slot={2}'><IMG SRC='images/btn-{3}'></A>"
 for pdu in pdulist:
  avocent = Avocent(pdu,domain)
  avocent.load_snmp()
  if pdu == pduop and slot and nstate:
   avocent.set_state(slot,nstate)
   # Avocent is not fast enough to execute something immediately after reboot op, halt output then :-)
   if nstate == 'reboot':
    from time import sleep
    sleep(10)
  for key in avocent.get_keys(aSortKey = lambda x: int(x.split('.')[0])*100+int(x.split('.')[1])):
   value = avocent.get_entry(key)
   print "<TR><TD TITLE='Open up a browser tab for {1}'><A TARGET='_blank' HREF='https://{0}:3502'>{1}</A></TD><TD>{2}</TD>".format(avocent._ip,pdu,value['pduslot'])
   print "<TD><A CLASS='z-btnop' OP=load DIV=div_navcont LNK='ajax.cgi?call=device_view_pduslot&domain={0}&pdu={1}&slot={2}&name={3}&slotname={4}' TITLE='Edit port info' >{3}</A></TD><TD>".format(domain,pdu,key,value['name'], value['pduslot'])
   if value['state'] == "off":
    print optemplate.format(pdu, "on", key, "start")
   else:
    print optemplate.format(pdu, "off", key, "shutdown")
    print optemplate.format(pdu, "reboot", key, "reboot")
   print "</TD></TR>"
 print "</TABLE></DIV></DIV>"

#
# View PDU slot info (same as in list - but nicer way of opening up for updating)
#
def device_view_pduslot(aWeb):
 pdu  = aWeb.get_value('pdu')
 slot = aWeb.get_value('slot')
 slotname = aWeb.get_value('slotname')
 name = aWeb.get_value('name')
 domain = aWeb.get_value('domain')

 print "<DIV CLASS='z-framed z-table' style='resize: horizontal; margin-left:0px; width:420px; z-index:101; height:150px;'>"
 print "<FORM ID=pdu_form>"
 print "<INPUT NAME=call VALUE=device_update_pduslot TYPE=HIDDEN>"
 print "<INPUT NAME=domain VALUE={} TYPE=HIDDEN>".format(domain)
 print "<INPUT NAME=slot   VALUE={} TYPE=HIDDEN>".format(slot)
 print "<INPUT NAME=pdu    VALUE={} TYPE=HIDDEN>".format(pdu)
 print "<TABLE style='width:100%'>"
 print "<TR><TH COLSPAN=2>PDU Info</TH></TR>"
 print "<TR><TD>PDU:</TD><TD>{0}</TD></TR>".format(pdu)
 print "<TR><TD>Slot:</TD><TD>{0}</TD></TR>".format(slotname)
 print "<TR><TD>Name:</TD><TD><INPUT NAME=name TYPE=TEXT CLASS='z-input' PLACEHOLDER='{0}'></TD></TR>".format(name)
 print "<TR><TD COLSPAN=2>&nbsp;</TD></TR>"
 print "</TABLE>"
 print "<A CLASS='z-btn z-btnop z-small-btn' DIV=update_results LNK=ajax.cgi FRM=pdu_form OP=post><IMG SRC='images/btn-save.png'></A><SPAN ID=update_results></SPAN>"
 print "</FORM>"
 print "</DIV>"

#
# Update PDU slot info (name basically)
#
def device_update_pduslot(aWeb):
 values = aWeb.get_keys()
 values.remove('call')
 if 'name' in values:
  from sdcp.devices.RackUtils import Avocent
  name = aWeb.get_value('name')
  pdu  = aWeb.get_value('pdu')
  slot = aWeb.get_value('slot')
  domain = aWeb.get_value('domain')
  avocent = Avocent(pdu,domain)
  avocent.set_name(slot,name)
  print "Updated name: {} for {}.{}:{}".format(name,pdu,domain,slot)
 else:
  print "Name not updated"

#
# View Consoles
#
def device_view_consolelist(aWeb):
 from sdcp.devices.RackUtils import OpenGear
 domain = aWeb.get_value('domain')
 conlist = aWeb.get_list('conlist')
 config="https://{0}/?form=serialconfig&action=edit&ports={1}&start=&end="
 print "<DIV CLASS='z-framed'><DIV CLASS='z-table'><TABLE WIDTH=330>"
 print "<TR><TH>Server</TH><TH>Port</TH><TH>Device</TH></TR>"
 for con in conlist:
  console = OpenGear(con,domain)
  console.load_snmp()
  conip = console._ip
  for key in console.get_keys():
   port = str(6000 + key)
   value = console.get_entry(key)
   print "<TR><TD><A HREF='https://{0}/'>{1}</A></TD><TD><A TITLE='Edit port info' HREF={5}>{2}</A></TD><TD><A HREF='telnet://{0}:{3}'>{4}</A></TD>".format(conip, con,str(key),port, value, config.format(conip,key))
 print "</TABLE></DIV></DIV>"

########################################### Device Details ##########################################
#
# Device Info
#
def device_view_devinfo(aWeb):
 from sdcp.devices.DevHandler import Devices, sys_int2ip
 node   = aWeb.get_value('node')
 height = 210
 devs   = Devices()
 db     = devs.connect_db()
 db.do("SELECT * FROM devices WHERE id ='{}'".format(node))
 values = db.get_row()
 
 print "<DIV CLASS='z-framed z-table' style='resize: horizontal; margin-left:0px; width:420px; z-index:101; height:{}px;'>".format(str(height))
 print "<FORM ID=info_form>"
 print "<TABLE style='width:100%;'><TR>"
 
 # First table
 print "<TD><TABLE style='width:200px; border: solid 1px green;'><TR><TH COLSPAN=2>Reachability Info</TH></TR>"
 print "<TR><TD>Name:</TD><TD><INPUT NAME=dns CLASS='z-input' TYPE=TEXT PLACEHOLDER='{}'></TD></TR>".format(values['dns'])
 print "<TR><TD>Domain:</TD><TD>{}</TD></TR>".format(values['domain'])
 print "<TR><TD>SNMP:</TD><TD>{}</TD></TR>".format(values['snmp'])
 print "<TR><TD>IP:</TD><TD>{}</TD></TR>".format(sys_int2ip(values['ip']))
 print "<TR><TD>Type:</TD><TD TITLE='Device type'><SELECT NAME=type CLASS='z-select'>"
 for tp in Devices.get_types():
  extra = " selected disabled" if values['type'] == tp else ""      
  print "<OPTION VALUE={0} {1}>{0}</OPTION>".format(str(tp),extra)
 print "</SELECT></TD></TR>"
 print "<TR><TD>Model:</TD><TD style='max-width:140px;'>{}</TD></TR>".format(values['model'])
 if values['graphed'] == "yes":
  print "<TR><TD><A CLASS='z-btnop' TITLE='View graphs for {1}' OP=load DIV=div_navcont LNK='/munin-cgi/munin-cgi-html/{0}/{1}/index.html#content'>Graphs</A>:</TD><TD>yes</TD></TR>".format(values['domain'],values['dns']+"."+values['domain'])
 else:
  if not values['dns'] == 'unknown':
   print "<TR><TD>Graphs:</TD><TD><A CLASS='z-btnop' OP=load DIV=div_navcont LNK='ajax.cgi?call=device_op_addgraph&node={}&name={}&domain={}' TITLE='Add Graphs for node?'>no</A></TD></TR>".format(node, values['dns'], values['domain'])
  else:
   print "<TR><TD>Graphs:</TD><TD>no</TD></TR>"
 print "</TABLE></TD>"

 # Second table
 print "<TD><TABLE style='border: solid 1px green;'><TR><TH COLSPAN=2>Rack Info</TH></TR>"

 print "<TR><TD>Rack:</TD><TD><SELECT NAME=rack_id CLASS='z-select'>"
 db.do("SELECT * FROM racks")
 racks = db.get_all_rows()
 racks.append({ 'id':0, 'name':'Not used', 'size':'48', 'fk_pdu':'0', 'fk_console':'0'})
 for rack in racks:
  extra = " selected" if values['rack_id'] == rack['id'] else ""
  print "<OPTION VALUE={0} {1}>{2}</OPTION>".format(rack['id'],extra,rack['name'])
 print "</SELECT></TD></TR>"

 print "<TR><TD>DNS_ID:</TD><TD>{}</TD></TR>".format(values['dns_id'])
 print "<TR><TD>IPAM_ID:</TD><TD>{}</TD></TR>".format(values['ipam_id'])
 if not values['rack_id'] == 0:
  print "<TR><TD>Rack_Unit:</TD><TD TITLE='Lower rack unit of device placement'><INPUT NAME=rack_unit CLASS='z-input' TYPE=TEXT PLACEHOLDER='{}'></TD></TR>".format(values['rack_unit'])
  print "<TR><TD>TS_Port:</TD><TD TITLE='Console port in rack TS'><INPUT NAME=consoleport CLASS='z-input' TYPE=TEXT PLACEHOLDER='{}'></TD></TR>".format(values['consoleport'])
  print "<TR><TD COLSPAN=2>&nbsp;</TD></TR>"
  print "<TR><TD COLSPAN=2>&nbsp;</TD></TR>"
 else:
  print "<TR><TD COLSPAN=2>&nbsp;</TD></TR>"
  print "<TR><TD COLSPAN=2>&nbsp;</TD></TR>"
  print "<TR><TD COLSPAN=2>&nbsp;</TD></TR>"
  print "<TR><TD COLSPAN=2>&nbsp;</TD></TR>"
 print "</TABLE></TD>"

 # Close large table
 print "</TR></TABLE>"
 print "<A CLASS='z-btn z-btnop z-small-btn' DIV=div_navcont LNK=ajax.cgi?call=device_view_devinfo&node={} OP=load><IMG SRC='images/btn-reboot.png'></A>".format(node)
 print "<A CLASS='z-btn z-btnop z-small-btn' DIV=update_results LNK=ajax.cgi?call=device_update_devinfo&node={} FRM=info_form OP=post TITLE='Update Entry'><IMG SRC='images/btn-save.png'></A>".format(node)
 print "<A CLASS='z-btn z-btnop z-small-btn' DIV=update_results LNK=ajax.cgi?call=device_update_dns&node={}  FRM=info_form OP=post TITLE='Update DNS'>D</A>".format(node)
 print "<A CLASS='z-btn z-btnop z-small-btn' DIV=update_results LNK=ajax.cgi?call=device_update_ipam&node={} FRM=info_form OP=post TITLE='Update IPAM'>I</A>".format(node)
 print "<SPAN style='float:right' ID=update_results></SPAN>&nbsp;"
 print "</FORM>"
 print "</DIV>"

 devs.close_db()

 print "<DIV CLASS='z-framed' style='margin-left:420px; overflow-x:hidden; z-index:100'><CENTER><IMG TITLE='Info image of {0}' ALT='Missing file images/info_{1}.jpg - 600px x 160px max' SRC='images/info_{1}.jpg'></CENTER></DIV>".format(values['dns'],values['model'])

 print "<DIV CLASS='z-navbar' style='top:{}px;'>".format(str(height + 40))
 functions = Devices.get_widgets(values['type'])
 if functions:
  if functions[0] == 'operated':
   if values['type'] == 'esxi':
    print "<A TARGET='main_cont' HREF='pane.cgi?view=esxi&domain={}&host={}'>Manage</A></B></DIV>".format(values['domain'], values['dns'])
  else:
   for fun in functions:
    name = " ".join(fun.split('_')[1:])
    print "<A CLASS='z-btnop' OP=load DIV=div_navdata SPIN=true LNK='ajax.cgi?call=device_view_devdata&ip={0}&type={1}&op={2}'>{3}</A>".format(sys_int2ip(values['ip']), values['type'], fun, name.title())
 else:
  print "&nbsp;"
 print "</DIV>"
 print "<DIV CLASS='z-navcontent' ID=div_navdata style='top:{}px; overflow-x:hidden; overflow-y:auto; z-index:100'></DIV>".format(str(height + 40))

##################################################
#
# Save data for device info
#
def device_update_devinfo(aWeb):
 from sdcp.devices.DevHandler import Devices
 node   = aWeb.get_value('node')
 values = aWeb.get_keys()
 values.remove('call')
 values.remove('node')
 if values:
  devs = Devices()
  db   = devs.connect_db()
  for key in values:
   db.do("UPDATE devices SET {0}='{1}' where id = '{2}'".format(key,aWeb.get_value(key),node))
  db.commit()
  devs.close_db()
  print "Updated: {}".format(" ".join(values))
 else:
  print "Nothing to update"

def device_update_detect(aWeb):
 print "not implemented yet"

def device_update_dns(aWeb):
 import sdcp.SettingsContainer as SC
 print "not implemented yet",SC.dnsdb_proxy

def device_update_ipam(aWeb):
 import sdcp.SettingsContainer as SC
 print "not implemented yet",SC.ipamdb_proxy

#
# View operation data / widgets
#
def device_view_devdata(aWeb):
 ip   = aWeb.get_value('ip')
 type = aWeb.get_value('type')
 op   = aWeb.get_value('op')
 try:
  from sdcp.devices.DevHandler import Devices
  dev = Devices.get_node(ip,type)
  fun = getattr(dev,op,None)
  fun()
 except Exception as err:
  print "<B>Error in devdata: {}</B>".format(str(err))

#
# find devices operations
#
def device_op_finddevices(aWeb):
 domain    = aWeb.get_value('domain')
 discstart = aWeb.get_value('discstart')
 discstop  = aWeb.get_value('discstop')
 clear     = aWeb.get_value('clear',False)
 if discstart and discstop and domain:
  from sdcp.devices.DevHandler import Devices
  devs = Devices() 
  devs.discover(discstart,discstop, domain, clear)
  print "<B>Done Discovering Devices: {} -> {} for {}!</B>".format(discstart,discstop,domain)
  aWeb.log_msg("devices.cgi: Discovered devices [{}] {} -> {} for {}".format(str(clear), discstart,discstop,domain))

#
# Find graphs
#
def device_op_findgraphs(aWeb):
 from sdcp.core.Grapher import Grapher
 try:
  graph = Grapher() 
  graph.discover()
  print "<B>Done discovering graphs</B>"
  aWeb.log_msg("Devices: Discovered graphs")
 except Exception as err:
  print "<B>Error: {}</B>".format(str(err))


#
# Sync graphs and devices
#
def device_op_syncgraphs(aWeb):
 from sdcp.devices.DevHandler import Devices
 from sdcp.core.Grapher import Grapher
 try:
  devs  = Devices()
  db = devs.connect_db()
  db.do("SELECT id,dns,domain FROM devices")
  rows = db.get_all_rows()
  graph = Grapher()
  graphdevices = graph.get_keys()
  sql = "UPDATE devices SET graphed = 'yes' WHERE id = '{}'"
  for row in rows:
   fqdn = row['dns'] + "." + row['domain']
   if fqdn in graphdevices:
    db.do(sql.format(row['id']))
  db.commit()
  devs.close_db()
  print "<B>Done syncing devices' graphing</B>"
  aWeb.log_msg("devices.cgi: Done syncing devices' graphing")
 except Exception as err:
  print "<B>Error: {}</B>".format(str(err))

#
# Add graphs
#
def device_op_addgraph(aWeb):
 node   = aWeb.get_value('node',None)
 name   = aWeb.get_value('name',None)
 domain = aWeb.get_value('domain',None)
 if name and domain:
  fqdn   = name + "." + domain
  from sdcp.core.Grapher import Grapher
  graph = Grapher()
  entry = graph.get_entry(fqdn)
  if entry:
   print "<B>Entry existed</B>"
  else:
   graph.add_entry(fqdn,'no')
   print "<B>Added graphing for node {0} ({1})</B>".format(node, fqdn)


################################################## Basic Rack Info ######################################################
#
# Basic rack info - right now only a display of a typical rack.. Change to table?
#

def rack_info(aWeb):
 rack = aWeb.get_value('rack', 0)
 print "<DIV style='padding:20px;'>"
 print "<H1>Rack {}</H1>".format(rack)
 print "Data: [{}]".format(" ".join(aWeb.get_keys()))
 print "<DIV style=' background-image: url(images/rack48u.png); background-position: center; background-repeat: no-repeat; height:1680px; width:770px;'></DIV>"
 print "</DIV>"

def rack_infra(aWeb):
 from sdcp.core.GenLib import DB, sys_int2ip 
 db   = DB()
 db.connect()
 type = aWeb.get_value('type','racks')
 print "<DIV CLASS='z-framed'>"
 print "<DIV CLASS='z-table'><TABLE WIDTH=330>"
 print "<TR style='height:20px'> <TH COLSPAN=3><CENTER>{0}</CENTER></TH></TR>".format(type.capitalize())
 print "<TR style='height:20px'> <TD COLSPAN=3><A CLASS='z-btn z-small-btn z-btnop' OP=load DIV=div_navcont LNK='ajax.cgi?call=rack_data&type={0}&id=new'><IMG SRC='images/btn-add.png'></A></TD></TR>".format(type)
 res  = db.do("SELECT * from {} ORDER by name".format(type))
 data = db.get_all_rows()
 if type == 'pdus' or type == 'consoles':
  print "<TR><TH>ID</TH><TH>Name</TH><TH>IP</TH></TR>"
  for unit in data:
   print "<TR><TD>{0}</TD><TD><A CLASS='z-btnop' OP=load DIV=div_navcont LNK='ajax.cgi?call=rack_data&type={3}&id={0}&name={1}&ip={2}'>{1}</A></TD><TD>{2}</TD>".format(unit['id'],unit['name'],sys_int2ip(unit['ip']),type)
 elif type == 'racks':
  print "<TR><TH>ID</TH><TH>Name</TH><TH>Size</TH></TR>"
  for unit in data:
   print "<TR><TD>{0}</TD><TD><A CLASS='z-btnop' OP=load DIV=div_navcont LNK='ajax.cgi?call=rack_data&type={3}&id={0}&name={1}'>{1}</A></TD><TD>{2}</TD>".format(unit['id'],unit['name'],unit['size'],type)  
 print "</TABLE></DIV>"
 db.close()

#
#
#
def rack_data(aWeb):
 type = aWeb.get_value('type')
 id   = aWeb.get_value('id','new')
 name = aWeb.get_value('name','new-name')
 ip   = aWeb.get_value('ip','127.0.0.1') 

 print "<DIV CLASS='z-framed z-table' style='resize: horizontal; margin-left:0px; width:420px; z-index:101; height:150px;'>"
 print "<FORM ID=rack_data_form>"
 print "<INPUT TYPE=HIDDEN NAME=type VALUE={}>".format(type)
 print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(id)
 print "<TABLE style='width:100%'>"
 print "<TR><TH COLSPAN=2>{} Info</TH></TR>".format(type[:-1].capitalize())

 if type == "pdus" or type == 'consoles':
  print "<TR><TD>IP:</TD><TD><INPUT NAME=ip TYPE=TEXT CLASS='z-input' VALUE='{0}'></TD></TR>".format(ip)
  print "<TR><TD>Name:</TD><TD><INPUT NAME=name TYPE=TEXT CLASS='z-input' VALUE='{0}'></TD></TR>".format(name)
 if type == 'racks':
  from sdcp.core.GenLib import DB
  db = DB()
  db.connect()
  rack = {}
  if id == 'new':
   rack = { 'id':'new', 'name':'new-name', 'size':'48', 'fk_pdu':0, 'fk_console':0 }
  else:
   db.do("SELECT * from racks WHERE id = {}".format(id))
   rack = db.get_row()
  db.do("SELECT id,name from pdus")
  pdus = db.get_all_rows()
  pdus.append({'id':0, 'name':'Not Used'})
  db.do("SELECT id,name from consoles")
  consoles = db.get_all_rows()
  consoles.append({'id':0, 'name':'Not Used'})
  db.close()
  print "<TR><TD>Name:</TD><TD><INPUT NAME=name TYPE=TEXT CLASS='z-input' VALUE='{0}'></TD></TR>".format(name)
  print "<TR><TD>Size:</TD><TD><INPUT NAME=size TYPE=TEXT CLASS='z-input' VALUE='{0}'></TD></TR>".format(rack['size'])
  print "<TR><TD>PDU:</TD><TD><SELECT NAME=fk_pdu CLASS='z-select'>"
  for unit in pdus:
   extra = " selected" if rack['fk_pdu'] == unit['id'] else ""
   print "<OPTION VALUE={0} {1}>{2}</OPTION>".format(unit['id'],extra,unit['name'])
  print "</SELECT></TD></TR>"
  print "<TR><TD>Console:</TD><TD><SELECT NAME=fk_console CLASS='z-select'>"
  for unit in consoles:
   extra = " selected" if rack['fk_console'] == unit['id'] else ""
   print "<OPTION VALUE={0} {1}>{2}</OPTION>".format(unit['id'],extra,unit['name'])
  print "</SELECT></TD></TR>"
 print "</TABLE>"
 print "<A TITLE='Update unit' CLASS='z-btn z-btnop z-small-btn' DIV=update_results LNK=ajax.cgi?call=rack_update FRM=rack_data_form OP=post><IMG SRC='images/btn-save.png'></A>"
 if not id == 'new':
  print "<A TITLE='Remove unit' CLASS='z-btn z-btnop z-small-btn' DIV=div_navcont LNK=ajax.cgi?call=rack_remove&type={0}&id={1} OP=load><IMG SRC='images/btn-remove.png'></A>".format(type,id)
 print "&nbsp;<SPAN ID=update_results></SPAN>"
 print "</FORM>"
 print "</DIV>"

#
#
#
def rack_update(aWeb):
 from sdcp.core.GenLib import DB, sys_int2ip, sys_ip2int 
 values = aWeb.get_keys()
 values.remove('call')
 db   = DB()
 db.connect()
 type = aWeb.get_value('type')
 id   = aWeb.get_value('id')
 name = aWeb.get_value('name')
 if type == 'pdus' or type == 'consoles':
  ip   = aWeb.get_value('ip')
  ipint = sys_ip2int(ip)
  sql = ""
  if id == 'new':
   print "New {} created".format(type[:-1])
   sql = "INSERT into {0} (name, ip) VALUES ('{1}','{2}')".format(type,name,ipint)
  else:
   print "Updated {} {}".format(type[:-1],id)
   sql = "UPDATE {0} SET name = '{1}', ip = '{2}' WHERE id = '{3}'".format(type,name,ipint,id)
  res = db.do(sql)
  db.commit()
 elif type == 'racks':
  size   = aWeb.get_value('size')
  fk_pdu = aWeb.get_value('fk_pdu')
  fk_console = aWeb.get_value('fk_console')
  if id == 'new':
   print "New rack created"
   sql = "INSERT into racks (name, size, fk_pdu, fk_console) VALUES ('{}','{}','{}','{}')".format(name,size,fk_pdu,fk_console)
  else:
   print "Updated rack {}".format(id)
   sql = "UPDATE racks SET name = '{0}', size = '{1}', fk_pdu = '{2}', fk_console = '{3}'  WHERE id = '{4}'".format(name,size,fk_pdu,fk_console,id)
  res = db.do(sql)
  db.commit()
 else:
  print "unknown type"
 db.close()

#
#
#
def rack_remove(aWeb):
 from sdcp.core.GenLib import DB
 type = aWeb.get_value('type')
 id   = aWeb.get_value('id')
 db   = DB()
 db.connect()
 db.do("DELETE FROM {0} WHERE id = '{1}'".format(type,id))
 db.do("UPDATE devices SET {}_id = '0' WHERE {}_id = '{1}'".format(type[:-1],id))
 db.commit()
 print "Unit {} of type {} deleted".format(id,type)
 db.close()
