"""Module docstring.

Ajax Openstack Neutron/Contrail calls module

"""
__author__= "Zacharias El Banna"
__version__ = "17.6.15GA"
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

############################### Neutron ##############################
#
def list(aWeb):
 cookie = aWeb.get_cookie()
 token  = cookie.get('os_user_token')
 if not token:
  print "Not logged in"
  return
 controller = OpenstackRPC(cookie.get('os_controller'),token)
 pname = cookie.get("os_project_name")

 ret = controller.call("8082","virtual-networks?fields=name,display_name,virtual_network_properties,network_ipam_refs")
 if not ret['result'] == "OK":
  print "Error retrieving list"
  return

 print "<DIV CLASS='z-table' style='width:394px'><TABLE style='width:99%'>"
 print "<THEAD style='height:20px'><TH COLSPAN=3><CENTER>Contrail VNs</CENTER></TH></THEAD>"
 print "<TR style='height:20px'><TD COLSPAN=3>"
 print "<A TITLE='Reload List' CLASS='z-btn z-small-btn z-op' OP=load DIV=div_navleft URL='ajax.cgi?call=neutron_list'><IMG SRC='images/btn-reboot.png'></A>"
 print "</TR>"
 print "<THEAD><TH>Network</TH><TH>Subnet</TH><TH>Operations</TH></THEAD>"
 for net in ret['data']['virtual-networks']:
  if not net.get('display_name'):
   continue
  print "<TR>"
  print "<!-- {} -->".format(str(net))
  print "<TD><A TITLE='Info' CLASS='z-op' DIV=div_navcont URL=ajax.cgi?call=neutron_action&id={0}&op=info OP=load SPIN=true>{1}</A></TD>".format(net['uuid'],net['display_name'])
  print "<TD>"
  if net.get('network_ipam_refs'):
   for ipam in net['network_ipam_refs']:
    for sub in ipam['attr']['ipam_subnets']:
     print "{}/{}".format(sub['subnet']['ip_prefix'],sub['subnet']['ip_prefix_len'])
  print "</TD>"
  print "<TD>"
  tmpl = "<A TITLE='{}' CLASS='z-btn z-op z-small-btn' DIV=div_navcont URL=ajax.cgi?call=neutron_action&name=" + net['display_name'] + "&id=" + net['uuid'] + "&op={} OP=load {} SPIN=true>{}</A>"
  print tmpl.format('Remove','remove',"MSG='Really delete network?'", '<IMG SRC=images/btn-remove.png>')
  print "</TD>" 
 print "</TR>"
 print "</TABLE>"
 print "</DIV>"

