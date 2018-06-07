"""Module docstring.

HTML5 Ajax Device module

"""
__author__= "Zacharias El Banna"
__version__ = "18.05.31GA"
__status__ = "Production"
__icon__ = 'images/icon-network.png'
__type__ = 'menuitem'

########################################## Device Operations ##########################################
#
#
def main(aWeb):
 target = aWeb['target']
 arg    = aWeb['arg']
 print "<NAV><UL>"
 print "<LI CLASS='dropdown'><A>Devices</A><DIV CLASS='dropdown-content'>"
 print "<A CLASS=z-op DIV=div_content_left URL='sdcp.cgi?device_list{0}'>List</A>".format('' if (not target or not arg) else "&target="+target+"&arg="+arg)
 print "<A CLASS=z-op DIV=div_content_left URL='sdcp.cgi?device_search'>Search</A>"
 print "</DIV></LI>"
 print "<LI><A CLASS=z-op DIV=div_content_left URL='sdcp.cgi?visualize_list'>Maps</A></LI>"
 if target == 'vm':
  print "<LI><A CLASS='z-op reload' DIV=main URL='sdcp.cgi?device_main&{}'></A></LI>".format(aWeb.get_args())
 else:
  data = aWeb.rest_call("rack_inventory",{'id':arg} if target == 'rack_id' else None)
  for type in ['pdu','console']:
   if len(data[type]) > 0:
    print "<LI CLASS='dropdown'><A>%s</A><DIV CLASS='dropdown-content'>"%(type.title())
    for row in data[type]:
     print "<A CLASS=z-op DIV=div_content_left SPIN=true URL='sdcp.cgi?%s_inventory&ip=%s'>%s</A>"%(row['type'],row['ipasc'],row['hostname'])
    print "</DIV></LI>"
  if data.get('name'):
   print "<LI><A CLASS='z-op' DIV=div_content_right  URL='sdcp.cgi?rack_inventory&rack=%s'>'%s' info</A></LI>"%(arg,data['name'])
  print "<LI><A CLASS='z-op reload' DIV=main URL='sdcp.cgi?device_main&{}'></A></LI>".format(aWeb.get_args())
  print "<LI CLASS=right><A CLASS=z-op DIV=div_content_left URL='sdcp.cgi?ipam_network_list'>IPAM</A></LI>"
  print "<LI CLASS='right dropdown'><A>DNS</A><DIV CLASS='dropdown-content'>"
  print "<A CLASS=z-op DIV=div_content_left URL='sdcp.cgi?dns_server_list'>Servers</A>"
  print "<A CLASS=z-op DIV=div_content_left URL='sdcp.cgi?dns_domain_list'>Domains</A>"
  print "</DIV></LI>"
  print "<LI CLASS='right dropdown'><A>Rackinfo</A><DIV CLASS='dropdown-content'>"
  print "<A CLASS=z-op DIV=div_content_left URL='sdcp.cgi?rack_list_infra&type=pdu'>PDUs</A>"
  print "<A CLASS=z-op DIV=div_content_left URL='sdcp.cgi?rack_list_infra&type=console'>Consoles</A>"
  print "<A CLASS=z-op DIV=div_content_left URL='sdcp.cgi?rack_list'>Racks</A>"
  print "</DIV></LI>"
 print "<LI CLASS='right'><A CLASS=z-op DIV=div_content URL='sdcp.cgi?bookings_list'>Bookings</A></LI>"
 print "</UL></NAV>"
 print "<SECTION CLASS=content       ID=div_content>"
 print "<SECTION CLASS=content-left  ID=div_content_left></SECTION>"
 print "<SECTION CLASS=content-right ID=div_content_right></SECTION>"
 print "</SECTION>"
 print "<SCRIPT>include_html('div_content_right','README.devices.html');</SCRIPT>"

#
#
def list(aWeb):
 args = aWeb.get_args2dict()
 args['sort'] = aWeb.get('sort','ip')
 if aWeb['target']:
  args['rack'] = "vm" if aWeb['target'] == "vm" else aWeb['arg']
 res = aWeb.rest_call("device_list",args)
 print "<ARTICLE><P>Device List</P><DIV CLASS='controls'>"
 print aWeb.button('reload',  DIV='div_content_left',  TITLE='Reload', URL='sdcp.cgi?device_list&{}'.format(aWeb.get_args()))
 print aWeb.button('add',     DIV='div_content_right', TITLE='Add device', URL='sdcp.cgi?device_new&{}'.format(aWeb.get_args()))
 print aWeb.button('network', DIV='div_content_right', TITLE='Discover', URL='sdcp.cgi?device_discover')
 print aWeb.button('web',     DIV='div_content_right', TITLE='Show webpages', URL='sdcp.cgi?device_webpages')
 print "</DIV>"
 print "<DIV CLASS=table>"
 print "<DIV CLASS=thead><DIV CLASS=th><A CLASS=z-op DIV=div_content_left URL='sdcp.cgi?device_list&sort=ip&{0}'>IP&darr;</A></DIV><DIV CLASS=th><A CLASS=z-op DIV=div_content_left URL='sdcp.cgi?device_list&sort=hostname&{0}'>FQDN&darr;</A></DIV><DIV CLASS=th>Model</DIV></DIV>".format(aWeb.get_args(['sort']))
 print "<DIV CLASS=tbody>"
 for row in res['data']:
  print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL='sdcp.cgi?device_info&id=%i' TITLE='%s'>%s</A></DIV><DIV CLASS=td STYLE='max-width:180px; overflow-x:hidden'>%s</DIV><DIV CLASS=td>%s</DIV></DIV>"%(row['id'],row['id'],row['ipasc'], row['fqdn'], row['model'])
 print "</DIV></DIV></ARTICLE>"

