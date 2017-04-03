"""Moduledocstring.

Ajax Device calls module

"""
__author__= "Zacharias El Banna"                     
__version__= "1.0GA"
__status__= "Production"

from sdcp.core.GenLib import DB, sys_ip2int, sys_int2ip

########################################## Device Operations ##########################################
#
#
#
def device_view_devicelist(aWeb):
 target = aWeb.get_value('target')
 arg    = aWeb.get_value('arg')
 db     = DB()
 db.connect()
 if target and arg:
  db.do("SELECT * FROM devices WHERE {0}='{1}' ORDER BY ip".format(target,arg))
 else:
  db.do("SELECT * FROM devices ORDER BY ip")
 print "<DIV CLASS='z-framed' ID=div_device_devicelist><DIV CLASS='z-table'>"
 print "<TABLE WIDTH=330>"
 print "<TR><TH>IP</TH><TH>FQDN</TH><TH>Model</TH></TR>"
 rows = db.get_all_rows()
 for row in rows:
  print "<TR><TD><A CLASS=z-btnop TITLE='Show device info for {0}' OP=load DIV=div_navcont LNK='ajax.cgi?call=device_device_info&node={3}'>{0}</A></TD><TD>{1}</TD><TD>{2}</TD></TR>".format(sys_int2ip(row['ip']), row['hostname']+"."+row['domain'], row['model'],row['id'])
 print "</TABLE>"
 print "</DIV></DIV>"
 db.close()

