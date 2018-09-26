"""Module docstring.

HTML5 Ajax Device module

"""
__author__= "Zacharias El Banna"
__version__ = "4.0GA"
__status__ = "Production"
__icon__ = '../images/icon-network.png'
__type__ = 'menuitem'

########################################## Device Operations ##########################################
#
#
def main(aWeb):
 aWeb.wr("<NAV><UL>")
 aWeb.wr("<LI CLASS='dropdown'><A>Devices</A><DIV CLASS='dropdown-content'>")
 aWeb.wr("<A CLASS=z-op DIV=div_content_left URL='device_list?{0}'>List</A>".format(aWeb.get_args()))
 aWeb.wr("<A CLASS=z-op DIV=div_content_left URL='device_search'>Search</A>")
 aWeb.wr("<A CLASS=z-op DIV=div_content_left URL='device_types_list'>Types</A>")
 aWeb.wr("<A CLASS=z-op DIV=div_content_left URL='device_tasks'>Tasks</A>")
 aWeb.wr("</DIV></LI>")
 aWeb.wr("<LI><A CLASS=z-op DIV=div_content_left URL='visualize_list'>Maps</A></LI>")
 if aWeb['rack']:
  data = aWeb.rest_call("rack_inventory",{'id':aWeb['rack']})
  for type in ['pdu','console']:
   if len(data[type]) > 0:
    aWeb.wr("<LI CLASS='dropdown'><A>%s</A><DIV CLASS='dropdown-content'>"%(type.title()))
    for row in data[type]:
     aWeb.wr("<A CLASS=z-op DIV=div_content_left SPIN=true URL='%s_inventory?ip=%s'>%s</A>"%(row['type'],row['ip'],row['hostname']))
    aWeb.wr("</DIV></LI>")
  if data.get('name'):
   aWeb.wr("<LI><A CLASS='z-op' DIV=div_content_right  URL='rack_inventory?rack=%s'>'%s'</A></LI>"%(aWeb['rack'],data['name']))
 aWeb.wr("<LI><A CLASS='z-op reload' DIV=main URL='device_main?{}'></A></LI>".format(aWeb.get_args()))
 aWeb.wr("<LI CLASS='right'><A CLASS=z-op DIV=div_content URL='reservations_list'>Reservations</A></LI>")
 aWeb.wr("<LI CLASS='right dropdown'><A>IPAM</A><DIV CLASS='dropdown-content'>")
 aWeb.wr("<A CLASS=z-op DIV=div_content_left URL='system_server_list?type=DHCP'>Servers</A>")
 aWeb.wr("<A CLASS=z-op DIV=div_content_left URL='ipam_network_list'>Networks</A>")
 aWeb.wr("</DIV></LI>")
 aWeb.wr("<LI CLASS='right dropdown'><A>DNS</A><DIV CLASS='dropdown-content'>")
 aWeb.wr("<A CLASS=z-op DIV=div_content_left URL='system_server_list?type=DNS'>Servers</A>")
 aWeb.wr("<A CLASS=z-op DIV=div_content_left URL='dns_domain_list'>Domains</A>")
 aWeb.wr("</DIV></LI>")
 aWeb.wr("<LI CLASS='right dropdown'><A>Rack</A><DIV CLASS='dropdown-content'>")
 aWeb.wr("<A CLASS=z-op DIV=div_content_left URL='rack_list'>Racks</A>")
 aWeb.wr("<A CLASS=z-op DIV=div_content_left URL='rack_list_infra?type=pdu'>PDUs</A>")
 aWeb.wr("<A CLASS=z-op DIV=div_content_left URL='rack_list_infra?type=console'>Consoles</A>")
 aWeb.wr("</DIV></LI>")
 aWeb.wr("</UL></NAV>")
 aWeb.wr("<SECTION CLASS=content       ID=div_content>")
 aWeb.wr("<SECTION CLASS=content-left  ID=div_content_left></SECTION>")
 aWeb.wr("<SECTION CLASS=content-right ID=div_content_right></SECTION>")
 aWeb.wr("</SECTION>")

#
#
def list(aWeb):
 args = aWeb.args()
 args['sort'] = aWeb.get('sort','hostname')
 res = aWeb.rest_call("device_list",args)
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
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td STYLE='max-width:180px; overflow-x:hidden'><A CLASS=z-op DIV=div_content_right URL='device_info?id=%i' TITLE='%s'>%s</A></DIV><DIV CLASS=td><DIV CLASS='state %s' /></DIV></DIV>"%(row['ip'],row['id'],row['id'], row['hostname'], {0:'grey',1:'green',2:'red',3:'orange'}.get(row['state'],'orange')))
 aWeb.wr("</DIV></DIV></ARTICLE>")

#
#
def tasks(aWeb):
 aWeb.wr("<ARTICLE><P>Device Tasks</P>")
 aWeb.wr("To be defined")
 aWeb.wr("</ARTICLE>")
 