#
#
def search(aWeb):
 print "<ARTICLE><P>Device Search</P>"
 print "<FORM ID='device_search'>"
 print "<INPUT TYPE=HIDDEN NAME=sort VALUE='hostname'>"
 print "Field:<SELECT CLASS='background' ID='field' NAME='field'><OPTION VALUE='hostname'>Hostname</OPTION><OPTION VALUE='ip'>IP</OPTION><OPTION VALUE='mac'>MAC</OPTION><OPTION VALUE='id'>ID</OPTION></SELECT>"
 print "<INPUT CLASS='background' TYPE=TEXT ID='search' NAME='search' STYLE='width:200px' REQUIRED>"
 print "</FORM><DIV CLASS=controls>"
 print aWeb.button('search', DIV='div_content_left', URL='sdcp.cgi?device_list', FRM='device_search')
 print "</DIV>"
 print "</ARTICLE>"

#
#
def info(aWeb):
 if not aWeb.cookies.get('system'):
  print "<SCRIPT>location.replace('index.cgi')</SCRIPT>"
  return

 cookie = aWeb.cookie_unjar('system')

 args = aWeb.get_args2dict()
 args['info'] = ['username','booking','infra']
 dev = aWeb.rest_call("device_info",args)

 if dev['xist'] == 0:
  print "<ARTICLE>Warning - device with either id:[{}]/ip[{}]: does not exist</ARTICLE>".format(aWeb['id'],aWeb['ip'])
  return

 ########################## Data Tables ######################

 width = 680 if dev['racked'] == 1 and not dev['type'] == 'pdu' else 470

 print "<ARTICLE CLASS='info' STYLE='position:relative; height:290px; width:%spx;'><P TITLE='%s'>Device Info</P>"%(width,dev['id'])
 print "<FORM ID=info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(dev['id'])
 print "<INPUT TYPE=HIDDEN NAME=ip VALUE={}>".format(dev['ip'])
 print "<INPUT TYPE=HIDDEN NAME=racked VALUE={}>".format(dev['racked'])
 print "<!-- Reachability Info -->"
 print "<DIV STYLE='margin:3px; float:left;'>"
 print "<DIV CLASS=table STYLE='width:210px;'><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Name:</DIV><DIV CLASS=td><INPUT NAME=devices_hostname TYPE=TEXT VALUE='{}'></DIV></DIV>".format(dev['info']['hostname'])
 print "<DIV CLASS=tr><DIV CLASS=td>IP:</DIV><DIV CLASS=td><INPUT NAME=ip TYPE=TEXT VALUE={} READONLY></DIV></DIV>".format(dev['ip'])
 print "<DIV CLASS=tr><DIV CLASS=td>Domain:</DIV><DIV CLASS=td><SELECT NAME=devices_a_dom_id>"
 for dom in dev['infra']['domains']:
  extra = " selected" if dev['info']['a_dom_id'] == dom['id'] else ""
  print "<OPTION VALUE={0} {1}>{2}</OPTION>".format(dom['id'],extra,dom['name'])
 print "</SELECT></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td>MAC:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=devices_mac VALUE={}></DIV></DIV>".format(dev['mac'])
 print "<DIV CLASS=tr><DIV CLASS=td>Type:</DIV><DIV CLASS=td TITLE='Device type'><SELECT NAME=devices_type_id>"
 for type in dev['infra']['types'].values():
  extra = " selected" if dev['info']['type_id'] == type['id'] or (not dev['info']['type_id'] and type['name'] == 'generic') else ""
  print "<OPTION VALUE={0} {1}>{2}</OPTION>".format(type['id'],extra,type['name'])
 print "</SELECT></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td>Model:</DIV><DIV CLASS=td STYLE='max-width:150px;'><INPUT TYPE=TEXT NAME=devices_model VALUE='%s'></DIV></DIV>"%(dev['info']['model'])
 print "<DIV CLASS=tr><DIV CLASS=td>VM:</DIV><DIV CLASS=td><INPUT NAME=devices_vm TYPE=checkbox VALUE=1 {0}></DIV></DIV>".format("checked=checked" if dev['info']['vm'] == 1 else "") 
 print "<DIV CLASS=tr><DIV CLASS=td>&nbsp;</DIV><DIV CLASS=td>&nbsp;</DIV></DIV>"
 print "</DIV></DIV></DIV>"

 print "<!-- Additional info -->"
 print "<DIV STYLE='margin:3px; float:left;'>"
 print "<DIV CLASS=table STYLE='width:227px;'><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Rack:</DIV>"
 print "<DIV CLASS=td><SELECT NAME=rackinfo_rack_id>"
 for rack in dev['infra']['racks']:
  extra = " selected" if ((dev['racked'] == 0 and rack['id'] == 'NULL') or (dev['racked'] == 1 and dev['info']['rack_id'] == rack['id'])) else ""
  print "<OPTION VALUE={0} {1}>{2}</OPTION>".format(rack['id'],extra,rack['name'])
 print "</SELECT></DIV>"
 print "</DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td>SNMP:</DIV><DIV CLASS=td><INPUT TYPE=TEXT READONLY VALUE='%s'></DIV></DIV>"%(dev['info']['snmp'])
 print "<DIV CLASS=tr ID=div_booking_info><DIV CLASS=td>Booking:</DIV>"
 if dev['booked']:
  print "<DIV CLASS='td %s'>"%("red" if dev['booking']['valid'] == 1 else "orange")
  if dev['booking']['user_id'] == int(cookie['id']):
   print "<A CLASS=z-op DIV=div_booking_info URL='sdcp.cgi?bookings_update&op=debook&id=%s'>%s</A>"%(dev['id'],dev['booking']['alias'])
  else:
   print dev['booking']['alias']
  print "</DIV>"
 else:
  print "<DIV CLASS='td green'><A CLASS=z-op DIV=div_booking_info URL='sdcp.cgi?bookings_update&op=book&id=%s'>Book</A></DIV>"%dev['id']
 print "</DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td>A ID:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=devices_a_id VALUE='%s' READONLY></DIV></DIV>"%(dev['info']['a_id'])
 print "<DIV CLASS=tr><DIV CLASS=td>PTR ID:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=devices_ptr_id VALUE='%s' READONLY></DIV></DIV>"%(dev['info']['ptr_id'])
 print "<DIV CLASS=tr><DIV CLASS=td>Device ID:</DIV><DIV CLASS=td>%s</DIV></DIV>"%(dev['id'])
 print "<DIV CLASS=tr><DIV CLASS=td>IPAM ID:</DIV><DIV CLASS=td>%s</DIV></DIV>"%(dev['info']['ipam_id'])
 print "<DIV CLASS=tr><DIV CLASS=td>&nbsp;</DIV><DIV CLASS=td>&nbsp;</DIV></DIV>"
 print "</DIV></DIV></DIV>"

 print "<!-- Rack Info -->"
 if dev['racked'] == 1 and not dev['type'] == 'pdu':
  print "<DIV STYLE='margin:3px; float:left;'>"
  print "<DIV CLASS=table STYLE='width:210px;'><DIV CLASS=tbody>"
  if not dev['type'] == 'controlplane':
   print "<DIV CLASS=tr><DIV CLASS=td>Rack Size:</DIV><DIV CLASS=td><INPUT NAME=rackinfo_rack_size TYPE=TEXT PLACEHOLDER='{}'></DIV></DIV>".format(dev['info']['rack_size'])
   print "<DIV CLASS=tr><DIV CLASS=td>Rack Unit:</DIV><DIV CLASS=td TITLE='Top rack unit of device placement'><INPUT NAME=rackinfo_rack_unit TYPE=TEXT PLACEHOLDER='{}'></DIV></DIV>".format(dev['info']['rack_unit'])
  if not dev['type'] == 'console' and len(dev['infra']['consoles']) > 0:
   print "<DIV CLASS=tr><DIV CLASS=td>TS:</DIV><DIV CLASS=td><SELECT NAME=rackinfo_console_id>"
   for console in dev['infra']['consoles']:
    extra = " selected='selected'" if (dev['info']['console_id'] == console['id']) or (not dev['info']['console_id'] and console['id'] == 'NULL') else ""
    print "<OPTION VALUE={0} {1}>{2}</OPTION>".format(console['id'],extra,console['hostname'])
   print "</SELECT></DIV></DIV>"
   print "<DIV CLASS=tr><DIV CLASS=td>TS Port:</DIV><DIV CLASS=td TITLE='Console port in rack TS'><INPUT NAME=rackinfo_console_port TYPE=TEXT PLACEHOLDER='{}'></DIV></DIV>".format(dev['info']['console_port'])
  if not dev['type'] == 'controlplane' and len(dev['infra']['pdus']) > 0:
   for pem in ['pem0','pem1']:
    print "<DIV CLASS=tr><DIV CLASS=td>{0} PDU:</DIV><DIV CLASS=td><SELECT NAME=rackinfo_{1}_pdu_slot_id>".format(pem.upper(),pem)
    for pdu in dev['infra']['pdus']:
     pduinfo = dev['infra']['pduinfo'].get(str(pdu['id']))
     if pduinfo:
      for slotid in range(0,pduinfo['slots']):
       pdu_slot_id   = pduinfo[str(slotid)+"_slot_id"]
       pdu_slot_name = pduinfo[str(slotid)+"_slot_name"]
       extra = "selected" if ((dev['info'][pem+"_pdu_id"] == pdu['id']) and (dev['info'][pem+"_pdu_slot"] == pdu_slot_id)) or (not dev['info'][pem+"_pdu_id"] and  pdu['id'] == 'NULL') else ""
       print "<OPTION VALUE=%s.%s %s>%s</OPTION>"%(pdu['id'],pdu_slot_id, extra, pdu['hostname']+":"+pdu_slot_name)
    print "</SELECT></DIV></DIV>"
    print "<DIV CLASS=tr><DIV CLASS=td>{0} Unit:</DIV><DIV CLASS=td><INPUT NAME=rackinfo_{1}_pdu_unit TYPE=TEXT PLACEHOLDER='{2}'></DIV></DIV>".format(pem.upper(),pem,dev['info'][pem + "_pdu_unit"])
  print "</DIV></DIV></DIV>"
 print "<!-- Text fields -->"
 print "<DIV STYLE='display:block; clear:both; margin-bottom:3px; margin-top:1px; width:99%;'><DIV CLASS=table><DIV CLASS=tbody>"
 print "<DIV CLASS='tr even'><DIV CLASS=td>Comments:</DIV><DIV CLASS=td><INPUT CLASS=odd TYPE=TEXT NAME=devices_comment VALUE='{}'></DIV></DIV>".format("" if not dev['info']['comment'] else dev['info']['comment'].encode("utf-8"))
 print "<DIV CLASS='tr even'><DIV CLASS=td>Web page:</DIV><DIV CLASS=td><INPUT CLASS=odd TYPE=TEXT NAME=devices_webpage VALUE='{}'></DIV></DIV>".format("" if not dev['info']['webpage'] else dev['info']['webpage'])
 print "</DIV></DIV></DIV>"
 print "</FORM><DIV CLASS=controls>"
 print aWeb.button('reload',DIV='div_content_right',URL='sdcp.cgi?device_info&id=%i'%dev['id'])
 print aWeb.button('trash', DIV='div_content_right',URL='sdcp.cgi?device_delete&id=%i'%dev['id'], MSG='Are you sure you want to delete device?', TITLE='Delete device',SPIN='true')
 print aWeb.button('search',DIV='div_content_right',URL='sdcp.cgi?device_info&op=lookup', FRM='info_form', TITLE='Lookup and Detect Device information')
 print aWeb.button('save',  DIV='div_content_right',URL='sdcp.cgi?device_info&op=update', FRM='info_form', TITLE='Save Device Information and Update DDI and PDU')
 print aWeb.button('document',    DIV='div_dev_data', URL='sdcp.cgi?device_conf_gen&id=%i'%(dev['id']),TITLE='Generate System Conf')
 print aWeb.button('connections', DIV='div_dev_data', URL='sdcp.cgi?device_interface_list&device=%i'%(dev['id']),TITLE='Device interfaces')
 print aWeb.button('network',     DIV='div_content_right', URL='sdcp.cgi?visualize_network&type=device&id=%s'%(dev['id']), SPIN='true', TITLE='Network map')
 print aWeb.button('term',TITLE='SSH',HREF='ssh://%s@%s'%(dev['username'],dev['ip']))
 if dev['racked'] == 1 and (dev['info']['console_ip'] and dev['info'].get('console_port',0) > 0):
  print aWeb.button('term',TITLE='Console', HREF='telnet://%s:%i'%(dev['info']['console_ip'],6000+dev['info']['console_port']))
 if dev['info'].get('webpage'):
  print aWeb.button('web',TITLE='WWW', TARGET='_blank', HREF=dev['info'].get('webpage'))
 print "<SPAN CLASS='results' ID=update_results>%s</SPAN>"%str(dev.get('result',''))
 print "</DIV></ARTICLE>"

 print "<!-- Function navbar and content -->"
 print "<NAV><UL>"
 for fun in dev['info']['functions'].split(','):
  if fun == 'manage':
   print "<LI><A CLASS=z-op DIV=main URL='sdcp.cgi?%s_manage&id=%i'>Manage</A></LI>"%(dev['info']['type_name'],dev['id'])
  else:
   print "<LI><A CLASS=z-op DIV=div_dev_data SPIN=true URL='sdcp.cgi?device_function&ip={0}&type={1}&op={2}'>{3}</A></LI>".format(dev['ip'], dev['info']['type_name'], fun, fun.title())
 print "</UL></NAV>"
 print "<SECTION CLASS='content' ID=div_dev_data STYLE='top:330px; overflow-x:hidden; overflow-y:auto;'></SECTION>"