#
#
#
def device_device_info(aWeb):
 from sdcp.devices.DevHandler import device_detect, device_types, device_get_widgets
 id   = aWeb.get_value('node')
 op   = aWeb.get_value('op')
 db   = DB()
 db.connect()
 if   op == 'lookup':
  ip    = aWeb.get_value('ip')
  entry = device_detect(ip,"")
  db.do("UPDATE devices SET hostname = '{}', snmp = '{}', fqdn = '{}', model = '{}', type = '{}' WHERE id = '{}'".format(entry['hostname'],entry['snmp'],entry['fqdn'],entry['model'],entry['type'],id))
  db.commit()
 elif op == 'update':
  keys = aWeb.get_keys()
  keys.remove('call')
  keys.remove('node')
  keys.remove('op')
  if keys:
   for key in keys:
    if not (key[0:3] == 'pem' and key[5:] == 'pdu_slot_id'):
     db.do("UPDATE devices SET {0}='{1}' where id = '{2}'".format(key,aWeb.get_value(key),id))
    else:
     pem = key[:4]
     [pemid,pemslot] = aWeb.get_value(key).split('.')
     db.do("UPDATE devices SET {0}_pdu_id='{1}', {0}_pdu_slot ='{2}' where id = '{3}'".format(pem,pemid,pemslot,id))
   db.commit()
 elif op == 'dnslookup':
  ip     = aWeb.get_value('ip')
  name   = aWeb.get_value('hostname')
  domain = aWeb.get_value('domain')
  import sdcp.SettingsContainer as SC
  if SC.dnsdb_proxy == 'True':
   remote_url  = SC.dnsdb_url
   remote_json = aWeb.get_include(remote_url + "&op=dns_lookup&ip={}&hostname={}&domain={}".format(ip,name,domain))
   print remote_json
  else:
   print "not implemented yet"
  db.close()
  return

 db.do("SELECT * FROM devices WHERE id ='{}'".format(id))
 device_data = db.get_row()
 ip     = sys_int2ip(device_data['ip'])
 height = 240
 conip  = None
 
 print "<DIV ID=div_device_info CLASS='z-framed z-table' style='resize:horizontal; margin-left:0px; width:654px; z-index:101; height:{}px;'>".format(str(height))
 print "<FORM ID=info_form>"
 
 print "<!-- 1st Table -->"
 print "<DIV style='margin:3px; float:left;'><TABLE style='width:210px;'><TR><TH COLSPAN=2>Reachability Info</TH></TR>"
 print "<TR><TD>Name:</TD><TD><INPUT NAME=hostname CLASS='z-input' TYPE=TEXT PLACEHOLDER='{}'></TD></TR>".format(device_data['hostname'])
 print "<TR><TD>Domain:</TD><TD>{}</TD></TR>".format(device_data['domain'])
 print "<TR><TD>SNMP:</TD><TD>{}</TD></TR>".format(device_data['snmp'])
 print "<TR><TD>IP:</TD><TD>{}</TD></TR>".format(ip)
 print "<TR><TD>Type:</TD><TD TITLE='Device type'><SELECT NAME=type CLASS='z-select'>"
 for tp in device_types():
  extra = " selected disabled" if device_data['type'] == tp else ""      
  print "<OPTION VALUE={0} {1}>{0}</OPTION>".format(str(tp),extra)
 print "</SELECT></TD></TR>"
 print "<TR><TD>Model:</TD><TD style='max-width:150px;'>{}</TD></TR>".format(device_data['model'])
 if device_data['graphed'] == "yes":
  print "<TR><TD><A CLASS='z-btnop' TITLE='View graphs for {1}' OP=load DIV=div_navcont LNK='/munin-cgi/munin-cgi-html/{0}/{1}/index.html#content'>Graphs</A>:</TD><TD>yes</TD></TR>".format(device_data['domain'],device_data['hostname']+"."+device_data['domain'])
 else:
  if not device_data['hostname'] == 'unknown':
   print "<TR><TD>Graphs:</TD><TD><A CLASS='z-btnop' OP=load DIV=div_navcont LNK='ajax.cgi?call=graph_add&node={}&name={}&domain={}' TITLE='Add Graphs for node?'>no</A></TD></TR>".format(id, device_data['hostname'], device_data['domain'])
  else:
   print "<TR><TD>Graphs:</TD><TD>no</TD></TR>"
 print "<TR><TD COLSPAN=2 style='width:210px'>&nbsp;</TD></TR>"
 print "</TABLE></DIV>"

 print "<!-- 2nd Table -->"
 print "<DIV style='margin:3px; float:left;'><TABLE style='width:210px;'><TR><TH COLSPAN=2>Rack Info</TH></TR>"
 print "<TR><TD>Rack:</TD><TD><SELECT NAME=rack_id CLASS='z-select'>"
 db.do("SELECT * FROM racks")
 racks = db.get_all_rows()
 racks.append({ 'id':0, 'name':'Not used', 'size':'48', 'fk_pdu_1':'0', 'fk_pdu_2':'0','fk_console':'0'})
 for rack in racks:
  extra = " selected" if device_data['rack_id'] == rack['id'] else ""
  print "<OPTION VALUE={0} {1}>{2}</OPTION>".format(rack['id'],extra,rack['name'])
 if device_data['rack_id'] == 0 or device_data['type'] == 'pdu':
  for index in range(0,7):
   print "<TR><TD COLSPAN=2 style='width:200px'>&nbsp;</TD></TR>"
 else:
  db.do("SELECT * FROM consoles")
  consoles = db.get_all_rows()
  consoles.append({ 'id':0, 'name':'Not used', 'ip':2130706433 })
  db.do("SELECT * FROM pdus")
  pdus = db.get_all_rows()
  pdus.append({ 'id':0, 'name':'Not used', 'ip':'127.0.0.1', 'slots':0, '0_slot_id':0, '0_slot_name':'Not used' })
  print "<TR><TD>Rack Unit:</TD><TD TITLE='Lower rack unit of device placement'><INPUT NAME=rack_unit CLASS='z-input' TYPE=TEXT PLACEHOLDER='{}'></TD></TR>".format(device_data['rack_unit'])
  if not device_data['type'] == 'console':
   print "<TR><TD>TS:</TD><TD><SELECT NAME=console_id CLASS='z-select'>"
   for console in consoles:
    extra = ""
    if device_data['console_id'] == console['id']:
     extra = " selected"
     conip = sys_int2ip(console['ip'])
    print "<OPTION VALUE={0} {1}>{2}</OPTION>".format(console['id'],extra,console['name'])
   print "<TR><TD>TS Port:</TD><TD TITLE='Console port in rack TS'><INPUT NAME=consoleport CLASS='z-input' TYPE=TEXT PLACEHOLDER='{}'></TD></TR>".format(device_data['consoleport'])
  else:
   print "<TR><TD COLSPAN=2 style='width:200px'>&nbsp;</TD></TR>"
   print "<TR><TD COLSPAN=2 style='width:200px'>&nbsp;</TD></TR>"
  for pem in ['pem0','pem1']:
   print "<TR><TD>{0} PDU:</TD><TD><SELECT NAME={1}_pdu_slot_id CLASS='z-select'>".format(pem.upper(),pem)
   for pdu in pdus:
    for slotid in range(0,pdu['slots'] + 1):
     extra = " selected" if ((device_data[pem+"_pdu_id"] == pdu['id']) and (device_data[pem+"_pdu_slot"] == pdu[str(slotid)+"_slot_id"])) else ""
     print "<OPTION VALUE={0} {1}>{2}</OPTION>".format(str(pdu['id'])+"."+str(pdu[str(slotid)+"_slot_id"]), extra, pdu['name']+":"+pdu[str(slotid)+"_slot_name"])
   print "</SELECT></TD></TR>"
   print "<TR><TD>{0} Unit:</TD><TD><INPUT NAME={1}_pdu_unit CLASS='z-input' TYPE=TEXT PLACEHOLDER='{2}'></TD></TR>".format(pem.upper(),pem,device_data[pem + "_pdu_unit"])
 print "</TABLE></DIV>"

 print "<!-- 3rd Table -->"
 print "<DIV style='margin:3px; float:left;'><TABLE style='width:210px;'><TR><TH COLSPAN=2>Extra info</TH></TR>"
 print "<TR><TD>Rack Size:</TD><TD><INPUT NAME=rack_size CLASS='z-input' TYPE=TEXT PLACEHOLDER='{}'></TD></TR>".format(device_data['rack_size'])
 print "<TR><TD>FQDN:</TD><TD>{}</TD></TR>".format(device_data['fqdn'])
 print "<TR><TD>DNS A ID:</TD><TD>{}</TD></TR>".format(device_data['dns_a_id'])
 print "<TR><TD>DNS PTR ID:</TD><TD>{}</TD></TR>".format(device_data['dns_ptr_id'])
 print "<TR><TD>IPAM ID:</TD><TD>{}</TD></TR>".format(device_data['ipam_id'])
 for index in range(0,3):
  print "<TR><TD COLSPAN=2 style='width:200px'>&nbsp;</TD></TR>" 
 print "</TABLE></DIV>"

 # print "</TR></TABLE>"
 print "<DIV ID=device_control style='clear:left;'>"
 print "<A CLASS='z-btn z-btnop z-small-btn' DIV=div_navcont LNK=ajax.cgi?call=device_device_info&node={} OP=load><IMG SRC='images/btn-reboot.png'></A>".format(id)
 print "<A CLASS='z-btn z-btnop z-small-btn' DIV=div_navcont LNK=ajax.cgi?call=device_device_info&node={}&op=update       FRM=info_form OP=post TITLE='Update Entry'><IMG SRC='images/btn-save.png'></A>".format(id)
 print "<A CLASS='z-btn z-btnop z-small-btn' DIV=div_navcont LNK=ajax.cgi?call=device_device_info&node={}&op=lookup&ip={} FRM=info_form OP=post TITLE='Update Entry'><IMG SRC='images/btn-search.png'></A>".format(id,ip)
 if (device_data['dns_a_id'] == 0 or device_data['dns_ptr_id'] == 0):
  print "<A CLASS='z-btn z-btnop z-small-btn' DIV=op_results LNK=ajax.cgi?call=device_device_info&node={}&op=dnslookup&ip={}&hostname={}&domain={} OP=load TITLE='Update DNS'><IMG SRC='images/btn-search.png'></A>".format(id,ip,device_data['hostname'],device_data['domain'])
 if conip and not conip == '127.0.0.1' and device_data['consoleport'] and device_data['consoleport'] > 0:
  print "<A CLASS='z-btn z-small-btn' HREF='telnet://{}:{}' TITLE='Console'><IMG SRC='images/btn-term.png'></A>".format(conip,6000+device_data['consoleport'])
 if device_data['type'] == 'pdu' or device_data['type'] == 'console':
  res = db.do("SELECT id FROM {0}s WHERE ip = '{1}'".format(device_data['type'],device_data['ip']))
  if res == 0:
   print "<A style='float:right;' TITLE='Add {0}' CLASS='z-btn z-small-btn z-btnop' OP=load DIV=div_navcont LNK='ajax.cgi?call={0}_device_info&id=new&ip={1}&name={2}'><IMG SRC='images/btn-add.png'></A>".format(device_data['type'],ip,device_data['hostname'])
 print "<SPAN ID=op_results style='float:right;'>&nbsp;</SPAN>"
 print "</DIV>"
 print "</FORM>"
 print "</DIV>"

 db.close()

 print "<!-- Function navbar and navcontent -->"
 print "<DIV CLASS='z-navbar' style='top:{}px;'>".format(str(height + 40))

 functions = device_get_widgets(device_data['type'])
 if functions:
  if functions[0] == 'operated':
   if device_data['type'] == 'esxi':
    print "<A TARGET='main_cont' HREF='pane.cgi?view=esxi&domain={}&host={}'>Manage</A></B></DIV>".format(device_data['domain'], device_data['hostname'])
  else:
   for fun in functions:
    name = " ".join(fun.split('_')[1:])
    print "<A CLASS='z-btnop' OP=load DIV=div_navdata SPIN=true LNK='ajax.cgi?call=device_op_function&ip={0}&type={1}&op={2}'>{3}</A>".format(ip, device_data['type'], fun, name.title())
 else:
  print "&nbsp;"
 print "</DIV>"
 print "<DIV CLASS='z-navcontent' ID=div_navdata style='top:{}px; overflow-x:hidden; overflow-y:auto; z-index:100'></DIV>".format(str(height + 40))


####################################################### Functions #######################################################
#
# View operation data / widgets
#
def device_op_function(aWeb):
 from sdcp.devices.DevHandler import device_get_instance
 ip   = aWeb.get_value('ip')
 type = aWeb.get_value('type')
 op   = aWeb.get_value('op')
 try:
  dev = device_get_instance(ip,type)
  fun = getattr(dev,op,None)
  fun()
 except Exception as err:
  print "<B>Error in devdata: {}</B>".format(str(err))

#
# find devices operations
#
def device_op_finddevices(aWeb):
 from sdcp.devices.DevHandler import device_discover
 domain    = aWeb.get_value('domain')
 discstart = aWeb.get_value('discstart')
 discstop  = aWeb.get_value('discstop')
 clear     = aWeb.get_value('clear',False)
 if discstart and discstop and domain:
  device_discover(discstart,discstop, domain, clear)
  print "<B>Done Discovering Devices: {} -> {} for {}!</B>".format(discstart,discstop,domain)
  aWeb.log_msg("devices_op_finddevices: Discovered devices [{}] {} -> {} for {}".format(str(clear), discstart,discstop,domain))
 else:
  print "<B>Not all parameters supplied</B>"
