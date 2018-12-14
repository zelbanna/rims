"""HTML5 Ajax Device module"""
__author__= "Zacharias El Banna"

########################################## Device Operations ##########################################
#
#
def main(aWeb):
 aWeb.wr("<NAV><UL>")
 aWeb.wr("<LI CLASS='dropdown'><A>Devices</A><DIV CLASS='dropdown-content'>")
 aWeb.wr("<A CLASS=z-op DIV=div_content_left URL='device_list?{0}'>List</A>".format(aWeb.get_args()))
 aWeb.wr("<A CLASS=z-op DIV=div_content_left URL='device_search'>Search</A>")
 aWeb.wr("<A CLASS=z-op DIV=div_content_left URL='device_type_list'>Types</A>")
 aWeb.wr("<A CLASS=z-op DIV=div_content_left URL='device_model_list'>Models</A>")
 aWeb.wr("</DIV></LI>")
 aWeb.wr("<LI><A CLASS=z-op DIV=div_content_left URL='visualize_list'>Maps</A></LI>")
 if aWeb['rack']:
  data = aWeb.rest_call("rack/inventory",{'id':aWeb['rack']})
  for type in ['pdu','console']:
   if len(data[type]) > 0:
    aWeb.wr("<LI CLASS='dropdown'><A>%s</A><DIV CLASS='dropdown-content'>"%(type.title()))
    for row in data[type]:
     aWeb.wr("<A CLASS=z-op DIV=div_content_left SPIN=true URL='%s_inventory?id=%s'>%s</A>"%(row['type'],row['id'],row['hostname']))
    aWeb.wr("</DIV></LI>")
  if data.get('name'):
   aWeb.wr("<LI><A CLASS='z-op' DIV=div_content_right  URL='racks_inventory?rack=%s'>'%s'</A></LI>"%(aWeb['rack'],data['name']))
 aWeb.wr("<LI CLASS='dropdown'><A>OUI</A><DIV CLASS='dropdown-content'>")
 aWeb.wr("<A CLASS=z-op DIV=div_content_right URL='device_oui_search'>Search</A>")
 aWeb.wr("<A CLASS=z-op DIV=div_content_right URL='device_oui_list' SPIN=true>List</A>")
 aWeb.wr("</DIV></LI>")
 aWeb.wr("<LI><A CLASS='z-op reload' DIV=main URL='device_main?{}'></A></LI>".format(aWeb.get_args()))
 aWeb.wr("<LI CLASS='right'><A CLASS=z-op DIV=div_content URL='reservations_list'>Reservations</A></LI>")
 aWeb.wr("<LI CLASS='right'><A CLASS=z-op DIV=div_content_left URL='locations_list'>Locations</A></LI>")
 aWeb.wr("<LI CLASS='right dropdown'><A>IPAM</A><DIV CLASS='dropdown-content'>")
 aWeb.wr("<A CLASS=z-op DIV=div_content      URL='servers_list?type=DHCP'>Servers</A>")
 aWeb.wr("<A CLASS=z-op DIV=div_content_left URL='ipam_network_list'>Networks</A>")
 aWeb.wr("</DIV></LI>")
 aWeb.wr("<LI CLASS='right dropdown'><A>DNS</A><DIV CLASS='dropdown-content'>")
 aWeb.wr("<A CLASS=z-op DIV=div_content      URL='servers_list?type=DNS'>Servers</A>")
 aWeb.wr("<A CLASS=z-op DIV=div_content_left URL='dns_domain_list'>Domains</A>")
 aWeb.wr("</DIV></LI>")
 aWeb.wr("<LI CLASS='right dropdown'><A>Rack</A><DIV CLASS='dropdown-content'>")
 aWeb.wr("<A CLASS=z-op DIV=div_content_left URL='racks_list'>Racks</A>")
 aWeb.wr("<A CLASS=z-op DIV=div_content_left URL='racks_list_infra?type=pdu'>PDUs</A>")
 aWeb.wr("<A CLASS=z-op DIV=div_content_left URL='racks_list_infra?type=console'>Consoles</A>")
 aWeb.wr("</DIV></LI>")
 aWeb.wr("</UL></NAV>")
 aWeb.wr("<SECTION CLASS=content       ID=div_content>")
 aWeb.wr("<SECTION CLASS=content-left  ID=div_content_left></SECTION>")
 aWeb.wr("<SECTION CLASS=content-right ID=div_content_right></SECTION>")
 aWeb.wr("</SECTION>")

#
#
def logs(aWeb):
 args = aWeb.args()
 res = aWeb.rest_call("device/logs",args)
 aWeb.wr("<ARTICLE>")
 aWeb.wr("<PRE>%s</PRE>"%("<BR>".join(res['data'])))
 aWeb.wr("</ARTICLE>")

#
#
def list(aWeb):
 args = aWeb.args()
 args['sort'] = aWeb.get('sort','hostname')
 res = aWeb.rest_call("device/list",args)
 aWeb.wr("<ARTICLE><P>Device List</P>")
 aWeb.wr(aWeb.button('reload', DIV='div_content_left',  URL='device_list?%s'%aWeb.get_args(), TITLE='Reload'))
 aWeb.wr(aWeb.button('items',  DIV='div_content_left',  URL='device_list?sort=%s'%args['sort'], TITLE='List All'))
 aWeb.wr(aWeb.button('search', DIV='div_content_left',  URL='device_search', TITLE='Search'))
 aWeb.wr(aWeb.button('add',    DIV='div_content_right', URL='device_new?%s'%aWeb.get_args(), TITLE='Add device'))
 aWeb.wr(aWeb.button('devices',DIV='div_content_right', URL='device_discover', TITLE='Discover'))
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead>")
 for sort in ['IP','Hostname']:
  aWeb.wr("<DIV CLASS=th><A CLASS=z-op DIV=div_content_left URL='device_list?sort=%s&%s'>%s<SPAN STYLE='font-size:14px; color:%s;'>&darr;</SPAN></A></DIV>"%(sort.lower(),aWeb.get_args(['sort']),sort,"black" if not sort.lower() == args['sort'] else "red"))
 aWeb.wr("<DIV CLASS=th STYLE='width:30px;'>&nbsp;</DIV></DIV><DIV CLASS=tbody>")
 for row in res['data']:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td STYLE='max-width:180px; overflow-x:hidden'><A CLASS=z-op DIV=div_content_right URL='device_info?id=%i' TITLE='%s'>%s</A></DIV><DIV CLASS=td><DIV CLASS='state %s' /></DIV></DIV>"%(row['ip'],row['id'],row['id'], row['hostname'], aWeb.state_ascii(row['state'])))
 aWeb.wr("</DIV></DIV></ARTICLE>")

#
#
def oui_search(aWeb):
 args = aWeb.args()
 aWeb.wr("<ARTICLE>")
 aWeb.wr("<FORM ID=oui_form>Type OUI or MAC address to find OUI/company name: <INPUT CLASS='background' TYPE=TEXT REQUIRED TYPE=TEXT NAME='oui' STYLE='width:100px' VALUE='%s'></FORM>"%args.get('oui','00:00:00'))
 aWeb.wr(aWeb.button('search',  DIV='div_content_right', URL='device_oui_search?op=find',   FRM='oui_form', TITLE='Find OUI'))
 aWeb.wr("</ARTICLE>")
 if args.get('op') == 'find':
  res = aWeb.rest_call("master/oui_info",{'oui':args['oui']})
  aWeb.wr("<ARTICLE CLASS='info'><DIV CLASS=table><DIV CLASS=tbody><DIV CLASS=tr><DIV CLASS=td>OUI:</DIV><DIV CLASS=td>%s</DIV></DIV><DIV CLASS=tr><DIV CLASS=td>Company:</DIV><DIV CLASS=td>%s</DIV></DIV></DIV></DIV></ARTICLE>"%(res['oui'],res['company']))

