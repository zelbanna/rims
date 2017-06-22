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

 print "<DIV CLASS='z-table' style='overflow:auto;'><TABLE style='width:99%'>"
 print "<THEAD style='height:20px'><TH COLSPAN=3><CENTER>Contrail VNs</CENTER></TH></THEAD>"
 print "<TR style='height:20px'><TD COLSPAN=3>"
 print "<A TITLE='Reload List' CLASS='z-btn z-small-btn z-op' OP=load DIV=div_navleft URL='ajax.cgi?call=neutron_list'><IMG SRC='images/btn-reboot.png'></A>"
 print "</TR>"
 print "<THEAD><TH>Network</TH><TH>Subnet</TH><TH></TH></THEAD>"
 for net in ret['data']['virtual-networks']:
  if not net.get('display_name'):
   continue
  print "<TR>"
  print "<!-- {} -->".format(str(net))
  print "<TD style='max-width:200px; overflow-x:hidden;'><A TITLE='Info {1}' CLASS='z-op' DIV=div_navcont URL=ajax.cgi?call=neutron_action&id={0}&op=info OP=load SPIN=true>{1}</A></TD>".format(net['uuid'],net['display_name'])
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

 print "<!-- action - op:{} - id:{} -->".format(op,id)
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
   fipool = ",".join(map(lambda x: x.get('uuid'), vn.get('floating_ip_pools')))
   print "<A TITLE='Network details' CLASS='z-btn z-op' DIV=div_os_info URL=ajax.cgi?call=neutron_action&op=floating-ip&fipool={} OP=load SPIN=true>Floating IPs</A>".format(fipool)

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
  print "<TABLE><THEAD><TH>IP</TH><TH>MAC</TH><TH>Interface</TH></THEAD>"
  for ip in vn['instance_ip_back_refs']:
   iip = controller.href(ip['href'])['data']['instance-ip']
   vmi = controller.href(iip['virtual_machine_interface_refs'][0]['href'])['data']['virtual-machine-interface']
   print "<!-- {} -->".format(iip['virtual_machine_interface_refs'][0]['href'])
   print "<TR>"
   if vmi.get('virtual_machine_refs'):
    print "<TD><A CLASS='z-op' DIV=div_navcont OP=load SPIN=true URL=ajax.cgi?call=nova_action&id={0}>{1}</A></TD>".format(vmi['virtual_machine_refs'][0]['uuid'],iip['instance_ip_address'])
   else:
    print "<TD>{}</TD>".format(iip['instance_ip_address'])
   print "<TD>{}</TD>".format(vmi['virtual_machine_interface_mac_addresses']['mac_address'][0])
   if   vmi.get('virtual_machine_interface_bindings'):
    host = vmi['virtual_machine_interface_bindings']['key_value_pair']
    for kvp in host:
     if kvp['key'] == 'host_id':
      print "<TD>{}</TD>".format(kvp['value'])
   elif vmi.get('logical_interface_back_refs'):
    li = vmi['logical_interface_back_refs'][0]
    interface = li['to'][1] + "-" + li['to'][3]
    print "<TD><A CLASS='z-op' DIV=div_os_info OP=load SPIN=true URL=ajax.cgi?call=neutron_action&op=print&id={}>{}</A></TD>".format(li['href'],interface)
   print "</TR>"
  print "</TABLE>"

 elif op == 'floating-ip':
  fipools = aWeb.get_value('fipool').split(',')
  print "<TABLE><THEAD><TH>Pool</TH><TH>Floating IP</TH><TH>Fixed IP</TH><TH>Fixed Network</TH><TH>Operations</TH></THEAD>"
  for fipool in fipools:
   pool  = controller.call("8082","floating-ip-pool/{}".format(fipool))['data']['floating-ip-pool']
   for fips in pool['floating_ips']:
    fip = controller.href(fips['href'])['data']['floating-ip']
    fixed =  fip.get('floating_ip_fixed_ip_address')
    print "<TR><TD>{}</TD><TD>{}</TD>".format(pool['display_name'],fip['floating_ip_address'])
    if fixed:
     # Do we select one or many VMI:s?
     print "<!-- {} -->".format(fip)
     vmi = controller.href(fip['virtual_machine_interface_refs'][0]['href'])['data']['virtual-machine-interface']
     print "<TD><A TITLE='VM info' CLASS='z-op' DIV=div_navcont  URL=ajax.cgi?call=nova_action&op=info&id={0} OP=load SPIN=true>{1}</TD>".format(vmi['virtual_machine_refs'][0]['to'][0],fixed)
     print "<TD><A TITLE='Network info' CLASS='z-op' DIV=div_navcont  URL=ajax.cgi?call=neutron_action&op=info&id={0} OP=load SPIN=true>{1}</TD>".format(vmi['virtual_network_refs'][0]['uuid'],vmi['virtual_network_refs'][0]['to'][2])
     print "<TD>"
     print "<A TITLE='Info' CLASS='z-btn z-small-btn z-op' DIV=div_os_info  URL=ajax.cgi?call=neutron_action&op=print&id={} OP=load SPIN=true><IMG SRC=images/btn-info.png></A>".format(fip['href'])
     print "<A TITLE='Disassociate floating IP' CLASS='z-btn z-small-btn z-op' DIV=div_os_info  URL=ajax.cgi?call=neutron_action&op=fi_disassociate&id={} MSG='Are you sure?' OP=load SPIN=true><IMG SRC=images/btn-remove.png></A>".format(fip['uuid'])
     print "</TD>"
    else:
     print "<TD></TD>"
     print "<TD></TD>"
     print "<TD>"
     print "<A TITLE='Info' CLASS='z-btn z-small-btn z-op' DIV=div_os_info  URL=ajax.cgi?call=neutron_action&op=print&id={} OP=load SPIN=true><IMG SRC=images/btn-info.png></A>".format(fip['href'])
     print "<A TITLE='Associate floating IP' CLASS='z-btn z-small-btn z-op' DIV=div_os_info  URL=ajax.cgi?call=neutron_action&op=fi_associate_choose_vm&id={} OP=load><IMG SRC=images/btn-add.png></A>".format(fip['uuid'])
     print "</TD>"
    print "</TR>"
  print "</TABLE>" 

 elif op == 'print':
  from json import dumps
  print "<PRE>{}</PRE>".format(dumps(controller.href(id)['data'],indent=4))

 elif op == 'remove':
  ret = controller.call("8082","virtual-network/{}".format(id), method='DELETE')
  print ret

 ############################################# Floating IP ##############################################
 elif op == 'fi_disassociate':
  fip = {'floating-ip':{'virtual_machine_interface_refs':None,'floating_ip_fixed_ip_address':None }}
  res = controller.call("8082","floating-ip/{}".format(id),args=fip,method='PUT')
  print "Floating IP association removed" if res['code'] == 200 else "Error - [{}]".format(res)

 elif op == 'fi_associate_choose_vm':
  vms = controller.call(cookie.get('os_nova_port'),cookie.get('os_nova_url') + "/servers")['data']['servers']
  print "<FORM ID=frm_fi_assoc_vm><INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(id)
  print "VM: <SELECT NAME=vm>"
  for vm in vms:
   print "<OPTION VALUE={0}#{1}>{0}</OPTION>".format(vm['name'],vm['id'])
  print "</SELECT></FORM>"
  print "<A TITLE='Choose interface' CLASS='z-btn z-small-btn z-op'  DIV=div_os_info FRM=frm_fi_assoc_vm URL=ajax.cgi?call=neutron_action&op=fi_associate_choose_interface><IMG SRC=images/btn-start.png></A>"

 elif op == 'fi_associate_choose_interface':
  vm_name,_,vm_id = aWeb.get_value('vm').partition('#')
  vmis = controller.call("8082","virtual-machine/{}".format(vm_id))['data']['virtual-machine']['virtual_machine_interface_back_refs']
  print "<FORM ID=frm_fi_assoc_vmi>"
  print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(id)
  print "<INPUT TYPE=HIDDEN NAME=vm VALUE={}>".format(vm_id)
  print "VM: <INPUT TYPE=TEXT VALUE={} disabled> Interface:<SELECT NAME=vmi>".format(vm_name)
  for vmi in vmis:
   uuid = vmi['uuid']
   vmi = controller.href(vmi['href'])['data']['virtual-machine-interface']
   iip = controller.href(vmi['instance_ip_back_refs'][0]['href'])['data']['instance-ip']
   print "<OPTION VALUE={0}#{1}>{2} ({1})</OPTION>".format(uuid,iip['instance_ip_address'],iip['virtual_network_refs'][0]['to'][2])
  print "</SELECT></FORM>"
  print "<A TITLE='Change VM' CLASS='z-btn z-small-btn z-op' DIV=div_os_info URL=ajax.cgi?call=neutron_action&op=fi_associate_choose_vm&id={}><IMG SRC=images/btn-back.png></A>".format(id)
  print "<A TITLE='Commit'    CLASS='z-btn z-small-btn z-op' DIV=div_os_info URL=ajax.cgi?call=neutron_action&op=fi_associate FRM=frm_fi_assoc_vmi><IMG SRC=images/btn-start.png></A>"

 elif op == 'fi_associate':
  from json import dumps
  vmid  = aWeb.get_value('vm')
  vmiid,_,ip = aWeb.get_value('vmi').partition('#')
  vmi = controller.call("8082","virtual-machine-interface/{}".format(vmiid))['data']['virtual-machine-interface']
  fip = { 'floating-ip':{ 'floating_ip_fixed_ip_address':ip, 'virtual_machine_interface_refs':[ {'href':vmi['href'],'attr':None,'uuid':vmi['uuid'],'to':vmi['fq_name'] } ] } }
  res = controller.call("8082","floating-ip/{}".format(id),args=fip,method='PUT')
  if res['code'] == 200:
   print "Floating IP association created"
  else:
   print "Error - [{}]".format(res)

