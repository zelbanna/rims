"""Module docstring.

Ajax Device calls module

"""
__author__= "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__= "Production"

from sdcp.core.dbase import DB

########################################## Device Operations ##########################################

def main(aWeb):
 # target rack_id or vm and arg = value, i.e. select all devices where vm = 1 or where rackinfo.device_id exists and rack_id = 5 :-)
 target = aWeb['target']
 arg    = aWeb['arg']

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
def list(aWeb):
 print "<DIV CLASS=z-frame>"
 print "<DIV CLASS=title>Devices</DIV>"
 print "<A TITLE='Reload List' CLASS='z-btn z-small-btn z-op' DIV=div_content_left URL='sdcp.cgi?{}'><IMG SRC='images/btn-reboot.png'></A>".format(aWeb.get_args())
 print "<A TITLE='Add Device'  CLASS='z-btn z-small-btn z-op' DIV=div_content_right URL='sdcp.cgi?call=device_new&{}'><IMG SRC='images/btn-add.png'></A>".format(aWeb.get_args())
 print "<DIV CLASS=z-table>"
 print "<DIV CLASS=thead><DIV CLASS=th><A CLASS=z-op DIV=div_content_left URL='sdcp.cgi?{0}&sort=ip'>IP</A></DIV><DIV CLASS=th><A CLASS=z-op DIV=div_content_left URL='sdcp.cgi?{0}&sort=hostname'>FQDN</A></DIV><DIV CLASS=th>Model</DIV></DIV>".format(aWeb.get_args_except(['sort']))
 args = {'sort':aWeb.get('sort','ip')}
 if aWeb['target']:
  args['rack'] = "vm" if aWeb['target'] == "vm" else aWeb['arg']
 from sdcp.rest.device import list as rest_list
 res = rest_list(args)
 print "<DIV CLASS=tbody>"
 for row in res['devices']:
  print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op TITLE='Show device info for {0}' DIV=div_content_right URL='sdcp.cgi?call=device_info&id={3}'>{0}</A></DIV><DIV CLASS=td>{1}</DIV><DIV CLASS=td>{2}</DIV></DIV>".format(row['ipasc'], row['hostname']+"."+row['domain'], row['model'],row['id'])
 print "</DIV></DIV></DIV>"