####################################################### Functions #######################################################
#
#
def webpages(aWeb):
 res = aWeb.rest_call("device_webpage_list")
 print "<ARTICLE CLASS=info STYLE='width:100%'>"
 print "<DIV CLASS=table><DIV CLASS=tbody>"
 for row in res['data']:
  print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op URL='sdcp.cgi?device_info&id=%s' DIV=div_content_right>%s</A></DIV><DIV CLASS=td><A HREF='%s' TARGET=_blank>%s</A></DIV></DIV>"%(row['id'],row['hostname'],row['webpage'],row['webpage'])
 print "</DIV></DIV>"
 print "</ARTICLE>"

#
#
def conf_gen(aWeb):
 print "<ARTICLE>"
 res = aWeb.rest_call("device_configuration_template",{'id':aWeb['id']})
 if res['result'] == 'OK':
  print "<BR>".join(res['data'])
 else:
  print "<B>%s</B>"%res['info']
 print "</ARTICLE>"

#
#
def function(aWeb):
 print "<ARTICLE>"
 res = aWeb.rest_call("device_function",{'ip':aWeb['ip'],'op':aWeb['op'],'type':aWeb['type']})
 if res['result'] == 'OK':
  if len(res['data']) > 0:
   print "<DIV CLASS=table><DIV CLASS=thead>"
   head = res['data'][0].keys()
   for th in head:
    print "<DIV CLASS=th>%s</DIV>"%(th.title())
   print "</DIV><DIV CLASS=tbody>"
   for row in res['data']:
    print "<DIV CLASS=tr>"
    for td in head:
     print "<DIV CLASS=td>%s</DIV>"%(row.get(td,'&nbsp;'))
    print "</DIV>"
   print "</DIV></DIV>"
  else:
   print "No data"
 else:
  print "<B>Error in devdata: %s</B>"%res['info']
 print "</ARTICLE>"

