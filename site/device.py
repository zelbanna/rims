"""Module docstring.

Ajax Device calls module

"""
__author__= "Zacharias El Banna"
__version__ = "17.10.4"
__status__= "Production"

from sdcp.core.dbase import DB

########################################## Device Operations ##########################################

def main(aWeb):
 # target rack_id or vm and arg = value, i.e. select all devices where vm = 1 or where rackinfo.device_id exists and rack_id = 5 :-)
 target = aWeb.get_value('target')
 arg    = aWeb.get_value('arg')
 
 print "<DIV CLASS=z-navbar ID=div_navbar>"
 print "<A CLASS=z-op DIV=div_content_left URL='sdcp.cgi?call=device_list{0}'>Devices</A>".format('' if (not target or not arg) else "&target="+target+"&arg="+arg)
 print "<A CLASS=z-op DIV=div_content_left URL=sdcp.cgi?call=graph_list{0}>Graphing</A>".format('' if (not target or not arg) else "&target="+target+"&arg="+arg)
 print "<A CLASS=z-op DIV=div_content_left URL='sdcp.cgi?call=bookings_list'>Bookings</A>"
 if target == 'vm':
  print "<A CLASS='z-reload z-op' DIV=div_main_cont URL='sdcp.cgi?{}'></A>".format(aWeb.get_args())
 else:
  with DB() as db:
   if target == 'rack_id':
    res = db.do("SELECT racks.name, fk_pdu_1, fk_pdu_2, INET_NTOA(consoles.ip) as con_ip FROM racks LEFT JOIN consoles ON consoles.id = racks.fk_console WHERE racks.id= '{}'".format(arg))
    if res > 0:
     data = db.get_row()
     if data.get('con_ip'):
      print "<A CLASS=z-op DIV=div_content_left SPIN=true URL='sdcp.cgi?call=console_inventory&consolelist={0}'>Console</A>".format(data['con_ip'])
     if (data.get('fk_pdu_1') or data.get('fk_pdu_2')):
      res = db.do("SELECT INET_NTOA(ip) as ip, id FROM pdus WHERE (pdus.id = {0}) OR (pdus.id = {1})".format(data.get('fk_pdu_1','0'),data.get('fk_pdu_2','0')))
      rows = db.get_rows()
      pdus = ""
      for row in rows:
       pdus = pdus + "&pdulist=" + row.get('ip')
      print "<A CLASS=z-op DIV=div_content_left SPIN=true URL='sdcp.cgi?call=pdu_inventory{0}'>Pdu</A>".format(pdus)  
     print "<A CLASS=z-op DIV=div_content_right URL='sdcp.cgi?call=rack_inventory&rack={0}'>'{1}' info</A>".format(arg,data['name'])
   else:
    for type in ['pdu','console']:
     res = db.do("SELECT id, INET_NTOA(ip) as ip FROM {}s".format(type))
     if res > 0:
      tprows = db.get_rows()
      arglist = "call={}_list".format(type)
      for row in tprows:
       arglist = arglist + "&{}list=".format(type) + row['ip']
      print "<A CLASS=z-op DIV=div_content_left SPIN=true URL='sdcp.cgi?call={0}_inventory&{1}'>{2}</A>".format(type,arglist,type.title())
  print "<A CLASS='z-reload z-op' DIV=div_main_cont URL='sdcp.cgi?{}'></A>".format(aWeb.get_args())
  print "<A CLASS='z-right z-op' DIV=div_content_right MSG='Discover devices?' URL='sdcp.cgi?call=device_discover'>Device Discovery</A>"
  print "<A CLASS='z-right z-op' DIV=div_content_left URL='sdcp.cgi?call=pdu_list'>PDUs</A>"
  print "<A CLASS='z-right z-op' DIV=div_content_left URL='sdcp.cgi?call=console_list'>Consoles</A>"
  print "<A CLASS='z-right z-op' DIV=div_content_left URL='sdcp.cgi?call=rack_list'>Racks</A>"
  print "<SPAN CLASS='z-right z-navinfo'>Configuration:</SPAN>"
 print "</DIV>"
 print "<DIV CLASS=z-content       ID=div_content>"
 print "<DIV CLASS=z-content-left  ID=div_content_left></DIV>"
 print "<DIV CLASS=z-content-right ID=div_content_right>" 
 from sdcp.core.extras import get_include
 print get_include('README.devices.html')
 print "</DIV></DIV>"


