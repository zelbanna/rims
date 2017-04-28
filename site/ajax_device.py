"""Module docstring.

Ajax Device calls module

"""
__author__= "Zacharias El Banna"                     
__version__ = "10.5GA"
__status__= "Production"

import sdcp.core.GenLib as GL

########################################## Device Operations ##########################################
#
#
#
def view_devicelist(aWeb):
 target = aWeb.get_value('target')
 arg    = aWeb.get_value('arg')
 sort   = aWeb.get_value('sort','ip')
 db     = GL.DB()
 db.connect()
 print "<DIV CLASS='z-table'>"
 print "<TABLE WIDTH=330><TR>"
 print "<TH><A CLASS=z-op OP=load DIV=div_navleft LNK='ajax.cgi?{0}&sort=ip'>IP</A></TH><TH><A CLASS=z-op OP=load DIV=div_navleft LNK='ajax.cgi?{0}&sort=hostname'>FQDN</A></TH><TH>Model</TH>".format(aWeb.get_args_except(['sort']))
 print "</TR><TR style='height:20px'><TD COLSPAN=3>"
 if not target or not arg:
  tune = ""
 elif target and arg == 'NULL':
  tune = "WHERE {0} is NULL".format(target)
 else:
  tune = "WHERE {0} = {1}".format(target,arg)
 res = db.do("SELECT devices.id, INET_NTOA(ip) as ipasc, hostname, domains.name as domain, model FROM devices JOIN domains ON domains.id = devices.a_dom_id {0} ORDER BY {1}".format(tune,sort))
 print "<A TITLE='Reload List' CLASS='z-btn z-small-btn z-op' OP=load DIV=div_navleft LNK='ajax.cgi?{0}'><IMG SRC='images/btn-reboot.png'></A>".format(aWeb.get_args_except())
 print "<A TITLE='Add Device'  CLASS='z-btn z-small-btn z-op' OP=load DIV=div_navcont LNK='ajax.cgi?call=device_new'><IMG SRC='images/btn-add.png'></A>"
 rows = db.get_all_rows()
 for row in rows:
  print "<TR><TD><A CLASS=z-op TITLE='Show device info for {0}' OP=load DIV=div_navcont LNK='ajax.cgi?call=device_device_info&id={3}'>{0}</A></TD><TD>{1}</TD><TD>{2}</TD></TR>".format(row['ipasc'], row['hostname']+"."+row['domain'], row['model'],row['id'])
 print "</TABLE></DIV>"
 db.close()


################################ Gigantic Device info and Ops function #################################
#

