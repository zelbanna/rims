"""Moduledocstring.

Ajax Device calls module

"""
__author__= "Zacharias El Banna"                     
__version__ = "10.1GA"
__status__= "Production"

from sdcp.core.GenLib import DB, sys_ip2int

def int2mac(aInt):
 return ':'.join(s.encode('hex') for s in str(hex(aInt))[2:].zfill(12).decode('hex')).upper()

########################################## Device Operations ##########################################
#
#
#
def device_view_devicelist(aWeb):
 target = aWeb.get_value('target')
 arg    = aWeb.get_value('arg')
 db     = DB()
 db.connect()
 print "<DIV CLASS='z-framed' ID=div_device_devicelist><DIV CLASS='z-table'>"
 print "<TABLE WIDTH=330>"
 print "<TR><TH>IP</TH><TH>FQDN</TH><TH>Model</TH></TR>"
 print "<TR style='height:20px'><TD COLSPAN=3>"
 if target and arg:
  db.do("SELECT id, INET_NTOA(ip) as ipasc, hostname, domain, model FROM devices WHERE {0}='{1}' ORDER BY ip".format(target,arg))
  print "<A TITLE='Reload List' CLASS='z-btn z-small-btn z-op' OP=load DIV=div_navleft LNK='ajax.cgi?call=device_view_devicelist&target={0}&arg={1}'><IMG SRC='images/btn-reboot.png'></A>".format(target,arg)
 else:
  db.do("SELECT id, INET_NTOA(ip) as ipasc, hostname, domain, model FROM devices ORDER BY ip")
  print "<A TITLE='Reload List' CLASS='z-btn z-small-btn z-op' OP=load DIV=div_navleft LNK='ajax.cgi?call=device_view_devicelist'><IMG SRC='images/btn-reboot.png'></A>"
 rows = db.get_all_rows()
 print "<A TITLE='Add Device' CLASS='z-btn z-small-btn z-op' OP=load DIV=div_navcont LNK='ajax.cgi?call=device_new'><IMG SRC='images/btn-add.png'></A>"
 for row in rows:
  print "<TR><TD><A CLASS=z-op TITLE='Show device info for {0}' OP=load DIV=div_navcont LNK='ajax.cgi?call=device_device_info&id={3}'>{0}</A></TD><TD>{1}</TD><TD>{2}</TD></TR>".format(row['ipasc'], row['hostname']+"."+row['domain'], row['model'],row['id'])
 print "</TABLE>"
 print "</DIV></DIV>"
 db.close()


################################ Gigantic Device info and Ops function #################################
#