#
#
#
def list(aWeb):
 target = aWeb.get_value('target')
 arg    = aWeb.get_value('arg')
 sort   = aWeb.get_value('sort','ip')
 print "<DIV CLASS=z-frame>"
 print "<DIV CLASS=title>Devices</DIV>"
 print "<A TITLE='Reload List' CLASS='z-btn z-small-btn z-op' DIV=div_content_left URL='sdcp.cgi?{}'><IMG SRC='images/btn-reboot.png'></A>".format(aWeb.get_args())
 print "<A TITLE='Add Device'  CLASS='z-btn z-small-btn z-op' DIV=div_content_right URL='sdcp.cgi?call=device_new&{}'><IMG SRC='images/btn-add.png'></A>".format(aWeb.get_args())
 print "<DIV CLASS=z-table>"
 print "<DIV CLASS=thead><DIV CLASS=th><A CLASS=z-op DIV=div_content_left URL='sdcp.cgi?{0}&sort=ip'>IP</A></DIV><DIV CLASS=th><A CLASS=z-op DIV=div_content_left URL='sdcp.cgi?{0}&sort=hostname'>FQDN</A></DIV><DIV CLASS=th>Model</DIV></DIV>".format(aWeb.get_args_except(['sort']))

 if not target or not arg:
  tune = ""
 elif target:
  if target == 'rack_id' and not arg == 'NULL':
   tune = "INNER JOIN rackinfo ON rackinfo.device_id = devices.id WHERE rackinfo.rack_id = '{}'".format(arg)
  elif target == 'vm' and not arg == 'NULL':
   tune = "WHERE vm = {}".format(arg)
  else:
   tune = "WHERE {0} is NULL".format(target)

 with DB() as db:
  sql = "SELECT devices.id, INET_NTOA(ip) as ipasc, hostname, domains.name as domain, model FROM devices JOIN domains ON domains.id = devices.a_dom_id {0} ORDER BY {1}".format(tune,sort)
  db.do(sql)
  rows = db.get_rows()
 
 print "<DIV CLASS=tbody>"
 print "<!-- {} -->".format(sql)
 for row in rows:
  print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op TITLE='Show device info for {0}' DIV=div_content_right URL='sdcp.cgi?call=device_info&id={3}'>{0}</A></DIV><DIV CLASS=td>{1}</DIV><DIV CLASS=td>{2}</DIV></DIV>".format(row['ipasc'], row['hostname']+"."+row['domain'], row['model'],row['id'])
 print "</DIV></DIV></DIV>"


################################ Gigantic Device info and Ops function #################################
#
#
#