def device_info(aWeb):
 from sdcp.devices.DevHandler import device_types, device_get_widgets
 id    = aWeb.get_value('id')
 op    = aWeb.get_value('op',"")
 opres = str(op).upper()
 conip = None

 ###################### Data operations ###################
 if   op == 'lookup':
  from rest_device import lookup_info
  opres = opres + " " + str(lookup_info({'id':id}))

 elif op == 'update':
  from rest_device import update_info
  d = aWeb.get_args2dict_except(['devices_ipam_gw','call','op'])
  opres = opres + " " + str(update_info(d))

 db  = GL.DB()
 db.connect()
 xist = db.do("SELECT *, INET_NTOA(ip) as ipasc, subnets.subnet, d2.name AS a_name, d1.name AS ptr_name FROM devices LEFT JOIN domains AS d1 ON devices.ptr_dom_id = d1.id LEFT JOIN domains AS d2 ON devices.a_dom_id = d2.id JOIN subnets ON devices.ipam_sub_id = subnets.id WHERE devices.id ='{}'".format(id))
 if xist > 0:
  device_data = db.get_row()
 else:
  print "Stale info! Reload device list"
  db.close()
  return
 db.do("SELECT * FROM racks")
 racks = db.get_all_rows()
 racks.append({ 'id':'NULL', 'name':'Not used', 'size':'48', 'fk_pdu_1':'0', 'fk_pdu_2':'0','fk_console':'0'})
 if device_data['rack_id']:
  rack_xist = db.do("SELECT * FROM rackinfo WHERE device_id = {}".format(id))
  rack_info = db.get_row()

 ip   = device_data['ipasc']
 name = device_data['hostname']

 if op == 'updateddi' and not name == 'unknown':
  from rest_ddi import dns_update, ipam_update
  if device_data['ipam_id'] == '0':
   opres = opres + " (please rerun lookup for proper sync)"
  dns_update( { 'ip':ip, 'name':name, 'a_dom_id': str(device_data['a_dom_id']), 'a_id':str(device_data['a_id']), 'ptr_id':str(device_data['ptr_id']) })
  ipam_update({ 'ip':ip, 'fqdn':name+"."+device_data['a_name'], 'a_dom_id': str(device_data['a_dom_id']), 'ipam_id':str(device_data['ipam_id']), 'ipam_sub_id':str(device_data['ipam_sub_id']),'ptr_id':str(device_data['ptr_id']) })

 ########################## Data Tables ######################
 
 print "<DIV ID=div_devinfo CLASS='z-table' style='position:relative; resize:horizontal; margin-left:0px; width:675px; z-index:101; height:240px; float:left;'>"
 print "<FORM ID=info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(id)
 print "<INPUT TYPE=HIDDEN NAME=racked VALUE={}>".format(1 if device_data['rack_id'] else 0)
 print "<!-- Reachability Info -->"
 print "<DIV style='margin:3px; float:left; height:190px;'><TABLE style='width:210px;'><TR><TH COLSPAN=2>Reachability Info</TH></TR>"
 print "<TR><TD>Name:</TD><TD><INPUT NAME=devices_hostname CLASS='z-input' TYPE=TEXT VALUE='{}'></TD></TR>".format(device_data['hostname'])
 print "<TR><TD>Domain:</TD><TD>{}</TD></TR>".format(device_data['a_name'])
 print "<TR><TD>SNMP:</TD><TD>{}</TD></TR>".format(device_data['snmp'])
 print "<TR><TD>IP:</TD><TD>{}</TD></TR>".format(ip)
 print "<TR><TD>Type:</TD><TD TITLE='Device type'><SELECT NAME=devices_type CLASS='z-select'>"
 for tp in device_types():
  extra = " selected" if device_data['type'] == tp else ""      
  print "<OPTION VALUE={0} {1}>{0}</OPTION>".format(str(tp),extra)
 print "</SELECT></TD></TR>"
 print "<TR><TD>Model:</TD><TD style='max-width:150px;'>{}</TD></TR>".format(device_data['model'])
 if device_data['graphed'] == "yes":
  print "<TR><TD><A CLASS='z-op' TITLE='View graphs for {1}' OP=load DIV=div_navcont LNK='/munin-cgi/munin-cgi-html/{0}/{1}/index.html#content'>Graphs</A>:</TD><TD>yes</TD></TR>".format(device_data['a_name'],device_data['hostname']+"."+ device_data['a_name'])
 else:
  if not device_data['hostname'] == 'unknown':
   print "<TR><TD>Graphs:</TD><TD><A CLASS='z-op' OP=load DIV=div_navcont LNK='ajax.cgi?call=graph_add&node={}&name={}&domain={}' TITLE='Add Graphs for node?'>no</A></TD></TR>".format(id, device_data['hostname'], device_data['a_name'])
  else:
   print "<TR><TD>Graphs:</TD><TD>no</TD></TR>"
 print "<TR><TD COLSPAN=2 style='width:200px'>&nbsp;</TD></TR>"
 print "</TABLE></DIV>"

 print "<!-- Additional info -->"
 print "<DIV style='margin:3px; float:left; height:190px;'><TABLE style='width:227px;'><TR><TH COLSPAN=2>Additional Info</TH></TR>"
 print "<TR><TD>Rack:</TD><TD><SELECT NAME=devices_rack_id CLASS='z-select'>"
 for rack in racks:
  extra = " selected" if ((not device_data['rack_id'] and rack['id'] == 'NULL') or (device_data['rack_id'] and device_data['rack_id'] == rack['id'])) else ""
  print "<OPTION VALUE={0} {1}>{2}</OPTION>".format(rack['id'],extra,rack['name'])
 print "</SELECT></TD></TR>"
 print "<TR><TD>FQDN:</TD><TD style='{0}'>{1}</TD></TR>".format("border: solid 1px red;" if (name + "." + device_data['a_name'] != device_data['fqdn']) else "", device_data['fqdn'])
 print "<TR><TD>DNS A ID:</TD><TD>{}</TD></TR>".format(device_data['a_id'])
 print "<TR><TD>DNS PTR ID:</TD><TD>{}</TD></TR>".format(device_data['ptr_id'])
 print "<TR><TD>IPAM ID:</TD><TD>{}</TD></TR>".format(device_data['ipam_id'])
 print "<TR><TD>MAC:</TD><TD>{}</TD></TR>".format(GL.sys_int2mac(device_data['mac']))
 print "<TR><TD>Gateway:</TD><TD><INPUT CLASS='z-input' TYPE=TEXT NAME=devices_ipam_gw VALUE={}></TD></TR>".format(GL.sys_int2ip(device_data['subnet'] + 1))
 print "<TR><TD COLSPAN=2 style='width:200px'>&nbsp;</TD></TR>" 
 print "</TABLE></DIV>"

 print "<!-- Rack Info if such exists -->"
 if device_data['rack_id'] and not device_data['type'] == 'pdu':
  print "<DIV style='margin:3px; float:left; height:190px;'><TABLE style='width:210px;'><TR><TH COLSPAN=2>Rack Info</TH></TR>"
  print "<TR><TD>Rack Size:</TD><TD><INPUT NAME=rackinfo_rack_size CLASS='z-input' TYPE=TEXT PLACEHOLDER='{}'></TD></TR>".format(rack_info['rack_size'])
  print "<TR><TD>Rack Unit:</TD><TD TITLE='Top rack unit of device placement'><INPUT NAME=rackinfo_rack_unit CLASS='z-input' TYPE=TEXT PLACEHOLDER='{}'></TD></TR>".format(rack_info['rack_unit'])
  if not device_data['type'] == 'console' and db.do("SELECT id, name, INET_NTOA(ip) as ipasc FROM consoles") > 0:
   consoles = db.get_all_rows()
   consoles.append({ 'id':'NULL', 'name':'No Console', 'ip':2130706433, 'ipasc':'127.0.0.1' })
   print "<TR><TD>TS:</TD><TD><SELECT NAME=rackinfo_console_id CLASS='z-select'>"
   for console in consoles:
    extra = ""
    if (rack_info['console_id'] == console['id']) or (not rack_info['console_id'] and console['id'] == 'NULL'):
     extra = " selected='selected'"
     conip = console['ipasc']
    print "<OPTION VALUE={0} {1}>{2}</OPTION>".format(console['id'],extra,console['name'])
   print "</SELECT></TD></TR>"
   print "<TR><TD>TS Port:</TD><TD TITLE='Console port in rack TS'><INPUT NAME=rackinfo_console_port CLASS='z-input' TYPE=TEXT PLACEHOLDER='{}'></TD></TR>".format(rack_info['console_port'])
  else:
   print "<TR><TD COLSPAN=2 style='width:200px'>&nbsp;</TD></TR>"
   print "<TR><TD COLSPAN=2 style='width:200px'>&nbsp;</TD></TR>"
  if not device_data['type'] == 'pdu' and db.do("SELECT *, INET_NTOA(ip) as ipasc FROM pdus") > 0:
   pdus = db.get_all_rows()
   pdus.append({ 'id':'NULL', 'name':'No', 'ip':'127.0.0.1', 'slots':0, '0_slot_id':0, '0_slot_name':'PDU' })
   for pem in ['pem0','pem1']:
    print "<TR><TD>{0} PDU:</TD><TD><SELECT NAME=rackinfo_{1}_pdu_slot_id CLASS='z-select'>".format(pem.upper(),pem)
    for pdu in pdus:
     for slotid in range(0,pdu['slots'] + 1):
      extra = " selected" if ((rack_info[pem+"_pdu_id"] == pdu['id']) and (rack_info[pem+"_pdu_slot"] == pdu[str(slotid)+"_slot_id"])) or (not rack_info[pem+"_pdu_id"] and  pdu['id'] == 'NULL')else ""
      print "<OPTION VALUE={0} {1}>{2}</OPTION>".format(str(pdu['id'])+"."+str(pdu[str(slotid)+"_slot_id"]), extra, pdu['name']+":"+pdu[str(slotid)+"_slot_name"])
    print "</SELECT></TD></TR>"
    print "<TR><TD>{0} Unit:</TD><TD><INPUT NAME=rackinfo_{1}_pdu_unit CLASS='z-input' TYPE=TEXT PLACEHOLDER='{2}'></TD></TR>".format(pem.upper(),pem,rack_info[pem + "_pdu_unit"])
  else:
   for index in range(0,4):
    print "<TR><TD COLSPAN=2 style='width:200px'>&nbsp;</TD></TR>"
  print "</TABLE></DIV>"
 print "</FORM>"
 print "<!-- Controls -->"
 print "<DIV ID=device_control style='clear:left;'>"
 print "<A CLASS='z-btn z-op z-small-btn' DIV=div_navcont LNK=ajax.cgi?call=device_device_info&id={} OP=load><IMG SRC='images/btn-reboot.png'></A>".format(id)
 print "<A CLASS='z-btn z-op z-small-btn' DIV=div_navcont LNK=ajax.cgi?call=device_remove&id={}      OP=confirm MSG='Are you sure you want to delete device?'><IMG SRC='images/btn-remove.png'></A>".format(id)
 print "<A CLASS='z-btn z-op z-small-btn' DIV=div_navcont LNK=ajax.cgi?call=device_device_info&op=lookup    FRM=info_form OP=post TITLE='Lookup and Detect Device information'><IMG SRC='images/btn-search.png'></A>"
 print "<A CLASS='z-btn z-op z-small-btn' DIV=div_navcont LNK=ajax.cgi?call=device_device_info&op=update    FRM=info_form OP=post TITLE='Save Device Information'><IMG SRC='images/btn-save.png'></A>"
 print "<A CLASS='z-btn z-op z-small-btn' DIV=div_navcont LNK=ajax.cgi?call=device_device_info&op=updateddi FRM=info_form OP=post TITLE='Update DNS/IPAM systems'><IMG SRC='images/btn-start.png'></A>"
 print "<A CLASS='z-btn z-op z-small-btn' DIV=div_navdata LNK=ajax.cgi?call=device_conf_gen                 FRM=info_form OP=post TITLE='Generate System Conf'><IMG SRC='images/btn-document.png'></A>"
 if device_data['rack_id'] and ((rack_info['pem0_pdu_id'] != 0 and rack_info['pem0_pdu_unit'] != 0) or (rack_info['pem1_pdu_id'] != 0 and rack_info['pem1_pdu_unit'] != 0)):
  print "<A CLASS='z-btn z-op z-small-btn' DIV=update_results LNK=ajax.cgi?call=pdu_update_device_pdus&pem0_unit={}&pem1_unit={}&name={} FRM=info_form OP=post TITLE='Update PDU with device info'><IMG SRC='images/btn-pdu-save.png' ALT='P'></A>".format(rack_info['pem0_pdu_unit'],rack_info['pem1_pdu_unit'],name)
 if device_data['rack_id'] and (conip and not conip == '127.0.0.1' and rack_info['console_port'] and rack_info['console_port'] > 0):
  print "<A CLASS='z-btn z-small-btn' HREF='telnet://{}:{}' TITLE='Console'><IMG SRC='images/btn-term.png'></A>".format(conip,6000+rack_info['console_port'])
 if (device_data['type'] == 'pdu' or device_data['type'] == 'console') and db.do("SELECT id FROM {0}s WHERE ip = '{1}'".format(device_data['type'],device_data['ip'])) == 0:
  print "<A CLASS='z-btn z-op z-small-btn' DIV=div_navcont LNK='ajax.cgi?call={0}_device_info&id=new&ip={1}&name={2}' OP=load style='float:right;' TITLE='Add {0}'><IMG SRC='images/btn-add.png'></A>".format(device_data['type'],ip,device_data['hostname']) 
 print "<SPAN ID=update_results style='max-width:400px; float:right; font-size:9px;'>{}</SPAN>".format(opres)
 print "</DIV>"
 db.close()
 print "</DIV>"

 print "<!-- Function navbar and navcontent -->"
 print "<DIV CLASS='z-navbar' style='top:280px;'>"
 functions = device_get_widgets(device_data['type'])
 if functions:
  if functions[0] == 'operated':
   if device_data['type'] == 'esxi':
    print "<A TARGET='main_cont' HREF='pane.cgi?view=esxi&domain={}&host={}'>Manage</A></B></DIV>".format(device_data['a_name'], device_data['hostname'])
  else:
   for fun in functions:
    funname = " ".join(fun.split('_')[1:])
    print "<A CLASS='z-op' OP=load DIV=div_navdata SPIN=true LNK='ajax.cgi?call=device_op_function&ip={0}&type={1}&op={2}'>{3}</A>".format(ip, device_data['type'], fun, funname.title())
 else:
  print "&nbsp;"
 print "</DIV>"
 print "<DIV CLASS='z-navcontent' ID=div_navdata style='top:280px; overflow-x:hidden; overflow-y:auto; z-index:100'></DIV>"



