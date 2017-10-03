"""Module docstring.

Ajax Openstack NOVA calls module

- left and right divs frames (div_content_left/right) needs to be created by ajax call
"""
__author__= "Zacharias El Banna"
__version__ = "17.10.4"
__status__= "Production"

from sdcp.devices.openstack import OpenstackRPC
from sdcp.site.ajax_openstack import dict2html

################################# Nova ###############################
#
def list(aWeb):
 cookie = aWeb.cookie
 token  = cookie.get('os_user_token')
 if not token:
  print "Not logged in"
  return
 controller = OpenstackRPC(cookie.get('os_controller'),token)

 ret = controller.call(cookie.get('os_nova_port'),cookie.get('os_nova_url') + "/servers/detail")
 if not ret['result'] == "OK":
  print "Error retrieving list {}".format(str(ret))
  return

 print "<DIV CLASS=z-content-left ID=div_content_left>"
 print "<DIV CLASS=z-frame style='width:394px'>"
 print "<DIV CLASS=z-table style='width:99%'>"
 print "<DIV CLASS=thead style='height:20px'><DIV CLASS=th><CENTER>Nova Servers</CENTER></DIV></DIV>"
 print "<DIV CLASS=tbody><DIV CLASS=tr style='height:20px'><DIV CLASS=td>"
 print "<A TITLE='Reload List' CLASS='z-btn z-small-btn z-op' DIV=div_content URL='ajax.cgi?call=nova_list'><IMG SRC='images/btn-reboot.png'></A>"
 print "<A TITLE='Add server'   CLASS='z-btn z-small-btn z-op' DIV=div_content_right URL='ajax.cgi?call=nova_select_parameters'><IMG SRC='images/btn-add.png'></A>"
 print "</DIV></DIV></DIV>"
 print "<DIV CLASS=thead><DIV CLASS=th>Name</DIV><DIV CLASS=th style='width:94px;'></DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for server in ret['data'].get('servers',None):
  qserver = aWeb.quote(server['name'])
  tmpl = "<A TITLE='{}' CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=ajax.cgi?call=nova_action&name=" + qserver + "&id=" + server['id'] + "&op={} SPIN=true>{}</A>"
  print "<DIV CLASS=tr>"
  print "<!-- {} - {} -->".format(server['status'],server['OS-EXT-STS:task_state'])
  print "<DIV CLASS=td><A TITLE='VM info' CLASS='z-op' DIV=div_content_right URL=ajax.cgi?call=nova_action&id={}&op=info SPIN=true>{}</A></DIV>".format(server['id'],server['name'])
  print "<DIV CLASS=td>"
  print "<A TITLE='New-tab Console'  CLASS='z-btn z-small-btn'	TARGET=_blank      HREF='pane.cgi?view=openstack_console&name={}&id={}'><IMG SRC='images/btn-term.png'></A>".format(qserver,server['id'])
  print "<A TITLE='Embedded Console' CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=ajax.cgi?call=nova_console&id={}><IMG SRC='images/btn-term-frame.png'></A>".format(server['id'])
  print "<A TITLE='Remove VM'        CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=ajax.cgi?call=nova_action&id={}&op=remove MSG='Are you sure you want to delete VM?' SPIN=true><IMG SRC='images/btn-remove.png'></A>".format(server['id'])
  if not server['OS-EXT-STS:task_state']:
   if   server['status'] == 'ACTIVE':
    print tmpl.format('Stop VM','stop',"<IMG SRC='images/btn-shutdown.png'>")
    print tmpl.format('Reboot','reboot',"<IMG SRC='images/btn-reboot.png'>")
   elif server['status'] == 'SHUTOFF':
    print tmpl.format('Start VM','start',"<IMG SRC='images/btn-start.png'>")
  else:
   print tmpl.format('VM info','info',"<IMG SRC='images/btn-info.png'>")
  print "</DIV></DIV>"
 print "</DIV>"
 print "</DIV></DIV></DIV><DIV CLASS=z-content-right ID=div_content_right></DIV>"