def info(aWeb):
 if not aWeb.cookie.get('sdcp_id'):
  print "<SCRIPT>location.replace('index.cgi')</SCRIPT>"
  return
 import sdcp.core.genlib as GL
 from sdcp.devices.DevHandler import device_types, device_get_widgets
 id    = aWeb.get_value('id')
 op    = aWeb.get_value('op',"")
 opres = {}
 conip = None

 ###################### Data operations ###################
 if   op == 'lookup':
  from sdcp.rest.device import lookup_info
  opres['lookup'] = lookup_info({'id':id})

 elif op == 'update':
  from sdcp.rest.device import update_info
  d = aWeb.get_args2dict_except(['devices_ipam_gw','call','op'])
  if not d.get('devices_vm'):
   d['devices_vm'] = 0
  opres['update'] = update_info(d)

 db = DB()
 db.connect()

 if op == 'book':
  user_id = aWeb.cookie.get('sdcp_id')
  db.do("INSERT INTO bookings (device_id,user_id) VALUES('{}','{}')".format(id,user_id))
  db.commit()

 if op == 'unbook':
  db.do("DELETE FROM bookings WHERE device_id = '{}'".format(id))
  db.commit()

 xist = db.do("SELECT *, INET_NTOA(ip) as ipasc, subnets.subnet, d2.name AS a_name, d1.name AS ptr_name, bookings.user_id FROM devices LEFT JOIN bookings ON bookings.device_id = devices.id LEFT JOIN domains AS d1 ON devices.ptr_dom_id = d1.id LEFT JOIN domains AS d2 ON devices.a_dom_id = d2.id JOIN subnets ON devices.ipam_sub_id = subnets.id WHERE devices.id ='{}'".format(id))
 if xist > 0:
  device_data = db.get_row()
 else:
  print "Stale info! Reload device list"
  db.close()
  return

 ip   = device_data['ipasc']
 name = device_data['hostname']
 rack_xist = db.do("SELECT * FROM rackinfo WHERE device_id = {}".format(id))
 ri = db.get_row()

 #
 # If inserts are return as x_op, update local db using newly constructed dict
 # 
 if op == 'update' and not name == 'unknown':
  from sdcp.rest.device import update_info
  import sdcp.PackageContainer as PC
  from sdcp.core.rest import call as rest_call
  opres['ddi_sync'] = (device_data['ipam_id'] == '0')
  res   = rest_call(PC.dns['url'],"sdcp.rest.{}_update".format(PC.dns['type']), { 'ip':ip, 'name':name, 'a_dom_id': str(device_data['a_dom_id']), 'a_id':str(device_data['a_id']), 'ptr_id':str(device_data['ptr_id']) })
  newop = { 'id':id, 'devices_a_id':res['a_id'], 'devices_ptr_id':res['ptr_id'] }
  res   = rest_call(PC.ipam['url'],"sdcp.rest.{}_update".format(PC.ipam['type']),{ 'ip':ip, 'fqdn':name+"."+device_data['a_name'], 'a_dom_id': str(device_data['a_dom_id']), 'ipam_id':str(device_data['ipam_id']), 'ipam_sub_id':str(device_data['ipam_sub_id']),'ptr_id':str(device_data['ptr_id']) })
  newop['devices_ipam_id'] = res.get('ipam_id',0)
  update_info(newop)
  device_data['a_id']    = newop['devices_a_id']
  device_data['ptr_id']  = newop['devices_ptr_id']
  device_data['ipam_id'] = newop['devices_ipam_id']
  if ri:
   from sdcp.rest.pdu import update_device_pdus
   ri['hostname'] = name
   opres['pdu'] = update_device_pdus(ri)

 ########################## Data Tables ######################
 
 print "<DIV CLASS=z-frame style='position:relative; resize:horizontal; margin-left:0px; width:{}px; z-index:101; height:240px; float:left;'>".format(675 if rack_xist == 1 and not device_data['type'] == 'pdu' else 470)
 # print "<!-- {} -->".format(device_data)
 # print "<!-- {} -->".format(rack_xist)
 print "<FORM ID=info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(id)
 print "<INPUT TYPE=HIDDEN NAME=racked VALUE={}>".format(1 if ri else 0)
 print "<!-- Reachability Info -->"
 print "<DIV style='margin:3px; float:left; height:190px;'><DIV CLASS=title>Reachability Info</DIV>"
 print "<DIV CLASS=z-table style='width:210px;'><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Name:</DIV><DIV CLASS=td><INPUT NAME=devices_hostname TYPE=TEXT VALUE='{}'></DIV></DIV>".format(device_data['hostname'])
 print "<DIV CLASS=tr><DIV CLASS=td>Domain:</DIV><DIV CLASS=td>{}</DIV></DIV>".format(device_data['a_name'])
 print "<DIV CLASS=tr><DIV CLASS=td>SNMP:</DIV><DIV CLASS=td>{}</DIV></DIV>".format(device_data['snmp'])
 print "<DIV CLASS=tr><DIV CLASS=td>IP:</DIV><DIV CLASS=td>{}</DIV></DIV>".format(ip)
 print "<DIV CLASS=tr><DIV CLASS=td>Type:</DIV><DIV CLASS=td TITLE='Device type'><SELECT NAME=devices_type>"
 for tp in device_types():
  extra = " selected" if device_data['type'] == tp else ""
  print "<OPTION VALUE={0} {1}>{0}</OPTION>".format(str(tp),extra)
 print "</SELECT></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td>Model:</DIV><DIV CLASS=td style='max-width:150px;'>{}</DIV></DIV>".format(device_data['model'])
 if device_data['graph_update'] == 1:
  print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op TITLE='View graphs for {1}' DIV=div_content_right URL='/munin-cgi/munin-cgi-html/{0}/{1}/index.html#content'>Graphs</A>:</DIV><DIV CLASS=td>yes</DIV></DIV>".format(device_data['a_name'],device_data['hostname']+"."+ device_data['a_name'])
 else:
  print "<DIV CLASS=tr><DIV CLASS=td>Graphs:</DIV><DIV CLASS=td>no</DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td>VM:</DIV><DIV CLASS=td><INPUT NAME=devices_vm style='width:auto;' TYPE=checkbox VALUE=1 {0}></DIV></DIV>".format("checked=checked" if device_data['vm'] == 1 else "") 
 print "</DIV></DIV></DIV>"

 print "<!-- Additional info -->"
 print "<DIV style='margin:3px; float:left; height:190px;'><DIV CLASS=title>Additional Info</DIV>"
 print "<DIV CLASS=z-table style='width:227px;'><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Rack:</DIV><DIV CLASS=td><SELECT NAME=rackinfo_rack_id>"
 if device_data['vm']:
  print "<OPTION VALUE=NULL>Not used (VM)</OPTION>"
 else:
  db.do("SELECT * FROM racks")
  racks = db.get_rows()
  racks.append({ 'id':'NULL', 'name':'Not used', 'size':'48', 'fk_pdu_1':'0', 'fk_pdu_2':'0','fk_console':'0'})
  for rack in racks:
   extra = " selected" if ((rack_xist == 0 and rack['id'] == 'NULL') or (rack_xist == 1 and ri['rack_id'] == rack['id'])) else ""
   print "<OPTION VALUE={0} {1}>{2}</OPTION>".format(rack['id'],extra,rack['name'])
 print "</SELECT></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td>FQDN:</DIV><DIV CLASS=td style='{0}'>{1}</DIV></DIV>".format("border: solid 1px red;" if (name + "." + device_data['a_name'] != device_data['fqdn']) else "", device_data['fqdn'])
 print "<DIV CLASS=tr><DIV CLASS=td>DNS A ID:</DIV><DIV CLASS=td>{}</DIV></DIV>".format(device_data['a_id'])
 print "<DIV CLASS=tr><DIV CLASS=td>DNS PTR ID:</DIV><DIV CLASS=td>{}</DIV></DIV>".format(device_data['ptr_id'])
 print "<DIV CLASS=tr><DIV CLASS=td>IPAM ID:</DIV><DIV CLASS=td>{}</DIV></DIV>".format(device_data['ipam_id'])
 print "<DIV CLASS=tr><DIV CLASS=td>MAC:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=devices_mac VALUE={}></DIV></DIV>".format(GL.int2mac(device_data['mac']))
 print "<DIV CLASS=tr><DIV CLASS=td>Gateway:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=devices_ipam_gw VALUE={}></DIV></DIV>".format(GL.int2ip(device_data['subnet'] + 1))
 if not device_data['bookings.user_id']:
  print "<DIV CLASS=tr><DIV CLASS=td>Booked by:</DIV><DIV CLASS=td STYLE='background-color:#00cc66'>None</DIV></DIV>"
 else:
  db.do("SELECT NOW() < ADDTIME(time_start, '30 0:0:0.0') AS valid FROM bookings WHERE device_id ='{}'".format(id))
  valid = db.get_row()['valid']
  db.do("SELECT alias FROM users WHERE id = '{}'".format(device_data['bookings.user_id']))
  alias = db.get_row()['alias']
  print "<DIV CLASS=tr>"
  print "<DIV CLASS=td><A CLASS='z-op' DIV='div_content_left' URL='sdcp.cgi?call=bookings_list'>Booked by</A>:</DIV>"
  print "<DIV CLASS=td STYLE='background-color:{0}'><A CLASS=z-op DIV=div_content_right URL=sdcp.cgi?call=users_info&id={1}&op=view>{1}</A> {2}</DIV>".format("#df3620" if valid == 1 else "orange",alias,'' if valid else "(obsolete)")
  print "</DIV>"
 print "</DIV></DIV></DIV>"

 print "<!-- Rack Info if such exists -->"
 if rack_xist == 1 and not device_data['type'] == 'pdu':
  print "<DIV style='margin:3px; float:left; height:190px;'><DIV CLASS=title>Rack Info</DIV>"
  print "<DIV CLASS=z-table style='width:210px;'><DIV CLASS=tbody>"
  print "<DIV CLASS=tr><DIV CLASS=td>Rack Size:</DIV><DIV CLASS=td><INPUT NAME=rackinfo_rack_size TYPE=TEXT PLACEHOLDER='{}'></DIV></DIV>".format(ri['rack_size'])
  print "<DIV CLASS=tr><DIV CLASS=td>Rack Unit:</DIV><DIV CLASS=td TITLE='Top rack unit of device placement'><INPUT NAME=rackinfo_rack_unit TYPE=TEXT PLACEHOLDER='{}'></DIV></DIV>".format(ri['rack_unit'])
  if not device_data['type'] == 'console' and db.do("SELECT id, name, INET_NTOA(ip) as ipasc FROM consoles") > 0:
   consoles = db.get_rows()
   consoles.append({ 'id':'NULL', 'name':'No Console', 'ip':2130706433, 'ipasc':'127.0.0.1' })
   print "<DIV CLASS=tr><DIV CLASS=td>TS:</DIV><DIV CLASS=td><SELECT NAME=rackinfo_console_id>"
   for console in consoles:
    extra = ""
    if (ri['console_id'] == console['id']) or (not ri['console_id'] and console['id'] == 'NULL'):
     extra = " selected='selected'"
     conip = console['ipasc']
    print "<OPTION VALUE={0} {1}>{2}</OPTION>".format(console['id'],extra,console['name'])
   print "</SELECT></DIV></DIV>"
   print "<DIV CLASS=tr><DIV CLASS=td>TS Port:</DIV><DIV CLASS=td TITLE='Console port in rack TS'><INPUT NAME=rackinfo_console_port TYPE=TEXT PLACEHOLDER='{}'></DIV></DIV>".format(ri['console_port'])
  else:
   print "<DIV CLASS=tr><DIV CLASS=td>&nbsp;</DIV><DIV CLASS=td>&nbsp;</DIV></DIV>"
   print "<DIV CLASS=tr><DIV CLASS=td>&nbsp;</DIV><DIV CLASS=td>&nbsp;</DIV></DIV>"
  if not device_data['type'] == 'pdu' and db.do("SELECT *, INET_NTOA(ip) as ipasc FROM pdus") > 0:
   pdus = db.get_rows()
   pdus.append({ 'id':'NULL', 'name':'No', 'ip':'127.0.0.1', 'slots':0, '0_slot_id':0, '0_slot_name':'PDU' })
   for pem in ['pem0','pem1']:
    print "<DIV CLASS=tr><DIV CLASS=td>{0} PDU:</DIV><DIV CLASS=td><SELECT NAME=rackinfo_{1}_pdu_slot_id>".format(pem.upper(),pem)
    for pdu in pdus:
     for slotid in range(0,pdu['slots'] + 1):
      extra = " selected" if ((ri[pem+"_pdu_id"] == pdu['id']) and (ri[pem+"_pdu_slot"] == pdu[str(slotid)+"_slot_id"])) or (not ri[pem+"_pdu_id"] and  pdu['id'] == 'NULL')else ""
      print "<OPTION VALUE={0} {1}>{2}</OPTION>".format(str(pdu['id'])+"."+str(pdu[str(slotid)+"_slot_id"]), extra, pdu['name']+":"+pdu[str(slotid)+"_slot_name"])
    print "</SELECT></DIV></DIV>"
    print "<DIV CLASS=tr><DIV CLASS=td>{0} Unit:</DIV><DIV CLASS=td><INPUT NAME=rackinfo_{1}_pdu_unit TYPE=TEXT PLACEHOLDER='{2}'></DIV></DIV>".format(pem.upper(),pem,ri[pem + "_pdu_unit"])
  else:
   for index in range(0,4):
    print "<DIV CLASS=tr><DIV CLASS=td>&nbsp;</DIV><DIV CLASS=td>&nbsp;</DIV></DIV>"
  print "</DIV></DIV></DIV>"
 print "</FORM>"
 print "<!-- Controls -->"
 print "<DIV ID=device_control style='clear:left;'>"
 print "<A CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=sdcp.cgi?call=device_info&id={}><IMG SRC='images/btn-reboot.png'></A>".format(id)
 print "<A CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=sdcp.cgi?call=device_remove&id={} MSG='Are you sure you want to delete device?' TITLE='Remove device'><IMG SRC='images/btn-remove.png'></A>".format(id)
 print "<A CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=sdcp.cgi?call=device_info&op=lookup    FRM=info_form TITLE='Lookup and Detect Device information'><IMG SRC='images/btn-search.png'></A>"
 print "<A CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=sdcp.cgi?call=device_info&op=update    FRM=info_form TITLE='Save Device Information and Update DDI and PDU'><IMG SRC='images/btn-save.png'></A>"
 if device_data['bookings.user_id']:
  if int(aWeb.cookie.get('sdcp_id')) == device_data['bookings.user_id']:
   print "<A CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=sdcp.cgi?call=device_info&op=unbook&id={} MSG='Are you sure you want to drop booking?' TITLE='Unbook'><IMG SRC='images/btn-remove.png'></A>".format(id)
 else:
  print "<A CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=sdcp.cgi?call=device_info&op=book&id={} TITLE='Book device'><IMG SRC='images/btn-add.png'></A>".format(id)
 print "<A CLASS='z-btn z-op z-small-btn' DIV=div_device_data URL=sdcp.cgi?call=device_conf_gen                 FRM=info_form TITLE='Generate System Conf'><IMG SRC='images/btn-document.png'></A>"
 import sdcp.PackageContainer as PC
 print "<A CLASS='z-btn z-small-btn' HREF='ssh://{}@{}' TITLE='SSH'><IMG SRC='images/btn-term.png'></A>".format(PC.netconf['username'],ip)
 if rack_xist == 1 and (conip and not conip == '127.0.0.1' and ri['console_port'] and ri['console_port'] > 0):
  print "<A CLASS='z-btn z-small-btn' HREF='telnet://{}:{}' TITLE='Console'><IMG SRC='images/btn-term.png'></A>".format(conip,6000+ri['console_port'])
 if (device_data['type'] == 'pdu' or device_data['type'] == 'console') and db.do("SELECT id FROM {0}s WHERE ip = '{1}'".format(device_data['type'],device_data['ip'])) == 0:
  print "<A CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL='sdcp.cgi?call={0}_info&id=new&ip={1}&name={2}' style='float:right;' TITLE='Add {0}'><IMG SRC='images/btn-add.png'></A>".format(device_data['type'],ip,device_data['hostname']) 
 print "<SPAN ID=upd_results style='text-overflow:ellipsis; overflow:hidden; float:right; font-size:9px;'>{}</SPAN>".format(str(opres) if len(opres) > 0 else "")
 print "</DIV>"
 db.close()
 print "</DIV>"

 print "<!-- Function navbar and content -->"
 print "<DIV CLASS='z-navbar' style='top:246px;'>"
 functions = device_get_widgets(device_data['type'])
 if functions:
  if functions[0] == 'operated':
   if device_data['type'] == 'esxi':
    print "<A TARGET='main_cont' HREF='sdcp.cgi?call=esxi_main&id={}'>Manage</A></B></DIV>".format(id)
  else:
   for fun in functions:
    funname = " ".join(fun.split('_')[1:])
    print "<A CLASS=z-op DIV=div_device_data SPIN=true URL='sdcp.cgi?call=device_op_function&ip={0}&type={1}&op={2}'>{3}</A>".format(ip, device_data['type'], fun, funname.title())
 else:
  print "&nbsp;"
 print "</DIV>"
 print "<DIV CLASS='z-content' ID=div_device_data style='top:280px; overflow-x:hidden; overflow-y:auto; z-index:100'></DIV>"