####################################################### Functions #######################################################
#
# View operation data / widgets
#

def conf_gen(aWeb):
 id = aWeb.get_value('id','0')
 gw = aWeb.get_value('devices_ipam_gw')
 db = GL.DB()
 db.connect()
 db.do("SELECT INET_NTOA(ip) as ipasc, hostname,domains.name as domain, subnets.subnet, subnets.mask FROM devices LEFT JOIN domains ON domains.id = devices.a_dom_id JOIN subnets ON subnets.id = devices.ipam_sub_id WHERE devices.id = '{}'".format(id))
 row = db.get_row()
 db.close()
 type = aWeb.get_value('devices_type')
 print "<DIV CLASS='z-table' style='margin-left:0px; z-index:101; width:100%; float:left; bottom:0px;'>"
 from sdcp.devices.DevHandler import device_get_instance
 try:
  dev  = device_get_instance(row['ipasc'],type)
  dev.print_conf({'name':row['hostname'], 'domain':row['domain'], 'gateway':gw, 'subnet':GL.sys_int2ip(int(row['subnet'])), 'mask':row['mask']})
 except Exception as err:
  print "No instance config specification for {} type".format(row.get('type','unknown'))
 print "</DIV>"

#
#
#
def op_function(aWeb):
 from sdcp.devices.DevHandler import device_get_instance
 try:
  dev = device_get_instance(aWeb.get_value('ip'),aWeb.get_value('type'))
  fun = getattr(dev,aWeb.get_value('op'),None)
  fun()
 except Exception as err:
  print "<B>Error in devdata: {}</B>".format(str(err))