def device_device_info(aWeb):
 from sdcp.devices.DevHandler import device_detect, device_types, device_get_widgets
 id     = aWeb.get_value('id')
 op     = aWeb.get_value('op',"")
 opres  = str(op).upper()
 height = 250
 conip  = None
 db     = DB()
 db.connect()

 ###################### Data operations ###################
 if   op == 'lookup':
  ip     = aWeb.get_value('ip')
  domain = aWeb.get_value('domain')
  name   = aWeb.get_value('hostname')
  entry  = device_detect(ip,domain)
  if entry['hostname'] == 'unknown':
   entry['hostname'] = name
  else:
   name = entry['hostname']
  db.do("UPDATE devices SET hostname = '{}', snmp = '{}', fqdn = '{}', model = '{}', type = '{}' WHERE id = '{}'".format(entry['hostname'],entry['snmp'],entry['fqdn'],entry['model'],entry['type'],id))
  if not name == 'unknown':
   opres = opres + " and updating DDI:"
   aWeb.log_msg("Device lookup: input [{}, {}, {}]".format(ip,name,domain))
   import sdcp.SettingsContainer as SC
   if SC.dnsdb_proxy == 'True':
    retvals = aWeb.get_proxy(SC.dnsdb_url, "ddi_dns_lookup","ip={}&hostname={}&domain={}".format(ip,name,domain))
   else:
    from sdcp.core.ddi import ddi_dns_lookup
    retvals = ddi_dns_lookup(ip,name,domain)
   dns_a_id   = retvals.get('dns_a_id','0')
   dns_ptr_id = retvals.get('dns_ptr_id','0')
   opres = opres + "{}".format(str(retvals))
   if SC.ipamdb_proxy == 'True':
    retvals = aWeb.get_proxy(SC.ipamdb_url, "ddi_ipam_lookup", "ip={}".format(ip))
   else:
    from sdcp.core.ddi import ddi_ipam_lookup
    retvals = ddi_ipam_lookup(ip)
   ipam_id    = retvals.get('ipam_id','0') 
   tmp_ptr_id = retvals.get('dns_ptr_id','0')
   opres = opres + "{}".format(str(retvals))
   if tmp_ptr_id != '0' and tmp_ptr_id != dns_ptr_id:
    opres = "<B>"+opres+"</B>"
   db.do("UPDATE devices SET ipam_id = {}, dns_a_id = '{}', dns_ptr_id = '{}' where id = '{}'".format(ipam_id, dns_a_id,dns_ptr_id,id))
  db.commit()

 elif op == 'update':
  keys = aWeb.get_keys()
  keys.remove('call')
  keys.remove('id')
  keys.remove('op')
  opres = opres + " values:" + " ".join(keys)
  if keys:
   for key in keys:
    if not (key[0:3] == 'pem' and key[5:] == 'pdu_slot_id'):
     db.do("UPDATE devices SET {0}='{1}' where id = '{2}'".format(key,aWeb.get_value(key),id))
    else:
     pem = key[:4]
     [pemid,pemslot] = aWeb.get_value(key).split('.')
     db.do("UPDATE devices SET {0}_pdu_id='{1}', {0}_pdu_slot ='{2}' where id = '{3}'".format(pem,pemid,pemslot,id))
   db.commit()

 db.do("SELECT *, INET_NTOA(ip) as ipasc FROM devices WHERE id ='{}'".format(id))
 device_data = db.get_row()
 if not device_data:
  # Stale info, quit
  print "Stale info! Reload device list"
  db.close()
  return
 ip   = device_data['ipasc']
 name = device_data['hostname']


 if op == 'updateddi' and not device_data['hostname'] == 'unknown':
  if device_data['ipam_id'] == '0':
   opres = opres + " (please rerun lookup for proper sync)"
  import sdcp.SettingsContainer as SC
  if SC.dnsdb_proxy == 'True':
   aWeb.get_proxy(SC.dnsdb_url, "ddi_dns_update","ip={}&hostname={}&domain={}&dns_a_id={}&dns_ptr_id={}".format(ip,device_data['hostname'],device_data['domain'],device_data['dns_a_id'],device_data['dns_ptr_id']))
  else:
   ddi_dns_update(ip,device_data['hostname'],device_data['domain'],device_data['dns_a_id'],device_data['dns_ptr_id'])
  if SC.ipamdb_proxy == 'True':
   aWeb.get_proxy(SC.ipamdb_url, "ddi_ipam_update","ip={}&fqdn={}&ipam_id={}&dns_ptr_id={}".format(ip,device_data['hostname'] + "." + device_data['domain'],device_data['ipam_id'],device_data['dns_ptr_id']))
  else:
   ddi_ipam_update(ip,device_data['hostname'] + "." + device_data['domain'],device_data['ipam_id'],device_data['dns_ptr_id'])

 ########################## Data Tables ######################
 
 print "<DIV ID=div_device_info CLASS='z-framed z-table' style='resize:horizontal; margin-left:0px; width:670px; z-index:101; height:{}px;'>".format(str(height))
 print "<FORM ID=info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(id)
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
  print "<TR><TD><A CLASS='z-op' TITLE='View graphs for {1}' OP=load DIV=div_navcont LNK='/munin-cgi/munin-cgi-html/{0}/{1}/index.html#content'>Graphs</A>:</TD><TD>yes</TD></TR>".format(device_data['domain'],device_data['hostname']+"."+device_data['domain'])
 else:
  if not device_data['hostname'] == 'unknown':
   print "<TR><TD>Graphs:</TD><TD><A CLASS='z-op' OP=load DIV=div_navcont LNK='ajax.cgi?call=graph_add&node={}&name={}&domain={}' TITLE='Add Graphs for node?'>no</A></TD></TR>".format(id, device_data['hostname'], device_data['domain'])
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
  print "<TR><TD>Rack Unit:</TD><TD TITLE='Top rack unit of device placement'><INPUT NAME=rack_unit CLASS='z-input' TYPE=TEXT PLACEHOLDER='{}'></TD></TR>".format(device_data['rack_unit'])
  if not device_data['type'] == 'console' and db.do("SELECT id, name, INET_NTOA(ip) as ipasc FROM consoles") > 0:
   consoles = db.get_all_rows()
   consoles.append({ 'id':0, 'name':'Not used', 'ip':2130706433, 'ipasc':'127.0.0.1' })
   print "<TR><TD>TS:</TD><TD><SELECT NAME=console_id CLASS='z-select'>"
   for console in consoles:
    extra = ""
    if device_data['console_id'] == console['id']:
     extra = " selected"
     conip = console['ipasc']
    print "<OPTION VALUE={0} {1}>{2}</OPTION>".format(console['id'],extra,console['name'])
   print "<TR><TD>TS Port:</TD><TD TITLE='Console port in rack TS'><INPUT NAME=consoleport CLASS='z-input' TYPE=TEXT PLACEHOLDER='{}'></TD></TR>".format(device_data['consoleport'])
  else:
   print "<TR><TD COLSPAN=2 style='width:200px'>&nbsp;</TD></TR>"
   print "<TR><TD COLSPAN=2 style='width:200px'>&nbsp;</TD></TR>"
  if not device_data['type'] == 'console' and db.do("SELECT *, INET_NTOA(ip) as ipasc FROM pdus") > 0:
   pdus = db.get_all_rows()
   pdus.append({ 'id':0, 'name':'Not used', 'ip':'127.0.0.1', 'slots':0, '0_slot_id':0, '0_slot_name':'Not used' })  
   for pem in ['pem0','pem1']:
    print "<TR><TD>{0} PDU:</TD><TD><SELECT NAME={1}_pdu_slot_id CLASS='z-select'>".format(pem.upper(),pem)
    for pdu in pdus:
     for slotid in range(0,pdu['slots'] + 1):
      extra = " selected" if ((device_data[pem+"_pdu_id"] == pdu['id']) and (device_data[pem+"_pdu_slot"] == pdu[str(slotid)+"_slot_id"])) else ""
      print "<OPTION VALUE={0} {1}>{2}</OPTION>".format(str(pdu['id'])+"."+str(pdu[str(slotid)+"_slot_id"]), extra, pdu['name']+":"+pdu[str(slotid)+"_slot_name"])
    print "</SELECT></TD></TR>"
    print "<TR><TD>{0} Unit:</TD><TD><INPUT NAME={1}_pdu_unit CLASS='z-input' TYPE=TEXT PLACEHOLDER='{2}'></TD></TR>".format(pem.upper(),pem,device_data[pem + "_pdu_unit"])
  else:
   for index in range(0,4):
    print "<TR><TD COLSPAN=2 style='width:200px'>&nbsp;</TD></TR>"
 print "</TABLE></DIV>"
 print "<!-- 3rd Table -->"
 print "<DIV style='margin:3px; float:left;'><TABLE style='width:227px;'><TR><TH COLSPAN=2>Extra info</TH></TR>"
 print "<TR><TD>Rack Size:</TD><TD><INPUT NAME=rack_size CLASS='z-input' TYPE=TEXT PLACEHOLDER='{}'></TD></TR>".format(device_data['rack_size'])
 print "<TR><TD>FQDN:</TD><TD style='{0}'>{1}</TD></TR>".format("border: solid 1px red;" if (name + "." + device_data['domain'] != device_data['fqdn']) else "", device_data['fqdn'])
 print "<TR><TD>DNS A ID:</TD><TD>{}</TD></TR>".format(device_data['dns_a_id'])
 print "<TR><TD>DNS PTR ID:</TD><TD>{}</TD></TR>".format(device_data['dns_ptr_id'])
 print "<TR><TD>IPAM ID:</TD><TD>{}</TD></TR>".format(device_data['ipam_id'])
 print "<TR><TD>MAC:</TD><TD>{}</TD></TR>".format(int2mac(device_data['mac']))
 print "<TR><TD COLSPAN=2 style='width:200px'>&nbsp;</TD></TR>" 
 print "<TR><TD COLSPAN=2 style='width:200px'>&nbsp;</TD></TR>" 
 print "</TABLE></DIV>"
 print "<!-- Controls -->"
 print "<DIV ID=device_control style='clear:left;'>"
 print "<A CLASS='z-btn z-op z-small-btn' DIV=div_navcont LNK=ajax.cgi?call=device_device_info&id={} OP=load><IMG SRC='images/btn-reboot.png'></A>".format(id)
 print "<A CLASS='z-btn z-op z-small-btn' DIV=div_navcont LNK=ajax.cgi?call=device_remove&id={}&dns_a_id={}&dns_ptr_id={}&ipam_id={} OP=confirm MSG='Are you sure you want to delete entry?'><IMG SRC='images/btn-remove.png'></A>".format(id,device_data['dns_a_id'],device_data['dns_ptr_id'],device_data['ipam_id'])
 print "<A CLASS='z-btn z-op z-small-btn' DIV=div_navcont LNK=ajax.cgi?call=device_device_info&op=lookup&ip={}&domain={}&hostname={} FRM=info_form OP=post TITLE='Lookup and Detect Device information'><IMG SRC='images/btn-search.png'></A>".format(ip,device_data['domain'],name)
 print "<A CLASS='z-btn z-op z-small-btn' DIV=div_navcont LNK=ajax.cgi?call=device_device_info&op=update    FRM=info_form OP=post TITLE='Save Device Information'><IMG SRC='images/btn-save.png'></A>"
 print "<A CLASS='z-btn z-op z-small-btn' DIV=div_navcont LNK=ajax.cgi?call=device_device_info&op=updateddi FRM=info_form OP=post TITLE='Update DNS/IPAM systems'><IMG SRC='images/btn-start.png'></A>"
 if (device_data['pem0_pdu_id'] != 0 and device_data['pem0_pdu_unit'] != 0) or (device_data['pem1_pdu_id'] != 0 and device_data['pem1_pdu_unit'] != 0):
  print "<A CLASS='z-btn z-op z-small-btn' DIV=update_results LNK=ajax.cgi?call=pdu_update_device_pdus&pem0_unit={}&pem1_unit={}&name={} FRM=info_form OP=post TITLE='Update PDU with device info'><IMG SRC='images/btn-pdu-save.png' ALT='P'></A>".format(device_data['pem0_pdu_unit'],device_data['pem1_pdu_unit'],name)
 if conip and not conip == '127.0.0.1' and device_data['consoleport'] and device_data['consoleport'] > 0:
  print "<A CLASS='z-btn z-small-btn' HREF='telnet://{}:{}' TITLE='Console'><IMG SRC='images/btn-term.png'></A>".format(conip,6000+device_data['consoleport'])
 if device_data['type'] == 'pdu' or device_data['type'] == 'console' and db.do("SELECT id FROM {0}s WHERE ip = '{1}'".format(device_data['type'],device_data['ip'])) == 0:
  print "<A style='float:right;' TITLE='Add {0}' CLASS='z-btn z-small-btn z-op' OP=load DIV=div_navcont LNK='ajax.cgi?call={0}_device_info&id=new&ip={1}&name={2}'><IMG SRC='images/btn-add.png'></A>".format(device_data['type'],ip,device_data['hostname'])
 print "<SPAN ID=update_results style='float:right; font-size:9px;'>{}</SPAN>".format(opres)
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
    funname = " ".join(fun.split('_')[1:])
    print "<A CLASS='z-op' OP=load DIV=div_navdata SPIN=true LNK='ajax.cgi?call=device_op_function&ip={0}&type={1}&op={2}'>{3}</A>".format(ip, device_data['type'], fun, funname.title())
 else:
  print "&nbsp;"
 print "</DIV>"
 print "<DIV CLASS='z-navcontent' ID=div_navdata style='top:{}px; overflow-x:hidden; overflow-y:auto; z-index:100'></DIV>".format(str(height + 40))




