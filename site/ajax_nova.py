"""Module docstring.

Ajax Openstack NOVA calls module

- left and right divs frames (div_os_left/right) needs to be created by ajax call
"""
__author__= "Zacharias El Banna"
__version__ = "17.6.1GA"
__status__= "Production"

from sdcp.devices.openstack import OpenstackRPC
from sdcp.site.ajax_openstack import dict2html

################################# Nova ###############################
#
def list(aWeb):
 cookie = aWeb.get_cookie()
 token  = cookie.get('os_user_token')
 if not token:
  print "Not logged in"
  return
 controller = OpenstackRPC(cookie.get('os_controller'),token)

 ret = controller.call(cookie.get('os_nova_port'),cookie.get('os_nova_url') + "/servers/detail")
 if not ret['result'] == "OK":
  print "Error retrieving list {}".format(str(ret))
  return

 print "<DIV CLASS=z-os-left ID=div_os_left>"
 print "<DIV CLASS=z-table style='width:394px'><TABLE style='width:99%'>"
 print "<THEAD style='height:20px'><TH COLSPAN=3><CENTER>Nova Servers</CENTER></TH></THEAD>"
 print "<TR style='height:20px'><TD COLSPAN=3>"
 print "<A TITLE='Reload List' CLASS='z-btn z-small-btn z-op' DIV=div_os_frame URL='ajax.cgi?call=nova_list'><IMG SRC='images/btn-reboot.png'></A>"
 print "<A TITLE='Add serer'   CLASS='z-btn z-small-btn z-op' DIV=div_os_right URL='ajax.cgi?call=nova_select_parameters'><IMG SRC='images/btn-add.png'></A>"
 print "</TR>"
 print "<THEAD><TH>Name</TH><TH style='width:94px;'></TH></THEAD>"
 for server in ret['data'].get('servers',None):
  qserver = aWeb.quote(server['name'])
  tmpl = "<A TITLE='{}' CLASS='z-btn z-op z-small-btn' DIV=div_os_right URL=ajax.cgi?call=nova_action&name=" + qserver + "&id=" + server['id'] + "&op={} SPIN=true>{}</A>"
  print "<TR>"
  print "<!-- {} - {} -->".format(server['status'],server['OS-EXT-STS:task_state'])
  print "<TD><A TITLE='VM info' CLASS='z-op' DIV=div_os_right URL=ajax.cgi?call=nova_action&id={}&op=info SPIN=true>{}</A></TD>".format(server['id'],server['name'])
  print "<TD>"
  print "<A TITLE='New-tab Console'  CLASS='z-btn z-small-btn'	TARGET=_blank      HREF='pane.cgi?view=openstack_console&name={}&id={}'><IMG SRC='images/btn-term.png'></A>".format(qserver,server['id'])
  print "<A TITLE='Embedded Console' CLASS='z-btn z-op z-small-btn' DIV=div_os_right URL=ajax.cgi?call=nova_console&id={} OP=load><IMG SRC='images/btn-term-frame.png'></A>".format(server['id'])
  print "<A TITLE='Remove VM'        CLASS='z-btn z-op z-small-btn' DIV=div_os_right URL=ajax.cgi?call=nova_action&id={}&op=remove MSG='Are you sure you want to delete VM?' SPIN=true><IMG SRC='images/btn-remove.png'></A>".format(server['id'])
  if not server['OS-EXT-STS:task_state']:
   if   server['status'] == 'ACTIVE':
    print tmpl.format('Stop VM','stop',"<IMG SRC='images/btn-shutdown.png'>")
    print tmpl.format('Reboot','reboot',"<IMG SRC='images/btn-reboot.png'>")
   elif server['status'] == 'SHUTOFF':
    print tmpl.format('Start VM','start',"<IMG SRC='images/btn-start.png'>")
  else:
   print tmpl.format('VM info','info',"<IMG SRC='images/btn-info.png'>")
  print "</TD></TR>"
 print "</TABLE></DIV>"
 print "</DIV>"
 print "<DIV CLASS=z-os-right ID=div_os_right></DIV>"


