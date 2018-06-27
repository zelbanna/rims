"""Module docstring.

HTML5 Ajax Device module

"""
__author__= "Zacharias El Banna"
__version__ = "1.0GA"
__status__ = "Production"
__icon__ = 'images/icon-network.png'
__type__ = 'menuitem'

########################################## Device Operations ##########################################
#
#
def main(aWeb):
 print "<NAV><UL>"
 print "<LI CLASS='dropdown'><A>Devices</A><DIV CLASS='dropdown-content'>"
 print "<A CLASS=z-op DIV=div_content_left URL='zdcp.cgi?device_list&{0}'>List</A>".format(aWeb.get_args())
 print "<A CLASS=z-op DIV=div_content_left URL='zdcp.cgi?device_search'>Search</A>"
 print "<A CLASS=z-op DIV=div_content_left URL='zdcp.cgi?device_types_list'>Types</A>"
 print "</DIV></LI>"
 print "<LI><A CLASS=z-op DIV=div_content_left URL='zdcp.cgi?visualize_list'>Maps</A></LI>"
 if aWeb['rack']:
  data = aWeb.rest_call("rack_inventory",{'id':aWeb['rack']})
  for type in ['pdu','console']:
   if len(data[type]) > 0:
    print "<LI CLASS='dropdown'><A>%s</A><DIV CLASS='dropdown-content'>"%(type.title())
    for row in data[type]:
     print "<A CLASS=z-op DIV=div_content_left SPIN=true URL='zdcp.cgi?%s_inventory&ip=%s'>%s</A>"%(row['type'],row['ip'],row['hostname'])
    print "</DIV></LI>"
  if data.get('name'):
   print "<LI><A CLASS='z-op' DIV=div_content_right  URL='zdcp.cgi?rack_inventory&rack=%s'>'%s'</A></LI>"%(aWeb['rack'],data['name'])
 print "<LI><A CLASS='z-op reload' DIV=main URL='zdcp.cgi?device_main&{}'></A></LI>".format(aWeb.get_args())
 print "<LI CLASS='right'><A CLASS=z-op DIV=div_content URL='zdcp.cgi?bookings_list'>Bookings</A></LI>"
 print "<LI CLASS=right><A CLASS=z-op DIV=div_content_left URL='zdcp.cgi?ipam_network_list'>IPAM</A></LI>"
 print "<LI CLASS='right dropdown'><A>DNS</A><DIV CLASS='dropdown-content'>"
 print "<A CLASS=z-op DIV=div_content_left URL='zdcp.cgi?dns_server_list'>Servers</A>"
 print "<A CLASS=z-op DIV=div_content_left URL='zdcp.cgi?dns_domain_list'>Domains</A>"
 print "</DIV></LI>"
 print "<LI CLASS='right dropdown'><A>Rack</A><DIV CLASS='dropdown-content'>"
 print "<A CLASS=z-op DIV=div_content_left URL='zdcp.cgi?rack_list'>Racks</A>"
 print "<A CLASS=z-op DIV=div_content_left URL='zdcp.cgi?rack_list_infra&type=pdu'>PDUs</A>"
 print "<A CLASS=z-op DIV=div_content_left URL='zdcp.cgi?rack_list_infra&type=console'>Consoles</A>"
 print "</DIV></LI>"
 print "</UL></NAV>"
 print "<SECTION CLASS=content       ID=div_content>"
 print "<SECTION CLASS=content-left  ID=div_content_left></SECTION>"
 print "<SECTION CLASS=content-right ID=div_content_right></SECTION>"
 print "</SECTION>"