################################ Gigantic Device info and Ops function #################################
#
def info(aWeb):
 if not aWeb.cookie.get('sdcp_id'):
  print "<SCRIPT>location.replace('index.cgi')</SCRIPT>"
  return
 from sdcp.core import genlib as GL
 id    = aWeb['id']
 op    = aWeb.get('op',"")
 opres = {}

 ###################### Update ###################
 if op == 'lookup':
  from sdcp.rest.device import detect as rest_detect
  opres['lookup'] = rest_detect({'ip':aWeb['ip'],'update':True,'id':id})

 elif op == 'update':
  from sdcp.rest.device import update as rest_update
  from sdcp import PackageContainer as PC
  from sdcp.core.rest import call as rest_call
  d = aWeb.get_args2dict_except(['devices_ipam_gw','call','op'])
  if not d.get('devices_vm'):
   d['devices_vm'] = 0
  if not d.get('devices_comment'):
   d['devices_comment'] = 'NULL'
  if d['devices_hostname'] != 'unknown':
   with DB() as db:
    db.do("SELECT hostname, INET_NTOA(ip) as ip, a_id, ptr_id, ipam_id, a_dom_id, ptr_dom_id, ipam_sub_id, domains.name AS domain FROM devices LEFT JOIN domains ON devices.a_dom_id = domains.id WHERE devices.id = {}".format(id))
    ddi = db.get_row()
   fqdn = d['devices_hostname'] + "." + ddi['domain']
   opres['a'] = rest_call(PC.dns['url'], "sdcp.rest.{}_update".format(PC.dns['type']),   { 'type':'a',   'id':ddi['a_id'],   'domain_id':ddi['a_dom_id'],   'ip':ddi['ip'], 'fqdn':fqdn })
   if opres['a']['id'] != ddi['a_id']:
    d['devices_a_id'] = opres['a']['id']
   opres['ptr'] = rest_call(PC.dns['url'], "sdcp.rest.{}_update".format(PC.dns['type']), { 'type':'ptr', 'id':ddi['ptr_id'], 'domain_id':ddi['ptr_dom_id'], 'ip':ddi['ip'], 'fqdn':fqdn })
   if opres['ptr']['id'] != ddi['ptr_id']:
    d['devices_ptr_id'] = opres['ptr']['id']
   opres['ipam'] = rest_call(PC.ipam['url'],"sdcp.rest.{}_{}".format(PC.ipam['type'],"update" if ddi['ipam_id'] > 0 else "new"),{ 'id':ddi['ipam_id'], 'ipam_sub_id':ddi['ipam_sub_id'], 'ip':ddi['ip'], 'fqdn':fqdn, 'ptr_id':opres['ptr']['id'] } )
   if opres['ipam']['id'] != ddi['ipam_id']:
    d['devices_ipam_id'] = opres['ipam']['id']
   opres['update'] = rest_update(d)

 elif "book" in op:
  from sdcp.rest.booking import booking
  booking({'device_id':id, 'user_id':aWeb.cookie['sdcp_id'], 'op':op})

 from sdcp.rest.device import info as rest_info
 from sdcp.rest.tools  import infra as rest_infra
 dev   = rest_info({'id':id})
 if dev['exist'] == 0:
  print "Stale info! Reload device list"
  return
 if op == 'update' and dev['racked'] and (dev['rack']['pem0_pdu_id'] or dev['rack']['pem1_pdu_id']):
  from sdcp.rest.pdu import update_device_pdus
  opres['pdu'] = update_device_pdus(dev['rack'])
 infra = rest_infra(None)

 ########################## Data Tables ######################

 width= 675 if dev['racked'] == 1 and not dev['type'] == 'pdu' else 470

 print "<DIV CLASS=z-frame style='position:relative; resize:horizontal; margin-left:0px; width:{}px; z-index:101; height:255px; float:left;'>".format(width)
 print "<!-- DEV:{} -->".format(dev['info'])
 print "<!-- OP:{} -->".format(opres)
 print "<FORM ID=info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(id)
 print "<INPUT TYPE=HIDDEN NAME=racked VALUE={}>".format(dev['racked'])
 print "<!-- Reachability Info -->"
 print "<DIV style='margin:3px; float:left; height:185px;'><DIV CLASS=title>Reachability Info</DIV>"
 print "<DIV CLASS=z-table style='width:210px;'><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Name:</DIV><DIV CLASS=td><INPUT NAME=devices_hostname TYPE=TEXT VALUE='{}'></DIV></DIV>".format(dev['info']['hostname'])
 print "<DIV CLASS=tr><DIV CLASS=td>Domain:</DIV><DIV CLASS=td>{}</DIV></DIV>".format(dev['info']['a_name'])
 print "<DIV CLASS=tr><DIV CLASS=td>SNMP:</DIV><DIV CLASS=td>{}</DIV></DIV>".format(dev['info']['snmp'])
 print "<DIV CLASS=tr><DIV CLASS=td>IP:</DIV><DIV CLASS=td>{}</DIV></DIV>".format(dev['ip'])
 print "<DIV CLASS=tr><DIV CLASS=td>Type:</DIV><DIV CLASS=td TITLE='Device type'><SELECT NAME=devices_type_id>"
 for type in infra['types']:
  extra = " selected" if dev['info']['type_id'] == type['id'] or (not dev['info']['type_id'] and type['name'] == 'generic') else ""
  print "<OPTION VALUE={0} {1}>{2}</OPTION>".format(type['id'],extra,type['name'])
 print "</SELECT></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td>Model:</DIV><DIV CLASS=td style='max-width:150px;'>{}</DIV></DIV>".format(dev['info']['model'])
 if dev['info']['graph_update'] == 1:
  print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op TITLE='View graphs for {1}' DIV=div_content_right URL='/munin-cgi/munin-cgi-html/{0}/{1}/index.html#content'>Graphs</A>:</DIV><DIV CLASS=td>yes</DIV></DIV>".format(dev['info']['a_name'],dev['info']['hostname']+"."+ dev['info']['a_name'])
 else:
  print "<DIV CLASS=tr><DIV CLASS=td>Graphs:</DIV><DIV CLASS=td>no</DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td>VM:</DIV><DIV CLASS=td><INPUT NAME=devices_vm style='width:auto;' TYPE=checkbox VALUE=1 {0}></DIV></DIV>".format("checked=checked" if dev['info']['vm'] == 1 else "") 
 print "</DIV></DIV></DIV>"

 print "<!-- Additional info -->"
 print "<DIV style='margin:3px; float:left; height:185px;'><DIV CLASS=title>Additional Info</DIV>"
 print "<DIV CLASS=z-table style='width:227px;'><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Rack:</DIV><DIV CLASS=td>"
 if dev['info']['vm']:
  print "Not used <INPUT TYPE=hidden NAME=rackinfo_rack_id VALUE=NULL>"
 else:
  print "<SELECT NAME=rackinfo_rack_id>"
  for rack in infra['racks']:
   extra = " selected" if ((dev['racked'] == 0 and rack['id'] == 'NULL') or (dev['racked'] == 1 and dev['rack']['rack_id'] == rack['id'])) else ""
   print "<OPTION VALUE={0} {1}>{2}</OPTION>".format(rack['id'],extra,rack['name'])
  print "</SELECT>"
 print "</DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td>Lookup:</DIV><DIV CLASS=td style='{0}'>{1}</DIV></DIV>".format("border: solid 1px red;" if (dev['fqdn'] != dev['info']['fqdn']) else "", dev['info']['fqdn'])
 print "<DIV CLASS=tr><DIV CLASS=td>DNS A ID:</DIV><DIV CLASS=td>{}</DIV></DIV>".format(dev['info']['a_id'])
 print "<DIV CLASS=tr><DIV CLASS=td>DNS PTR ID:</DIV><DIV CLASS=td>{}</DIV></DIV>".format(dev['info']['ptr_id'])
 print "<DIV CLASS=tr><DIV CLASS=td>IPAM ID:</DIV><DIV CLASS=td>{}</DIV></DIV>".format(dev['info']['ipam_id'])
 print "<DIV CLASS=tr><DIV CLASS=td>MAC:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=devices_mac VALUE={}></DIV></DIV>".format(dev['mac'])
 print "<DIV CLASS=tr><DIV CLASS=td>Gateway:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=devices_ipam_gw VALUE={}></DIV></DIV>".format(GL.int2ip(dev['info']['subnet'] + 1))
 print "<DIV CLASS=tr><DIV CLASS=td>Booked by:</DIV>"
 if int(dev['booked']) == 0:
  print "<DIV CLASS=td STYLE='background-color:#00cc66'>None</DIV></DIV>"
 else:
  print "<DIV CLASS=td STYLE='background-color:{0}'><A CLASS=z-op DIV=div_content_right URL=sdcp.cgi?call=users_info&id={1}&op=view>{2}</A> {3}</DIV>".format("#df3620" if dev['booking']['valid'] == 1 else "orange",dev['booking']['user_id'],dev['booking']['alias'],'' if dev['booking']['valid'] else "(obsolete)")
  print "</DIV>"
 print "</DIV></DIV></DIV>"

 print "<!-- Rack Info if such exists -->"
 if dev['racked'] == 1 and not dev['type'] == 'pdu':
  print "<DIV style='margin:3px; float:left; height:185px;'><DIV CLASS=title>Rack Info</DIV>"
  print "<DIV CLASS=z-table style='width:210px;'><DIV CLASS=tbody>"
  print "<DIV CLASS=tr><DIV CLASS=td>Rack Size:</DIV><DIV CLASS=td><INPUT NAME=rackinfo_rack_size TYPE=TEXT PLACEHOLDER='{}'></DIV></DIV>".format(dev['rack']['rack_size'])
  print "<DIV CLASS=tr><DIV CLASS=td>Rack Unit:</DIV><DIV CLASS=td TITLE='Top rack unit of device placement'><INPUT NAME=rackinfo_rack_unit TYPE=TEXT PLACEHOLDER='{}'></DIV></DIV>".format(dev['rack']['rack_unit'])
  if not dev['type'] == 'console' and infra['consolexist'] > 0:
   print "<DIV CLASS=tr><DIV CLASS=td>TS:</DIV><DIV CLASS=td><SELECT NAME=rackinfo_console_id>"
   for console in infra['consoles']:
    extra = " selected='selected'" if (dev['rack']['console_id'] == console['id']) or (not dev['rack']['console_id'] and console['id'] == 'NULL') else ""
    print "<OPTION VALUE={0} {1}>{2}</OPTION>".format(console['id'],extra,console['name'])
   print "</SELECT></DIV></DIV>"
   print "<DIV CLASS=tr><DIV CLASS=td>TS Port:</DIV><DIV CLASS=td TITLE='Console port in rack TS'><INPUT NAME=rackinfo_console_port TYPE=TEXT PLACEHOLDER='{}'></DIV></DIV>".format(dev['rack']['console_port'])
  else:
   print "<DIV CLASS=tr><DIV CLASS=td>&nbsp;</DIV><DIV CLASS=td>&nbsp;</DIV></DIV>"
   print "<DIV CLASS=tr><DIV CLASS=td>&nbsp;</DIV><DIV CLASS=td>&nbsp;</DIV></DIV>"

  if not dev['type'] == 'pdu' and infra['pduxist'] > 0:
   for pem in ['pem0','pem1']:
    print "<DIV CLASS=tr><DIV CLASS=td>{0} PDU:</DIV><DIV CLASS=td><SELECT NAME=rackinfo_{1}_pdu_slot_id>".format(pem.upper(),pem)
    for pdu in infra['pdus']:
     for slotid in range(0,pdu['slots'] + 1):
      extra = " selected" if ((dev['rack'][pem+"_pdu_id"] == pdu['id']) and (dev['rack'][pem+"_pdu_slot"] == pdu[str(slotid)+"_slot_id"])) or (not dev['rack'][pem+"_pdu_id"] and  pdu['id'] == 'NULL')else ""
      print "<OPTION VALUE={0} {1}>{2}</OPTION>".format(str(pdu['id'])+"."+str(pdu[str(slotid)+"_slot_id"]), extra, pdu['name']+":"+pdu[str(slotid)+"_slot_name"])
    print "</SELECT></DIV></DIV>"
    print "<DIV CLASS=tr><DIV CLASS=td>{0} Unit:</DIV><DIV CLASS=td><INPUT NAME=rackinfo_{1}_pdu_unit TYPE=TEXT PLACEHOLDER='{2}'></DIV></DIV>".format(pem.upper(),pem,dev['rack'][pem + "_pdu_unit"])
  else:
   for index in range(0,4):
    print "<DIV CLASS=tr><DIV CLASS=td>&nbsp;</DIV><DIV CLASS=td>&nbsp;</DIV></DIV>"
  print "</DIV></DIV></DIV>"
 print "<DIV STYLE='display:block; font-size:11px; clear:both; margin-bottom:3px; width:99%'><SPAN>Comments:</SPAN><INPUT STYLE='width:{}px; border:none; background-color:white; overflow-x:auto; font-size:11px;' TYPE=TEXT NAME=devices_comment VALUE='{}'></DIV>".format(width-90,"" if not dev['info']['comment'] else dev['info']['comment'])
 print "</FORM>"

 print "<!-- Controls -->"
 print "<DIV ID=device_control style='clear:left;'>"
 print "<A CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=sdcp.cgi?call=device_info&id={}><IMG SRC='images/btn-reboot.png'></A>".format(id)
 print "<A CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=sdcp.cgi?call=device_remove&id={} MSG='Are you sure you want to delete device?' TITLE='Remove device'><IMG SRC='images/btn-remove.png'></A>".format(id)
 print "<A CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=sdcp.cgi?call=device_info&op=lookup&id={}&ip={} TITLE='Lookup and Detect Device information'><IMG SRC='images/btn-search.png'></A>".format(id,dev['info']['ipasc'])
 print "<A CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=sdcp.cgi?call=device_info&op=update    FRM=info_form TITLE='Save Device Information and Update DDI and PDU'><IMG SRC='images/btn-save.png'></A>"
 if dev['booked']:
  if int(aWeb.cookie.get('sdcp_id')) == dev['booking']['user_id']:
   print "<A CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=sdcp.cgi?call=device_info&op=debook&id={} MSG='Are you sure you want to drop booking?' TITLE='Unbook'><IMG SRC='images/btn-remove.png'></A>".format(id)
 else:
  print "<A CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=sdcp.cgi?call=device_info&op=book&id={} TITLE='Book device'><IMG SRC='images/btn-add.png'></A>".format(id)
 print "<A CLASS='z-btn z-op z-small-btn' DIV=div_dev_data URL=sdcp.cgi?call=device_conf_gen&type_name={}  FRM=info_form TITLE='Generate System Conf'><IMG SRC='images/btn-document.png'></A>".format(dev['info']['type_name'])
 from sdcp import PackageContainer as PC
 print "<A CLASS='z-btn z-small-btn' HREF='ssh://{}@{}' TITLE='SSH'><IMG SRC='images/btn-term.png'></A>".format(PC.netconf['username'],dev['ip'])
 if dev['racked'] == 1 and (dev['rack']['console_ip'] and dev['rack'].get('console_port',0) > 0):
  print "<A CLASS='z-btn z-small-btn' HREF='telnet://{}:{}' TITLE='Console'><IMG SRC='images/btn-term.png'></A>".format(dev['rack']['console_ip'],6000+dev['rack']['console_port'])

 res = ""
 for key,value in opres.iteritems():
  if value.get('res','NOT_FOUND') != 'OK':
   res += "{}({})".format(key,value)
 print "<SPAN ID=upd_results style='text-overflow:ellipsis; overflow:hidden; float:right; font-size:9px;'>{}</SPAN>".format(res)
 print "</DIV>"
 print "</DIV>"

 print "<!-- Function navbar and content -->"
 print "<DIV CLASS='z-navbar' style='top:260px;'>"
 try:
  from importlib import import_module
  module = import_module("sdcp.devices.{}".format(dev['info']['type_name']))
  Device = getattr(module,'Device',None)
  functions = Device.get_widgets() if Device else []
  if functions:
   if functions[0] == 'operated':
    if dev['info']['type_name'] == 'esxi':
     print "<A CLASS=z-op DIV=div_main_cont URL='sdcp.cgi?call=esxi_info&id={}'>Manage</A></B></DIV>".format(id)
   else:
    for fun in functions:
     funname = " ".join(fun.split('_')[1:])
     print "<A CLASS=z-op DIV=div_dev_data SPIN=true URL='sdcp.cgi?call=device_op_function&ip={0}&type={1}&op={2}'>{3}</A>".format(dev['ip'], dev['info']['type_name'], fun, funname.title())
 except:
  print "&nbsp;"
 print "</DIV>"
 print "<DIV CLASS='z-content' ID=div_dev_data style='top:294px; overflow-x:hidden; overflow-y:auto; z-index:100'></DIV>"