def select_parameters(aWeb):
 cookie = aWeb.get_cookie()
 token  = cookie.get('os_user_token')
 if not token:
  print "Not logged in"
  return
 controller = OpenstackRPC(cookie.get('os_controller'),token)
 port,url = cookie.get('os_nova_port'),cookie.get('os_nova_url')
 print "<DIV CLASS=z-table>"
 print "<H2>New VM parameters</H2>"
 print "<FORM ID=frm_os_create_vm><TABLE><THEAD><TH>Parameter</TH><TH>Value</TH></THEAD>"
 print "<TR><TD>Name</TD><TD><INPUT CLASS=z-input NAME=os_name PLACEHOLDER='Unique Name'></TD></TR>"
 print "<TR><TD>Image</TD><TD><SELECT CLASS=z-select NAME=os_image>"
 images = controller.call(cookie.get('os_glance_port'),cookie.get('os_glance_url') + "/v2/images?sort=name:asc")['data']['images']
 for img in images:
  print "<OPTION VALUE={}>{} (Min Ram: {}Mb)</OPTION>".format(img['id'],img['name'],img['min_ram'])
 print "</SELECT></TD></TR>"

 flavors = controller.call(port,url + "/flavors/detail?sort_key=name")['data']['flavors']
 print "<TR><TD>Flavor</TD><TD><SELECT CLASS=z-select NAME=os_flavor>"
 for fl in flavors:
  print "<OPTION VALUE={}>{} (Ram: {}Mb, vCPUs: {}, Disk: {}Gb</OPTION>".format(fl['id'],fl['name'],fl['ram'],fl['vcpus'],fl['disk'])
 print "</SELECT></TD></TR>"

 print "<TR><TD>Network</TD><TD><SELECT CLASS=z-select NAME=os_network>"
 networks = controller.call(cookie.get('os_neutron_port'),cookie.get('os_neutron_url') + "/v2.0/networks?sort_key=name")['data']['networks']
 for net in networks:
  if net.get('contrail:subnet_ipam'):
   print "<OPTION VALUE={}>{} ({})</OPTION>".format(net['id'],net['name'],net['contrail:subnet_ipam'][0]['subnet_cidr'])
 print "</SELECT></TD></TR>"

 print "</TABLE>"
 print "</FORM>"
 print "<A TITLE='Create VM' CLASS='z-btn z-op z-small-btn' FRM=frm_os_create_vm DIV=div_os_right URL=ajax.cgi?call=nova_action&id={}&op=add SPIN=true><IMG SRC='images/btn-start.png'></A>".format("new") 
 print "</DIV>"

