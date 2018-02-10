"""Module docstring.

HTML5 Ajax Openstack NOVA calls module

- left and right divs frames (div_content_left/right) needs to be created by ajax call
"""
__author__= "Zacharias El Banna"
__version__ = "18.02.09GA"
__status__= "Production"

from ..devices.openstack import OpenstackRPC
from ..site.openstack import dict2html

################################# Nova ###############################
#
def list(aWeb):
 from ..core.extras import get_quote
 cookie = aWeb.cookie_unjar('nova')
 token  = cookie.get('token')
 if not token:
  print "Not logged in"
  return
 controller = OpenstackRPC(cookie.get('controller'),token)
 try:
  data = controller.call(cookie.get('port'),cookie.get('url') + "/servers/detail")['data']
 except Exception as e:
  print "Error retrieving list %s"%str(e)
  return

 print "<SECTION CLASS=content-left ID=div_content_left><ARTICLE><P>Nova Servers</P>"
 print "<DIV CLASS=controls>"
 print aWeb.button('reload', DIV='div_content', URL='sdcp.cgi?call=nova_list')
 print aWeb.button('add', DIV='div_content_right', URL='sdcp.cgi?call=nova_select_parameters')
 print "</DIV>"
 print "<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Name</DIV><DIV CLASS=th STYLE='width:135px;'>&nbsp;</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for server in data.get('servers',None):
  print "<DIV CLASS=tr>"
  print "<!-- {} - {} -->".format(server['status'],server['OS-EXT-STS:task_state'])
  print "<DIV CLASS=td STYLE='max-width:200px'><A CLASS='z-op' TITLE='VM info' DIV=div_content_right URL=sdcp.cgi?call=nova_action&id={}&op=info SPIN=true>{}</A></DIV>".format(server['id'],server['name'])
  print "<DIV CLASS='td controls'>"
  qserver = get_quote(server['name'])
  actionurl = 'sdcp.cgi?call=nova_action&name=%s&id=%s&op={}'%(qserver,server['id'])
  print aWeb.button('term', TARGET='_blank', HREF='sdcp.cgi?call=nova_console&headers=no&name=%s&id=%s'%(qserver,server['id']), TITLE='New window console')
  print aWeb.button('term-frame', DIV='div_content_right', URL='sdcp.cgi?call=nova_console&id=%s'%server['id'], TITLE='Embedded console')
  print aWeb.button('delete', DIV='div_content_right', URL=actionurl.format('remove'), MSG='Are you sure you want to delete VM?', SPIN='true')
  if not server['OS-EXT-STS:task_state']:
   if   server['status'] == 'ACTIVE':
    print aWeb.button('shutdown', DIV='div_content_right', URL=actionurl.format('stop'), SPIN='true', TITLE='Stop VM')
    print aWeb.button('reboot', DIV='div_content_right', URL=actionurl.format('reboot'), SPIN='true', TITLE='Reboot')
   elif server['status'] == 'SHUTOFF':
    print aWeb.button('start', DIV='div_content_right', URL=actionurl.format('start'), SPIN='true', TITLE='Start VM')
  else:
   print aWeb.button('info', DIV='div_content_right', URL=actionurl.format('info'), SPIN='true', TITLE='VM info')
  print "</DIV></DIV>"
 print "</DIV></DIV>"
 print "</ARTICLE></SECTION>"
 print "<SECTION CLASS=content-right ID=div_content_right></SECTION>"