####################################################### Functions #######################################################
#
# View operation data / widgets
#
def conf_gen(aWeb):
 import sdcp.core.genlib as GL
 id = aWeb.get_value('id','0')
 gw = aWeb.get_value('devices_ipam_gw')
 with DB() as db:
  db.do("SELECT INET_NTOA(ip) as ipasc, hostname,domains.name as domain, subnets.subnet, subnets.mask FROM devices LEFT JOIN domains ON domains.id = devices.a_dom_id JOIN subnets ON subnets.id = devices.ipam_sub_id WHERE devices.id = '{}'".format(id))
  row = db.get_row()
 type = aWeb.get_value('devices_type')
 print "<DIV CLASS=z-frame style='margin-left:0px; z-index:101; width:100%; float:left; bottom:0px;'>"
 from sdcp.devices.DevHandler import device_get_instance
 try:
  dev  = device_get_instance(row['ipasc'],type)
  dev.print_conf({'name':row['hostname'], 'domain':row['domain'], 'gateway':gw, 'subnet':GL.int2ip(int(row['subnet'])), 'mask':row['mask']})
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


def mac_sync(aWeb):
 import sdcp.core.genlib as GL
 from sdcp.tools.mac_tool import load_macs
 arps = load_macs()
 print "<DIV CLASS=z-frame style='overflow-x:auto; width:400px;'><DIV CLASS=z-table>"
 print "<DIV CLASS=thead><DIV CLASS=th>Id</DIV><DIV CLASS=th>IP</DIV><DIV CLASS=th>Hostname</DIV><DIV CLASS=th>MAC</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 with DB() as db:
  db.do("SELECT id, hostname, INET_NTOA(ip) as ipasc,mac FROM devices WHERE hostname <> 'unknown' ORDER BY ip")
  rows = db.get_rows()
  for row in rows:
   xist = arps.get(row['ipasc'],None)
   print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV></DIV>".format(row['id'],row['ipasc'],row['hostname'],xist)
   if xist:
    db.do("UPDATE devices SET mac = {} WHERE id = {}".format(GL.mac2int(xist),row['id']))
  db.commit()
 print "</DIV></DIV></DIV>"