#
#
def list(aWeb):
 args = aWeb.get_args2dict()
 args['sort'] = aWeb.get('sort','ip')
 res = aWeb.rest_call("device_list",args)
 print "<ARTICLE><P>Device List</P><DIV CLASS='controls'>"
 print aWeb.button('reload', DIV='div_content_left',  URL='zdcp.cgi?device_list&%s'%aWeb.get_args(), TITLE='Reload')
 print aWeb.button('items',  DIV='div_content_left',  URL='zdcp.cgi?device_list&sort=%s'%args['sort'], TITLE='List All')
 print aWeb.button('search', DIV='div_content_left',  URL='zdcp.cgi?device_search', TITLE='Search')
 print aWeb.button('add',    DIV='div_content_right', URL='zdcp.cgi?device_new&%s'%aWeb.get_args(), TITLE='Add device')
 print aWeb.button('network',DIV='div_content_right', URL='zdcp.cgi?device_discover', TITLE='Discover')
 print "</DIV><DIV CLASS=table><DIV CLASS=thead>"
 for sort in ['IP','Hostname']:
  print "<DIV CLASS=th><A CLASS=z-op DIV=div_content_left URL='zdcp.cgi?device_list&sort=%s&%s'>%s<SPAN STYLE='font-size:14px; color:%s;'>&darr;</SPAN></A></DIV>"%(sort.lower(),aWeb.get_args(['sort']),sort,"black" if not sort.lower() == args['sort'] else "red")
 print "<DIV CLASS=th>Model</DIV></DIV><DIV CLASS=tbody>"
 for row in res['data']:
  print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL='zdcp.cgi?device_info&id=%i' TITLE='%s'>%s</A></DIV><DIV CLASS=td STYLE='max-width:180px; overflow-x:hidden'>%s</DIV><DIV CLASS=td>%s</DIV></DIV>"%(row['id'],row['id'],row['ip'], row['hostname'], row['model'])
 print "</DIV></DIV></ARTICLE>"

#
#
def search(aWeb):
 print "<ARTICLE><P>Device Search</P>"
 print "<FORM ID='device_search'>"
 print "<INPUT TYPE=HIDDEN NAME=sort VALUE='hostname'>"
 print "<SPAN>Field:</SPAN><SELECT CLASS='background' ID='field' NAME='field'><OPTION VALUE='hostname'>Hostname</OPTION><OPTION VALUE='type'>Type</OPTION><OPTION VALUE='ip'>IP</OPTION><OPTION VALUE='mac'>MAC</OPTION><OPTION VALUE='id'>ID</OPTION></SELECT>"
 print "<INPUT CLASS='background' TYPE=TEXT ID='search' NAME='search' STYLE='width:200px' REQUIRED>"
 print "</FORM><DIV CLASS=controls>"
 print aWeb.button('search', DIV='div_content_left', URL='zdcp.cgi?device_list', FRM='device_search')
 print aWeb.button('items',  DIV='div_content_left', URL='zdcp.cgi?device_list', TITLE='List All items')
 print "</DIV>"
 print "</ARTICLE>"

#
#
def types_list(aWeb):
 res = aWeb.rest_call("device_types_list")
 print "<ARTICLE><P>Device Types<P>"
 print "<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Class</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>Icon</DIV></DIV><DIV CLASS=tbody>"
 for tp in res['types']:
  print "<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td><A CLASS=z-op DIV=div_content_left URL='zdcp.cgi?device_list&field=type&search=%s'>%s</A></DIV><DIV CLASS=td>%s</DIV></DIV>"%(tp['base'],tp['name'],tp['name'],tp['icon'])
 print "</DIV></DIV>"
 print "</ARTICLE>"