#
#
#
def rack_info(aWeb):
 db = GL.DB()
 db.connect()
 res  = db.do("SELECT rackinfo.*, devices.hostname, devices.rack_id, devices.ip, INET_NTOA(devices.ip) as ipasc FROM rackinfo JOIN devices ON devices.id = rackinfo.device_id")
 devs = db.get_all_rows()
 if res == 0:
  db.close()
  return
 order = devs[0].keys()
 order.sort()
 db.do("SELECT id, name FROM pdus")
 pdus  = db.get_all_dict('id')
 db.do("SELECT id, name FROM consoles")
 cons  = db.get_all_dict('id')
 db.do("SELECT id, name FROM racks")
 racks = db.get_all_dict('id')
 row   = "<TR style='border: 1px solid grey'><TD>{}</TD><TD>{}</TD><TD>{}</TD><TD>{}</TD><TD>{}</TD><TD>{}</TD><TD>{}</TD><TD>{}</TD><TD>{}</TD></TR>" 
 print "<DIV CLASS='z-table' style='overflow-x:auto;'><TABLE>"
 print "<TR style='border: 1px solid grey'><TH>Hostname</TH><TH>Device</TH><TH>IP</TH><TH>Console</TH><TH>Port</TH><TH>PEM0-PDU</TH><TH>slot</TH><TH>unit</TH><TH>PEM1-PDU</TH><TH>slot</TH><TH>unit</TH><TH>Rack</TH><TH>size</TH><TH>unit</TH></TR>"
 for dev in devs:
  if not dev['backup_ip']:
   db.do("UPDATE rackinfo SET backup_ip = {} WHERE device_id = {}".format(dev['ip'],dev['device_id']))
  print "<TR>"
  print "<TD>{}</TD><TD>{}</TD><TD>{}</TD>".format(dev['hostname'],dev['device_id'],dev['ipasc'])
  print "<TD>{}</TD><TD>{}</TD>".format(cons.get(dev['console_id'],{}).get('name',None),dev['console_port'])
  print "<TD>{}</TD><TD>{}</TD><TD>{}</TD>".format( pdus.get(dev['pem0_pdu_id'],{}).get('name',None),dev['pem0_pdu_slot'],dev['pem0_pdu_unit'])
  print "<TD>{}</TD><TD>{}</TD><TD>{}</TD>".format( pdus.get(dev['pem1_pdu_id'],{}).get('name',None),dev['pem1_pdu_slot'],dev['pem1_pdu_unit'])
  print "<TD>{}</TD><TD>{}</TD><TD>{}</TD>".format(racks.get(dev['rack_id'],{}).get('name',None),dev['rack_size'],dev['rack_unit'])
  print "</TR>"
 print "</TABLE></DIV>"
 db.commit()
 db.close()