####################################################### Functions #######################################################
#
# View operation data / widgets
#

def device_remove(aWeb):
 device_id  = aWeb.get_value('id')
 dns_a_id   = aWeb.get_value('dns_a_id','0')
 dns_ptr_id = aWeb.get_value('dns_ptr_id','0')
 ipam_id    = aWeb.get_value('ipam_id','0')
 print "<DIV CLASS='z-table'>"
 db = DB()
 db.connect()
 res = db.do("DELETE FROM devices WHERE id = '{0}'".format(device_id))
 db.commit()
 if (dns_a_id != '0') or (dns_ptr_id != '0'):
  import sdcp.SettingsContainer as SC
  if SC.dnsdb_proxy == 'True':
   dres = aWeb.get_proxy(SC.dnsdb_url, "ddi_dns_remove","dns_a_id={}&dns_ptr_id={}".format(dns_a_id,dns_ptr_id))
  else:
   from sdcp.core.ddi import ddi_dns_remove
   dres = ddi_dns_remove(dns_a_id,dns_ptr_id)
  print "DNS  entries removed:{}<BR>".format(str(dres))
 if not ipam_id == '0':
  import sdcp.SettingsContainer as SC
  if SC.ipamdb_proxy == 'True':
   ires = aWeb.get_proxy(SC.ipamdb_url, "ddi_ipam_remove","ipam_id={}".format(ipam_id))
  else:
   from sdcp.core.ddi import ddi_ipam_remove
   ires = ddi_ipam_remove(ipam_id)
  print "IPAM entries removed:{}<BR>".format(str(ires))
 print "Unit {0} deleted ({1})".format(device_id,res)
 print "</DIV>"
 db.close()

