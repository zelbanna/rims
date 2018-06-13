"""Module docstring.

HTML5 Ajax Openstack NOVA module

- left and right divs frames (div_content_left/right) needs to be created by ajax call
"""
__author__= "Zacharias El Banna"
__version__ = "1.0GA"
__status__= "Production"

################################# Nova ###############################
#
def list(aWeb):
 from zdcp.core.extras import get_quote
 cookie = aWeb.cookie_unjar('openstack')
 token  = cookie.get('token')
 if not token:
  print "Not logged in"
  return
 data = aWeb.rest_call("openstack_call",{'token':cookie['token'],'service':"nova",'call':"servers/detail"})['data']
 print "<SECTION CLASS=content-left ID=div_content_left><ARTICLE><P>Nova Servers</P>"
 print "<DIV CLASS=controls>"
 print aWeb.button('reload', DIV='div_content', URL='zdcp.cgi?nova_list')
 print aWeb.button('add', DIV='div_content_right', URL='zdcp.cgi?nova_select_parameters')
 print "</DIV>"
 print "<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Name</DIV><DIV CLASS=th STYLE='width:135px;'>&nbsp;</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for server in data.get('servers'):
  print "<DIV CLASS=tr>"
  print "<!-- {} - {} -->".format(server['status'],server['OS-EXT-STS:task_state'])
  print "<DIV CLASS=td STYLE='max-width:200px'><A CLASS='z-op' TITLE='VM info' DIV=div_content_right URL=zdcp.cgi?nova_action&id={}&op=info SPIN=true>{}</A></DIV>".format(server['id'],server['name'])
  print "<DIV CLASS=td><DIV CLASS=controls>"
  qserver = get_quote(server['name'])
  actionurl = 'zdcp.cgi?nova_action&name=%s&id=%s&op={}'%(qserver,server['id'])
  print aWeb.button('term', TARGET='_blank', HREF='zdcp.cgi?nova_console&name=%s&id=%s'%(qserver,server['id']), TITLE='New window console')
  print aWeb.button('term-frame', DIV='div_content_right', URL='zdcp.cgi?nova_console&inline=yes&id=%s'%server['id'], TITLE='Embedded console')
  print aWeb.button('delete', DIV='div_content_right', URL=actionurl.format('remove'), MSG='Are you sure you want to delete VM?', SPIN='true')
  if not server['OS-EXT-STS:task_state']:
   if   server['status'] == 'ACTIVE':
    print aWeb.button('stop', DIV='div_content_right', URL=actionurl.format('stop'), SPIN='true', TITLE='Stop VM')
    print aWeb.button('reload', DIV='div_content_right', URL=actionurl.format('reboot'), SPIN='true', TITLE='Reboot')
   elif server['status'] == 'SHUTOFF':
    print aWeb.button('start', DIV='div_content_right', URL=actionurl.format('start'), SPIN='true', TITLE='Start VM')
  else:
   print aWeb.button('info', DIV='div_content_right', URL=actionurl.format('info'), SPIN='true', TITLE='VM info')
  print "</DIV></DIV></DIV>"
 print "</DIV></DIV>"
 print "</ARTICLE></SECTION>"
 print "<SECTION CLASS=content-right ID=div_content_right></SECTION>"

def select_parameters(aWeb):
 cookie = aWeb.cookie_unjar('openstack')
 token  = cookie.get('token')
 if not token:
  print "Not logged in"
  return
 resources = aWeb.rest_call("openstack_vm_resources",{'token':token})
 print aWeb.dragndrop()
 print "<ARTICLE CLASS='info'><P>New VM parameters</P>"
 print "<FORM ID=frm_os_create_vm>"
 print "<INPUT TYPE=HIDDEN NAME=os_network ID=os_network>"
 print "<DIV CLASS=table><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Name</DIV><DIV CLASS=td><INPUT NAME=os_name PLACEHOLDER='Unique Name'></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td>Image</DIV><DIV CLASS=td><SELECT NAME=os_image>"
 for img in resources['images']:
  print "<OPTION VALUE={}>{} (Min Ram: {}Mb)</OPTION>".format(img['id'],img['name'],img['min_ram'])
 print "</SELECT></DIV></DIV>"

 print "<DIV CLASS=tr><DIV CLASS=td>Flavor</DIV><DIV CLASS='table-val td'><SELECT NAME=os_flavor>"
 for fl in resources['flavors']:
  print "<OPTION VALUE={}>{} (Ram: {}Mb, vCPUs: {}, Disk: {}Gb</OPTION>".format(fl['id'],fl['name'],fl['ram'],fl['vcpus'],fl['disk'])
 print "</SELECT></DIV></DIV>"
 print "</DIV></DIV>"
 print "<DIV CLASS='border'><UL CLASS='drop vertical' ID=ul_network DEST=os_network></UL></DIV>"
 print "</FORM><DIV CLASS=controls>"
 print aWeb.button('start',DIV='div_content_right', URL='zdcp.cgi?nova_action&id=new&op=add',FRM='frm_os_create_vm', SPIN='true')
 print "</DIV>"
 print "<DIV CLASS='border'><UL CLASS='drop vertical' ID=ul_avail>"
 for net in resources['networks']:
  if net.get('contrail:subnet_ipam'):
   print "<LI ID=net_%s CLASS='drag'>%s (%s)</LI>"%(net['id'],net['name'],net['contrail:subnet_ipam'][0]['subnet_cidr'])
 print "</UL></DIV>"
 print "</ARTICLE>"