def select_parameters(aWeb):
 cookie = aWeb.cookie
 token  = cookie.get('os_user_token')
 if not token:
  print "Not logged in"
  return
 controller = OpenstackRPC(cookie.get('os_controller'),token)
 port,url = cookie.get('os_nova_port'),cookie.get('os_nova_url')
 print "<DIV CLASS=z-frame>"
 print """
 <script>
  $( function() {
	$(".z-drag").attr("draggable","true");
	$(".z-drag").on("dragstart", function(e){
		console.log("Drag " + $(this).prop("id") + " FROM " + $(this).parent().prop("id"));
		e.originalEvent.dataTransfer.setData("Text",e.target.id);
	});

	$(document.body).on("drop dragover", ".z-drop", function(e){ e.preventDefault();
		if (e.type == 'drop') {
			var elem_id = e.originalEvent.dataTransfer.getData("Text");
			var elem    = document.getElementById(elem_id);
			var input   = $("#" + elem_id + " input");
			console.log("Drop " + elem_id + " INTO " + $(this).prop("id"));
			e.target.appendChild(elem);
			$(this).removeClass("z-drop");
			if ($(elem).attr("name")) {
				console.log("Restoring drop to: " + $(elem).attr("name"));
				$("#" + $(elem).attr("name")).addClass("z-drop");
			}
			
			input.attr("name",$(this).prop("id"));
		}
   });
 });
</script>
 """
 print "<H2>New VM parameters</H2>"
 print "<FORM ID=frm_os_create_vm>"
 print "<DIV ID=div_os_form CLASS='z-table' style='float:left;'><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Name</DIV><DIV CLASS=td><INPUT NAME=os_name PLACEHOLDER='Unique Name'></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td>Image</DIV><DIV CLASS=td><SELECT NAME=os_image>"
 images = controller.call(cookie.get('os_glance_port'),cookie.get('os_glance_url') + "/v2/images?sort=name:asc")['data']['images']
 for img in images:
  print "<OPTION VALUE={}>{} (Min Ram: {}Mb)</OPTION>".format(img['id'],img['name'],img['min_ram'])
 print "</SELECT></DIV></DIV>"

 flavors = controller.call(port,url + "/flavors/detail?sort_key=name")['data']['flavors']
 print "<DIV CLASS=tr><DIV CLASS=td>Flavor</DIV><DIV CLASS='z-table-val td'><SELECT NAME=os_flavor>"
 for fl in flavors:
  print "<OPTION VALUE={}>{} (Ram: {}Mb, vCPUs: {}, Disk: {}Gb</OPTION>".format(fl['id'],fl['name'],fl['ram'],fl['vcpus'],fl['disk'])
 print "</SELECT></DIV></DIV>"

 print "<DIV CLASS=tr><DIV CLASS=td>Network</DIV><DIV CLASS='td z-drop' ID=os_network1></DIV></DIV>"
 print "</DIV></DIV></FORM>"

 print "<DIV ID=div_os_nets style='float:left; height:200px; overflow:auto;'>"
 networks = controller.call(cookie.get('os_neutron_port'),cookie.get('os_neutron_url') + "/v2.0/networks?sort_key=name")['data']['networks']
 for net in networks:
  if net.get('contrail:subnet_ipam'):
   print "<DIV ID=div_drag_{0} CLASS='z-drag z-drag-input' style='font-size:11px;'><INPUT ID=input_{0} NAME=unused TYPE=HIDDEN VALUE={0}>{1} ({2})</DIV>".format(net['id'],net['name'],net['contrail:subnet_ipam'][0]['subnet_cidr'])
 print "</DIV>"
 print "<BR style='clear:left;'>"
 print "<A TITLE='Create VM' CLASS='z-btn z-op z-small-btn' FRM=frm_os_create_vm DIV=div_content_right URL=ajax.cgi?call=nova_action&id={}&op=add SPIN=true><IMG SRC='images/btn-start.png'></A>".format("new") 
 print "</DIV>"

######################################## Actions ########################################
#
# 
def action(aWeb):
 cookie = aWeb.cookie
 token  = cookie.get('os_user_token')
 if not token:
  print "Not logged in"
  return
 controller = OpenstackRPC(cookie.get('os_controller'),token)

 port = cookie.get('os_nova_port')
 url  = cookie.get('os_nova_url')
 id   = aWeb.get_value('id')
 op   = aWeb.get_value('op','info')

 import sdcp.PackageContainer as PC
 PC.log_msg("nova_action - id:{} op:{} for project:{}".format(id,op,cookie.get('os_project_name')))

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
  print "<DIV CLASS=z-frame style='overflow:auto;' ID=div_os_info>"
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
  print "<DIV CLASS=z-table>"
  print "<DIV CLASS=thead><DIV CLASS=th>MAC</DIV><DIV CLASS=th>Routing Instance</DIV><DIV CLASS=th>Network</DIV><DIV CLASS=th>IP</DIV><DIV CLASS=th>Floating IP</DIV><DIV CLASS=th>Operation</DIV></DIV>"
  for vmir in vm['virtual_machine_interface_back_refs']:
   vmi = controller.href(vmir['href'])['data']['virtual-machine-interface']
   ip = controller.href(vmi['instance_ip_back_refs'][0]['href'])['data']['instance-ip']
   print "<DIV CLASS=tbody>"
   print "<DIV CLASS=tr>"
   print "<!-- {} -->".format(vmir['href'])
   print "<DIV CLASS=td>{}</DIV>".format(vmi['virtual_machine_interface_mac_addresses']['mac_address'][0])
   print "<DIV CLASS=td>{}</DIV>".format(vmi['routing_instance_refs'][0]['to'][3])
   print "<DIV CLASS=td><A CLASS='z-op' DIV=div_content_right SPIN=true URL=ajax.cgi?call=neutron_action&id={0}&op=info>{1}</A></DIV>".format(vmi['virtual_network_refs'][0]['uuid'],vmi['virtual_network_refs'][0]['to'][2])
   print "<DIV CLASS=td>{}</DIV>".format(ip['instance_ip_address'])
   if vmi.get('floating_ip_back_refs'):
    fip = controller.href(vmi['floating_ip_back_refs'][0]['href'])['data']['floating-ip']
    print "<DIV CLASS=td>{} ({})</DIV>".format(fip['floating_ip_address'],fip['fq_name'][2])
    print "<DIV CLASS=td><A TITLE='Disassociate' CLASS='z-btn z-small-btn z-op' DIV=div_os_info URL=ajax.cgi?call=neutron_action&op=fi_disassociate&id={} SPIN=true><IMG SRC=images/btn-remove.png></A>&nbsp;</DIV>".format(fip['uuid'])
   else:
    print "<DIV CLASS=td></DIV>"
    print "<DIV CLASS=td></DIV>"
   print "</DIV>"
  print "</DIV>"
  print "</DIV>"

 elif op == 'add':
  print "TBD"

 elif op == 'remove':
  ret = controller.call(port,url + "/servers/{}".format(id), method='DELETE')
  if not ret['result'] == "OK":
   print "Error performing op {}".format(str(ret))
   return
  print "<DIV CLASS='z-frame'>"
  print "<H2>Removing VM</H2>"
  if ret['code'] == 204:
   print "VM removed"
  else:
   print "Error code: {}".format(ret['code'])
  print "</DIV>"

def console(aWeb):
 cookie = aWeb.cookie
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