##################################### Rest API #########################################

#
# new device:
#
def new(aWeb):
 ip     = aWeb.get_value('ip',"127.0.0.1")
 name   = aWeb.get_value('hostname','unknown')
 mac    = aWeb.get_value('mac',"00:00:00:00:00:00")
 op     = aWeb.get_value('op')
 sub_id = aWeb.get_value('ipam_sub_id')
 if op == 'new':
  import sdcp.PackageContainer as PC
  from sdcp.rest.device import new as rest_new

  a_dom_id,_,domain = aWeb.get_value('a_dom_id').partition('_')
  fqdn = "{}.{}".format(name,domain)
  args = { 'ip':ip, 'mac':mac, 'hostname':name, 'fqdn':fqdn, 'a_dom_id':a_dom_id, 'ipam_sub_id':sub_id, 'ipam_id':aWeb.get_value('ipam_id','0') }

  if args['ipam_id'] == '0':
   from sdcp.core.rest import call as rest_call
   ipam = rest_call(PC.ipam['url'],"sdcp.rest.{}_new".format(PC.ipam['type']),{'ip':ip, 'ipam_sub_id':sub_id ,'fqdn':fqdn } )
   args['ipam_id'] = str(ipam.get('id'))

  if aWeb.get_value('vm'):
   args['vm'] = 1
  else:
   args['target'] = aWeb.get_value('target')
   args['arg']    = aWeb.get_value('arg')
   args['vm'] = 0
  res  = rest_new(args)
  print "DB:{}".format(res)
  PC.log_msg("{} ({}): New device operation:[{}] -> [{}]".format(aWeb.cookie.get('sdcp_user'),aWeb.cookie.get('sdcp_id'),args,res))
 elif op == 'find':
  import sdcp.PackageContainer as PC
  from sdcp.core.rest import call as rest_call
  res = rest_call(PC.ipam['url'],"sdcp.rest.{}_find".format(PC.ipam['type']),{'ipam_sub_id':sub_id})
  print res['ip']
 else:
  domain = aWeb.get_value('domain')
  with DB() as db:
   db.do("SELECT id, subnet, INET_NTOA(subnet) as subasc, mask, subnet_description, section_name FROM subnets ORDER BY subnet")
   subnets = db.get_rows()
   db.do("SELECT id, name FROM domains")
   domains = db.get_rows()
  print "<DIV CLASS=z-frame style='resize: horizontal; margin-left:0px; z-index:101; width:430px; height:200px;'>"
  print "<DIV CLASS=title>Add Device</DIV>"
  print "<!-- {} -->".format(aWeb.get_args2dict_except())
  print "<DIV CLASS=z-table><DIV CLASS=tbody>"
  print "<FORM ID=device_new_form>"
  print "<INPUT TYPE=HIDDEN NAME=ipam_id VALUE={}>".format(aWeb.get_value('ipam_id',0))
  print "<DIV CLASS=tr><DIV CLASS=td>IP:</DIV><DIV CLASS=td><INPUT       NAME=ip       TYPE=TEXT VALUE={}></DIV></DIV>".format(ip)
  print "<DIV CLASS=tr><DIV CLASS=td>Hostname:</DIV><DIV CLASS=td><INPUT NAME=hostname TYPE=TEXT VALUE={}></DIV></DIV>".format(name)
  print "<DIV CLASS=tr><DIV CLASS=td>Domain:</DIV><DIV CLASS=td><SELECT  NAME=a_dom_id>"
  for d in domains:
   if not "in-addr.arpa" in d.get('name'):
    print "<OPTION VALUE={0}_{2} {1}>{2}</OPTION>".format(d['id'],"selected" if d['name'] == domain else "",d['name'])
  print "</SELECT></DIV></DIV>"
  print "<DIV CLASS=tr><DIV CLASS=td>Subnet:</DIV><DIV CLASS=td><SELECT NAME=ipam_sub_id>"
  for s in subnets:
   print "<OPTION VALUE={} {}>{}/{} ({})</OPTION>".format(s['id'],"selected" if str(s['id']) == sub_id else "", s.get('subasc'),s.get('mask'),s.get('subnet_description'))
  print "</SELECT></DIV></DIV>"
  print "<DIV CLASS=tr><DIV CLASS=td>MAC:</DIV><DIV CLASS=td><INPUT NAME=mac TYPE=TEXT PLACEHOLDER='{0}'></DIV></DIV>".format(mac)
  if aWeb.get_value('target') == 'rack_id':
   print "<INPUT TYPE=HIDDEN NAME=target VALUE={}>".format(aWeb.get_value('target'))
   print "<INPUT TYPE=HIDDEN NAME=arg VALUE={}>".format(aWeb.get_value('arg'))
  else:
   print "<DIV CLASS=tr><DIV CLASS=td>VM:</DIV><DIV  CLASS=td><INPUT NAME=vm  TYPE=CHECKBOX VALUE=1  {0} ></DIV></DIV>".format("checked" if aWeb.get_value('target') == 'vm' else '')
  print "</FORM>"
  print "</DIV></DIV>"
  print "<A CLASS='z-btn z-op z-small-btn' TITLE='Create'  DIV=device_new_span URL=sdcp.cgi?call=device_new&op=new  FRM=device_new_form><IMG SRC='images/btn-start.png'></A>"
  print "<A CLASS='z-btn z-op z-small-btn' TITLE='Find IP' DIV=device_new_span URL=sdcp.cgi?call=device_new&op=find FRM=device_new_form><IMG SRC='images/btn-search.png'></A>"
  print "<SPAN ID=device_new_span style='max-width:400px; font-size:9px; float:right'></SPAN>"
  print "</DIV>"