######################################## Actions ########################################
#
def action(aWeb):
 from zdcp.site.openstack import dict2html
 cookie = aWeb.cookie_unjar('openstack')
 token  = cookie.get('token')
 if not token:
  print "Not logged in"
  return
 args ={'token':cookie['token'],'service':'nova'}
 op   = aWeb.get('op','info')

 if   op == 'info':
  from zdcp.core.extras import get_quote
  args['call'] = "servers/%s"%aWeb['id']
  server = aWeb.rest_call("openstack_call",args)['data']['server']
  qserver = get_quote(server['name'])
  tmpl = "<BUTTON CLASS='z-op' TITLE='{}' DIV=div_os_info URL=zdcp.cgi?nova_action&id=%s&op={} SPIN=true>{}</BUTTON>"%aWeb['id']
  print "<DIV>"
  print tmpl.format('Details','details','VM Details')
  print tmpl.format('Diagnostics','diagnostics','Diagnostics')
  print tmpl.format('Networks','networks','Networks')
  print "<A CLASS=btn TITLE='New-tab Console' TARGET=_blank HREF='zdcp.cgi?nova_console&name={0}&id={1}'>Console</A>".format(qserver,aWeb['id'])
  print "</DIV>"
  print "<ARTICLE STYLE='overflow:auto;' ID=div_os_info>"
  dict2html(server,server['name'])
  print "</ARTICLE>"

 elif op == 'details':
  args['call'] = "servers/%s"%aWeb['id']
  server = aWeb.rest_call("openstack_call",args)['data']['server']
  dict2html(server,server['name'])

 elif op == 'stop' or op == 'start' or op == 'reboot':
  args['arguments'] = {"os-"+op:None} if op != 'reboot' else {"reboot":{ "type":"SOFT" }}
  args['call'] = "servers/%s/action"%aWeb['id']
  res = aWeb.rest_call("openstack_call",args)
  print "<ARTICLE>"
  if res['code'] == 202:
   print "Command executed successfully [%s]"%(op)
  else:
   print "Error executing command [%s]"%str(res)
  print "</ARTICLE>"

 elif op == 'diagnostics':
  args['call'] = "servers/%s/diagnostics"%aWeb['id']
  data = aWeb.rest_call("openstack_call",args)['data']
  dict2html(data)

 elif op == 'networks':
  from json import dumps
  args['vm']  = aWeb['id']
  data = aWeb.rest_call("openstack_vm_networks",args)

  print "<DIV CLASS=table STYLE='width:auto'>"
  print "<DIV CLASS=thead><DIV CLASS=th>MAC</DIV><DIV CLASS=th>Routing Instance</DIV><DIV CLASS=th>Network</DIV><DIV CLASS=th>IP</DIV><DIV CLASS=th>Floating IP</DIV><DIV CLASS=th>Operation</DIV></DIV><DIV CLASS=tbody>"
  for intf in data['interfaces']:
   print "<DIV CLASS=tr>"
   print "<DIV CLASS=td>{}</DIV>".format(intf['mac_address'])
   print "<DIV CLASS=td>{}</DIV>".format(intf['routing-instance'])
   print "<DIV CLASS=td><A CLASS='z-op' DIV=div_content_right SPIN=true URL=zdcp.cgi?neutron_action&id={0}&op=info>{1}</A></DIV>".format(intf['network_uuid'],intf['network_fqdn'])
   print "<DIV CLASS=td>{}</DIV>".format(intf['ip_address'])
   if intf.get('floating_ip_address'):
    print "<DIV CLASS=td>{} ({})</DIV><DIV CLASS=td>&nbsp;".format(intf['floating_ip_address'],intf['floating_ip_name'])
    print aWeb.button('delete',DIV='div_os_info', URL='zdcp.cgi?neutron_action&op=fi_disassociate&id=%s'%intf['floating_ip_uuid'], SPIN='true')
    print "</DIV>"
   else:
    print "<DIV CLASS=td>&nbsp;</DIV>"
    print "<DIV CLASS=td>&nbsp;</DIV>"
   print "</DIV>"
  print "</DIV></DIV>"

 elif op == 'add':
  print aWeb

 elif op == 'remove':
  args['call'] = "servers/{}".format(aWeb['id'])
  args['method'] = 'DELETE'
  res = aWeb.rest_call("openstack_rest",args)
  print "<ARTICLE><P>Removing VM</P>"
  print "VM removed" if res['code'] == 204 else "Error code: %s"%(res['code'])
  print "</ARTICLE>"

def console(aWeb):
 cookie = aWeb.cookie_unjar('openstack')
 token  = cookie.get('token')
 res = aWeb.rest_call("openstack_vm_console",{'token':cookie['token'],'vm':aWeb['id']})
 if aWeb['inline']:
  print "<iframe id='console_embed' src='{}' STYLE='width: 100%; height: 100%;'></iframe>".format(res['url'])
 else:
  aWeb.put_redirect("%s&title=%s"%(res['url'],aWeb['name']))
