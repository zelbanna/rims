"""Module docstring.

Ajax Openstack NOVA calls module

"""
__author__= "Zacharias El Banna"
__version__ = "17.6.1GA"
__status__= "Production"

from sdcp.devices.openstack import OpenstackRPC
import sdcp.SettingsContainer as SC

def _print_info(aData):
 print "<TABLE style='width:99%'>"
 print "<THEAD><TH>Field</TH><TH>Data</TH></THEAD>"
 for key,value in aData.iteritems():
  if not isinstance(value,dict):
   print "<TR><TD>{}</TD><TD style='white-space:normal; overflow:auto;'>{}</TD></TR>".format(key,value)
  else:
   print "<TR><TD>{}</TD><TD style='white-space:normal; overflow:auto;'><TABLE style='width:100%'>".format(key)
   for k,v in value.iteritems():
    print "<TR><TD>{}</TD><TD>{}</TD></TR>".format(k,v)
   print "</TABLE></TD></TR>"
 print "</TABLE>"

################################# Nova ###############################
#
def list(aWeb):
 cookie = aWeb.get_cookie()
 token  = cookie.get('os_user_token')
 if not token:
  print "Not logged in"
  return
 controller = OpenstackRPC(cookie.get('os_controller'),token)

 port  = cookie.get('os_nova_port')
 url   = cookie.get('os_nova_url')

 ret = controller.call(port,url + "/servers/detail")
 if not ret['result'] == "OK":
  print "Error retrieving list {}".format(str(ret))
  return

 print "<DIV CLASS='z-table' style='width:394px'><TABLE style='width:99%'>"
 print "<THEAD style='height:20px'><TH COLSPAN=3><CENTER>Nova Servers</CENTER></TH></THEAD>"
 print "<TR style='height:20px'><TD COLSPAN=3>"
 print "<A TITLE='Reload List' CLASS='z-btn z-small-btn z-op' OP=load DIV=div_navleft URL='ajax.cgi?call=nova_list'><IMG SRC='images/btn-reboot.png'></A>"
 print "</TR>"
 print "<THEAD><TH>Name</TH><TH style='width:94px;'>Operations</TH></THEAD>"
 for server in ret['data'].get('servers',None):
  qserver = aWeb.quote(server['name'])
  tmpl = "<A TITLE='{}' CLASS='z-btn z-op z-small-btn' DIV=div_navcont URL=ajax.cgi?call=nova_action&name=" + qserver + "&id=" + server['id'] + "&op={} OP=load SPIN=true>{}</A>"
  print "<TR>"
  print "<!-- {} - {} -->".format(server['status'],server['OS-EXT-STS:task_state'])
  print "<TD><A TITLE='VM info' CLASS='z-op' DIV=div_navcont URL=ajax.cgi?call=nova_action&id={}&op=info OP=load SPIN=true>{}</A></TD>".format(server['id'],server['name'])
  print "<TD>"
  print "<A TITLE='New-tab Console'  CLASS='z-btn z-small-btn'	TARGET=_blank      HREF='pane.cgi?view=openstack_console&name={}&id={}'><IMG SRC='images/btn-term.png'></A>".format(qserver,server['id'])
  print "<A TITLE='Embedded Console' CLASS='z-btn z-op z-small-btn' DIV=div_navcont URL=ajax.cgi?call=nova_console&id={} OP=load><IMG SRC='images/btn-term-frame.png'></A>".format(server['id'])
  print "<A TITLE='Remove VM'        CLASS='z-btn z-op z-small-btn' DIV=div_navcont URL=ajax.cgi?call=nova_action&id={}&op=remove OP=load MSG='Are you sure you want to delete VM?' SPIN=true><IMG SRC='images/btn-remove.png'></A>".format(server['id'])
  if not server['OS-EXT-STS:task_state']:
   if   server['status'] == 'ACTIVE':
    print tmpl.format('Stop VM','stop',"<IMG SRC='images/btn-shutdown.png'>")
    print tmpl.format('Reboot','reboot',"<IMG SRC='images/btn-reboot.png'>")
   elif server['status'] == 'SHUTOFF':
    print tmpl.format('Start VM','start',"<IMG SRC='images/btn-start.png'>")
  else:
   print tmpl.format('VM info','info',"<IMG SRC='images/btn-info.png'>")
  print "</TD>"
  print "</TR>"
 print "</TABLE>"
 print "</DIV>"