def select_parameters(aWeb):
 nova_cookie = aWeb.cookie_unjar('nova')
 token  = nova_cookie.get('token')
 if not token:
  print "Not logged in"
  return
 controller = OpenstackRPC(nova_cookie.get('controller'),token)
 port,url = nova_cookie.get('port'),nova_cookie.get('url')
 flavors  = controller.call(port,url + "/flavors/detail?sort_key=name")['data']['flavors']
 glance_cookie  = aWeb.cookie_unjar('glance')
 images   = controller.call(glance_cookie.get('port'),glance_cookie.get('url') + "/v2/images?sort=name:asc")['data']['images']
 neutron_cookie = aWeb.cookie_unjar('neutron')
 networks = controller.call(neutron_cookie.get('port'),neutron_cookie.get('url') + "/v2.0/networks?sort_key=name")['data']['networks']
 print aWeb.dragndrop()
 print "<ARTICLE CLASS='info'><P>New VM parameters</P>"
 print "<FORM ID=frm_os_create_vm>"
 print "<INPUT TYPE=HIDDEN NAME=os_network ID=os_network>"
 print "<DIV CLASS=table><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Name</DIV><DIV CLASS=td><INPUT NAME=os_name PLACEHOLDER='Unique Name'></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td>Image</DIV><DIV CLASS=td><SELECT NAME=os_image>"
 for img in images:
  print "<OPTION VALUE={}>{} (Min Ram: {}Mb)</OPTION>".format(img['id'],img['name'],img['min_ram'])
 print "</SELECT></DIV></DIV>"

 print "<DIV CLASS=tr><DIV CLASS=td>Flavor</DIV><DIV CLASS='table-val td'><SELECT NAME=os_flavor>"
 for fl in flavors:
  print "<OPTION VALUE={}>{} (Ram: {}Mb, vCPUs: {}, Disk: {}Gb</OPTION>".format(fl['id'],fl['name'],fl['ram'],fl['vcpus'],fl['disk'])
 print "</SELECT></DIV></DIV>"
 print "</DIV></DIV>"
 print "<DIV CLASS='border'><UL CLASS='drop vertical' ID=ul_network DEST=os_network></UL></DIV>"
 print "</FORM><DIV CLASS=controls>"
 print aWeb.button('start',DIV='div_content_right', URL='sdcp.cgi?call=nova_action&id=new&op=add',FRM='frm_os_create_vm', SPIN='true')
 print "</DIV>"
 print "<DIV CLASS='border'><UL CLASS='drop vertical' ID=ul_avail>"
 for net in networks:
  if net.get('contrail:subnet_ipam'):
   print "<LI ID=net_%s CLASS='drag'>%s (%s)</LI>"%(net['id'],net['name'],net['contrail:subnet_ipam'][0]['subnet_cidr'])
 print "</UL></DIV>"
 print "</ARTICLE>"