#
#
def report(aWeb):
 args = aWeb.args()
 res = aWeb.rest_call("device_list",{'extra': ['system', 'type', 'mac']})
 aWeb.wr("<ARTICLE><P>Devices</P>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Id</DIV><DIV CLASS=th>Device</DIV><DIV CLASS=th>Domain</DIV><DIV CLASS=th>IP</DIV><DIV CLASS=th>MAC</DIV><DIV CLASS=th>Model</DIV><DIV CLASS=th>OID</DIV><DIV CLASS=th>Serial</DIV><DIV CLASS=th>State</DIV></DIV><DIV CLASS=tbody>")
 for dev in res['data']:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%(id)s</DIV><DIV CLASS=td>%(hostname)s</DIV><DIV CLASS=td>%(domain)s</DIV><DIV CLASS=td>%(ip)s</DIV><DIV CLASS=td>%(mac)s</DIV><DIV CLASS=td>%(model)s</DIV><DIV CLASS=td>%(oid)s</DIV><DIV CLASS=td>%(serial)s</DIV>"%dev)
  aWeb.wr("<DIV CLASS=td><DIV CLASS='state %s' /></DIV></DIV>"%{0:'grey',1:'green',2:'red'}.get(dev['state'],0))
 aWeb.wr("</DIV></DIV></ARTICLE>")

#
#
def search(aWeb):
 aWeb.wr("<ARTICLE><P>Device Search</P>")
 aWeb.wr("<FORM ID='device_search'>")
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=sort VALUE='hostname'>")
 aWeb.wr("<SPAN>Field:</SPAN><SELECT CLASS='background' ID='field' NAME='field'><OPTION VALUE='hostname'>Hostname</OPTION><OPTION VALUE='type'>Type</OPTION><OPTION VALUE='ip'>IP</OPTION><OPTION VALUE='mac'>MAC</OPTION><OPTION VALUE='id'>ID</OPTION></SELECT>")
 aWeb.wr("<INPUT CLASS='background' TYPE=TEXT ID='search' NAME='search' STYLE='width:200px' REQUIRED>")
 aWeb.wr("</FORM><DIV CLASS=inline>")
 aWeb.wr(aWeb.button('search', DIV='div_content_left', URL='device_list', FRM='device_search'))
 aWeb.wr(aWeb.button('items',  DIV='div_content_left', URL='device_list', TITLE='List All items'))
 aWeb.wr("</DIV>")
 aWeb.wr("</ARTICLE>")