#
#
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
 start = aWeb.get_value('start','127.0.0.1')
 stop  = aWeb.get_value('stop','127.0.0.1')
 clear = aWeb.get_value('clear',False)
 domain  = aWeb.get_value('domain')
 results = ""
 if not start == '127.0.0.1' and not stop == '127.0.0.1' and domain:
  device_discover(start,stop, domain, clear)
  results = "Discovered devices [{}] {} -> {}".format(str(clear), start,stop)
  aWeb.log_msg("devices_op_finddevices: " + results)
 elif clear:
  db = DB()
  db.connect()
  db.do("TRUNCATE table devices")
  db.commit()
  db.close()
  results = "Cleared table"
  aWeb.log_msg("devices_op_finddevices: " + results)
 print "<DIV CLASS='z-framed z-table' style='resize: horizontal; margin-left:0px; z-index:101; width:350px; height:160px;'>"
 print "<FORM ID=device_discover_form>"
 print "<TABLE style='width:100%'>"
 print "<TR><TH COLSPAN=2>Device Discovery</TH></TR>"
 print "<TR><TD>Start IP:</TD><TD><INPUT NAME=start  TYPE=TEXT CLASS='z-input' PLACEHOLDER='{0}'></TD></TR>".format(start)
 print "<TR><TD>End IP:</TD><TD><INPUT   NAME=stop   TYPE=TEXT CLASS='z-input' PLACEHOLDER='{0}'></TD></TR>".format(stop)
 print "<TR><TD>Domain:</TD><TD><INPUT   NAME=domain TYPE=TEXT CLASS='z-input' VALUE='{0}'></TD></TR>".format(domain)
 print "<TR><TD>Clear</TD><TD><INPUT TYPE=checkbox NAME=clear VALUE=True {}></TD></TR>".format("checked" if clear else "")
 print "</TABLE>"
 print "<A CLASS='z-btn z-op z-small-btn' DIV=div_navcont SPIN=true LNK=ajax.cgi?call=device_op_finddevices FRM=device_discover_form OP=post><IMG SRC='images/btn-start.png'></A>"
 print "<SPAN style='font-size:9px; float:right'>{}</SPAN>".format(results)
 print "</DIV>"