#
#
def mac_sync(aWeb):
 macs = aWeb.rest_call("device_mac_sync")
 print "<ARTICLE CLASS=info>"
 print "<DIV CLASS=table>"
 print "<DIV CLASS=thead><DIV CLASS=th>Id</DIV><DIV CLASS=th>IP</DIV><DIV CLASS=th>Hostname</DIV><DIV CLASS=th>MAC</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for row in macs:
  print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV></DIV>".format(row['id'],row['ipasc'],row['hostname'],row['found'])
 print "</DIV></DIV></ARTICLE>"

#
#
def new(aWeb):
 cookie = aWeb.cookie_unjar('system')
 if not aWeb.cookies.get('system'):
  print "<SCRIPT>location.replace('index.cgi')</SCRIPT>"
  return
 ip   = aWeb.get('ip')
 name = aWeb.get('hostname','unknown')
 mac  = aWeb.get('mac',"00:00:00:00:00:00")
 op   = aWeb['op']
 network = aWeb['ipam_network_id']
 if not ip:
  from sdcp.core import genlib as GL
  ip = "127.0.0.1" if not aWeb['ipint'] else GL.int2ip(int(aWeb['ipint']))

 if op == 'new':
  args = { 'ip':ip, 'mac':mac, 'hostname':name, 'a_dom_id':aWeb['a_dom_id'], 'ipam_network_id':network }
  if aWeb['vm']:
   args['vm'] = 1
  else:
   args['target'] = aWeb['target']
   args['arg']    = aWeb['arg']
   args['vm'] = 0
  res = aWeb.rest_call("device_new",args)
  print "Operation:%s"%str(res)
 elif op == 'find':
  print aWeb.rest_call("ipam_ip_find",{'network_id':network})['ip']
 else:
  networks = aWeb.rest_call("ipam_network_list")['networks']
  domains  = aWeb.rest_call("dns_domain_list",{'filter':'forward'})['domains']
  print "<ARTICLE CLASS=info><P>Device Add</P>"
  print "<FORM ID=device_new_form>"
  print "<DIV CLASS=table><DIV CLASS=tbody>"
  print "<DIV CLASS=tr><DIV CLASS=td>Hostname:</DIV><DIV CLASS=td><INPUT NAME=hostname TYPE=TEXT VALUE={}></DIV></DIV>".format(name)
  print "<DIV CLASS=tr><DIV CLASS=td>Domain:</DIV><DIV CLASS=td><SELECT  NAME=a_dom_id>"
  for d in domains:
   print "<OPTION VALUE={0} {1}>{2}</OPTION>".format(d['id'],"selected" if d['name'] == aWeb['domain'] else "",d['name'])
  print "</SELECT></DIV></DIV>"
  print "<DIV CLASS=tr><DIV CLASS=td>Network:</DIV><DIV CLASS=td><SELECT NAME=ipam_network_id>"
  for s in networks:
   print "<OPTION VALUE={} {}>{} ({})</OPTION>".format(s['id'],"selected" if str(s['id']) == network else "", s['netasc'],s['description'])
  print "</SELECT></DIV></DIV>"
  print "<DIV CLASS=tr><DIV CLASS=td>IP:</DIV><DIV CLASS=td><INPUT  NAME=ip ID=device_ip TYPE=TEXT VALUE='{}'></DIV></DIV>".format(ip)
  print "<DIV CLASS=tr><DIV CLASS=td>MAC:</DIV><DIV CLASS=td><INPUT NAME=mac TYPE=TEXT PLACEHOLDER='{0}'></DIV></DIV>".format(mac)
  if aWeb['target'] == 'rack_id':
   print "<INPUT TYPE=HIDDEN NAME=target VALUE={}>".format(aWeb['target'])
   print "<INPUT TYPE=HIDDEN NAME=arg VALUE={}>".format(aWeb['arg'])
  else:
   print "<DIV CLASS=tr><DIV CLASS=td>VM:</DIV><DIV  CLASS=td><INPUT NAME=vm  TYPE=CHECKBOX VALUE=1  {0} ></DIV></DIV>".format("checked" if aWeb['target'] == 'vm' else '')
  print "</DIV></DIV>"
  print "</FORM><DIV CLASS=controls>"
  print aWeb.button('start', DIV='device_span', URL='sdcp.cgi?device_new&op=new',  FRM='device_new_form', TITLE='Create')
  print aWeb.button('search',DIV='device_ip',   URL='sdcp.cgi?device_new&op=find', FRM='device_new_form', TITLE='Find IP',INPUT='True')
  print "</DIV><SPAN CLASS='results' ID=device_span STYLE='max-width:400px;'></SPAN>"
  print "</ARTICLE>"