def action(aWeb):
 cookie = aWeb.get_cookie()
 token  = cookie.get('os_user_token')
 if not token:
  print "Not logged in"
  return
 controller = OpenstackRPC(cookie.get('os_controller'),token)

 id   = aWeb.get_value('id')
 op   = aWeb.get_value('op')

 print "<!-- {} - {} -->".format(op,id)
 if   op == 'info':
  vn = controller.call("8082","virtual-network/{}".format(id))['data']['virtual-network']
  name = vn['display_name']
  tmpl = "<A TITLE='{}' CLASS='z-btn z-op' DIV=div_os_info URL=ajax.cgi?call=neutron_action&name=" + name + "&id=" + id+ "&op={} OP=load SPIN=true>{}</A>"
  print "<DIV>"
  print "<A TITLE='Network details' CLASS='z-btn z-op' DIV=div_os_info URL=ajax.cgi?call=neutron_action&id={}&op=details    OP=load SPIN=true>Network Details</A>".format(id)
  if vn.get('instance_ip_back_refs'):
   print "<A TITLE='Network details' CLASS='z-btn z-op' DIV=div_os_info URL=ajax.cgi?call=neutron_action&id={}&op=interfaces OP=load SPIN=true>Interfaces</A>".format(id)
  if vn.get('floating_ip_pools'):
   # create a list of floating-ips
   fip = ",".join(map(lambda x: x.get('uuid'), vn.get('floating_ip_pools')))
   print "<A TITLE='Network details' CLASS='z-btn z-op' DIV=div_os_info URL=ajax.cgi?call=neutron_action&op=floating-ip&fip={} OP=load SPIN=true>Floating IPs</A>".format(fip)

  print "</DIV>"
  print "<DIV CLASS='z-table' style='overflow:auto' ID=div_os_info>"
  print "<H2>{} ({})</H2>".format(name,id)
  _print_info(vn)
  print "</DIV>"

 elif op == 'details':
  vn = controller.call("8082","virtual-network/{}".format(id))['data']['virtual-network']
  name = vn['display_name']
  print "<H2>{} ({})</H2>".format(name,id)
  _print_info(vn)

 elif op == 'interfaces':
  vn = controller.call("8082","virtual-network/{}".format(id))['data']['virtual-network']
  print "<TABLE><THEAD><TH>IP</TH><TH>MAC</TH></THEAD>"
  for ip in vn['instance_ip_back_refs']:
   iip = controller.href(ip['href'])['data']['instance-ip']
   vmi = controller.href(iip['virtual_machine_interface_refs'][0]['href'])['data']['virtual-machine-interface']
   print "<TR><TD><A CLASS='z-op' DIV=div_navcont OP=load SPIN=true URL=ajax.cgi?call=nova_action&id={0}>{1}</TD><TD>{2}</TD></TR>".format(vmi['virtual_machine_refs'][0]['uuid'],iip['instance_ip_address'],vmi['virtual_machine_interface_mac_addresses']['mac_address'][0])

  print "</TABLE>"

 elif op == 'floating-ip':
  fips = aWeb.get_value('fip').split(',')
  print "<TABLE><THEAD><TH>Pool</TH><TH>Floating IP</TH><TH>Fixed IP</TH><TH>Fixed Network</TH><TH>Operations</TH></THEAD>"
  for fip in fips:
   pool  = controller.call("8082","floating-ip-pool/{}".format(fip))['data']['floating-ip-pool']
   for ips in pool['floating_ips']:
    ip = controller.href(ips['href'])['data']['floating-ip']
    fixed =  ip.get('floating_ip_fixed_ip_address')
    print "<TR><TD>{}</TD><TD>{}</TD>".format(pool['display_name'],ip['floating_ip_address'])
    if fixed:
     # Do we select one or many VMI:s?
     print "<!-- {} -->".format(ip)
     vmi = controller.href(ip['virtual_machine_interface_refs'][0]['href'])['data']['virtual-machine-interface']
     print "<TD><A TITLE='VM info' CLASS='z-op' DIV=div_navcont  URL=ajax.cgi?call=nova_action&op=info&id={0} OP=load SPIN=true>{1}</TD>".format(vmi['virtual_machine_refs'][0]['to'][0],fixed)
     print "<TD><A TITLE='Network info' CLASS='z-op' DIV=div_navcont  URL=ajax.cgi?call=neutron_action&op=info&id={0} OP=load SPIN=true>{1}</TD>".format(vmi['virtual_network_refs'][0]['uuid'],vmi['virtual_network_refs'][0]['to'][2])
     print "<TD>"
     print "<A TITLE='Info'         CLASS='z-btn z-small-btn z-op' DIV=div_os_info  URL=ajax.cgi?call=neutron_action&op=fip_info&fip={} OP=load SPIN=true><IMG SRC=images/btn-info.png></A>".format(ip['uuid'])
     print "<A TITLE='Disassociate' CLASS='z-btn z-small-btn z-op' DIV=div_os_info  URL=ajax.cgi?call=neutron_action&op=fip_disassociate&fip={} OP=load SPIN=true><IMG SRC=images/btn-remove.png></A>".format(ip['uuid'])
     print "</TD>"
    else:
     print "<TD></TD>"
     print "<TD></TD>"
     print "<TD>"
     print "<A TITLE='Info'         CLASS='z-btn z-small-btn z-op' DIV=div_os_info  URL=ajax.cgi?call=neutron_action&op=fip_info&fip={} OP=load SPIN=true><IMG SRC=images/btn-info.png></A>".format(ip['uuid'])
     print "</TD>"
    print "</TR>"
  print "</TABLE>" 

 elif op == 'fip_info':
  from json import dumps
  fip  = aWeb.get_value('fip')
  print "<PRE>{}</PRE>".format(dumps(controller.call("8082","floating-ip/{}".format(fip))['data']['floating-ip'],indent=4))

 elif op == 'fip_disassociate':
  from json import dumps
  fipid = aWeb.get_value('fip')
  fip = controller.call("8082","floating-ip/{}".format(fipid))['data']['floating-ip']
  fip.pop('virtual_machine_interface_refs')
  fip.pop('floating_ip_fixed_ip_address')
  print "<PRE>{}</PRE>".format(dumps(fip,indent=4))

 elif op == 'remove':
  ret = controller.call("8082","virtual-network/{}".format(id), method='DELETE')
  print ret