#
#
#
def device_op_syncddi(aWeb):
 import sdcp.SettingsContainer as SC
 db = DB()
 db.connect()
 db.do("SELECT id, ip, hostname, INET_NTOA(ip) as ipasc, domain FROM devices WHERE (dns_a_id = 0 or dns_ptr_id = 0 or ipam_id = 0) ORDER BY ip")
 rows = db.get_all_rows()
 print "<DIV CLASS='z-table'>"
 print "<TABLE>"
 print "<TR><TH>Id</TH><TH>IP</TH><TH>Hostname</TH><TH>Domain</TH><TH>A</TH><TH>PTR</TH><TH>IPAM</TH><TH>Extra</TH>"
 for row in rows:
  ip   = row['ipasc']
  name = row['hostname']
  dom  = row['domain'] 
  if SC.dnsdb_proxy == 'True':
   retvals = aWeb.get_proxy(SC.dnsdb_url,"ddi_dns_lookup","ip={}&hostname={}&domain={}".format(ip,name,dom))
  else:
   from sdcp.core.ddi import ddi_dns_lookup
   retvals = ddi_dns_lookup(ip,name,dom)
  dns_a_id   = retvals.get('dns_a_id','0')
  dns_ptr_id = retvals.get('dns_ptr_id','0')
  if SC.ipamdb_proxy == 'True':
   retvals = aWeb.get_proxy(SC.ipamdb_url,"ddi_ipam_lookup","ip={}".format(ip))                                  
  else:
   from sdcp.core.ddi import ddi_ipam_lookup 
   retvals = ddi_ipam_lookup(ip)             

  ipam_id    = retvals.get('ipam_id','0')

  print "<TR><TD>{}</<TD><TD>{}</TD><TD>{}</TD><TD>{}</TD><TD>{}</TD><TD>{}</TD><TD>{}</TD><TD>".format(row['id'],ip,name,dom,dns_a_id,dns_ptr_id,ipam_id)
  if not name == 'unknown':
   print "updating"
   if SC.dnsdb_proxy == 'True':
    aWeb.get_proxy(SC.dnsdb_url, "ddi_dns_update","ip={}&hostname={}&domain={}&dns_a_id={}&dns_ptr_id={}".format(ip,name,dom,dns_a_id,dns_ptr_id))
    retvals = aWeb.get_proxy(SC.dnsdb_url, "ddi_dns_lookup","ip={}&hostname={}&domain={}".format(ip,name,dom))
   else:
    from sdcp.core.ddi import ddi_dns_update
    ddi_dns_update(ip,name,dom,dns_a_id,dns_ptr_id)
    retvals = ddi_dns_lookup(ip,name,dom)
   if SC.ipamdb_proxy == 'True':
    aWeb.get_proxy(SC.ipamdb_url, "ddi_ipam_update","ip={}&fqdn={}&ipam_id={}&dns_ptr_id={}".format(ip,name + '.' + dom, ipam_id, retvals.get('dns_ptr_id','0')))
   else:
    from sdcp.core.ddi import ddi_ipam_updates
    ddi_ipam_update(ip,name + '.' + dom, ipam_id, retvals.get('dns_ptr_id','0'))

   print str(retvals)
   db.do("UPDATE devices SET ipam_id = {}, dns_a_id = '{}', dns_ptr_id = '{}' WHERE id = '{}'".format(ipam_id, retvals.get('dns_a_id','0'),retvals.get('dns_ptr_id','0'), row['id']))
  print "</TD></TR>"

 db.commit()
 db.close()
 print "</TABLE></DIV>"