#
#
def delete(aWeb):
 res = aWeb.rest_call("device_delete",{ 'id':aWeb['id'] })
 print "<ARTICLE>Unit {} deleted, op:{}</ARTICLE>".format(aWeb['id'],res)

#
#
def discover(aWeb):
 if aWeb['op']:
  res = aWeb.rest_full(aWeb._rest_url,"device_discover",{ 'network_id':aWeb['network_id'], 'a_dom_id':aWeb['a_dom_id']}, aTimeout = 200)['data']
  print "<ARTICLE>%s</ARTICLE>"%(res)
 else:
  networks = aWeb.rest_call("ipam_network_list")['networks']
  domains = aWeb.rest_call("dns_domain_list",{'filter':'forward'})['domains']
  dom_name = aWeb['domain']
  print "<ARTICLE CLASS=info><P>Device Discovery</P>"
  print "<FORM ID=device_discover_form>"
  print "<INPUT TYPE=HIDDEN NAME=op VALUE=json>"
  print "<DIV CLASS=table><DIV CLASS=tbody>"
  print "<DIV CLASS=tr><DIV CLASS=td>Domain:</DIV><DIV CLASS=td><SELECT NAME=a_dom_id>"
  for d in domains:
   extra = "" if not dom_name == d.get('name') else "selected=selected"
   print "<OPTION VALUE=%s %s>%s</OPTION>"%(d.get('id'),extra,d.get('name'))
  print "</SELECT></DIV></DIV>"
  print "<DIV CLASS=tr><DIV CLASS=td>Network:</DIV><DIV CLASS=td><SELECT NAME=network_id>"
  for s in networks:
   print "<OPTION VALUE=%s>%s (%s)</OPTION>"%(s['id'],s['netasc'],s['description'])
  print "</SELECT></DIV></DIV>"
  print "</DIV></DIV>"
  print "</FORM><DIV CLASS=controls>"
  print aWeb.button('start', DIV='div_content_right', SPIN='true', URL='sdcp.cgi?device_discover', FRM='device_discover_form')
  print "</DIV></ARTICLE>"