#
#
def info(aWeb):
 if not aWeb.cookies.get('system'):
  print "<SCRIPT>location.replace('index.cgi')</SCRIPT>"
  return

 cookie = aWeb.cookie_unjar('system')
 args = aWeb.get_args2dict()
 dev = aWeb.rest_call("device_info",args)
 if not dev['found']:
  print "<ARTICLE>Warning - device with either id:[{}]/ip[{}]: does not exist</ARTICLE>".format(aWeb['id'],aWeb['ip'])
  return
 ########################## Data Tables ######################
 width = 680 if dev['racked'] and not dev['info']['type_base'] == 'pdu' else 470
 print "<ARTICLE CLASS='info' STYLE='position:relative; height:268px; width:%spx;'><P TITLE='%s'>Device Info</P>"%(width,dev['id'])
 print "<FORM ID=info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(dev['id'])
 print "<!-- Reachability Info -->"
 print "<DIV STYLE='margin:3px; float:left;'><DIV CLASS=table STYLE='width:210px;'><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Name:  </DIV><DIV CLASS=td>%s</DIV></DIV>"%dev['info']['hostname']
 print "<DIV CLASS=tr><DIV CLASS=td>Domain:</DIV><DIV CLASS=td>%s</DIV></DIV>"%dev['info']['domain']
 print "<DIV CLASS=tr><DIV CLASS=td>IP:    </DIV><DIV CLASS=td>%s</DIV></DIV>"%dev['ip']
 print "<DIV CLASS=tr><DIV CLASS=td>MAC:   </DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=mac VALUE='%s'></DIV></DIV>"%dev['info']['mac'].upper()
 print "<DIV CLASS=tr><DIV CLASS=td>VM:    </DIV><DIV CLASS=td><INPUT NAME=vm TYPE=checkbox VALUE=1 {0}></DIV></DIV>".format("checked=checked" if dev['info']['vm'] == 1 else "")
 print "<DIV CLASS=tr ID=div_booking_info><DIV CLASS=td>Booking:</DIV>"
 if dev['booked']:
  print "<DIV CLASS='td %s'>"%("red" if dev['booking']['valid'] == 1 else "orange")
  print dev['booking']['alias'] if dev['booking']['user_id'] != int(cookie['id']) else "<A CLASS=z-op DIV=div_booking_info URL='zdcp.cgi?bookings_update&op=debook&id=%s'>%s</A>"%(dev['id'],dev['booking']['alias'])
  print "</DIV>"
 else:
  print "<DIV CLASS='td green'><A CLASS=z-op DIV=div_booking_info URL='zdcp.cgi?bookings_update&op=book&id=%s'>Book</A></DIV>"%dev['id']
 print "</DIV>"
 print "<DIV CLASS='tr even'><DIV CLASS=td>&nbsp;</DIV><DIV CLASS=td>&nbsp;</DIV></DIV>"
 print "</DIV></DIV></DIV>"
 print "<!-- Additional info -->"
 print "<DIV STYLE='margin:3px; float:left;'><DIV CLASS=table STYLE='width:227px;'><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>SNMP:</DIV><DIV CLASS=td>%s</DIV></DIV>"%dev['info']['snmp']
 print "<DIV CLASS=tr><DIV CLASS=td>Device ID:</DIV><DIV CLASS=td>%s</DIV></DIV>"%dev['id']
 print "<DIV CLASS=tr><DIV CLASS=td>A ID:     </DIV><DIV CLASS=td>%s</DIV></DIV>"%dev['info']['a_id']
 print "<DIV CLASS=tr><DIV CLASS=td>PTR ID:   </DIV><DIV CLASS=td>%s</DIV></DIV>"%dev['info']['ptr_id']
 print "<DIV CLASS=tr><DIV CLASS=td>Type:  </DIV><DIV CLASS=td>%s</DIV></DIV>"%dev['info']['type_name']
 print "<DIV CLASS=tr><DIV CLASS=td>Model: </DIV><DIV CLASS=td STYLE='max-width:150px;'><INPUT TYPE=TEXT NAME=model VALUE='%s'></DIV></DIV>"%(dev['info']['model'])
 print "<DIV CLASS='tr even'><DIV CLASS=td>&nbsp;</DIV><DIV CLASS=td>&nbsp;</DIV></DIV>"
 print "</DIV></DIV></DIV>"
 print "<!-- Rack Info -->"
 if dev['racked'] and not dev['info']['type_base'] == 'pdu':
  print "<DIV STYLE='margin:3px; float:left;'><DIV CLASS=table STYLE='width:210px;'><DIV CLASS=tbody>"
  print "<DIV CLASS=tr><DIV CLASS=td>Rack/Pos: </DIV><DIV CLASS=td>%s (%s)</DIV></DIV>"%(dev['rack']['rack_name'],dev['rack']['rack_unit'])
  if not dev['info']['type_base'] == 'controlplane':
   print "<DIV CLASS=tr><DIV CLASS=td>Size:    </DIV><DIV CLASS=td>%s U</DIV></DIV>"%(dev['rack']['rack_size'])
  if not dev['info']['type_base'] == 'console':
   print "<DIV CLASS=tr><DIV CLASS=td>TS/Port: </DIV><DIV CLASS=td>%s (%s)</DIV></DIV>"%(dev['rack']['console_name'],dev['rack']['console_port'])
  for pem in ['pem0','pem1']:
   print "<DIV CLASS=tr><DIV CLASS=td>%s PDU: </DIV><DIV CLASS=td>%s</DIV></DIV>"%(pem.upper(),dev['rack']['%s_pdu_name'%pem])
   print "<DIV CLASS=tr><DIV CLASS=td>%s Port:</DIV><DIV CLASS=td>%s</DIV></DIV>"%(pem.upper(),dev['rack']['%s_pdu_unit'%pem])
  print "</DIV></DIV></DIV>"
 print "<!-- Text fields -->"
 print "<DIV STYLE='display:block; clear:both; margin-bottom:3px; margin-top:1px; width:99%;'><DIV CLASS=table><DIV CLASS=tbody>"
 print "<DIV CLASS='tr even'><DIV CLASS=td>Comments:</DIV><DIV CLASS=td><INPUT CLASS=odd TYPE=TEXT NAME=comment VALUE='{}'></DIV></DIV>".format("" if not dev['info']['comment'] else dev['info']['comment'].encode("utf-8"))
 print "<DIV CLASS='tr even'><DIV CLASS=td>Web page:</DIV><DIV CLASS=td><INPUT CLASS=odd TYPE=TEXT NAME=webpage VALUE='{}'></DIV></DIV>".format("" if not dev['info']['webpage'] else dev['info']['webpage'])
 print "</DIV></DIV></DIV>"
 print "</FORM><DIV CLASS=controls>"
 print aWeb.button('reload',     DIV='div_content_right',URL='zdcp.cgi?device_info&id=%i'%dev['id'])
 print aWeb.button('trash',      DIV='div_content_right',URL='zdcp.cgi?device_delete&id=%i'%dev['id'], MSG='Are you sure you want to delete device?', TITLE='Delete device',SPIN='true')
 print aWeb.button('configure',  DIV='div_content_right',URL='zdcp.cgi?device_update&id=%i'%dev['id'], TITLE='Configure Extended Device Information')
 print aWeb.button('save',       DIV='div_content_right',URL='zdcp.cgi?device_info&op=update', FRM='info_form', TITLE='Save Basic Device Information')
 print aWeb.button('document',   DIV='div_dev_data',     URL='zdcp.cgi?device_conf_gen&id=%i'%(dev['id']),TITLE='Generate System Conf')
 print aWeb.button('connections',DIV='div_dev_data',     URL='zdcp.cgi?device_interface_list&device=%i'%(dev['id']),TITLE='Device interfaces')
 print aWeb.button('visualize',  DIV='div_content_right',URL='zdcp.cgi?visualize_network&type=device&id=%s'%(dev['id']), SPIN='true', TITLE='Network map')
 print aWeb.button('term',TITLE='SSH',HREF='ssh://%s@%s'%(dev['username'],dev['ip']))
 if dev['racked'] and dev['rack'].get('console_ip') and dev['rack'].get('console_port'):
  # Hardcoded port to 60xx
  print aWeb.button('term',TITLE='Console', HREF='telnet://%s:%i'%(dev['rack']['console_ip'],6000+dev['rack']['console_port']))
 if dev['info'].get('webpage'):
  print aWeb.button('web',TITLE='WWW', TARGET='_blank', HREF=dev['info'].get('webpage'))
 print "<SPAN CLASS='results' ID=update_results>%s</SPAN>"%str(dev.get('result',''))
 print "</DIV></ARTICLE>"
 print "<!-- Function navbar and content -->"
 print "<NAV><UL>"
 for fun in dev['info']['functions'].split(','):
  if fun == 'manage':
   print "<LI><A CLASS=z-op DIV=main URL='zdcp.cgi?%s_manage&id=%i'>Manage</A></LI>"%(dev['info']['type_name'],dev['id'])
  else:
   print "<LI><A CLASS=z-op DIV=div_dev_data SPIN=true URL='zdcp.cgi?device_function&ip={0}&type={1}&op={2}'>{3}</A></LI>".format(dev['ip'], dev['info']['type_name'], fun, fun.title())
 print "</UL></NAV>"
 print "<SECTION CLASS='content' ID=div_dev_data STYLE='top:308px; overflow-x:hidden; overflow-y:auto;'></SECTION>"