#
#
#

def is_mac(aMAC):
 try:
  aMAC = aMAC.replace(":","")
  return len(aMAC) == 12 and int(aMAC,16)
 except:
  return False

def device_new(aWeb):
 ip  = aWeb.get_value('ip',"127.0.0.1")
 mac = aWeb.get_value('mac',"00:00:00:00:00:00")
 dom = aWeb.get_value('dom',"domain")
 results = ""
 if not (ip == '127.0.0.1' or dom == 'domain'):
  ipint = sys_ip2int(ip)
  db = DB()
  db.connect()
  xist = db.do("SELECT id,hostname,domain FROM devices WHERE ip ='{}'".format(ipint))
  if xist == 0:
   mac = mac.replace(":","")
   if not is_mac(mac):
    mac = "000000000000"
   res = db.do("INSERT INTO devices (ip,mac,domain,hostname,snmp,model,type,fqdn,rack_size) VALUES('{}',x'{}','{}','unknown','unknown','unknown','unknown','unknown',1)".format(ipint,mac,dom))
   db.commit()
   results = "Added IP {} and MAC {} ({})".format(ip,mac,res)
  else:
   xist = db.get_row()
   results = "Existing IP: {}.{} ({})".format(xist['hostname'],xist['domain'],xist['id']) 
  db.close()

 print "<DIV CLASS='z-framed z-table' style='resize: horizontal; margin-left:0px; z-index:101; width:350px; height:140px;'>"
 print "<FORM ID=device_new_form>"
 print "<TABLE style='width:100%'>"
 print "<TR><TH COLSPAN=2>Add Device</TH></TR>"
 print "<TR><TD>IP:</TD><TD><INPUT     NAME=ip     TYPE=TEXT CLASS='z-input' PLACEHOLDER='{0}'></TD></TR>".format(ip)
 print "<TR><TD>Domain:</TD><TD><INPUT NAME=dom TYPE=TEXT CLASS='z-input' PLACEHOLDER='{0}'></TD></TR>".format(dom)
 print "<TR><TD>MAC:</TD><TD><INPUT NAME=mac TYPE=TEXT CLASS='z-input' PLACEHOLDER='{0}'></TD></TR>".format(mac)
 print "</TABLE>"
 print "<A CLASS='z-btn z-op z-small-btn' DIV=div_navcont LNK=ajax.cgi?call=device_new FRM=device_new_form OP=post><IMG SRC='images/btn-start.png'></A>"
 print "<SPAN style='font-size:9px; float:right'>{}</SPAN>".format(results)
 print "</DIV>"