################################################## interfaces #################################################
#
#
def interface_list(aWeb):
 if   aWeb['op'] == 'delete':
  opres = aWeb.rest_call("device_interface_delete",{'id':aWeb['id'],'device':aWeb['device']})
 elif aWeb['op'] == 'delete_list':
  args = aWeb.get_args2dict()
  opres = aWeb.rest_call("device_interface_delete_list",args)
 elif aWeb['op'] == 'discover':
  opres = aWeb.rest_call("device_interface_discover",{'device':aWeb['device']})
 elif aWeb['op'] == 'link':
  opres = aWeb.rest_call("device_interface_link",{'a_id':aWeb['id'],'b_id':aWeb['peer_interface']})
 else:
  opres = ""
 res = aWeb.rest_call("device_interface_list",{'device':aWeb['device']})
 print "<ARTICLE><P>Interfaces (%s)</P><DIV CLASS='controls'>"%(res['hostname'])
 print aWeb.button('reload', DIV='div_dev_data',URL='sdcp.cgi?device_interface_list&device=%s'%res['id'])
 print aWeb.button('add',    DIV='div_dev_data',URL='sdcp.cgi?device_interface_info&device=%s&id=new'%res['id'])
 print aWeb.button('search', DIV='div_dev_data',URL='sdcp.cgi?device_interface_list&device=%s&op=discover'%res['id'], SPIN='true', MSG='Rediscover interfaces?')
 print aWeb.button('trash',  DIV='div_dev_data',URL='sdcp.cgi?device_interface_list&device=%s&op=delete_list'%res['id'], MSG='Delete interfaces?', FRM='interface_list', TITLE='Delete selected interfaces')
 print "</DIV><SPAN CLASS=results>%s</SPAN><FORM ID=interface_list>"%(opres)
 print "<DIV CLASS=table>"
 print "<DIV CLASS=thead><DIV CLASS=th>Id</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>Description</DIV><DIV CLASS=th>SNMP Index</DIV><DIV CLASS=th>Peer interface</DIV><DIV CLASS=th>&nbsp;</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for row in res['data']:
  print "<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td><DIV CLASS=controls>"%(row['id'],row['name'],row['description'],row['snmp_index'],row['peer_interface'] if not row['multipoint'] else 'multipoint')
  print "<INPUT TYPE=CHECKBOX VALUE=1 NAME='interface_%s'>"%row['id']
  print aWeb.button('info',  DIV='div_dev_data',URL='sdcp.cgi?device_interface_info&device=%s&id=%s'%(aWeb['device'],row['id']))
  print aWeb.button('sync',  DIV='div_dev_data',URL='sdcp.cgi?device_interface_link_device&device=%s&id=%s&name=%s'%(aWeb['device'],row['id'],row['name']), TITLE='Connect')
  print "</DIV></DIV></DIV>"
 print "</DIV></DIV>"
 print "</FORM></ARTICLE>"