####################################### UPDATE INFO ###################################
#
#
def update(aWeb):
 args = aWeb.get_args2dict()
 dev = aWeb.rest_call("device_update",args)
 domains = aWeb.rest_call("dns_domain_list",{'filter':'forward'})['domains']

 print "<ARTICLE CLASS='info'><P>Device Update Info</P>"
 print "<FORM ID=info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(dev['id'])
 print "<INPUT TYPE=HIDDEN NAME=ip VALUE={}>".format(dev['ip'])
 print "<INPUT TYPE=HIDDEN NAME=racked VALUE={}>".format(dev['racked'])
 print "<!-- Reachability Info -->"
 print "<DIV CLASS=table><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Name:</DIV><DIV CLASS=td><INPUT NAME=devices_hostname TYPE=TEXT VALUE='%s'></DIV></DIV>"%(dev['info']['hostname'])
 print "<DIV CLASS=tr><DIV CLASS=td>Domain:</DIV><DIV CLASS=td><SELECT NAME=devices_a_dom_id>"
 for dom in domains:
  extra = " selected" if dev['info']['a_dom_id'] == dom['id'] else ""
  print "<OPTION VALUE='%s' %s>%s</OPTION>"%(dom['id'],extra,dom['name'])
 print "</SELECT></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td>IP:</DIV><DIV CLASS=td><INPUT NAME=ip TYPE=TEXT VALUE='%s'></DIV><DIV CLASS=td>"%(dev['ip'])
 print aWeb.button('sync',DIV='div_content_right', FRM='info_form', URL='zdcp.cgi?device_update_ip&id=%s'%dev['id'], TITLE='Modify IP')
 print "</DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td>MAC:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=devices_mac VALUE={}></DIV></DIV>".format(dev['info']['mac'])
 print "<DIV CLASS=tr><DIV CLASS=td>Type:</DIV><DIV CLASS=td><SELECT NAME=devices_type_id>"
 types = dev['infra']['types'].values()
 types.sort(key=lambda x: x['name'])
 for type in types:
  extra = " selected" if dev['info']['type_id'] == type['id'] or (not dev['info']['type_id'] and type['name'] == 'generic') else ""
  print "<OPTION VALUE={0} {1}>{2}</OPTION>".format(type['id'],extra,type['name'])
 print "</SELECT></DIV><DIV CLASS=td>"
 print aWeb.button('search',DIV='div_content_right',URL='zdcp.cgi?device_update&op=lookup', FRM='info_form', TITLE='Lookup and Detect Device information')
 print "</DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td>Model:  </DIV><DIV CLASS=td STYLE='max-width:250px;'><INPUT TYPE=TEXT NAME=devices_model VALUE='%s'></DIV></DIV>"%(dev['info']['model'])
 print "<DIV CLASS=tr><DIV CLASS=td>VM:     </DIV><DIV CLASS=td><INPUT NAME=devices_vm TYPE=checkbox VALUE=1 {0}></DIV></DIV>".format("checked=checked" if dev['info']['vm'] == 1 else "") 
 print "<DIV CLASS=tr><DIV CLASS=td>SNMP:   </DIV><DIV CLASS=td><INPUT TYPE=TEXT READONLY VALUE='%s'></DIV></DIV>"%(dev['info']['snmp'])
 print "<DIV CLASS=tr><DIV CLASS=td>A ID:   </DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=devices_a_id VALUE='%s' READONLY></DIV></DIV>"%(dev['info']['a_id'])
 print "<DIV CLASS=tr><DIV CLASS=td>PTR ID: </DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=devices_ptr_id VALUE='%s' READONLY></DIV></DIV>"%(dev['info']['ptr_id'])
 print "<DIV CLASS=tr><DIV CLASS=td>IPAM ID:</DIV><DIV CLASS=td><INPUT TYPE=TEXT READONLY VALUE='%s'></DIV></DIV>"%dev['info']['ipam_id']
 print "<DIV CLASS=tr><DIV CLASS=td>&nbsp;</DIV><DIV CLASS=td>&nbsp;</DIV></DIV>"
 print "<!-- Rack Info -->"
 print "<DIV CLASS=tr><DIV CLASS=td>Rack:</DIV><DIV CLASS=td><SELECT NAME=rack_info_rack_id>"
 for rack in dev['infra']['racks']:
  extra = " selected" if ((dev['racked'] == 0 and rack['id'] == 'NULL') or (dev['racked'] == 1 and dev['rack']['rack_id'] == rack['id'])) else ""
  print "<OPTION VALUE={0} {1}>{2}</OPTION>".format(rack['id'],extra,rack['name'])
 print "</SELECT></DIV></DIV>"
 if dev['racked'] == 1 and not dev['info']['type_base'] == 'pdu':
  if not dev['info']['type_base'] == 'controlplane':
   print "<DIV CLASS=tr><DIV CLASS=td>Rack Size:</DIV><DIV CLASS=td><INPUT NAME=rack_info_rack_size TYPE=TEXT PLACEHOLDER='{}'></DIV></DIV>".format(dev['rack']['rack_size'])
   print "<DIV CLASS=tr><DIV CLASS=td>Rack Unit:</DIV><DIV CLASS=td TITLE='Top rack unit of device placement'><INPUT NAME=rack_info_rack_unit TYPE=TEXT PLACEHOLDER='{}'></DIV></DIV>".format(dev['rack']['rack_unit'])
  if not dev['info']['type_base'] == 'console':
   print "<DIV CLASS=tr><DIV CLASS=td>TS:</DIV><DIV CLASS=td><SELECT NAME=rack_info_console_id>"
   for console in dev['infra']['consoles']:
    extra = " selected='selected'" if (dev['rack']['console_id'] == console['id']) or (not dev['rack']['console_id'] and console['id'] == 'NULL') else ""
    print "<OPTION VALUE={0} {1}>{2}</OPTION>".format(console['id'],extra,console['hostname'])
   print "</SELECT></DIV></DIV>"
   print "<DIV CLASS=tr><DIV CLASS=td>TS Port:</DIV><DIV CLASS=td TITLE='Console port in rack TS'><INPUT NAME=rack_info_console_port TYPE=TEXT PLACEHOLDER='{}'></DIV></DIV>".format(dev['rack']['console_port'])
  if not dev['info']['type_base'] == 'controlplane':
   for pem in ['pem0','pem1']:
    print "<DIV CLASS=tr><DIV CLASS=td>{0} PDU:</DIV><DIV CLASS=td><SELECT NAME=rack_info_{1}_pdu_slot_id>".format(pem.upper(),pem)
    for pdu in dev['infra']['pdus']:
     pdu_info = dev['infra']['pdu_info'].get(str(pdu['id']))
     if pdu_info:
      for slotid in range(0,pdu_info['slots']):
       pdu_slot_id   = pdu_info[str(slotid)+"_slot_id"]
       pdu_slot_name = pdu_info[str(slotid)+"_slot_name"]
       extra = "selected" if ((dev['rack'][pem+"_pdu_id"] == pdu['id']) and (dev['rack'][pem+"_pdu_slot"] == slotid)) or (not dev['rack'][pem+"_pdu_id"] and  pdu['id'] == 'NULL') else ""
       print "<OPTION VALUE=%s.%s %s>%s</OPTION>"%(pdu['id'],slotid, extra, pdu['hostname']+":"+pdu_slot_name)
    print "</SELECT></DIV></DIV>"
    print "<DIV CLASS=tr><DIV CLASS=td>{0} Unit:</DIV><DIV CLASS=td><INPUT NAME=rack_info_{1}_pdu_unit TYPE=TEXT PLACEHOLDER='{2}'></DIV></DIV>".format(pem.upper(),pem,dev['rack'][pem + "_pdu_unit"])
 print "<DIV CLASS=tr><DIV CLASS=td>&nbsp;</DIV><DIV CLASS=td>&nbsp;</DIV></DIV>"
 print "<!-- Text fields -->"
 print "<DIV CLASS='tr even'><DIV CLASS=td>Comments:</DIV><DIV CLASS=td><INPUT CLASS=odd TYPE=TEXT NAME=devices_comment VALUE='%s'></DIV></DIV>"%("" if not dev['info']['comment'] else dev['info']['comment'].encode("utf-8"))
 print "<DIV CLASS='tr even'><DIV CLASS=td>Web page:</DIV><DIV CLASS=td><INPUT CLASS=odd TYPE=TEXT NAME=devices_webpage VALUE='%s'></DIV></DIV>"%("" if not dev['info']['webpage'] else dev['info']['webpage'])
 print "<DIV CLASS='tr even'><DIV CLASS=td STYLE='font-style:italic'>Result:  </DIV><DIV CLASS=td ID=update_results>%s</DIV></DIV>"%str(dev.get('result',''))
 print "</DIV></DIV></DIV>"
 print "</FORM><DIV CLASS=controls>"
 print aWeb.button('reload',DIV='div_content_right',URL='zdcp.cgi?device_update&id=%i'%dev['id'])
 print aWeb.button('back',  DIV='div_content_right',URL='zdcp.cgi?device_info&id=%i'%dev['id'])
 print aWeb.button('trash', DIV='div_content_right',URL='zdcp.cgi?device_delete&id=%i'%dev['id'], MSG='Are you sure you want to delete device?', TITLE='Delete device',SPIN='true')
 print aWeb.button('save',  DIV='div_content_right',URL='zdcp.cgi?device_update&op=update', FRM='info_form', TITLE='Save Device Information')
 print "</DIV></ARTICLE>"