##################################### Rest API #########################################

#
# new device:
#
def new(aWeb):
 ip       = aWeb.get_value('ip',"127.0.0.1")
 hostname = aWeb.get_value('hostname','unknown')
 mac      = aWeb.get_value('mac',"00:00:00:00:00:00")
 op       = aWeb.get_value('op')
 if op:
  from rest_device import new
  a_dom    = aWeb.get_value('a_dom_id')
  ipam_sub = aWeb.get_value('ipam_sub_id')
  print new({ 'ip':ip, 'mac':mac, 'hostname':hostname, 'a_dom_id':a_dom, 'ipam_sub_id':ipam_sub })
 else:
  db = GL.DB()
  db.connect()
  db.do("SELECT id, subnet, INET_NTOA(subnet) as subasc, mask, subnet_description, section_name FROM subnets ORDER BY subnet");
  subnets = db.get_all_rows()
  db.do("SELECT id, name FROM domains")
  domains = db.get_all_rows()
  db.close()
  print "<DIV CLASS='z-table' style='resize: horizontal; margin-left:0px; z-index:101; width:430px; height:180px;'>"
  print "<FORM ID=device_new_form>"
  print "<INPUT TYPE=HIDDEN NAME=op VALUE=json>"
  print "<TABLE style='width:100%'>"
  print "<TR><TH COLSPAN=2>Add Device</TH></TR>"
  print "<TR><TD>IP:</TD><TD><INPUT       NAME=ip       TYPE=TEXT CLASS='z-input' PLACEHOLDER='{0}'></TD></TR>".format(ip)
  print "<TR><TD>Hostname:</TD><TD><INPUT NAME=hostname TYPE=TEXT CLASS='z-input' PLACEHOLDER='{0}'></TD></TR>".format(hostname)
  print "<TR><TD>Domain:</TD><TD><SELECT CLASS='z-select' NAME=a_dom_id>"
  for d in domains:
   if not "in-addr.arpa" in d.get('name'):
    print "<OPTION VALUE={0}>{1}</OPTION>".format(d.get('id'),d.get('name'))
  print "</SELECT></TD></TR>"
  print "<TR><TD>Subnet:</TD><TD><SELECT CLASS='z-select' NAME=ipam_sub_id>"
  for s in subnets:
   print "<OPTION VALUE={0}>{1}/{2} ({3})</OPTION>".format(s.get('id'),s.get('subasc'),s.get('mask'),s.get('subnet_description'))
  print "</SELECT></TD></TR>"
  print "<TR><TD>MAC:</TD><TD><INPUT      NAME=mac  TYPE=TEXT CLASS='z-input' PLACEHOLDER='{0}'></TD></TR>".format(mac)
  print "</TABLE>"
  print "<A CLASS='z-btn z-op z-small-btn' DIV=device_new_span LNK=ajax.cgi?call=device_new FRM=device_new_form OP=post><IMG SRC='images/btn-start.png'></A>&nbsp;"
  print "<SPAN ID=device_new_span style='max-width:400px; font-size:9px; float:right'></SPAN>"
  print "</DIV>"