#
#
def interface_info(aWeb):
 args = aWeb.get_args2dict()
 data = aWeb.rest_call("device_interface_info",args)['data']
 print "<ARTICLE CLASS=info STYLE='width:100%;'><P>Interface</P>"
 print "<FORM ID=interface_info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE='%s'>"%(data['id'])
 print "<INPUT TYPE=HIDDEN NAME=device VALUE='%s'>"%(data['device'])
 print "<DIV CLASS=table STYLE='float:left; width:auto;'><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Name:</DIV><DIV CLASS=td><INPUT        NAME=name        VALUE='%s' TYPE=TEXT REQUIRED STYLE='min-width:400px'></DIV></DIV>"%(data['name'])
 print "<DIV CLASS=tr><DIV CLASS=td>Description:</DIV><DIV CLASS=td><INPUT NAME=description VALUE='%s' TYPE=TEXT REQUIRED STYLE='min-width:400px'></DIV></DIV>"%(data['description'])
 print "<DIV CLASS=tr><DIV CLASS=td>SNMP Index:</DIV><DIV CLASS=td><INPUT  NAME=snmp_index  VALUE='%s' TYPE=TEXT REQUIRED STYLE='min-width:400px'></DIV></DIV>"%(data['snmp_index'])
 print "<DIV CLASS=tr><DIV CLASS=td>Multipoint:</DIV><DIV CLASS=td><INPUT  NAME=multipoint  VALUE=1    TYPE=CHECKBOX %s></DIV></DIV>"%("checked" if data['multipoint'] else "")
 print "<DIV CLASS=tr><DIV CLASS=td>Peer interface:</DIV><DIV CLASS=td>%s</DIV></DIV>"%data['peer_interface']
 if data['peer_device']:
  print "<DIV CLASS=tr><DIV CLASS=td>Peer Device</DIV><DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL=sdcp.cgi?device_info&id=%s>%s</A></DIV></DIV>"%(data['peer_device'],data['peer_device'])
 print "</DIV></DIV>"
 print "</FORM><DIV CLASS=controls>"
 print aWeb.button('back', DIV='div_dev_data', URL='sdcp.cgi?device_interface_list&device=%s'%data['device'])
 print aWeb.button('save', DIV='div_dev_data', URL='sdcp.cgi?device_interface_info&op=update', FRM='interface_info_form')
 if data['id'] != 'new':
  print aWeb.button('trash', DIV='div_dev_data', URL='sdcp.cgi?device_interface_list&op=delete&device=%s&id=%s'%(data['device'],data['id']), MSG='Delete interface?')
 print "</DIV></ARTICLE>"

#
#
def interface_link_device(aWeb):
 print "<ARTICLE>"
 print "<FORM ID=interface_link>"
 print "<INPUT TYPE=HIDDEN NAME=device VALUE=%s>"%aWeb['device']
 print "<INPUT TYPE=HIDDEN NAME=id   VALUE=%s>"%aWeb['id']
 print "<INPUT TYPE=HIDDEN NAME=name VALUE=%s>"%aWeb['name']
 print "Connect '%s' to device (Id or IP): <INPUT CLASS='background' REQUIRED TYPE=TEXT NAME='peer' STYLE='width:100px' VALUE='%s'>"%(aWeb['name'],aWeb.get('peer','0'))
 print "</FORM><DIV CLASS=controls>"
 print aWeb.button('back',    DIV='div_dev_data', URL='sdcp.cgi?device_interface_list&device=%s'%aWeb['device'])
 print aWeb.button('forward', DIV='div_dev_data', URL='sdcp.cgi?device_interface_link_interface', FRM='interface_link')
 print "</DIV></ARTICLE>"