#
#
def update_ip(aWeb):
 print "<ARTICLE>"
 print "To Be Done"
 print "</ARTICLE>"

#
#
def delete(aWeb):
 res = aWeb.rest_call("device_delete",{ 'id':aWeb['id'] })
 print "<ARTICLE>Unit {} deleted, op:{}</ARTICLE>".format(aWeb['id'],res)

####################################################### Functions #######################################################
#
#
def to_console(aWeb):
 res = aWeb.rest_call("device_info&op=basics",{'id':aWeb['id']})
 aWeb.put_redirect("%s&title=%s"%(res['url'],aWeb['name']))

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
  from zdcp.core import genlib as GL
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
  print aWeb.rest_call("ipam_address_find",{'network_id':network})['ip']
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
  if aWeb['rack']:
   print "<INPUT TYPE=HIDDEN NAME=rack VALUE={}>".format(aWeb['rack'])
  else:
   print "<DIV CLASS=tr><DIV CLASS=td>VM:</DIV><DIV  CLASS=td><INPUT NAME=vm  TYPE=CHECKBOX VALUE=1  {0} ></DIV></DIV>".format("checked" if aWeb['target'] == 'vm' else '')
  print "</DIV></DIV>"
  print "</FORM><DIV CLASS=controls>"
  print aWeb.button('start', DIV='device_span', URL='zdcp.cgi?device_new&op=new',  FRM='device_new_form', TITLE='Create')
  print aWeb.button('search',DIV='device_ip',   URL='zdcp.cgi?device_new&op=find', FRM='device_new_form', TITLE='Find IP',INPUT='True')
  print "</DIV><SPAN CLASS='results' ID=device_span STYLE='max-width:400px;'></SPAN>"
  print "</ARTICLE>"

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
  print aWeb.button('start', DIV='div_content_right', SPIN='true', URL='zdcp.cgi?device_discover', FRM='device_discover_form')
  print "</DIV></ARTICLE>"