#
#
#
def remove(aWeb):
 from rest_device import remove
 id      = aWeb.get_value('id')
 print "<DIV CLASS='z-table'>"
 res = remove({ 'id':id })
 print "Unit {0} deleted ({1})".format(id,str(res))
 print "</DIV>"

#
#
#
def dump_db(aWeb):
 from json import dumps
 from rest_device import dump_db
 table = aWeb.get_value('table','devices')
 cols  = aWeb.get_value('columns','*')
 print "<PRE>{}</PRE>".format(dumps(dump_db({'table':table,'columns':cols}), indent=4, sort_keys=True))

#
# find devices operations
#
def discover(aWeb):
 op = aWeb.get_value('op')
 db = GL.DB()
 db.connect()
 if op:
  from rest_device import discover
  clear = aWeb.get_value('clear',False)
  a_dom = aWeb.get_value('a_dom_id')
  ipam  = aWeb.get_value('ipam_sub',"0_0_32").split('_')
  # id, subnet int, subnet mask
  res = discover({ 'ipam_sub_id':ipam[0], 'ipam_mask':ipam[2], 'start':int(ipam[1]), 'end':int(ipam[1])+2**(32-int(ipam[2])), 'a_dom_id':a_dom, 'clear':clear})
  aWeb.log_msg("ajax_devices_discover: " + str(res))
  print "<DIV CLASS='z-table'>{}</DIV>".format(res)
 else:
  db.do("SELECT id, subnet, INET_NTOA(subnet) as subasc, mask, subnet_description, section_name FROM subnets ORDER BY subnet");
  subnets = db.get_all_rows()              
  db.do("SELECT id, name FROM domains")
  domains  = db.get_all_rows()      
  dom_name = aWeb.get_value('domain')  
  print "<DIV CLASS='z-table' style='resize: horizontal; margin-left:0px; z-index:101; width:350px; height:160px;'>"
  print "<FORM ID=device_discover_form>"
  print "<INPUT TYPE=HIDDEN NAME=op VALUE=json>"
  print "<TABLE style='width:100%'>"
  print "<TR><TH COLSPAN=2>Device Discovery</TH></TR>"
  print "<TR><TD>Domain:</TD><TD><SELECT CLASS='z-select' NAME=a_dom_id>"
  for d in domains:
   if not "in-addr.arpa" in d.get('name'):
    extra = "" if not dom_name == d.get('name') else "selected=selected"
    print "<OPTION VALUE={0} {2}>{1}</OPTION>".format(d.get('id'),d.get('name'),extra)
  print "</SELECT></TD></TR>"
  print "<TR><TD>Subnet:</TD><TD><SELECT CLASS='z-select' NAME=ipam_sub>"
  for s in subnets:
   print "<OPTION VALUE={0}_{1}_{3}>{2}/{3} ({4})</OPTION>".format(s.get('id'),s.get('subnet'),s.get('subasc'),s.get('mask'),s.get('subnet_description'))
  print "</SELECT></TD></TR>"
  print "<TR><TD>Clear</TD><TD><INPUT TYPE=checkbox NAME=clear VALUE=True></TD></TR>"
  print "</TABLE>"
  print "<A CLASS='z-btn z-op z-small-btn' DIV=div_navcont SPIN=true LNK=ajax.cgi?call=device_discover FRM=device_discover_form OP=post><IMG SRC='images/btn-start.png'></A>"
  print "</DIV>"
 db.close() 

#
# clear db
#
def clear_db(aWeb):
 db = GL.DB()
 db.connect()
 db.do("TRUNCATE TABLE devices")
 db.close()
 print "<DIV CLASS='z-table'>Cleared DB</DIV>"