######################################## Actions ########################################
#
# 
def action(aWeb):
 cookie = aWeb.get_cookie()
 token  = cookie.get('os_user_token')
 if not token:
  print "Not logged in"
  return
 controller = OpenstackRPC(cookie.get('os_controller'),token)

 port  = cookie.get('os_nova_port')
 url   = cookie.get('os_nova_url')
 id   = aWeb.get_value('id')
 op   = aWeb.get_value('op','info')

 aWeb.log_msg("nova_action - id:{} op:{} for project:{}".format(id,op,cookie.get('os_project_name')))

 if   op == 'info':
  server = controller.call(port,url + "/servers/{}".format(id))['data']['server']
  qserver = aWeb.quote(server['name'])
  tmpl = "<A TITLE='{}' CLASS='z-btn z-op' DIV=div_os_info URL=ajax.cgi?call=nova_action&id=" + id+ "&op={} SPIN=true>{}</A>"
  print "<DIV>"
  print tmpl.format('Details','details','VM Details')
  print tmpl.format('Diagnostics','diagnostics','Diagnostics')
  print tmpl.format('Networks','networks','Networks')
  print "<A TITLE='New-tab Console'  CLASS='z-btn'  TARGET=_blank HREF='pane.cgi?view=openstack_console&name={0}&id={1}'>Console</A>".format(qserver,id)
  print "</DIV>"
  print "<DIV CLASS=z-table style='overflow:auto;' ID=div_os_info>"
  dict2html(server,server['name'])
  print "</DIV>"

 elif op == 'details':
  server = controller.call(port,url + "/servers/{}".format(id))['data']['server']
  dict2html(server,server['name'])

 elif op == 'stop' or op == 'start' or op == 'reboot':
  arg = {"os-"+op:None} if op != 'reboot' else {"reboot":{ "type":"SOFT" }}
  ret = controller.call(port,url + "/servers/{}/action".format(id),args=arg)
  if ret.get('code') == 202:
   print "Command executed successfully [{}]".format(str(arg))
  else:
   print "Error executing command [{}]".format(str(arg))

 elif op == 'diagnostics':
  ret = controller.call(port,url + "/servers/{}/diagnostics".format(id))
  dict2html(ret['data'])

 elif op == 'print':
  from json import dumps
  print "<PRE>{}</PRE>".format(dumps(controller.href(id)['data'],indent=4))

 elif op == 'networks':
  from json import dumps
  vm  = controller.call("8082","virtual-machine/{}".format(id))['data']['virtual-machine']
  print "<TABLE>"
  print "<THEAD><TH>MAC</TH><TH>Routing Instance</TH><TH>Network</TH><TH>IP</TH><TH>Floating IP</TH><TH>Operation</TH></THEAD>"
  for vmir in vm['virtual_machine_interface_back_refs']:
   vmi = controller.href(vmir['href'])['data']['virtual-machine-interface']
   ip = controller.href(vmi['instance_ip_back_refs'][0]['href'])['data']['instance-ip']
   print "<TR>"
   print "<!-- {} -->".format(vmir['href'])
   print "<TD>{}</TD>".format(vmi['virtual_machine_interface_mac_addresses']['mac_address'][0])
   print "<TD>{}</TD>".format(vmi['routing_instance_refs'][0]['to'][3])
   print "<TD><A CLASS='z-op' DIV=div_os_right SPIN=true URL=ajax.cgi?call=neutron_action&id={0}&op=info>{1}</A></TD>".format(vmi['virtual_network_refs'][0]['uuid'],vmi['virtual_network_refs'][0]['to'][2])
   print "<TD>{}</TD>".format(ip['instance_ip_address'])
   if vmi.get('floating_ip_back_refs'):
    fip = controller.href(vmi['floating_ip_back_refs'][0]['href'])['data']['floating-ip']
    print "<TD>{} ({})</TD>".format(fip['floating_ip_address'],fip['fq_name'][2])
    print "<TD><A TITLE='Disassociate' CLASS='z-btn z-small-btn z-op' DIV=div_os_info  URL=ajax.cgi?call=neutron_action&op=fi_disassociate&id={} SPIN=true><IMG SRC=images/btn-remove.png></TD>".format(fip['uuid'])
   else:
    print "<TD></TD>"
    print "<TD></TD>"
   print "</TR>"
  print "</TABLE>"

 elif op == 'add':
  print aWeb.get_keys()

 elif op == 'remove':
  ret = controller.call(port,url + "/servers/{}".format(id), method='DELETE')
  if not ret['result'] == "OK":
   print "Error performing op {}".format(str(ret))
   return
  print "<DIV CLASS='z-table'>"
  print "<H2>Removing VM</H2>"
  if ret['code'] == 204:
   print "VM removed"
  else:
   print "Error code: {}".format(ret['code'])
  print "</DIV>"

def console(aWeb):
 cookie = aWeb.get_cookie()
 token = cookie.get('os_user_token')
 if not token:
  print "Not logged in"
  return
 id   = aWeb.get_value('id')
 controller = OpenstackRPC(cookie.get('os_controller'),token)
 data = controller.call(cookie.get('os_nova_port'), cookie.get('os_nova_url') + "/servers/{}/remote-consoles".format(id), { "remote_console": { "protocol": "vnc", "type": "novnc" } }, header={'X-OpenStack-Nova-API-Version':'2.8'})
 if data['code'] == 200:
  url = data['data']['remote_console']['url']
  # URL is not always proxy ... so force it through: remove http:// and replace IP (assume there is a port..) with controller IP
  url = "http://" + cookie.get('os_controller') + ":" + url[7:].partition(':')[2]
  print "<iframe id='console_embed' src='{}' style='width: 100%; height: 100%;'></iframe>".format(url)