#
#
def oui_list(aWeb):
 args = aWeb.args()
 res = aWeb.rest_call("master/oui_list",args)
 aWeb.wr("<ARTICLE><P>OUI</P>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Id</DIV><DIV CLASS=th>Company</DIV></DIV><DIV CLASS=tbody>")
 for oui in res['data']:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV></DIV>"%(":".join(oui['oui'][i:i+2] for i in [0,2,4]),oui['company']))
 aWeb.wr("</DIV></DIV></ARTICLE>")

#
#
def report(aWeb):
 args = aWeb.args()
 res = aWeb.rest_call("device/list",{'extra': ['system', 'type', 'mac','oui','class']})
 aWeb.wr("<ARTICLE><P>Devices</P>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Id</DIV><DIV CLASS=th>Device</DIV><DIV CLASS=th>Class</DIV><DIV CLASS=th>IP</DIV><DIV CLASS=th>MAC</DIV><DIV CLASS=th>OUI</DIV><DIV CLASS=th>Model</DIV><DIV CLASS=th>OID</DIV><DIV CLASS=th>Serial</DIV><DIV CLASS=th>State</DIV></DIV><DIV CLASS=tbody>")
 for dev in res['data']:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%(id)s</DIV><DIV CLASS=td>%(hostname)s</DIV><DIV CLASS=td>%(class)s</DIV><DIV CLASS=td>%(ip)s</DIV><DIV CLASS=td>%(mac)s</DIV><DIV CLASS=td>%(oui)s</DIV><DIV CLASS=td>%(model)s</DIV><DIV CLASS=td>%(oid)s</DIV><DIV CLASS=td>%(serial)s</DIV>"%dev)
  aWeb.wr("<DIV CLASS=td><DIV CLASS='state %s' /></DIV></DIV>"%aWeb.state_ascii(dev['state']))
 aWeb.wr("</DIV></DIV></ARTICLE>")

#
#
def search(aWeb):
 aWeb.wr("<ARTICLE><P>Device Search</P>")
 aWeb.wr("<FORM ID='device_search'>")
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=sort VALUE='hostname'>")
 aWeb.wr("<SPAN>Field:</SPAN><SELECT CLASS='background' ID='field' NAME='field'><OPTION VALUE='hostname'>Hostname</OPTION><OPTION VALUE='type'>Type</OPTION><OPTION VALUE='ip'>IP</OPTION><OPTION VALUE='mac'>MAC</OPTION><OPTION VALUE='id'>ID</OPTION><OPTION VALUE='mac'>MAC</OPTION><OPTION VALUE='ipam_id'>IPAM ID</OPTION></SELECT>")
 aWeb.wr("<INPUT CLASS='background' TYPE=TEXT ID='search' NAME='search' STYLE='width:200px' REQUIRED>")
 aWeb.wr("</FORM><DIV CLASS=inline>")
 aWeb.wr(aWeb.button('search', DIV='div_content_left', URL='device_list', FRM='device_search'))
 aWeb.wr("</DIV>")
 aWeb.wr("</ARTICLE>")