#
#
def types_list(aWeb):
 res = aWeb.rest_call("device_types_list")
 aWeb.wr("<ARTICLE><P>Device Types<P>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Class</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>Icon</DIV></DIV><DIV CLASS=tbody>")
 for tp in res['types']:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td><A CLASS=z-op DIV=div_content_left URL='device_list?field=type&search=%s'>%s</A></DIV><DIV CLASS=td>%s</DIV></DIV>"%(tp['base'],tp['name'],tp['name'],tp['icon'].rpartition('/')[2]))
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</ARTICLE>")
#
#
def info(aWeb):
 cookie = aWeb.cookie('system')
 args = aWeb.args()
 args['extra'] = ['types']
 dev = aWeb.rest_call("device_info",args)
 if not dev['found']:
  aWeb.wr("<ARTICLE>Warning - device with either id:[{}]/ip[{}]: does not exist</ARTICLE>".format(aWeb['id'],aWeb['ip']))
  return
 ########################## Data Tables ######################
 width = 680 if dev['racked'] and not dev['info']['type_base'] == 'pdu' else 470
 aWeb.wr("<ARTICLE CLASS='info' STYLE='position:relative; height:268px; width:%spx;'><P TITLE='%s'>Device Info</P>"%(width,dev['id']))
 aWeb.wr("<FORM ID=info_form>")
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(dev['id']))
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=ip VALUE={}>".format(dev['ip']))
 aWeb.wr("<!-- Reachability Info -->")
 aWeb.wr("<DIV STYLE='margin:3px; float:left;'><DIV CLASS=table STYLE='width:210px;'><DIV CLASS=tbody>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Name:  </DIV><DIV CLASS='td readonly'>%s</DIV></DIV>"%dev['info']['hostname'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Domain:</DIV><DIV CLASS='td readonly'>%s</DIV></DIV>"%dev['info']['domain'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>IP:    </DIV><DIV CLASS='td readonly'>%s</DIV></DIV>"%dev['ip'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>ID:    </DIV><DIV CLASS='td readonly'>%s</DIV></DIV>"%dev['id'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>SNMP:</DIV><DIV CLASS='td readonly'>%s</DIV></DIV>"%dev['info']['snmp'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Version:</DIV><DIV CLASS='td readonly'>%s</DIV></DIV>"%dev['info']['version'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>State:</DIV><DIV CLASS=td><DIV CLASS='state %s' /></DIV></DIV>"%dev['state'])
 aWeb.wr("</DIV></DIV></DIV>")
 aWeb.wr("<!-- Additional info -->")
 aWeb.wr("<DIV STYLE='margin:3px; float:left;'><DIV CLASS=table STYLE='width:227px;'><DIV CLASS=tbody>")
 aWeb.wr("<DIV CLASS=tr ID=div_reservation_info><DIV CLASS=td>Reserve:</DIV>")
 if dev['info']['type_name'] == 'controlplane':
  aWeb.wr("<DIV CLASS=td>N/A</DIV>")
 elif dev['reserved']:
  aWeb.wr("<DIV CLASS='td %s'>"%("red" if dev['reservation']['valid'] == 1 else "orange"))
  aWeb.wr(dev['reservation']['alias'] if dev['reservation']['user_id'] != int(cookie['id']) else "<A CLASS=z-op DIV=div_reservation_info URL='reservations_update?op=drop&id=%s'>%s</A>"%(dev['id'],dev['reservation']['alias']))
  aWeb.wr("</DIV>")
 else:
  aWeb.wr("<DIV CLASS='td green'><A CLASS=z-op DIV=div_reservation_info URL='reservations_update?op=reserve&id=%s'>Available</A></DIV>"%dev['id'])
 aWeb.wr("</DIV>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>MAC:   </DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=mac VALUE='%s'></DIV></DIV>"%dev['info']['mac'].upper())
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>VM:    </DIV><DIV CLASS=td><INPUT NAME=vm TYPE=checkbox VALUE=1 {0}></DIV></DIV>".format("checked=checked" if dev['info']['vm'] == 1 else ""))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Type:</DIV>")
 if dev.get('types'):
  aWeb.wr("<DIV CLASS=td><SELECT NAME=type_id>")
  for type in dev['types']:
   extra = " selected" if dev['info']['type_id'] == type['id'] else ""
   aWeb.wr("<OPTION VALUE={0} {1}>{2}</OPTION>".format(type['id'],extra,type['name']))
  aWeb.wr("</SELECT></DIV>")
 else:
  aWeb.wr("<DIV CLASS=td>%s</DIV>"%dev['info']['type_name'])
 aWeb.wr("</DIV>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Model: </DIV><DIV CLASS=td STYLE='max-width:150px;'><INPUT TYPE=TEXT NAME=model VALUE='%s'></DIV></DIV>"%(dev['info']['model']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>S/N: </DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=serial VALUE='%s'></DIV></DIV>"%(dev['info']['serial']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td TITLE='Auto shutdown if not used'>Shutdown:</DIV><DIV CLASS=td><INPUT NAME=shutdown TYPE=checkbox VALUE=1 {0}></DIV></DIV>".format("checked=checked" if dev['info']['shutdown'] == 1 else ""))
 aWeb.wr("</DIV></DIV></DIV>")
 aWeb.wr("<!-- Rack Info -->")
 if dev['racked'] and not dev['info']['type_base'] == 'pdu':
  aWeb.wr("<DIV STYLE='margin:3px; float:left;'><DIV CLASS=table STYLE='width:210px;'><DIV CLASS=tbody>")
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Rack/Pos: </DIV><DIV CLASS=td>%s (%s)</DIV></DIV>"%(dev['rack']['rack_name'],dev['rack']['rack_unit']))
  if not dev['info']['type_base'] == 'controlplane':
   aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Size:    </DIV><DIV CLASS=td>%s U</DIV></DIV>"%(dev['rack']['rack_size']))
  if not dev['info']['type_base'] == 'console':
   aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>TS/Port: </DIV><DIV CLASS=td>%s (%s)</DIV></DIV>"%(dev['rack']['console_name'],dev['rack']['console_port']))
  for count,pem in enumerate(dev['pems'],0):
   if count < 4:
    aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%s PDU: </DIV><DIV CLASS=td>%s (%s)</DIV></DIV>"%(pem['name'],pem['pdu_name'], pem['pdu_unit']))
  aWeb.wr("</DIV></DIV></DIV>")
 aWeb.wr("<!-- Text fields -->")
 aWeb.wr("<DIV STYLE='display:block; clear:both; margin-bottom:3px; margin-top:1px; width:99%;'><DIV CLASS=table><DIV CLASS=tbody>")
 aWeb.wr("<DIV CLASS='tr even'><DIV CLASS=td>Comments:</DIV><DIV CLASS=td><INPUT CLASS=odd TYPE=TEXT NAME=comment VALUE='{}'></DIV></DIV>".format("" if not dev['info']['comment'] else dev['info']['comment'].encode("utf-8")))
 aWeb.wr("<DIV CLASS='tr even'><DIV CLASS=td>Web UI:</DIV><DIV CLASS=td><INPUT CLASS=odd TYPE=TEXT NAME=url VALUE='{}'></DIV></DIV>".format("" if not dev['info']['url'] else dev['info']['url']))
 aWeb.wr("</DIV></DIV></DIV>")
 aWeb.wr("</FORM>")
 aWeb.wr(aWeb.button('reload',     DIV='div_content_right',URL='device_info?id=%i'%dev['id']))
 aWeb.wr(aWeb.button('trash',      DIV='div_content_right',URL='device_delete?id=%i'%dev['id'], MSG='Are you sure you want to delete device?', TITLE='Delete device',SPIN='true'))
 aWeb.wr(aWeb.button('edit',       DIV='div_content_right',URL='device_extended?id=%i'%dev['id'], TITLE='Configure Extended Device Information'))
 aWeb.wr(aWeb.button('save',       DIV='div_content_right',URL='device_info?op=update', FRM='info_form', TITLE='Save Basic Device Information'))
 aWeb.wr(aWeb.button('search',     DIV='div_content_right',URL='device_info?op=lookup', FRM='info_form', TITLE='Lookup and Detect Device information', SPIN='true'))
 aWeb.wr(aWeb.button('document',   DIV='div_dev_data',     URL='device_conf_gen?id=%i'%(dev['id']),TITLE='Generate System Conf'))
 aWeb.wr(aWeb.button('connections',DIV='div_dev_data',     URL='device_interface_list?device=%i'%(dev['id']),TITLE='Device interfaces'))
 aWeb.wr(aWeb.button('network',  DIV='div_content_right',URL='visualize_network?type=device&id=%s'%(dev['id']), SPIN='true', TITLE='Network map'))
 aWeb.wr(aWeb.button('term',TITLE='SSH',HREF='ssh://%s@%s'%(dev['username'],dev['ip'])))
 if dev['racked'] and dev['rack'].get('console_ip') and dev['rack'].get('console_port'):
  # Hardcoded port to 60xx
  aWeb.wr(aWeb.button('term',TITLE='Console', HREF='telnet://%s:%i'%(dev['rack']['console_ip'],6000+dev['rack']['console_port'])))
 if dev['info'].get('url'):
  aWeb.wr(aWeb.button('ui',TITLE='WWW', TARGET='_blank', HREF=dev['info'].get('url')))
 aWeb.wr("<SPAN CLASS='results' ID=update_results>%s</SPAN>"%str(dev.get('update','')))
 aWeb.wr("</ARTICLE>")
 aWeb.wr("<!-- Function navbar and content -->")
 aWeb.wr("<NAV><UL>")
 for fun in dev['info']['functions'].split(','):
  if fun == 'manage':
   aWeb.wr("<LI><A CLASS=z-op DIV=main URL='%s_manage?id=%i'>Manage</A></LI>"%(dev['info']['type_name'],dev['id']))
  else:
   aWeb.wr("<LI><A CLASS=z-op DIV=div_dev_data SPIN=true URL='device_function?ip={0}&type={1}&op={2}'>{3}</A></LI>".format(dev['ip'], dev['info']['type_name'], fun, fun.title()))
 aWeb.wr("</UL></NAV>")
 aWeb.wr("<SECTION CLASS='content' ID=div_dev_data STYLE='top:308px; overflow-x:hidden; overflow-y:auto;'></SECTION>")

####################################### UPDATE INFO ###################################
#
#
def extended(aWeb):
 args = aWeb.args()
 dev = aWeb.rest_call("device_extended",args)
 domains = aWeb.rest_call("dns_domain_list",{'filter':'forward'})['domains']

 aWeb.wr("<ARTICLE CLASS='info'><P>Device Extended Info</P>")
 aWeb.wr("<FORM ID=info_form>")
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(dev['id']))
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=ip VALUE={}>".format(dev['ip']))
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=racked VALUE={}>".format(dev['racked']))
 aWeb.wr("<!-- Reachability Info -->")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=tbody>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Name:</DIV><DIV CLASS=td><INPUT NAME=hostname TYPE=TEXT VALUE='%s'></DIV></DIV>"%(dev['info']['hostname']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Domain:</DIV><DIV CLASS=td><SELECT NAME=a_dom_id>")
 for dom in domains:
  extra = " selected" if dev['info']['a_dom_id'] == dom['id'] else ""
  aWeb.wr("<OPTION VALUE='%s' %s>%s</OPTION>"%(dom['id'],extra,dom['name']))
 aWeb.wr("</SELECT></DIV></DIV>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>IP:</DIV><DIV CLASS=td><INPUT NAME=ip TYPE=TEXT VALUE='%s'></DIV><DIV CLASS=td>"%(dev['ip']))
 aWeb.wr(aWeb.button('sync',DIV='div_content_right', FRM='info_form', URL='device_update_ip?id=%s'%dev['id'], TITLE='Modify IP'))
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>LLDP MAC:</DIV><DIV CLASS='td readonly'>%s</DIV></DIV>"%dev['info']['mac'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Priv OID:</DIV><DIV CLASS='td readonly'>%s</DIV></DIV>"%dev['info']['oid'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>A ID:   </DIV><DIV CLASS='td readonly'>%s</DIV></DIV>"%dev['info']['a_id'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>PTR ID: </DIV><DIV CLASS='td readonly'>%s</DIV></DIV>"%dev['info']['ptr_id'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>IPAM ID:</DIV><DIV CLASS='td readonly'>%s</DIV></DIV>"%dev['info']['ipam_id'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>&nbsp;</DIV><DIV CLASS=td>&nbsp;</DIV></DIV>")
 aWeb.wr("<!-- Rack Info -->")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Rack:</DIV><DIV CLASS=td><SELECT NAME=rack_info_rack_id>")
 for rack in dev['infra']['racks']:
  extra = " selected" if ((dev['racked'] == 0 and rack['id'] == 'NULL') or (dev['racked'] == 1 and dev['rack']['rack_id'] == rack['id'])) else ""
  aWeb.wr("<OPTION VALUE={0} {1}>{2}</OPTION>".format(rack['id'],extra,rack['name']))
 aWeb.wr("</SELECT></DIV></DIV>")
 if dev['racked'] == 1 and not dev['info']['type_base'] == 'pdu':
  if not dev['info']['type_base'] == 'controlplane':
   aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Rack Size:</DIV><DIV CLASS=td><INPUT NAME=rack_info_rack_size TYPE=TEXT PLACEHOLDER='{}'></DIV></DIV>".format(dev['rack']['rack_size']))
   aWeb.wr("<DIV CLASS=tr><DIV CLASS=td TITLE='Top rack unit of device placement'>Rack Unit:</DIV><DIV CLASS=td><INPUT NAME=rack_info_rack_unit TYPE=TEXT PLACEHOLDER='{}'></DIV></DIV>".format(dev['rack']['rack_unit']))
  if not dev['info']['type_base'] == 'console':
   aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>TS:</DIV><DIV CLASS=td><SELECT NAME=rack_info_console_id>")
   for console in dev['infra']['consoles']:
    extra = " selected='selected'" if (dev['rack']['console_id'] == console['id']) or (not dev['rack']['console_id'] and console['id'] == 'NULL') else ""
    aWeb.wr("<OPTION VALUE={0} {1}>{2}</OPTION>".format(console['id'],extra,console['hostname']))
   aWeb.wr("</SELECT></DIV></DIV>")
   aWeb.wr("<DIV CLASS=tr><DIV CLASS=td TITLE='Console port in rack TS'>TS Port:</DIV><DIV CLASS=td><INPUT NAME=rack_info_console_port TYPE=TEXT PLACEHOLDER='{}'></DIV></DIV>".format(dev['rack']['console_port']))
  if not dev['info']['type_base'] == 'controlplane':
   aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>&nbsp;</DIV><DIV CLASS=td><CENTER>Add PEM<CENTER></DIV><DIV CLASS=td>")
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
       pdu_slot_id   = pdu_info[str(slotid)+"_slot_id"]
       pdu_slot_name = pdu_info[str(slotid)+"_slot_name"]
       extra = "selected" if ((pem['pdu_id'] == pdu['id']) and (pem['pdu_slot'] == slotid)) or (not pem['pdu_id'] and pdu['id'] == 'NULL') else ""
       aWeb.wr("<OPTION VALUE=%s.%s %s>%s</OPTION>"%(pdu['id'],slotid, extra, pdu['hostname']+":"+pdu_slot_name))
    aWeb.wr("</SELECT></DIV></DIV>")
    aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Unit:</DIV><DIV CLASS=td><INPUT NAME=pems_%s_pdu_unit TYPE=TEXT VALUE='%s'></DIV></DIV>"%(pem['id'],pem['pdu_unit']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>&nbsp;</DIV><DIV CLASS=td>&nbsp;</DIV></DIV>")
 aWeb.wr("</DIV></DIV></FORM>")
 aWeb.wr(aWeb.button('reload',DIV='div_content_right',URL='device_extended?id=%s'%dev['id']))
 aWeb.wr(aWeb.button('back',  DIV='div_content_right',URL='device_info?id=%s'%dev['id']))
 aWeb.wr(aWeb.button('trash', DIV='div_content_right',URL='device_delete?id=%s'%dev['id'], MSG='Are you sure you want to delete device?', TITLE='Delete device',SPIN='true'))
 aWeb.wr(aWeb.button('save',  DIV='div_content_right',URL='device_extended?op=update', FRM='info_form', TITLE='Save Device Information'))
 aWeb.wr("<SPAN CLASS='results' ID=update_results>%s</SPAN>"%str(dev.get('result','')))
 aWeb.wr("</ARTICLE>")

#
#
def update_ip(aWeb):
 args = aWeb.args()
 op = args.pop('op',None)
 if   op == 'update':
  aWeb.wr(str(aWeb.rest_call("device_update_ip", args)))
 elif op == 'find':
  aWeb.wr(aWeb.rest_call("ipam_address_find",args)['ip'])
 else:
  ipam = aWeb.rest_call("ipam_network_list")
  info = aWeb.rest_call("device_info",{'id':args['id'],'op':'basics'})
  aWeb.wr("<ARTICLE CLASS=info><P>Change IP</P>")
  aWeb.wr("<FORM ID=device_new_form>")
  aWeb.wr("<INPUT TYPE=HIDDEN NAME=id VALUE=%s>"%args['id'])
  aWeb.wr("<DIV CLASS=table><DIV CLASS=tbody>")
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Original IP:</DIV><DIV CLASS=td>%s</DIV></DIV>"%info['ip'])
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Network:</DIV><DIV CLASS=td><SELECT NAME=network_id>")
  for s in ipam['networks']:
   aWeb.wr("<OPTION VALUE={} {}>{} ({})</OPTION>".format(s['id'],"selected" if s['id'] == info['info']['network_id'] else "", s['netasc'],s['description']))
  aWeb.wr("</SELECT></DIV></DIV>")
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>New IP:</DIV><DIV CLASS=td><INPUT NAME=ip ID=device_ip TYPE=TEXT VALUE='%s'></DIV></DIV>"%info['ip'])
  aWeb.wr("</DIV></DIV>")
  aWeb.wr("</FORM>")
  aWeb.wr(aWeb.button('back',    DIV='div_content_right', URL='device_extended?id=%s'%args['id']))
  aWeb.wr(aWeb.button('search',  DIV='device_ip',         URL='device_update_ip?op=find',   FRM='device_new_form', TITLE='Find IP',INPUT='True'))
  aWeb.wr(aWeb.button('forward', DIV='update_results',    URL='device_update_ip?op=update', FRM='device_new_form', TITLE='Update IP'))
  aWeb.wr("<SPAN CLASS='results' ID=update_results></SPAN>")
  aWeb.wr("</ARTICLE>")

#
#
def delete(aWeb):
 res = aWeb.rest_call("device_delete",{ 'id':aWeb['id'] })
 aWeb.wr("<ARTICLE>Unit {} deleted, op:{}</ARTICLE>".format(aWeb['id'],res))

####################################################### Functions #######################################################
#
#
def to_console(aWeb):
 res = aWeb.rest_call("device_info",{'id':aWeb['id'],'op':'basics'})
 aWeb.wr("<SCRIPT> window.location.replace('%s&title=%s'); </SCRIPT>"%(res['url'],aWeb['name']))

#
#
def conf_gen(aWeb):
 aWeb.wr("<ARTICLE>")
 res = aWeb.rest_call("device_configuration_template",{'id':aWeb['id']})
 if res['result'] == 'OK':
  aWeb.wr("<BR>".join(res['data']))
 else:
  aWeb.wr("<B>%s</B>"%res['info'])
 aWeb.wr("</ARTICLE>")

#
#
def function(aWeb):
 aWeb.wr("<ARTICLE>")
 res = aWeb.rest_call("device_function",{'ip':aWeb['ip'],'op':aWeb['op'],'type':aWeb['type']})
 if res['result'] == 'OK':
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
 cookie = aWeb.cookie('system') 
 ip   = aWeb.get('ip')
 name = aWeb.get('hostname','unknown')
 mac  = aWeb.get('mac',"00:00:00:00:00:00")
 op   = aWeb['op']
 network = aWeb['ipam_network_id']
 if not ip:
  def int2ip(addr):
   from struct import pack
   from socket import inet_ntoa
   return inet_ntoa(pack("!I", addr))
  ip = "127.0.0.1" if not aWeb['ipint'] else int2ip(int(aWeb['ipint']))

 if op == 'new':
  args = { 'ip':ip, 'mac':mac, 'hostname':name, 'a_dom_id':aWeb['a_dom_id'], 'ipam_network_id':network }
  if aWeb['vm']:
   args['vm'] = 1
  else:
   args['rack'] = aWeb['rack']
   args['vm'] = 0
  res = aWeb.rest_call("device_new",args)
  aWeb.wr("Operation:%s"%str(res))
 elif op == 'find':
  aWeb.wr(aWeb.rest_call("ipam_address_find",{'network_id':network})['ip'])
 else:
  networks = aWeb.rest_call("ipam_network_list")['networks']
  domains  = aWeb.rest_call("dns_domain_list",{'filter':'forward'})['domains']
  aWeb.wr("<ARTICLE CLASS=info><P>Device Add</P>")
  aWeb.wr("<FORM ID=device_new_form>")
  aWeb.wr("<DIV CLASS=table><DIV CLASS=tbody>")
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Hostname:</DIV><DIV CLASS=td><INPUT NAME=hostname TYPE=TEXT VALUE={}></DIV></DIV>".format(name))
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Domain:</DIV><DIV CLASS=td><SELECT  NAME=a_dom_id>")
  for d in domains:
   aWeb.wr("<OPTION VALUE={0} {1}>{2}</OPTION>".format(d['id'],"selected" if d['name'] == aWeb['domain'] else "",d['name']))
  aWeb.wr("</SELECT></DIV></DIV>")
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Network:</DIV><DIV CLASS=td><SELECT NAME=ipam_network_id>")
  for s in networks:
   aWeb.wr("<OPTION VALUE={} {}>{} ({})</OPTION>".format(s['id'],"selected" if str(s['id']) == network else "", s['netasc'],s['description']))
  aWeb.wr("</SELECT></DIV></DIV>")
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>IP:</DIV><DIV CLASS=td><INPUT  NAME=ip ID=device_ip TYPE=TEXT VALUE='{}'></DIV></DIV>".format(ip))
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>MAC:</DIV><DIV CLASS=td><INPUT NAME=mac TYPE=TEXT PLACEHOLDER='{0}'></DIV></DIV>".format(mac))
  if aWeb['rack']:
   aWeb.wr("<INPUT TYPE=HIDDEN NAME=rack VALUE={}>".format(aWeb['rack']))
  else:
   aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>VM:</DIV><DIV  CLASS=td><INPUT NAME=vm  TYPE=CHECKBOX VALUE=1  {0} ></DIV></DIV>".format("checked" if aWeb['target'] == 'vm' else ''))
  aWeb.wr("</DIV></DIV>")
  aWeb.wr("</FORM>")
  aWeb.wr(aWeb.button('start', DIV='device_span', URL='device_new?op=new',  FRM='device_new_form', TITLE='Create'))
  aWeb.wr(aWeb.button('search',DIV='device_ip',   URL='device_new?op=find', FRM='device_new_form', TITLE='Find IP',INPUT='True'))
  aWeb.wr("<SPAN CLASS='results' ID=device_span STYLE='max-width:400px;'></SPAN>")
  aWeb.wr("</ARTICLE>")

#
#
def discover(aWeb):
 if aWeb['op']:
  res = aWeb.rest_call("device_discover",{ 'network_id':aWeb['network_id'], 'a_dom_id':aWeb['a_dom_id']}, 200)
  aWeb.wr("<ARTICLE>%s</ARTICLE>"%(res))
 else:
  networks = aWeb.rest_call("ipam_network_list")['networks']
  domains = aWeb.rest_call("dns_domain_list",{'filter':'forward'})['domains']
  dom_name = aWeb['domain']
  aWeb.wr("<ARTICLE CLASS=info><P>Device Discovery</P>")
  aWeb.wr("<FORM ID=device_discover_form>")
  aWeb.wr("<INPUT TYPE=HIDDEN NAME=op VALUE=json>")
  aWeb.wr("<DIV CLASS=table><DIV CLASS=tbody>")
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Domain:</DIV><DIV CLASS=td><SELECT NAME=a_dom_id>")
  for d in domains:
   extra = "" if not dom_name == d.get('name') else "selected=selected"
   aWeb.wr("<OPTION VALUE=%s %s>%s</OPTION>"%(d.get('id'),extra,d.get('name')))
  aWeb.wr("</SELECT></DIV></DIV>")
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Network:</DIV><DIV CLASS=td><SELECT NAME=network_id>")
  for s in networks:
   aWeb.wr("<OPTION VALUE=%s>%s (%s)</OPTION>"%(s['id'],s['netasc'],s['description']))
  aWeb.wr("</SELECT></DIV></DIV>")
  aWeb.wr("</DIV></DIV>")
  aWeb.wr("</FORM>")
  aWeb.wr(aWeb.button('start', DIV='div_content_right', SPIN='true', URL='device_discover', FRM='device_discover_form'))
  aWeb.wr("</ARTICLE>")

################################################## interfaces #################################################
#
#
def interface_list(aWeb):
 if   aWeb['op'] == 'delete':
  args = aWeb.args()
  opres = aWeb.rest_call("device_interface_delete",args)
 elif aWeb['op'] == 'discover':
  opres = aWeb.rest_call("device_interface_discover",{'device':aWeb['device'],'cleanup':False})
 elif aWeb['op'] == 'link':
  opres = aWeb.rest_call("device_interface_link",{'a_id':aWeb['id'],'b_id':aWeb['peer_interface']})
 elif aWeb['op'] == 'unlink':
  opres = aWeb.rest_call("device_interface_unlink",{'a_id':aWeb['id'],'b_id':aWeb['peer_interface']})
 else:
  opres = ""
 res = aWeb.rest_call("device_interface_list",{'device':aWeb['device']})
 aWeb.wr("<ARTICLE><P>Interfaces (%s)</P>"%(res['hostname']))
 aWeb.wr(aWeb.button('reload', DIV='div_dev_data',URL='device_interface_list?device=%s'%res['id']))
 aWeb.wr(aWeb.button('add',    DIV='div_dev_data',URL='device_interface_info?device=%s&id=new'%res['id']))
 aWeb.wr(aWeb.button('trash',  DIV='div_dev_data',URL='device_interface_list?device=%s&op=delete'%res['id'], MSG='Delete interfaces?', FRM='interface_list', TITLE='Delete selected interfaces'))
 aWeb.wr("<A CLASS='z-op btn small text' DIV=div_dev_data URL='device_interface_list?device=%(id)s&op=discover' SPIN='true' MSG='Rediscover interfaces?' TITLE='Discover interfaces'>Discover</A>"%res)
 aWeb.wr("<A CLASS='z-op btn small text' DIV=div_dev_data URL='device_interface_sync?id=%(id)s' TITLE='LLDP Sync' SPIN=true>LLDP</A>"%res)
 aWeb.wr("<A CLASS='z-op btn small text' DIV=div_dev_data URL='device_interface_list?device=%(id)s&op=delete&device_id=%(id)s' TITLE='Clean up empty interfaces' SPIN=true>Cleanup</A>"%res)
 aWeb.wr("<SPAN CLASS=results>%s</SPAN><FORM ID=interface_list>"%(opres))
 aWeb.wr("<DIV CLASS=table>")
 aWeb.wr("<DIV CLASS=thead><DIV CLASS=th>Id</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>Description</DIV><DIV CLASS=th>SNMP Index</DIV><DIV CLASS=th>MAC</DIV><DIV CLASS=th TITLE='Peer ID of connecting interface'>Peer interface</DIV><DIV CLASS=th>&nbsp;</DIV></DIV>")
 aWeb.wr("<DIV CLASS=tbody>")
 for row in res['data']:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>"%(row['id'],row['name'],row['description'],row['snmp_index'],row['mac'],row['peer_interface'] if not row['multipoint'] else 'multipoint'))
  aWeb.wr("<INPUT TYPE=CHECKBOX VALUE=%(id)s ID='interface_%(id)s' NAME='interface_%(id)s'>"%row)
  aWeb.wr(aWeb.button('info',  DIV='div_dev_data',URL='device_interface_info?device=%s&id=%s'%(aWeb['device'],row['id'])))
  aWeb.wr(aWeb.button('sync',  DIV='div_dev_data',URL='device_interface_link_device?device=%s&id=%s&name=%s'%(aWeb['device'],row['id'],row['name']), TITLE='Connect'))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</FORM></ARTICLE>")

#
#
def interface_sync(aWeb):
 res = aWeb.rest_call("device_interface_sync",{'id':aWeb['id']})
 tmpl = "<DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>"
 aWeb.wr("<ARTICLE><P>LLDP sync operation</P>")
 aWeb.wr(aWeb.button('items', DIV='div_dev_data',URL='device_interface_list?device=%s'%res['id']))
 aWeb.wr("<A CLASS='z-op btn small text' DIV=div_dev_data URL='device_interface_list?device=%(id)s&op=discover' SPIN='true' MSG='Rediscover interfaces?' TITLE='Discover interfaces'>Discover</A>"%res)
 aWeb.wr("<A CLASS='z-op btn small text' DIV=div_dev_data URL='device_interface_sync?id=%(id)s' TITLE='LLDP Sync' SPIN=true>LLDP</A>"%res)
 aWeb.wr("<A CLASS='z-op btn small text' DIV=div_dev_data URL='device_interface_list?device=%(id)s&op=delete&device_id=%(id)s' TITLE='Clean up empty interfaces' SPIN=true>Cleanup</A>"%res)
 aWeb.wr("<DIV CLASS=table>")
 aWeb.wr("<DIV CLASS=thead><DIV CLASS=th>Type</DIV><DIV CLASS=th>SNMP Name</DIV><DIV CLASS=th>SNMP Index</DIV><DIV CLASS=th>Chassis Type</DIV><DIV CLASS=th>Chassis ID</DIV><DIV CLASS=th>Port Type</DIV><DIV CLASS=th>Port ID</DIV><DIV CLASS=th>Port Desc</DIV><DIV CLASS=th>Sys Name</DIV><DIV CLASS=th>Local ID</DIV><DIV CLASS=th>Peer ID</DIV><DIV CLASS=th>&nbsp;</DIV></DIV>")
 aWeb.wr("<DIV CLASS=tbody>")
 for i in res['connections'].values():
  aWeb.wr("<DIV CLASS=tr>")
  aWeb.wr(tmpl%(i['result'], i['snmp_name'],i['snmp_index'],i['chassis_type'],i['chassis_id'],i['port_type'],i['port_id'],i['port_desc'],i['sys_name'],i['local_id'],i.get('peer_id','-')))
  if i.get('peer_id'):
   aWeb.wr(aWeb.button('trash', DIV='div_dev_data', URL='device_interface_list?device=%s&op=unlink&id=%s&peer_interface=%s'%(aWeb['id'],i['local_id'],i['peer_id'])))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</ARTICLE>")

#
#
def interface_info(aWeb):
 args = aWeb.args()
 data = aWeb.rest_call("device_interface_info",args)['data']
 aWeb.wr("<ARTICLE CLASS=info STYLE='width:100%;'><P>Interface</P>")
 aWeb.wr("<FORM ID=interface_info_form>")
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=id VALUE='%s'>"%(data['id']))
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=device VALUE='%s'>"%(data['device']))
 aWeb.wr("<DIV CLASS=table STYLE='float:left; width:auto;'><DIV CLASS=tbody>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Name:</DIV><DIV CLASS=td><INPUT        NAME=name        VALUE='%s' TYPE=TEXT REQUIRED STYLE='min-width:400px'></DIV></DIV>"%(data['name']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Description:</DIV><DIV CLASS=td><INPUT NAME=description VALUE='%s' TYPE=TEXT REQUIRED STYLE='min-width:400px'></DIV></DIV>"%(data['description']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>SNMP Index:</DIV><DIV CLASS=td><INPUT  NAME=snmp_index  VALUE='%s' TYPE=TEXT REQUIRED STYLE='min-width:400px'></DIV></DIV>"%(data['snmp_index']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>MAC:</DIV><DIV CLASS='td readonly'>%s</DIV></DIV>"%(data['mac']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Multipoint:</DIV><DIV CLASS=td><INPUT  NAME=multipoint  VALUE=1    TYPE=CHECKBOX %s></DIV></DIV>"%("checked" if data['multipoint'] else ""))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Peer interface:</DIV><DIV CLASS=td>%s</DIV></DIV>"%data['peer_interface'])
 if data['peer_device']:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Peer Device</DIV><DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL='device_info?id=%s'>%s</A></DIV></DIV>"%(data['peer_device'],data['peer_device']))
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</FORM>")
 aWeb.wr(aWeb.button('back', DIV='div_dev_data', URL='device_interface_list?device=%s'%data['device']))
 aWeb.wr(aWeb.button('save', DIV='div_dev_data', URL='device_interface_info?op=update', FRM='interface_info_form'))
 if data['id'] != 'new':
  aWeb.wr(aWeb.button('trash', DIV='div_dev_data', URL='device_interface_list?op=delete&device=%s&id=%s'%(data['device'],data['id']), MSG='Delete interface?'))
 aWeb.wr("</ARTICLE>")

#
#
def interface_link_device(aWeb):
 aWeb.wr("<ARTICLE>")
 aWeb.wr("<FORM ID=interface_link>")
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=device VALUE=%s>"%aWeb['device'])
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=id   VALUE=%s>"%aWeb['id'])
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=name VALUE=%s>"%aWeb['name'])
 aWeb.wr("Connect '%s' to device (Id or IP): <INPUT CLASS='background' REQUIRED TYPE=TEXT NAME='peer' STYLE='width:100px' VALUE='%s'>"%(aWeb['name'],aWeb.get('peer','0')))
 aWeb.wr("</FORM><DIV CLASS=inline>")
 aWeb.wr(aWeb.button('back',    DIV='div_dev_data', URL='device_interface_list?device=%s'%aWeb['device']))
 aWeb.wr(aWeb.button('forward', DIV='div_dev_data', URL='device_interface_link_interface', FRM='interface_link'))
 aWeb.wr("</DIV></ARTICLE>")

#
#
def interface_link_interface(aWeb):
 res = aWeb.rest_call("device_interface_list",{'device':aWeb['peer'],'sort':'name'})
 aWeb.wr("<ARTICLE>")
 aWeb.wr("<FORM ID=interface_link>")
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=device VALUE=%s>"%aWeb['device'])
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=id   VALUE=%s>"%aWeb['id'])
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=name VALUE=%s>"%aWeb['name'])
 aWeb.wr("Connect '%s' to device id: <INPUT CLASS='background' READONLY TYPE=TEXT NAME='peer' STYLE='width:100px' VALUE=%s> on"%(aWeb['name'],res['id']))
 aWeb.wr("<SELECT NAME=peer_interface REQUIRED>")
 for intf in res.get('data',[]):
  aWeb.wr("<OPTION VALUE=%s>%s (%s)</OPTION>"%(intf['id'],intf['name'],intf['description']))
 aWeb.wr("</SELECT>")
 aWeb.wr("</FORM>")
 aWeb.wr(aWeb.button('back',    DIV='div_dev_data', URL='device_interface_link_device', FRM='interface_link'))
 aWeb.wr(aWeb.button('forward', DIV='div_dev_data', URL='device_interface_list?op=link', FRM='interface_link'))
 aWeb.wr("</ARTICLE>")