####################################################### Functions #######################################################
#
# View operation data / widgets
#

def conf_gen(aWeb):
 from importlib import import_module
 id = aWeb.get('id','0')
 gw = aWeb['devices_ipam_gw']
 type = aWeb['type_name']
 print "<DIV CLASS=z-frame style='margin-left:0px; z-index:101; width:100%; float:left; bottom:0px;'>"
 with DB() as db:
  db.do("SELECT INET_NTOA(ip) AS ipasc, hostname,domains.name as domain, INET_NTOA(subnets.subnet) AS subnet, subnets.mask FROM devices LEFT JOIN domains ON domains.id = devices.a_dom_id JOIN subnets ON subnets.id = devices.ipam_sub_id WHERE devices.id = '{}'".format(id))
  row = db.get_row()
 try:
  module = import_module("sdcp.devices.{}".format(type))
  dev = getattr(module,'Device',lambda x: None)(row['ipasc'])
  dev.print_conf({'name':row['hostname'], 'domain':row['domain'], 'gateway':gw, 'subnet':row['subnet'], 'mask':row['mask']})
 except Exception as err:
  print "No instance config specification for type:[{}]".format(type)
 print "</DIV>"

#
#
#
def op_function(aWeb):
 from sdcp.devices.devhandler import device_get_instance
 from sdcp.core import extras as EXT
 from importlib import import_module
 print "<DIV CLASS=z-frame>"
 try:
  module = import_module("sdcp.devices.{}".format(aWeb['type']))
  dev = getattr(module,'Device',lambda x: None)(aWeb['ip'])
  with dev:
   EXT.dict2table(getattr(dev,aWeb['op'],None)())
 except Exception as err:
  print "<B>Error in devdata: {}</B>".format(str(err))
 print "</DIV>"