#
#
def info(aWeb):
 cookie = aWeb.cookie('rims')
 args = aWeb.args()
 args['extra'] = ['types','classes']
 dev = aWeb.rest_call("device/info",args)
 if not dev['found']:
  aWeb.wr("<ARTICLE>Warning - device with id (%s) does not exist</ARTICLE>"%aWeb.args())
  return
 reservation = aWeb.rest_call("reservation/status",{"device_id":dev['id']})['reservation']
 dev_info = dev['data']
 dev_extra= dev['extra']
 dev_id   = dev['id']
 """ 3 parallell tables """
 width = 700 if (dev.get('rack') and not dev_extra['type_base'] == 'pdu') or dev.get('vm') else 480
 aWeb.wr("<ARTICLE CLASS='info' STYLE='position:relative; height:268px; width:%spx;'><P TITLE='%s'>Device Info</P>"%(width,dev_id))
 aWeb.wr("<FORM ID=info_form>")
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(dev_id))
 aWeb.wr("<!-- Reachability Info -->")
 aWeb.wr("<DIV STYLE='margin:3px; float:left;'><DIV CLASS=table STYLE='width:210px;'><DIV CLASS=tbody>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Name:  </DIV><DIV CLASS='td readonly'>%s</DIV></DIV>"%dev_info['hostname'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>ID:    </DIV><DIV CLASS='td readonly'>%s</DIV></DIV>"%dev_id)
 aWeb.wr("<DIV CLASS=tr><DIV CLASS='td title' title='System MAC'>Sys MAC:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=mac VALUE='%s'></DIV></DIV>"%dev_info['mac'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS='td title' title='Management interface MAC'>Mgmt MAC:</DIV><DIV CLASS='td readonly'>%s</DIV></DIV>"%dev_extra['interface_mac'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Mgmt IP:</DIV><DIV CLASS='td readonly'>%s</DIV></DIV>"%dev_extra['interface_ip'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>SNMP:</DIV><DIV CLASS='td readonly'>%s</DIV></DIV>"%dev_info['snmp'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>State:</DIV><DIV CLASS=td><DIV CLASS='state %s' TITLE='interface' />&nbsp;<DIV CLASS='state %s' TITLE='IP' /></DIV></DIV>"%(aWeb.state_ascii(dev_extra['if_state']),aWeb.state_ascii(dev_extra['ip_state'])))
 aWeb.wr("</DIV></DIV></DIV>")
 aWeb.wr("<!-- Additional info -->")
 aWeb.wr("<DIV STYLE='margin:3px; float:left;'><DIV CLASS=table STYLE='width:227px;'><DIV CLASS=tbody>")
 aWeb.wr("<DIV CLASS=tr ID=div_reservation_info><DIV CLASS=td>Reserve:</DIV>")
 if dev_extra['type_name'] == 'controlplane':
  aWeb.wr("<DIV CLASS=td>N/A</DIV>")
 elif reservation:
  aWeb.wr("<DIV CLASS='td %s'>"%("red" if reservation['valid'] else "orange"))
  aWeb.wr(reservation['alias'] if reservation['user_id'] != int(cookie['id']) else "<A CLASS=z-op DIV=div_reservation_info URL='reservations_update?op=drop&id=%s'>%s</A>"%(dev_id,reservation['alias']))
  aWeb.wr("</DIV>")
 else:
  aWeb.wr("<DIV CLASS='td green'><A CLASS=z-op DIV=div_reservation_info URL='reservations_update?op=reserve&id=%s'>Available</A></DIV>"%dev_id)
 aWeb.wr("</DIV>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Class:</DIV>")
 if dev.get('classes'):
  aWeb.wr("<DIV CLASS=td><SELECT NAME=class>")
  for cls in dev['classes']:
   aWeb.wr("<OPTION VALUE={0} {1}>{0}</OPTION>".format(cls," selected" if dev_info['class'] == cls else ""))
  aWeb.wr("</SELECT></DIV>")
 else:
  aWeb.wr("<DIV CLASS=td>%s</DIV>"%dev_info['class'])
 aWeb.wr("</DIV>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Type:</DIV>")
 if dev.get('types'):
  aWeb.wr("<DIV CLASS=td><SELECT NAME=type_id>")
  for type in dev['types']:
   aWeb.wr("<OPTION VALUE={0} {1}>{2}</OPTION>".format(type['id']," selected" if dev_info['type_id'] == type['id'] else "",type['name']))
  aWeb.wr("</SELECT></DIV>")
 else:
  aWeb.wr("<DIV CLASS=td>%s</DIV>"%dev_extra['type_name'])
 aWeb.wr("</DIV>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Model: </DIV><DIV CLASS=td STYLE='max-width:150px;'><INPUT TYPE=TEXT NAME=model VALUE='%s'></DIV></DIV>"%(dev_info['model']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Version:</DIV><DIV CLASS='td readonly'>%s</DIV></DIV>"%dev_info['version'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>S/N: </DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=serial VALUE='%s'></DIV></DIV>"%(dev_info['serial']))
 aWeb.wr("</DIV></DIV></DIV>")
 if dev.get('rack') and not dev_extra['type_base'] == 'pdu':
  aWeb.wr("<!-- Rack Info -->")
  aWeb.wr("<DIV STYLE='margin:3px; float:left;'><DIV CLASS=table STYLE='width:230px;'><DIV CLASS=tbody>")
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Rack/Pos: </DIV><DIV CLASS=td>%s (%s)</DIV></DIV>"%(dev['rack']['rack_name'],dev['rack']['rack_unit']))
  if not dev_extra['type_base'] == 'controlplane':
   aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Size:    </DIV><DIV CLASS=td>%s U</DIV></DIV>"%(dev['rack']['rack_size']))
  if not dev_extra['type_base'] == 'console':
   aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>TS/Port: </DIV><DIV CLASS=td>%s (%s)</DIV></DIV>"%(dev['rack']['console_name'],dev['rack']['console_port']))
  for count,pem in enumerate(dev['pems'],0):
   if count < 4:
    aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%s PDU: </DIV><DIV CLASS=td>%s (%s)</DIV></DIV>"%(pem['name'],pem['pdu_name'], pem['pdu_unit']))
  aWeb.wr("</DIV></DIV></DIV>")
 elif dev.get('vm'):
  aWeb.wr("<!-- VM Info -->")
  aWeb.wr("<DIV STYLE='margin:3px; float:left;'><DIV CLASS=table STYLE='max-width:230px;'><DIV CLASS=tbody>")
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>VM Name:</DIV><DIV CLASS='td readonly small-text' STYLE='max-width:170px;'>%s</DIV></DIV>"%dev['vm']['name'])
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>VM Host:</DIV><DIV CLASS='td readonly small-text' STYLE='max-width:170px;'>%s</DIV></DIV>"%dev['vm']['host'])
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td TITLE='Device UUID'>UUID:</DIV><DIV CLASS='td readonly small-text' STYLE='max-width:170px;'>%s</DIV></DIV>"%dev['vm']['device_uuid'])
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td TITLE='Management UUID'>MGMT:</DIV><DIV CLASS='td readonly small-text' STYLE='max-width:170px;'>%s</DIV></DIV>"%dev['vm']['server_uuid'])
  aWeb.wr("<!-- Config: %s -->"%dev['vm']['config'])
  aWeb.wr("</DIV></DIV></DIV>")
 aWeb.wr("<!-- Text fields -->")
 aWeb.wr("<DIV STYLE='display:block; clear:both; margin-bottom:3px; margin-top:1px; width:99%;'><DIV CLASS=table><DIV CLASS=tbody>")
 aWeb.wr("<DIV CLASS='tr even'><DIV CLASS=td>Comments:</DIV><DIV CLASS=td><INPUT CLASS=odd TYPE=TEXT NAME=comment VALUE='{}'></DIV></DIV>".format("" if not dev_info['comment'] else dev_info['comment']))
 aWeb.wr("<DIV CLASS='tr even'><DIV CLASS=td>Web UI:</DIV><DIV CLASS=td><INPUT CLASS=odd TYPE=TEXT NAME=url VALUE='{}'></DIV></DIV>".format("" if not dev_info['url'] else dev_info['url']))
 aWeb.wr("</DIV></DIV></DIV>")
 aWeb.wr("</FORM>")
 aWeb.wr(aWeb.button('reload',     DIV='div_content_right',URL='device_info?id=%i'%dev_id))
 aWeb.wr(aWeb.button('save',       DIV='div_content_right',URL='device_info?op=update', FRM='info_form', TITLE='Save Basic Device Information'))
 aWeb.wr(aWeb.button('trash',      DIV='div_content_right',URL='device_delete?id=%i'%dev_id, MSG='Are you sure you want to delete device?', TITLE='Delete device',SPIN='true'))
 aWeb.wr(aWeb.button('edit',       DIV='div_content_right',URL='device_extended?id=%i'%dev_id, TITLE='Extended Device Information'))
 aWeb.wr(aWeb.button('connections',DIV='div_dev_data',     URL='device_interface_list?device_id=%i'%(dev_id),TITLE='Device interfaces'))
 aWeb.wr(aWeb.button('start',      DIV='div_dev_data',     URL='device_control?id=%s'%dev_id, TITLE='Device Control'))
 aWeb.wr(aWeb.button('document',   DIV='div_dev_data',     URL='device_conf_gen?id=%i'%(dev_id),TITLE='Generate System Conf'))
 if dev_extra['interface_ip']:
  aWeb.wr(aWeb.button('search',    DIV='div_content_right',URL='device_info?id=%i&op=lookup'%dev_id, TITLE='Lookup and Detect Device information', SPIN='true'))
  aWeb.wr(aWeb.button('logs',      DIV='div_dev_data',     URL='device_logs?id=%i'%(dev_id),TITLE='Device logs'))
 aWeb.wr(aWeb.button('network',    DIV='div_content_right',URL='visualize_network?type=device&id=%s'%(dev_id), SPIN='true', TITLE='Network map'))
 if dev_extra['interface_ip']:
  aWeb.wr(aWeb.button('term',TITLE='SSH',HREF='ssh://%s@%s'%(dev_extra['username'],dev_extra['interface_ip'])))
 if dev.get('rack') and dev['rack'].get('console_ip') and dev['rack'].get('console_port'):
  # Hardcoded port to 60xx
  aWeb.wr(aWeb.button('term',TITLE='Console', HREF='telnet://%s:%i'%(dev['rack']['console_ip'],6000+dev['rack']['console_port'])))
 if dev_info.get('url'):
  aWeb.wr(aWeb.button('ui',TITLE='WWW', TARGET='_blank', HREF=dev_info['url']))
 aWeb.wr("<SPAN CLASS='results' ID=update_results>%s</SPAN>"%str(dev.get('update','')))
 aWeb.wr("</ARTICLE>")
 aWeb.wr("<!-- Function navbar and content -->")
 aWeb.wr("<NAV><UL>")
 for fun in dev_extra['functions'].split(','):
  if fun == 'manage':
   aWeb.wr("<LI><A CLASS=z-op DIV=main URL='%s_manage?id=%i'>Manage</A></LI>"%(dev_extra['type_name'],dev_id))
  else:
   aWeb.wr("<LI><A CLASS=z-op DIV=div_dev_data SPIN=true URL='device_function?id=%s&ip=%s&type=%s&op=%s'>%s</A></LI>"%(dev_id, dev_extra['interface_ip'], dev_extra['type_name'], fun, fun.title()))
 aWeb.wr("</UL></NAV>")
 aWeb.wr("<SECTION CLASS='content' ID=div_dev_data STYLE='top:308px; overflow-x:hidden; overflow-y:auto;'></SECTION>")

####################################### UPDATE INFO ###################################
#
#
def extended(aWeb):
 args = aWeb.args()
 dev  = aWeb.rest_call("device/extended",args)
 domains = aWeb.rest_call("dns/domain_list",{'filter':'forward'})['domains']
 dev_info = dev['data']
 dev_extra= dev['extra']
 aWeb.wr("<ARTICLE CLASS='info' STYLE='min-width:800px;'><P>Extended Info</P>")
 aWeb.wr("<FORM ID=info_form>")
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(dev['id']))
 aWeb.wr("<!-- Reachability Info -->")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=tbody>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Name:</DIV><DIV CLASS=td><INPUT NAME=hostname TYPE=TEXT VALUE='%s'></DIV></DIV>"%(dev_info['hostname']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Priv OID:</DIV><DIV CLASS='td readonly'>.1.3.6.1.4.1.%s</DIV></DIV>"%dev_extra['oid'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Mgmt OUI:  </DIV><DIV CLASS='td readonly'>%s</DIV></DIV>"%dev_extra['oui'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Mgmt Interface:</DIV><DIV CLASS=td><SELECT NAME=management_id>")
 for intf in dev['interfaces']:
  extra = " selected" if ((dev_info['management_id'] is None and intf['interface_id'] == 'NULL') or (dev_info['management_id'] == intf['interface_id'])) else ""
  aWeb.wr("<OPTION VALUE={0} {1}>{2} ({3} - {4})</OPTION>".format(intf['interface_id'],extra,intf['name'],intf['ip'],intf['fqdn']))
 aWeb.wr("</SELECT></DIV></DIV>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>MGMT Domain:</DIV><DIV CLASS=td><SELECT NAME=a_domain_id>")
 for dom in domains:
  extra = " selected" if dev_extra['management_domain'] == dom['id'] or dev_extra['management_domain'] is None and dom['id'] == 0 else ""
  aWeb.wr("<OPTION VALUE='%s' %s>%s</OPTION>"%(dom['id'],extra,dom['name']))
 aWeb.wr("</SELECT></DIV></DIV>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>&nbsp;</DIV><DIV CLASS=td><CENTER>Device-Unique Data Points<CENTER></DIV><DIV CLASS=td>")
 aWeb.wr(aWeb.button('add',   DIV='div_content_right',URL='device_extended?op=add_ddp&id=%s'%(dev['id']), TITLE='Add data point'))
 aWeb.wr("</DIV></DIV>")
 for stat in dev['data_points']:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td TITLE='%s'>Data Point:</DIV><DIV CLASS=td>"%stat['id'])
  aWeb.wr("<INPUT TYPE=TEXT NAME=ddp_%(id)s_measurement VALUE='%(measurement)s' PLACEHOLDER='measurement' TITLE='measurement' STYLE='width:unset;'>"%stat)
  aWeb.wr("<INPUT TYPE=TEXT NAME=ddp_%(id)s_tags VALUE='%(tags)s' PLACEHOLDER='tags' TITLE='tags' STYLE='width:unset;'>"%stat)
  aWeb.wr("<INPUT TYPE=TEXT NAME=ddp_%(id)s_name VALUE='%(name)s' PLACEHOLDER='name' TITLE='name' STYLE='width:unset;'>"%stat)
  aWeb.wr("<INPUT TYPE=TEXT NAME=ddp_%(id)s_oid VALUE='%(oid)s' PLACEHOLDER='oid' TITLE='OID' STYLE='width:30%%;'>"%stat)
  aWeb.wr("</DIV><DIV CLASS=td>")
  aWeb.wr(aWeb.button('delete',DIV='div_content_right',URL='device_extended?op=remove_ddp&id=%s&ddp_id=%s'%(dev['id'],stat['id']), TITLE='Remove data point'))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>&nbsp;</DIV><DIV CLASS=td>&nbsp;</DIV></DIV>")
 aWeb.wr("<!-- Rack Info -->")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Rack:</DIV><DIV CLASS=td><SELECT NAME=rack_info_rack_id>")
 for rack in dev['infra']['racks']:
  extra = " selected" if ((not dev.get('rack') and rack['id'] == 'NULL') or (dev.get('rack') and dev['rack']['rack_id'] == rack['id'])) else ""
  aWeb.wr("<OPTION VALUE={0} {1}>{2}</OPTION>".format(rack['id'],extra,rack['name']))
 aWeb.wr("</SELECT></DIV></DIV>")
 if dev.get('rack') and not dev_extra['type_base'] == 'pdu':
  if not dev_extra['type_base'] == 'controlplane':
   aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Rack Size:</DIV><DIV CLASS=td><INPUT NAME=rack_info_rack_size TYPE=TEXT VALUE='{}'></DIV></DIV>".format(dev['rack']['rack_size']))
   aWeb.wr("<DIV CLASS=tr><DIV CLASS=td TITLE='Top rack unit of device placement'>Rack Unit:</DIV><DIV CLASS=td><INPUT NAME=rack_info_rack_unit TYPE=TEXT VALUE='{}'></DIV></DIV>".format(dev['rack']['rack_unit']))
  if not dev_extra['type_base'] == 'console':
   aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>TS:</DIV><DIV CLASS=td><SELECT NAME=rack_info_console_id>")
   for console in dev['infra']['consoles']:
    extra = " selected='selected'" if (dev['rack']['console_id'] == console['id']) or (not dev['rack']['console_id'] and console['id'] == 'NULL') else ""
    aWeb.wr("<OPTION VALUE={0} {1}>{2}</OPTION>".format(console['id'],extra,console['hostname']))
   aWeb.wr("</SELECT></DIV></DIV>")
   aWeb.wr("<DIV CLASS=tr><DIV CLASS=td TITLE='Console port in rack TS'>TS Port:</DIV><DIV CLASS=td><INPUT NAME=rack_info_console_port TYPE=TEXT VALUE='{}'></DIV></DIV>".format(dev['rack']['console_port']))
  if not dev_extra['type_base'] == 'controlplane':
   aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>&nbsp;</DIV><DIV CLASS=td><CENTER>Power Entry Modules<CENTER></DIV><DIV CLASS=td>")
   aWeb.wr(aWeb.button('add',DIV='div_content_right',URL='device_extended?op=add_pem&id=%s'%(dev['id']), TITLE='Add PEM'))
   aWeb.wr("</DIV></DIV>")
   for pem in dev['pems']:
    aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>PEM:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=pems_%(id)s_name VALUE='%(name)s'></DIV><DIV CLASS=td>"%(pem))
    aWeb.wr(aWeb.button('delete',DIV='div_content_right',URL='device_extended?op=remove_pem&id=%s&pem_id=%s'%(dev['id'],pem['id']), TITLE='Remove PEM'))
    aWeb.wr("</DIV></DIV>")
    aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>PDU:</DIV><DIV CLASS=td><SELECT NAME=pems_%(id)s_pdu_slot>"%pem)
    for pdu in dev['infra']['pdus']:
     pdu_info = dev['infra']['pdu_info'].get(str(pdu['id']))
     if pdu_info:
      for slotid in range(0,pdu_info['slots']):
       pdu_slot_id   = pdu_info["%s_slot_id"%slotid]
       pdu_slot_name = pdu_info["%s_slot_name"%slotid]
       extra = "selected" if ((pem['pdu_id'] == pdu['id']) and (pem['pdu_slot'] == slotid)) or (not pem['pdu_id'] and pdu['id'] == 'NULL') else ""
       aWeb.wr("<OPTION VALUE=%s.%s %s>%s</OPTION>"%(pdu['id'],slotid, extra, pdu['hostname']+":"+pdu_slot_name))
    aWeb.wr("</SELECT></DIV></DIV>")
    aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Unit:</DIV><DIV CLASS=td><INPUT NAME=pems_%s_pdu_unit TYPE=TEXT VALUE='%s'></DIV></DIV>"%(pem['id'],pem['pdu_unit']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>&nbsp;</DIV><DIV CLASS=td>&nbsp;</DIV></DIV>")
 aWeb.wr("</DIV></DIV></FORM>")
 aWeb.wr(aWeb.button('reload',DIV='div_content_right',URL='device_extended?id=%s'%dev['id']))
 aWeb.wr(aWeb.button('back',  DIV='div_content_right',URL='device_info?id=%s'%dev['id']))
 aWeb.wr(aWeb.button('save',  DIV='div_content_right',URL='device_extended?op=update', FRM='info_form', TITLE='Save Device Information'))
 aWeb.wr("<SPAN CLASS='results' ID=update_results>%s</SPAN>"%str(dev.get('result','')))
 aWeb.wr("</ARTICLE>")

#
#
def control(aWeb):
 args = aWeb.args()
 res = aWeb.rest_call("device/control",args)
 aWeb.wr("<ARTICLE CLASS='info'><P>Device Controls</P>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=tbody>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Reboot:</DIV><DIV CLASS=td>&nbsp;")
 aWeb.wr(aWeb.button('revert', DIV='div_dev_data', SPIN='true', URL='device_control?id=%s&dev_op=reboot'%res['id'], MSG='Really reboot device?', TITLE='reboot device'))
 aWeb.wr("</DIV><DIV CLASS=td>%s</DIV></DIV>"%(res.get('dev_op') if args.get('dev_op') == 'reboot' else '&nbsp;'))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Shutdown:</DIV><DIV CLASS=td>&nbsp;")
 aWeb.wr(aWeb.button('off', DIV='div_dev_data', SPIN='true', URL='device_control?id=%s&dev_op=shutdown'%res['id'], MSG='Really shutdown device?', TITLE='Shutdown device'))
 aWeb.wr("</DIV><DIV CLASS=td>%s</DIV></DIV>"%(res.get('dev_op') if args.get('dev_op') == 'shutdown' else '&nbsp;'))
 for pem in res.get('pems',[]):
  aWeb.wr("<!-- %(pdu_type)s@%(pdu_ip)s:%(pdu_slot)s/%(pdu_unit)s -->"%pem)
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>PEM: %s</DIV><DIV CLASS=td>&nbsp;"%pem['name'])
  if   pem['state'] == 'off':
   aWeb.wr(aWeb.button('start', DIV='div_dev_data', SPIN='true', URL='device_control?id=%s&pem_id=%s&pem_op=on'%(res['id'],pem['id'])))
  elif pem['state'] == 'on':
   aWeb.wr(aWeb.button('stop',  DIV='div_dev_data', SPIN='true', URL='device_control?id=%s&pem_id=%s&pem_op=off'%(res['id'],pem['id'])))
  else:
   aWeb.wr(aWeb.button('help', TITLE='Unknown state'))
  aWeb.wr("</DIV><DIV CLASS=td>%s</DIV></DIV>"%(pem.get('op',{'status':'&nbsp;'})['status']))
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</ARTICLE>")

#
#
def delete(aWeb):
 res = aWeb.rest_call("device/delete",{ 'id':aWeb['id'] })
 aWeb.wr("<ARTICLE>Unit {} deleted, op:{}</ARTICLE>".format(aWeb['id'],res))

#
#
def type_list(aWeb):
 res = aWeb.rest_call("device/type_list")
 aWeb.wr("<ARTICLE><P>Device Types<P>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Class</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>Icon</DIV></DIV><DIV CLASS=tbody>")
 for tp in res['types']:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td><A CLASS=z-op DIV=div_content_left URL='device_list?field=type&search=%s'>%s</A></DIV><DIV CLASS=td>%s</DIV></DIV>"%(tp['base'],tp['name'],tp['name'],tp['icon'].rpartition('/')[2]))
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</ARTICLE>")

#
#
def model_list(aWeb):
 args = aWeb.args()
 res = aWeb.rest_call("device/model_list",args)
 aWeb.wr("<ARTICLE><P>Device Models<P>")
 aWeb.wr(aWeb.button('reload',DIV='div_content_left',  URL='device_model_list'))
 aWeb.wr(aWeb.button('sync',  DIV='div_content_left',  URL='device_model_list?op=sync', TITLE='ReSync models'))
 aWeb.wr("<SPAN CLASS='results' ID=device_span STYLE='max-width:400px;'>%s</SPAN>"%res.get('status',""))
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Id</DIV><DIV CLASS=th>Model</DIV><DIV CLASS=th>Type</DIV><DIV CLASS=th>&nbsp;</DIV></DIV><DIV CLASS=tbody>")
 for row in res['models']:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%(id)s</DIV><DIV CLASS=td>%(name)s</DIV><DIV CLASS=td>%(type)s</DIV><DIV CLASS=td>"%row)
  aWeb.wr(aWeb.button('info', DIV='div_content_right', URL='device_model_info?id=%s'%row['id']))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</ARTICLE>")

#
#
def model_info(aWeb):
 args = aWeb.args()
 res = aWeb.rest_call("device/model_info",args)
 aWeb.wr("<ARTICLE CLASS='info'><P>Device Model<P>")
 aWeb.wr("<FORM ID='device_model_info_form'>")
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=id VALUE='%s'>"%res['data']['id'])
 aWeb.wr("<DIV CLASS=table><DIV CLASS=tbody>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Name:</DIV><DIV CLASS='td readonly'>%s</DIV></DIV>"%res['data']['name'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Type:</DIV><DIV CLASS='td readonly'>%s</DIV></DIV>"%res['data']['type'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Defaults File:</DIV><DIV CLASS=td><INPUT NAME=defaults_file TYPE=TEXT VALUE='%s' STYLE='min-width:400px'></DIV></DIV>"%res['data']['defaults_file'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Image File:</DIV><DIV CLASS=td><INPUT NAME=image_file    TYPE=TEXT VALUE='%s'></DIV></DIV>"%res['data']['image_file'])
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("<LABEL FOR=parameters>Parameters:</LABEL><TEXTAREA CLASS='maxed' ID=parameters NAME=parameters STYLE='height:400px'>%s</TEXTAREA>"%res['data']['parameters'])
 aWeb.wr("</FORM>")
 aWeb.wr(aWeb.button('save',    DIV='div_content_right', URL='device_model_info?op=update', FRM='device_model_info_form', TITLE='Save'))
 aWeb.wr("</ARTICLE>")

#
#
def logs(aWeb):
 args = aWeb.args()
 res = aWeb.rest_call("device/logs_get",args)
 aWeb.wr("<ARTICLE>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Time</DIV><DIV CLASS=th>Event</DIV></DIV><DIV CLASS=tbody>")
 for row in res['logs']:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%(time)s</DIV><DIV CLASS=td>%(message)s</DIV></DIV>"%row)
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</ARTICLE>")



####################################################### Functions #######################################################
#
#
def to_console(aWeb):
 res = aWeb.rest_call("device/management",{'id':aWeb['id']})
 aWeb.wr("<SCRIPT> window.location.replace('%s&title=%s'); </SCRIPT>"%(res['data']['url'],aWeb['name']))

#
#
def conf_gen(aWeb):
 aWeb.wr("<ARTICLE>")
 res = aWeb.rest_call("device/configuration_template",{'id':aWeb['id']})
 if res['status'] == 'OK':
  aWeb.wr("<BR>".join(res['data']))
 else:
  aWeb.wr("<B>%s</B>"%res['info'])
 aWeb.wr("</ARTICLE>")

#
#
def function(aWeb):
 aWeb.wr("<ARTICLE>")
 res = aWeb.rest_call("device/function",aWeb.args())
 if res['status'] == 'OK':
  if len(res['data']) > 0:
   aWeb.wr("<DIV CLASS=table><DIV CLASS=thead>")
   head = res['data'][0].keys()
   for th in head:
    aWeb.wr("<DIV CLASS=th>%s</DIV>"%(th.title()))
   aWeb.wr("</DIV><DIV CLASS=tbody>")
   for row in res['data']:
    aWeb.wr("<DIV CLASS=tr>")
    for td in head:
     aWeb.wr("<DIV CLASS=td>%s</DIV>"%(row.get(td,'&nbsp;')))
    aWeb.wr("</DIV>")
   aWeb.wr("</DIV></DIV>")
  else:
   aWeb.wr("No data")
 else:
  aWeb.wr("<B>Error in devdata: %s</B>"%res['info'])
 aWeb.wr("</ARTICLE>")

#
#
def new(aWeb):
 ip   = aWeb.get('ip')
 name = aWeb.get('hostname','unknown')
 mac  = aWeb.get('mac',"00:00:00:00:00:00")
 cls  = aWeb.get('class','device')
 dom  = aWeb.get('a_domain_id','NULL')
 op   = aWeb['op']
 network = aWeb['ipam_network_id']
 if not ip and aWeb['ipint']:
  def int2ip(addr):
   from struct import pack
   from socket import inet_ntoa
   return inet_ntoa(pack("!I", addr))
  ip = int2ip(int(aWeb['ipint']))

 if op == 'new':
  args = { 'ip':ip, 'mac':mac, 'hostname':name, 'class':cls, 'ipam_network_id':network, 'a_domain_id':dom}
  res = aWeb.rest_call("device/new",args)
  aWeb.wr("Operation:%s"%str(res))
 elif op == 'find':
  aWeb.wr(aWeb.rest_call("ipam/address_find",{'network_id':network})['ip'])
 else:
  domains  = aWeb.rest_call("dns/domain_list",{'filter':'forward'})['domains']
  networks = aWeb.rest_call("ipam/network_list")['networks']
  classes  = aWeb.rest_call("device/class_list")['classes']
  aWeb.wr("<ARTICLE CLASS=info><P>Device Add</P>")
  aWeb.wr("<FORM ID=device_new_form>")
  aWeb.wr("<DIV CLASS=table><DIV CLASS=tbody>")
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Hostname:</DIV><DIV CLASS=td><INPUT NAME=hostname TYPE=TEXT VALUE={}></DIV></DIV>".format(name))
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Class:</DIV><DIV CLASS=td><SELECT  NAME=class>")
  for c in classes:
   aWeb.wr("<OPTION VALUE={0} {1}>{0}</OPTION>".format(c,"selected" if c == cls else ""))
  aWeb.wr("</SELECT></DIV></DIV>")
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Network:</DIV><DIV CLASS=td><SELECT NAME=ipam_network_id>")
  for s in networks:
   aWeb.wr("<OPTION VALUE={} {}>{} ({})</OPTION>".format(s['id'],"selected" if str(s['id']) == network else "", s['netasc'],s['description']))
  aWeb.wr("</SELECT></DIV></DIV>")
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Domain:</DIV><DIV CLASS=td><SELECT NAME=a_domain_id>")
  for d in domains:
   aWeb.wr("<OPTION VALUE={} {}>{}</OPTION>".format(d['id'],"selected" if str(d['id']) == dom else "", d['name']))
  aWeb.wr("</SELECT></DIV></DIV>")
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>IP:</DIV><DIV CLASS=td><INPUT  NAME=ip ID=device_ip TYPE=TEXT VALUE='{}'></DIV></DIV>".format(ip))
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>MAC:</DIV><DIV CLASS=td><INPUT NAME=mac TYPE=TEXT PLACEHOLDER='{0}'></DIV></DIV>".format(mac))
  aWeb.wr("</DIV></DIV>")
  aWeb.wr("</FORM>")
  aWeb.wr(aWeb.button('start', DIV='device_span', URL='device_new?op=new',  FRM='device_new_form', TITLE='Create'))
  aWeb.wr(aWeb.button('search',DIV='device_ip',   URL='device_new?op=find', FRM='device_new_form', TITLE='Find IP',INPUT='True'))
  aWeb.wr("<SPAN CLASS='results' ID=device_span STYLE='max-width:400px;'></SPAN>")
  aWeb.wr("</ARTICLE>")

#
#
def discover(aWeb):
 args = aWeb.args()
 op = args.pop('op',None)
 if op:
  res = aWeb.rest_call("device/discover",args,200)
  aWeb.wr("<ARTICLE>%s</ARTICLE>"%(res))
 else:
  networks = aWeb.rest_call("ipam/network_list")['networks']
  domains = aWeb.rest_call("dns/domain_list",{'filter':'forward'})['domains']
  aWeb.wr("<ARTICLE CLASS=info><P>Device Discovery</P>")
  aWeb.wr("<FORM ID=device_discover_form>")
  aWeb.wr("<INPUT TYPE=HIDDEN NAME=op VALUE=json>")
  aWeb.wr("<DIV CLASS=table><DIV CLASS=tbody>")
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Domain:</DIV><DIV CLASS=td><SELECT NAME=a_domain_id>")
  for d in domains:
   aWeb.wr("<OPTION VALUE=%s>%s</OPTION>"%(d.get('id'),d.get('name')))
  aWeb.wr("</SELECT></DIV></DIV>")
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Network:</DIV><DIV CLASS=td><SELECT NAME=network_id>")
  for s in networks:
   aWeb.wr("<OPTION VALUE=%s>%s (%s)</OPTION>"%(s['id'],s['netasc'],s['description']))
  aWeb.wr("</SELECT></DIV></DIV>")
  aWeb.wr("</DIV></DIV>")
  aWeb.wr("</FORM>")
  aWeb.wr(aWeb.button('start', DIV='div_content_right', SPIN='true', URL='device_discover', FRM='device_discover_form'))
  aWeb.wr("</ARTICLE>")

################################################## Interfaces #################################################
#
#
def interface_list(aWeb):
 args = aWeb.args()
 id = args.pop('device_id',None)
 op = args.pop('op',None)
 if   op == 'delete':
  interfaces = [val for intf,val in args.items() if intf[0:10] == "interface_"]
  opres = aWeb.rest_call("device/interface_delete",{'interfaces':interfaces})
 elif op == 'cleanup':
  opres = aWeb.rest_call("device/interface_delete",{'device_id':id})
 elif op == 'discover':
  opres = aWeb.rest_call("device/interface_snmp",{'device_id':id})
 else:
  opres = ""
 res = aWeb.rest_call("device/interface_list",{'device_id':id})
 aWeb.wr("<ARTICLE><P>Interfaces</P>")
 aWeb.wr(aWeb.button('reload', DIV='div_dev_data',URL='device_interface_list?device_id=%s'%id))
 aWeb.wr(aWeb.button('add',    DIV='div_dev_data',URL='device_interface_info?device_id=%s&interface_id=new'%id))
 aWeb.wr(aWeb.button('trash',  DIV='div_dev_data',URL='device_interface_list?device_id=%s&op=delete'%id, MSG='Delete interfaces?', FRM='interface_list', TITLE='Delete selected interfaces'))
 aWeb.wr("<A CLASS='z-op btn small text' DIV=div_dev_data URL='device_interface_list?device_id=%s&op=discover' SPIN='true' MSG='Rediscover interfaces?' TITLE='Discover interfaces'>Discover</A>"%id)
 aWeb.wr("<A CLASS='z-op btn small text' DIV=div_dev_data URL='device_interface_lldp?device_id=%s' SPIN='true' MSG='Map interfaces using LLDP?' TITLE='Map interfaces'>LLDP</A>"%id)
 aWeb.wr("<A CLASS='z-op btn small text' DIV=div_dev_data URL='device_interface_list?device_id=%s&op=cleanup' TITLE='Clean up empty interfaces' SPIN=true>Cleanup</A>"%id)
 aWeb.wr("<SPAN CLASS=results>%s</SPAN><FORM ID=interface_list>"%(opres))
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Id</DIV><DIV CLASS=th>MAC</DIV><DIV CLASS=th>IP</DIV><DIV CLASS=th>SNMP</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>Description</DIV><DIV CLASS=th>Class</DIV><DIV CLASS='th title' TITLE='Database id of connection'>Link</DIV><DIV CLASS=th TITLE='State as per last invoked check'>&nbsp;</DIV><DIV CLASS=th>&nbsp;</DIV></DIV><DIV CLASS=tbody>")
 for row in res['data']:
  row.update({'if_state_ascii':aWeb.state_ascii(row['if_state']),'ip_state_ascii':aWeb.state_ascii(row['ip_state'])})
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%(interface_id)s</DIV><DIV CLASS=td>%(mac)s</DIV><DIV CLASS=td>%(ip)s (%(ipam_id)s)</DIV><DIV CLASS=td>%(snmp_index)s</DIV><DIV CLASS=td>%(name)s</DIV><DIV CLASS=td>%(description)s</DIV><DIV CLASS=td>%(class)s</DIV><DIV CLASS=td>"%row)
  aWeb.wr("<A CLASS='z-op' DIV='div_dev_data' URL='device_connection_info?id=%(connection_id)s'>%(connection_id)s</A>"%row if row['connection_id'] else "-")
  aWeb.wr("</DIV><DIV CLASS=td><DIV CLASS='state %(if_state_ascii)s' />&nbsp;<DIV CLASS='state %(ip_state_ascii)s' /></DIV><DIV CLASS=td><INPUT TYPE=CHECKBOX VALUE=%(interface_id)s ID='interface_%(interface_id)s' NAME='interface_%(interface_id)s'>"%row)
  aWeb.wr(aWeb.button('info',  DIV='div_dev_data', URL='device_interface_info?device_id=%s&interface_id=%s'%(id,row['interface_id'])))
  aWeb.wr(aWeb.button('sync',  DIV='div_dev_data', URL='device_interface_connect?op=device&interface_id=%s&name=%s'%(row['interface_id'],row['name']), TITLE='Connect'))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</FORM></ARTICLE>")

#
def interface_lldp(aWeb):
 res = aWeb.rest_call('device/lldp_mapping',{'device_id':aWeb['device_id']})
 aWeb.wr("<ARTICLE><P>Interface</P>")
 aWeb.wr(aWeb.button('back', DIV='div_dev_data', URL='device_interface_list?device_id=%s'%aWeb['device_id']))
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Chassis ID</DIV><DIV CLASS=th>Type</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>Port ID</DIV><DIV CLASS=th>Type</DIV><DIV CLASS=th>Description</DIV><DIV CLASS=th>SNMP Index</DIV><DIV CLASS=th>SNMP Name</DIV><DIV CLASS=th>Conn</DIV><DIV CLASS=th>Status</DIV></DIV><DIV CLASS=tbody>")
 for con in res['data'].values():
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%(chassis_id)s</DIV><DIV CLASS=td>%(chassis_type)s</DIV><DIV CLASS=td>%(sys_name)s</DIV><DIV CLASS=td>%(port_id)s</DIV><DIV CLASS=td>%(port_type)s</DIV><DIV CLASS=td>%(port_desc)s</DIV><DIV CLASS=td>%(snmp_index)s</DIV><DIV CLASS=td>%(snmp_name)s</DIV><DIV CLASS=td>%(connection_id)s</DIV><DIV CLASS=td>%(status)s</DIV></DIV>"%con)
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</ARTICLE>")

#
def interface_info(aWeb):
 args = aWeb.args()
 op   = args.pop('op',None)
 opres = ""
 if   op == 'connect':
  opres = aWeb.rest_call("device/interface_connect",{'a_id':args['interface_id'],'b_id':args['peer_interface'],'map':True if args.get('map') else False})
 elif op == 'disconnect':
  opres = aWeb.rest_call("device/interface_connect",{'a_id':args['interface_id'],'b_id':args['peer_interface'],'disconnect':True})
 elif op == 'dns':
  opres = aWeb.rest_call("ipam/address_info",{'op':'update','hostname':args['name'],'id':args['ipam_id']})
 elif op == 'noip':
  opres = aWeb.rest_call("ipam/address_delete",{'id':args['ipam_id']})
 elif op == 'ipam':
  args['op'] = 'update'
  args['ipam_record'] = { 'ip':args.pop('ip','0.0.0.0'), 'network_id':args.pop('network_id',None), 'a_domain_id':args.pop('a_domain_id','NULL')}
 elif op == 'update':
  args['op'] = 'update'
 args['extra'] = ['classes']
 data = aWeb.rest_call("device/interface_info",args)
 info = data['data']
 extra= data.get('peer')
 opres = data['info'] if data['status'] == 'NOT_OK' else opres
 aWeb.wr("<ARTICLE CLASS=info STYLE='width:100%;'><P>Interface</P>")
 aWeb.wr("<FORM ID=interface_info_form>")
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=interface_id VALUE='%s'>"%(info['interface_id']))
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=device_id VALUE='%s'>"%(info['device_id']))
 aWeb.wr("<DIV CLASS=table STYLE='float:left; width:auto;'><DIV CLASS=tbody>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Name:</DIV><DIV CLASS=td><INPUT        NAME=name        VALUE='%s' TYPE=TEXT REQUIRED STYLE='min-width:400px'></DIV><DIV CLASS=td>"%(info['name']))
 if not info['ipam_id'] is None:
  aWeb.wr(aWeb.button('forward', DIV='div_dev_data', URL='device_interface_info?op=dns', FRM='interface_info_form', MSG='Update DNS with device-interface-name'))
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Class:</DIV><DIV CLASS=td><SELECT NAME=class>")
 for cls in data['classes']:
  aWeb.wr("<OPTION VALUE={0} {1}>{2}</OPTION>".format(cls," selected" if info['class'] == cls else "",cls))
 aWeb.wr("</SELECT></DIV></DIV>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Description:</DIV><DIV CLASS=td><INPUT NAME=description VALUE='%s' TYPE=TEXT REQUIRED STYLE='min-width:300px'></DIV></DIV>"%(info['description']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>SNMP Index:</DIV><DIV CLASS=td><INPUT  NAME=snmp_index  VALUE='%s' TYPE=TEXT REQUIRED STYLE='min-width:300px'></DIV></DIV>"%(info['snmp_index']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>MAC:</DIV><DIV CLASS=td><INPUT         NAME=mac         VALUE='%s' TYPE=TEXT REQUIRED STYLE='min-width:300px'></DIV></DIV>"%(info['mac']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>IPAM id:</DIV><DIV CLASS=td><INPUT     NAME=ipam_id     VALUE='%s' TYPE=TEXT REQUIRED STYLE='min-width:300px'></DIV><DIV CLASS=td>"%(info['ipam_id']))
 if not info['ipam_id'] is None:
  aWeb.wr(aWeb.button('forward', DIV='div_dev_data', URL='ipam_address_info?id=%s&vpl=div_dev_data'%info['ipam_id']))
  aWeb.wr(aWeb.button('trash',   DIV='div_dev_data', URL='device_interface_info?op=noip&interface_id=%s&ipam_id=%s'%(info['interface_id'],info['ipam_id']), MSG='Remove IP?'))
 elif info['interface_id'] != 'new':
  aWeb.wr(aWeb.button('forward', DIV='div_dev_data', URL='device_interface_ipam?interface_id=%s'%info['interface_id']))
 aWeb.wr("</DIV></DIV>")
 if extra:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Peer interface:</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>"%extra['interface_id'])
  aWeb.wr(aWeb.button('trash', DIV='div_dev_data', URL='device_interface_info?interface_id=%s&peer_interface=%s&op=disconnect'%(info['interface_id'],extra['interface_id'])))
  aWeb.wr("</DIV></DIV>")
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Peer Device</DIV><DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL='device_info?id=%(device_id)s'>%(device_id)s</A></DIV></DIV>"%extra)
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</FORM>")
 aWeb.wr(aWeb.button('reload', DIV='div_dev_data', URL='device_interface_info?device_id=%s&interface_id=%s'%(info['device_id'],info['interface_id'])))
 aWeb.wr(aWeb.button('back',   DIV='div_dev_data', URL='device_interface_list?device_id=%s'%info['device_id']))
 aWeb.wr(aWeb.button('save',   DIV='div_dev_data', URL='device_interface_info?op=update', FRM='interface_info_form'))
 aWeb.wr(aWeb.button('sync',   DIV='div_dev_data', URL='device_interface_connect?op=device&interface_id=%s&name=%s'%(info['interface_id'],info['name']), TITLE='Connect'))
 if info['interface_id'] != 'new':
  aWeb.wr(aWeb.button('trash', DIV='div_dev_data', URL='device_interface_list?op=delete&device_id=%s&interface_%s=%s'%(info['device_id'],info['interface_id'],info['interface_id']), MSG='Delete interface?'))
 aWeb.wr("<SPAN CLASS='results' ID=operation_results>%s</SPAN>"%opres)
 aWeb.wr("</ARTICLE>")

#
#
def interface_ipam(aWeb):
 if aWeb['op'] == 'find':
  aWeb.wr(aWeb.rest_call("ipam/address_find",{'network_id':aWeb['network_id']})['ip'])
 else:
  domains  = aWeb.rest_call("dns/domain_list",{'filter':'forward'})['domains']
  networks = aWeb.rest_call("ipam/network_list")['networks']
  aWeb.wr("<ARTICLE CLASS=info><P>Create IPAM record</P>")
  aWeb.wr("<FORM ID=interface_ipam_form>")
  aWeb.wr("<INPUT TYPE=HIDDEN NAME=interface_id VALUE='%s'>"%(aWeb['interface_id']))
  aWeb.wr("<DIV CLASS=table><DIV CLASS=tbody>")
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Network:</DIV><DIV CLASS=td><SELECT NAME=network_id>")
  for s in networks:
   aWeb.wr("<OPTION VALUE={} {}>{} ({})</OPTION>".format(s['id'],"selected" if str(s['id']) == aWeb['network_id'] else "", s['netasc'],s['description']))
  aWeb.wr("</SELECT></DIV></DIV>")
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>IP:</DIV><DIV CLASS=td><INPUT  NAME=ip ID=div_ip TYPE=TEXT VALUE='%s'></DIV></DIV>"%aWeb.get('ip','0.0.0.0'))
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Domain:</DIV><DIV CLASS=td><SELECT NAME=a_domain_id>")
  for d in domains:
   aWeb.wr("<OPTION VALUE={} {}>{}</OPTION>".format(d['id'],"selected" if str(d['id']) == aWeb.get('a_domain_id','NULL') else "", d['name']))
  aWeb.wr("</SELECT></DIV></DIV>")
  aWeb.wr("</DIV></DIV>")
  aWeb.wr("</FORM>")
  aWeb.wr(aWeb.button('back',    DIV='div_dev_data', URL='device_interface_info', FRM='interface_ipam_form'))
  aWeb.wr(aWeb.button('search',  DIV='div_ip',       URL='device_interface_ipam?op=find', FRM='interface_ipam_form', TITLE='Find IP',INPUT='True'))
  aWeb.wr(aWeb.button('forward', DIV='div_dev_data', URL='device_interface_info?op=ipam', FRM='interface_ipam_form', TITLE='Create'))
  aWeb.wr("<SPAN CLASS='results' ID=interface_span STYLE='max-width:400px;'></SPAN>")
  aWeb.wr("</ARTICLE>")
#
#
def interface_connect(aWeb):
 aWeb.wr("<ARTICLE>")
 aWeb.wr("<FORM ID=interface_link>")
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=interface_id VALUE=%s>"%(aWeb['interface_id']))
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=name VALUE=%s>"%aWeb['name'])
 if aWeb['op'] == 'device':
  aWeb.wr("Connect '%s' to device id: <INPUT CLASS='background' REQUIRED TYPE=TEXT NAME='peer' STYLE='width:100px' VALUE=0>"%(aWeb['name']))
  aWeb.wr("</FORM>")
  aWeb.wr(aWeb.button('back',    DIV='div_dev_data', URL='device_interface_info', FRM='interface_link'))
  aWeb.wr(aWeb.button('forward', DIV='div_dev_data', URL='device_interface_connect?op=interface', FRM='interface_link'))
 else:
  aWeb.wr("<INPUT TYPE=HIDDEN NAME=peer VALUE=%s>"%aWeb['peer'])
  res = aWeb.rest_call("device/interface_list",{'device_id':aWeb['peer'],'sort':'name','filter':['connected']})
  aWeb.wr("Connect '%s' to device id: %s on <SELECT NAME=peer_interface REQUIRED>"%(aWeb['name'],aWeb['peer']))
  for intf in res.get('data',[]):
   aWeb.wr("<OPTION VALUE=%s>%s (%s - %s)</OPTION>"%(intf['interface_id'],intf['interface_id'],intf['name'],intf['description']))
  aWeb.wr("</SELECT>")
  aWeb.wr(" Map: <INPUT TYPE=CHECKBOX NAME=map VALUE=1 CHECKED='checked'>")
  aWeb.wr("</FORM>")
  aWeb.wr(aWeb.button('back',    DIV='div_dev_data', URL='device_interface_connect?op=device', FRM='interface_link'))
  aWeb.wr(aWeb.button('forward', DIV='div_dev_data', URL='device_interface_info?op=connect',   FRM='interface_link'))
 aWeb.wr("</ARTICLE>")

#
#
def connection_info(aWeb):
 data = aWeb.rest_call("device/connection_info",{"connection_id":aWeb['id']})['data']
 aWeb.wr("<ARTICLE CLASS='info'><P>Connection</P>")
 aWeb.wr("<DIV CLASS=table STYLE='float:left; width:auto;'><DIV CLASS=tbody>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Map:</DIV><DIV CLASS=td><INPUT TYPE=CHECKBOX NAME=map VALUE=1 %s ></DIV></DIV>"%("CHECKED=checked" if data['map'] else ""))
 for intf in data['interfaces']:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Device - Interface:</DIV><DIV CLASS=td>%s - %s (%s)</DIV></DIV>"%(intf['device_name'],intf['interface_name'], intf['interface_id']))
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</ARTICLE>")