#
#
#
def remove(aWeb):
 from sdcp.rest.device import remove
 id      = aWeb.get_value('id')
 print "<DIV CLASS=z-frame>"
 res = remove({ 'id':id })
 print "Unit {0} deleted ({1})".format(id,str(res))
 print "</DIV>"

#
#
#
def dump_db(aWeb):
 from json import dumps
 from sdcp.rest.device import dump_db
 table = aWeb.get_value('table','devices')
 cols  = aWeb.get_value('columns','*')
 print "<PRE>{}</PRE>".format(dumps(dump_db({'table':table,'columns':cols}), indent=4, sort_keys=True))

#
# find devices operations
#
def discover(aWeb):
 op = aWeb.get_value('op')
 if op:
  from sdcp.rest.device import discover
  clear = aWeb.get_value('clear',False)
  a_dom = aWeb.get_value('a_dom_id')
  ipam  = aWeb.get_value('ipam_sub',"0_0_32").split('_')
  # id, subnet int, subnet mask
  res = discover({ 'ipam_sub_id':ipam[0], 'ipam_mask':ipam[2], 'start':int(ipam[1]), 'end':int(ipam[1])+2**(32-int(ipam[2])), 'a_dom_id':a_dom, 'clear':clear})
  print "<DIV CLASS=z-frame>{}</DIV>".format(res)
 else:
  with DB() as db:
   db.do("SELECT id, subnet, INET_NTOA(subnet) as subasc, mask, subnet_description, section_name FROM subnets ORDER BY subnet");
   subnets = db.get_rows()
   db.do("SELECT id, name FROM domains")
   domains  = db.get_rows()
  dom_name = aWeb.get_value('domain')
  print "<DIV CLASS=z-frame style='resize: horizontal; margin-left:0px; z-index:101; width:350px; height:160px;'>"
  print "<FORM ID=device_discover_form>"
  print "<INPUT TYPE=HIDDEN NAME=op VALUE=json>"
  print "<DIV CLASS=title>Device Discovery</DIV>"
  print "<DIV CLASS=z-table><DIV CLASS=tbody>"
  print "<DIV CLASS=tr><DIV CLASS=td>Domain:</DIV><DIV CLASS=td><SELECT NAME=a_dom_id>"
  for d in domains:
   if not "in-addr.arpa" in d.get('name'):
    extra = "" if not dom_name == d.get('name') else "selected=selected"
    print "<OPTION VALUE={0} {2}>{1}</OPTION>".format(d.get('id'),d.get('name'),extra)
  print "</SELECT></DIV></DIV>"
  print "<DIV CLASS=tr><DIV CLASS=td>Subnet:</DIV><DIV CLASS=td><SELECT NAME=ipam_sub>"
  for s in subnets:
   print "<OPTION VALUE={0}_{1}_{3}>{2}/{3} ({4})</OPTION>".format(s.get('id'),s.get('subnet'),s.get('subasc'),s.get('mask'),s.get('subnet_description'))
  print "</SELECT></DIV></DIV>"
  print "<DIV CLASS=tr><DIV CLASS=td>Clear</DIV><DIV CLASS=td><INPUT TYPE=checkbox NAME=clear VALUE=True></DIV></DIV>"
  print "</DIV></DIV>"
  print "<A CLASS='z-btn z-op z-small-btn' DIV=div_content_right SPIN=true URL=sdcp.cgi?call=device_discover FRM=device_discover_form><IMG SRC='images/btn-start.png'></A>"
  print "</DIV>"

#
# clear db
#
def clear_db(aWeb):
 with DB() as db:
  db.do("TRUNCATE TABLE devices")
 print "<DIV CLASS=z-frame>Cleared DB</DIV>"