#
#
def interface_link_interface(aWeb):
 res = aWeb.rest_call("device_interface_list",{'device':aWeb['peer'],'sort':'name'})
 print "<ARTICLE>"
 print "<FORM ID=interface_link>"
 print "<INPUT TYPE=HIDDEN NAME=device VALUE=%s>"%aWeb['device']
 print "<INPUT TYPE=HIDDEN NAME=id   VALUE=%s>"%aWeb['id']
 print "<INPUT TYPE=HIDDEN NAME=name VALUE=%s>"%aWeb['name']
 print "Connect '%s' to device id: <INPUT CLASS='background' READONLY TYPE=TEXT NAME='peer' STYLE='width:100px' VALUE=%s> on"%(aWeb['name'],res['id'])
 print "<SELECT NAME=peer_interface REQUIRED>"
 for intf in res.get('data',[]):
  print "<OPTION VALUE=%s>%s (%s)</OPTION>"%(intf['id'],intf['name'],intf['description'])
 print "</SELECT>"
 print "</FORM><DIV CLASS=controls>"
 print aWeb.button('back',    DIV='div_dev_data', URL='sdcp.cgi?device_interface_link_device', FRM='interface_link')
 print aWeb.button('forward', DIV='div_dev_data', URL='sdcp.cgi?device_interface_list&op=link', FRM='interface_link')
 print "</DIV></ARTICLE>"

#
#
def network(aWeb):
 res = aWeb.rest_call("device_network",{'id':aWeb['id']})
 nodes = ["{'id':%s, 'label':'%s', 'shape':'image', 'image':'%s', 'font':'14px verdana blue'}"%(key,val['hostname'],val['icon']) for key,val in res['devices'].iteritems()]
 edges = ["{'from':%s, 'to':%s, title:'%s:%s <-> %s:%s' }"%(con['a_device'],con['b_device'],res['devices'][str(con['a_device'])]['hostname'],con['a_name'],res['devices'][str(con['b_device'])]['hostname'],con['b_name']) for con in res['interfaces']]
 print "<ARTICLE><P>Device '%s':s network</P><DIV CLASS=controls>"%(aWeb['hostname'])
 print aWeb.button('reload', DIV='div_content_right', URL='sdcp.cgi?device_network&id=%s&hostname=%s'%(aWeb['id'],aWeb['hostname']), TITLE='Reload')
 print aWeb.button('back',   DIV='div_content_right', URL='sdcp.cgi?device_info&id=%s'%aWeb['id'], TITLE='Back')
 print aWeb.button('start',  onclick='network_start()')
 print aWeb.button('stop',   onclick='network_stop()')
 print aWeb.button('save',   onclick='network_save()')
 print "</DIV><LABEL FOR=network_name>Name:</LABEL><INPUT TYPE=TEXT CLASS=background STYLE='width:120px' ID=network_name><SPAN CLASS='results' ID=network_result></SPAN>"
 print "<DIV ID='device_network' CLASS='network'></DIV><DIV ID=network_config><SCRIPT>"
 print "var nodes = new vis.DataSet([%s]);"%",".join(nodes)
 print "var edges = new vis.DataSet([%s]);"%",".join(edges)
 print """
 var data = {nodes:nodes, edges:edges};
 var options = { 'nodes':{ 'shadow':true }, 'edges':{ 'length':220, 'smooth':{ 'type':'dynamic'} } };
 var network = new vis.Network(document.getElementById('device_network'), data, options);
 network.on('stabilizationIterationsDone', function () { network.setOptions({ physics: false }); });

 function network_start(){ 
  network.setOptions({ physics:true  });
 };

 function network_stop(){
  network.setOptions({ physics:false });
 };

 function network_save(){
  var output = { options:options,edges:[],nodes:{},name:$("#network_name").val()};
  positions = network.getPositions();
  Object.entries(nodes._data).forEach(([key,value]) => {
   var node = value;
   node.x   = positions[key].x;
   node.y   = positions[key].y;
   output.nodes[key] = node;
  });
  Object.entries(edges._data).forEach(([key,value]) => {
   var edge   = {};
   edge.from  = value.from;
   edge.to    = value.to;
   edge.title = value.title;
   output.edges.push(edge);
  });
  $.post('rest.cgi?device_network_save',JSON.stringify(output), result => { $('#network_result').html(JSON.stringify(result)); console.log(result);});
 };
 """
 print "</SCRIPT></DIV></ARTICLE>"