######################################## Actions ########################################
#
def action(aWeb):
 cookie = aWeb.cookie_unjar('nova')
 token  = cookie.get('token')
 if not token:
  print "Not logged in"
  return
 controller = OpenstackRPC(cookie.get('controller'),token)

 port = cookie.get('port')
 url  = cookie.get('url')
 op   = aWeb.get('op','info')

 aWeb.log("nova_action - id:{} op:{}".format(aWeb['id'],op))

 if   op == 'info':
  from ..core.extras import get_quote
  server = controller.call(port,url + "/servers/%s"%aWeb['id'])['data']['server']
  qserver = get_quote(server['name'])
  tmpl = "<BUTTON CLASS='z-op' TITLE='{}' DIV=div_os_info URL=sdcp.cgi?call=nova_action&id=%s&op={} SPIN=true>{}</BUTTON>"%aWeb['id']
  print "<DIV>"
  print tmpl.format('Details','details','VM Details')
  print tmpl.format('Diagnostics','diagnostics','Diagnostics')
  print tmpl.format('Networks','networks','Networks')
  print "<A CLASS=btn TITLE='New-tab Console' TARGET=_blank HREF='sdcp.cgi?call=nova_console&name={0}&id={1}'>Console</A>".format(qserver,aWeb['id'])
  print "</DIV>"
  print "<ARTICLE STYLE='overflow:auto;' ID=div_os_info>"
  dict2html(server,server['name'])
  print "</ARTICLE>"

 elif op == 'details':
  server = controller.call(port,url + "/servers/{}".format(aWeb['id']))['data']['server']
  dict2html(server,server['name'])

 elif op == 'stop' or op == 'start' or op == 'reboot':
  arg = {"os-"+op:None} if op != 'reboot' else {"reboot":{ "type":"SOFT" }}
  try:
   ret = controller.call(port,url + "/servers/{}/action".format(aWeb['id']),args=arg)
   print "Command executed successfully [{}]".format(str(arg))
  except Exception as e:
   print "Error executing command [%s]"%str(e)

 elif op == 'diagnostics':
  data = controller.call(port,url + "/servers/{}/diagnostics".format(aWeb['id']))['data']
  dict2html(data)

 elif op == 'print':
  from json import dumps
  print "<PRE>{}</PRE>".format(dumps(controller.href(aWeb['id'])['data'],indent=4))

 elif op == 'networks':
  from json import dumps
  vm  = controller.call("8082","virtual-machine/{}".format(aWeb['id']))['data']['virtual-machine']
  print "<DIV CLASS=table STYLE='width:auto'>"
  print "<DIV CLASS=thead><DIV CLASS=th>MAC</DIV><DIV CLASS=th>Routing Instance</DIV><DIV CLASS=th>Network</DIV><DIV CLASS=th>IP</DIV><DIV CLASS=th>Floating IP</DIV><DIV CLASS=th>Operation</DIV></DIV><DIV CLASS=tbody>"
  for vmir in vm['virtual_machine_interface_back_refs']:
   vmi = controller.href(vmir['href'])['data']['virtual-machine-interface']
   ip = controller.href(vmi['instance_ip_back_refs'][0]['href'])['data']['instance-ip']
   print "<DIV CLASS=tr>"
   print "<!-- {} -->".format(vmir['href'])
   print "<DIV CLASS=td>{}</DIV>".format(vmi['virtual_machine_interface_mac_addresses']['mac_address'][0])
   print "<DIV CLASS=td>{}</DIV>".format(vmi['routing_instance_refs'][0]['to'][3])
   print "<DIV CLASS=td><A CLASS='z-op' DIV=div_content_right SPIN=true URL=sdcp.cgi?call=neutron_action&id={0}&op=info>{1}</A></DIV>".format(vmi['virtual_network_refs'][0]['uuid'],vmi['virtual_network_refs'][0]['to'][2])
   print "<DIV CLASS=td>{}</DIV>".format(ip['instance_ip_address'])
   if vmi.get('floating_ip_back_refs'):
    fip = controller.href(vmi['floating_ip_back_refs'][0]['href'])['data']['floating-ip']
    print "<DIV CLASS=td>{} ({})</DIV><DIV CLASS=td>&nbsp;".format(fip['floating_ip_address'],fip['fq_name'][2])
    print aWeb.button('delete',DIV='div_os_info', URL='sdcp.cgi?call=neutron_action&op=fi_disassociate&id=%s'%fip['uuid'], SPIN='true')
    print "</DIV>"
   else:
    print "<DIV CLASS=td>&nbsp;</DIV>"
    print "<DIV CLASS=td>&nbsp;</DIV>"
   print "</DIV>"
  print "</DIV></DIV>"

 elif op == 'add':
  print aWeb

 elif op == 'remove':
  try:
   ret = controller.call(port,url + "/servers/{}".format(aWeb['id']), method='DELETE')
   print "<ARTICLE><P>Removing VM</P>"
   print "VM removed" if ret['code'] == 204 else "Error code: %s"%(ret['code'])
   print "</ARTICLE>"
  except Exception as e:
   print "Error performing op %s"%str(e)

def console(aWeb):
 cookie = aWeb.cookie_unjar('nova')
 token  = cookie.get('token')
 if not token:
  if aWeb['headers'] == 'no':
   aWeb.put_html('Openstack Nova')
  print "Not logged in"
  return
 controller = OpenstackRPC(cookie.get('controller'),token)

 try:
  data = controller.call(cookie.get('port'), cookie.get('url') + "/servers/{}/remote-consoles".format(aWeb['id']), { "remote_console": { "protocol": "vnc", "type": "novnc" } }, header={'X-OpenStack-Nova-API-Version':'2.8'})['data']
  url = data['remote_console']['url']
  # URL is not always proxy ... so force it through: remove http:// and replace IP (assume there is a port..) with controller IP
  url = "http://" + cookie.get('controller') + ":" + url[7:].partition(':')[2]
  if not aWeb['headers']:
   print "<iframe id='console_embed' src='{}' STYLE='width: 100%; height: 100%;'></iframe>".format(url)
  else:
   aWeb.put_redirect("{}&title={}".format(url,aWeb['name']))
 except: pass