#
#
#
def mac_sync(aWeb):
 from sdcp.core import genlib as GL
 print "<DIV CLASS=z-frame style='overflow-x:auto; width:400px;'><DIV CLASS=z-table>"
 print "<DIV CLASS=thead><DIV CLASS=th>Id</DIV><DIV CLASS=th>IP</DIV><DIV CLASS=th>Hostname</DIV><DIV CLASS=th>MAC</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 try:
  arps = {}
  with open('/proc/net/arp') as f:
   _ = f.readline()
   for data in f:
    ( ip, _, _, mac, _, _ ) = data.split()
    if not mac == '00:00:00:00:00:00':
     arps[ip] = mac
  with DB() as db:
   db.do("SELECT id, hostname, INET_NTOA(ip) as ipasc,mac FROM devices WHERE hostname <> 'unknown' ORDER BY ip")
   rows = db.get_rows()
   for row in rows:
    xist = arps.get(row['ipasc'],None)
    print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV></DIV>".format(row['id'],row['ipasc'],row['hostname'],xist)
    if xist:
     db.do("UPDATE devices SET mac = {} WHERE id = {}".format(GL.mac2int(xist),row['id']))
 except:
  pass
 print "</DIV></DIV></DIV>"

#
# new device:
#
def new(aWeb):
 ip     = aWeb.get('ip',"127.0.0.1")
 name   = aWeb.get('hostname','unknown')
 mac    = aWeb.get('mac',"00:00:00:00:00:00")
 op     = aWeb['op']
 sub_id = aWeb['ipam_sub_id']
 if op == 'new':
  from sdcp import PackageContainer as PC
  from sdcp.rest.device import new as rest_new

  a_dom_id,_,domain = aWeb['a_dom_id'].partition('_')
  fqdn = "{}.{}".format(name,domain)
  args = { 'ip':ip, 'mac':mac, 'hostname':name, 'fqdn':fqdn, 'a_dom_id':a_dom_id, 'ipam_sub_id':sub_id, 'ipam_id':aWeb.get('ipam_id','0') }

  if args['ipam_id'] == '0':
   from sdcp.core.rest import call as rest_call
   ipam = rest_call(PC.ipam['url'],"sdcp.rest.{}_new".format(PC.ipam['type']),{'ip':ip, 'ipam_sub_id':sub_id ,'fqdn':fqdn } )
   args['ipam_id'] = str(ipam.get('id'))

  if aWeb['vm']:
   args['vm'] = 1
  else:
   args['target'] = aWeb['target']
   args['arg']    = aWeb['arg']
   args['vm'] = 0
  res  = rest_new(args)
  print "DB:{}".format(res)
  aWeb.log("{} - 'new device' operation:[{}] -> [{}]".format(aWeb.cookie.get('sdcp_user'),args,res))
 elif op == 'find':
  from sdcp import PackageContainer as PC
  from sdcp.core.rest import call as rest_call
  from sdcp.rest.device import find_ip as rest_find_ip
  res  = rest_find_ip({'ipam_sub_id':sub_id})
  ipam_free = rest_call(PC.ipam['url'],"sdcp.rest.{}_free".format(PC.ipam['type']),{'ipam_sub_id':sub_id,'ip':res['ip']})
  ipam_find = rest_call(PC.ipam['url'],"sdcp.rest.{}_find".format(PC.ipam['type']),{'ipam_sub_id':sub_id})
  print "Sync:{} IP:{}".format(ipam_free['res'],ipam_find['ip'])
 else:
  domain = aWeb['domain']
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
  print "<INPUT TYPE=HIDDEN NAME=ipam_id VALUE={}>".format(aWeb.get('ipam_id',0))
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
  if aWeb['target'] == 'rack_id':
   print "<INPUT TYPE=HIDDEN NAME=target VALUE={}>".format(aWeb['target'])
   print "<INPUT TYPE=HIDDEN NAME=arg VALUE={}>".format(aWeb['arg'])
  else:
   print "<DIV CLASS=tr><DIV CLASS=td>VM:</DIV><DIV  CLASS=td><INPUT NAME=vm  TYPE=CHECKBOX VALUE=1  {0} ></DIV></DIV>".format("checked" if aWeb['target'] == 'vm' else '')
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
 id  = aWeb['id']
 ret = remove({ 'id':id })
 if ret['res'] == 'OK':
  from sdcp.core.rest import call as rest_call
  from sdcp import PackageContainer as PC
  dns = rest_call(PC.dns['url'],"sdcp.rest.{}_remove".format(PC.dns['type']),  ret)
  ipam= rest_call(PC.ipam['url'],"sdcp.rest.{}_remove".format(PC.ipam['type']), ret)
 print "<DIV CLASS=z-frame>"
 print "Unit {} deleted (DB:{},DNS:{},IPAM:{})".format(id,ret,dns,ipam)
 print "</DIV>"

#
# find devices operations
#
def discover(aWeb):
 op = aWeb['op']
 if op:
  from sdcp.rest.device import discover
  clear = aWeb.get('clear',False)
  a_dom = aWeb['a_dom_id']
  ipam  = aWeb.get('ipam_sub',"0_0_32").split('_')
  # id, subnet int, subnet mask
  res = discover({ 'ipam_sub_id':ipam[0], 'ipam_mask':ipam[2], 'start':int(ipam[1]), 'end':int(ipam[1]) + 2**(32-int(ipam[2])) - 1, 'a_dom_id':a_dom, 'clear':clear})
  print "<DIV CLASS=z-frame>{}</DIV>".format(res)
 else:
  with DB() as db:
   db.do("SELECT id, subnet, INET_NTOA(subnet) as subasc, mask, subnet_description, section_name FROM subnets ORDER BY subnet");
   subnets = db.get_rows()
   db.do("SELECT id, name FROM domains")
   domains  = db.get_rows()
  dom_name = aWeb['domain']
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