#
# Actions
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
  tmpl = "<A TITLE='{}' CLASS='z-btn z-op' DIV=div_os_info URL=ajax.cgi?call=nova_action&id=" + id+ "&op={} OP=load SPIN=true>{}</A>"
  print "<DIV>"
  print tmpl.format('Details','details','VM Details')
  print tmpl.format('Diagnostics','diagnostics','Diagnostics')
  print tmpl.format('Networks','networks','Networks')
  print "</DIV>"

  print "<DIV CLASS='z-table' style='overflow:auto' ID=div_os_info>"
  server = controller.call(port,url + "/servers/{}".format(id))['data']['server']
  print "<H2>{}</H2>".format(server['name'])
  _print_info(server)
  print "</DIV>"

 elif op == 'details':
  server = controller.call(port,url + "/servers/{}".format(id))['data']['server']
  print "<H2>{}</H2>".format(server['name'])
  _print_info(server)

 elif op == 'stop' or op == 'start' or op == 'reboot':
  arg = {"os-"+op:None} if op != 'reboot' else {"reboot":{ "type":"SOFT" }}
  ret = controller.call(port,url + "/servers/{}/action".format(id),arg)
  if ret.get('code') == 202:
   print "Command executed successfully [{}]".format(str(arg))
  else:
   print "Error executing command [{}]".format(str(arg))

 elif op == 'diagnostics':
  ret = controller.call(port,url + "/servers/{}/diagnostics".format(id))
  _print_info(ret['data'])

 elif op == 'networks':
  from json import dumps
  vm  = controller.call("8082","virtual-machine/{}".format(id))['data']['virtual-machine']
  print "<TABLE>"
  print "<THEAD><TH>MAC</TH><TH>Routing Instance</TH><TH>Network</TH><TH>IP</TH><TH>Floating IP</TH><TH>Operation</TH></THEAD>"
  for vmir in vm['virtual_machine_interface_back_refs']:
   input = "virtual-machine-interface/{}".format(vmir['uuid'])
   vmi = controller.call("8082",input)['data']['virtual-machine-interface']
   ip = controller.call("8082","instance-ip/{}".format(vmi['instance_ip_back_refs'][0]['uuid']))['data']['instance-ip']
   print "<TR>"
   print "<!-- {} -->".format(input)
   print "<TD>{}</TD>".format(vmi['virtual_machine_interface_mac_addresses']['mac_address'][0])
   print "<TD>{}</TD>".format(vmi['routing_instance_refs'][0]['to'][3])
   print "<TD>{}</TD>".format(vmi['virtual_network_refs'][0]['to'][2])
   print "<TD>{}</TD>".format(ip['instance_ip_address'])
   if vmi.get('floating_ip_back_refs'):
    fip = controller.call("8082","floating-ip/{}".format(vmi['floating_ip_back_refs'][0]['uuid']))['data']['floating-ip']
    print "<TD>{} ({})</TD>".format(fip['floating_ip_address'],fip['fq_name'][2])
    print "<TD><A TITLE='Disassociate' CLASS='z-btn z-small-btn z-op' DIV=div_os_info  URL=ajax.cgi?call=neutron_action&op=fip_disassociate&fip={} OP=load SPIN=true><IMG SRC=images/btn-remove.png></TD>".format(fip['uuid'])
   else:
    print "<TD></TD>"
    print "<TD></TD>"
   print "</TR>"
  print "</TABLE>"

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
 # Old school version, before microapi 2.6
 # - after: /servers/{server_id}/remote-consoles , body: { "remote_console": { "protocol": "vnc", "type": "novnc" }
 cookie = aWeb.get_cookie()
 token = cookie.get('os_user_token')
 if not token:
  print "Not logged in"
  return
 id   = aWeb.get_value('id')
 controller = OpenstackRPC(cookie.get('os_controller'),token)
 data = controller.call(cookie.get('os_nova_port'), cookie.get('os_nova_url') + "/servers/" + id + "/action", { "os-getVNCConsole": { "type": "novnc" } } )
 if data['code'] == 200:
  url = data['data']['console']['url']
  # URL is not always proxy ... so force it through: remove http:// and replace IP (assume there is a port..) with controller IP
  url = "http://" + cookie.get('os_controller') + ":" + url[7:].partition(':')[2]
  print "<iframe id='console_embed' src='{}' style='width: 100%; height: 100%;'></iframe>".format(url)