################################################## interfaces #################################################
#
#
def interface_list(aWeb):
 if   aWeb['op'] == 'delete':
  args = aWeb.get_args2dict()
  opres = aWeb.rest_call("device_interface_delete",args)
 elif aWeb['op'] == 'discover':
  opres = aWeb.rest_call("device_interface_discover",{'device':aWeb['device']})
 elif aWeb['op'] == 'link':
  opres = aWeb.rest_call("device_interface_link",{'a_id':aWeb['id'],'b_id':aWeb['peer_interface']})
 else:
  opres = ""
 res = aWeb.rest_call("device_interface_list",{'device':aWeb['device']})
 print "<ARTICLE><P>Interfaces (%s)</P><DIV CLASS='controls'>"%(res['hostname'])
 print aWeb.button('reload', DIV='div_dev_data',URL='zdcp.cgi?device_interface_list&device=%s'%res['id'])
 print aWeb.button('add',    DIV='div_dev_data',URL='zdcp.cgi?device_interface_info&device=%s&id=new'%res['id'])
 print aWeb.button('search', DIV='div_dev_data',URL='zdcp.cgi?device_interface_list&device=%s&op=discover'%res['id'], SPIN='true', MSG='Rediscover interfaces?')
 print aWeb.button('trash',  DIV='div_dev_data',URL='zdcp.cgi?device_interface_list&device=%s&op=delete'%res['id'], MSG='Delete interfaces?', FRM='interface_list', TITLE='Delete selected interfaces')
 print "<A CLASS='z-op btn small text' DIV=div_dev_data URL='zdcp.cgi?device_interface_list&device=%(id)s&op=delete&device_id=%(id)s' TITLE='Clean up empty interfaces' SPIN=true>Cleanup</A>"%res
 print "</DIV><SPAN CLASS=results>%s</SPAN><FORM ID=interface_list>"%(opres)
 print "<DIV CLASS=table>"
 print "<DIV CLASS=thead><DIV CLASS=th>Id</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>Description</DIV><DIV CLASS=th>SNMP Index</DIV><DIV CLASS=th>Peer interface</DIV><DIV CLASS=th>&nbsp;</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for row in res['data']:
  print "<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td><DIV CLASS=controls>"%(row['id'],row['name'],row['description'],row['snmp_index'],row['peer_interface'] if not row['multipoint'] else 'multipoint')
  print "<INPUT TYPE=CHECKBOX VALUE=1 NAME='interface_%s'>"%row['id']
  print aWeb.button('info',  DIV='div_dev_data',URL='zdcp.cgi?device_interface_info&device=%s&id=%s'%(aWeb['device'],row['id']))
  print aWeb.button('sync',  DIV='div_dev_data',URL='zdcp.cgi?device_interface_link_device&device=%s&id=%s&name=%s'%(aWeb['device'],row['id'],row['name']), TITLE='Connect')
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
  print "<DIV CLASS=tr><DIV CLASS=td>Peer Device</DIV><DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL=zdcp.cgi?device_info&id=%s>%s</A></DIV></DIV>"%(data['peer_device'],data['peer_device'])
 print "</DIV></DIV>"
 print "</FORM><DIV CLASS=controls>"
 print aWeb.button('back', DIV='div_dev_data', URL='zdcp.cgi?device_interface_list&device=%s'%data['device'])
 print aWeb.button('save', DIV='div_dev_data', URL='zdcp.cgi?device_interface_info&op=update', FRM='interface_info_form')
 if data['id'] != 'new':
  print aWeb.button('trash', DIV='div_dev_data', URL='zdcp.cgi?device_interface_list&op=delete&device=%s&id=%s'%(data['device'],data['id']), MSG='Delete interface?')
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
 print aWeb.button('back',    DIV='div_dev_data', URL='zdcp.cgi?device_interface_list&device=%s'%aWeb['device'])
 print aWeb.button('forward', DIV='div_dev_data', URL='zdcp.cgi?device_interface_link_interface', FRM='interface_link')
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
 print aWeb.button('back',    DIV='div_dev_data', URL='zdcp.cgi?device_interface_link_device', FRM='interface_link')
 print aWeb.button('forward', DIV='div_dev_data', URL='zdcp.cgi?device_interface_list&op=link', FRM='interface_link')
 print "</DIV></ARTICLE>"
