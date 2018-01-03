"""Module docstring.

HTML5 Ajax Openstack Neutron/Contrail calls module

- left and right divs frames (div_content_left/right) needs to be created by ajax call

"""
__author__= "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__= "Production"

from sdcp.devices.openstack import OpenstackRPC
from sdcp.site.openstack import dict2html

############################### Neutron ##############################
#
def list(aWeb):
 cookie = aWeb.cookies
 token  = cookie.get('os_user_token')
 if not token:
  print "Not logged in"
  return
 controller = OpenstackRPC(cookie.get('os_controller'),token)
 pname = cookie.get("os_project_name")

 try:
  data = controller.call("8082","virtual-networks?fields=name,display_name,virtual_network_properties,network_ipam_refs")['data']
 except Exception as e:
  print "<!-- %s -->Error retrieving list"%str(e)
  return

 print "<SECTION CLASS=content-left ID=div_content_left>"
 print "<ARTICLE STYLE='overflow:auto;'><P>Contrail VNs</P>"
 print aWeb.button('reload',DIV='div_content',  URL='sdcp.cgi?call=neutron_list')
 print "<DIV CLASS=table>"
 print "<DIV CLASS=thead><DIV CLASS=th>Network</DIV><DIV CLASS=th>Subnet</DIV><DIV CLASS=th>&nbsp;</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for net in data['virtual-networks']:
  if not net.get('display_name'):
   continue
  print "<DIV CLASS=tr>"
  print "<!-- {} -->".format(net.get('href'))
  print "<DIV CLASS=td STYLE='max-width:200px; overflow-x:hidden;'><A TITLE='Info {1}' CLASS='z-op' DIV=div_content_right URL=sdcp.cgi?call=neutron_action&id={0}&op=info SPIN=true>{1}</A></DIV>".format(net['uuid'],net['display_name'])
  print "<DIV CLASS=td>"
  if net.get('network_ipam_refs'):
   for ipam in net['network_ipam_refs']:
    for sub in ipam['attr']['ipam_subnets']:
     print "{}/{}".format(sub['subnet']['ip_prefix'],sub['subnet']['ip_prefix_len'])
  print "</DIV>"
  print "<DIV CLASS=td>&nbsp;"
  print aWeb.button('delete',DIV='div_content_right', SPIN='true', URL='sdcp.cgi?call=neutron_action&name=%s&id=%s&op=remove'%(net['display_name'],net['uuid']), MSG='Delete network?')
  print "</DIV>"
  print "</DIV>"
 print "</DIV></DIV></ARTICLE></SECTION>"
 print "<SECTION CLASS=content-right ID=div_content_right></SECTION>"

def action(aWeb):
 cookie = aWeb.cookies
 token  = cookie.get('os_user_token')
 if not token:
  print "Not logged in"
  return
 controller = OpenstackRPC(cookie.get('os_controller'),token)

 id   = aWeb['id']
 op   = aWeb['op']

 print "<!-- action - op:{} - id:{} -->".format(op,id)
 if   op == 'info':
  vn = controller.call("8082","virtual-network/{}".format(id))['data']['virtual-network']
  name = vn['display_name']
  tmpl = "<A CLASS='btn z-op' DIV=div_os_info URL=sdcp.cgi?call=neutron_action&name=%s&id=%s&op={} SPIN=true>{}</A>"%(name,id)
  print "<DIV>"
  print tmpl.format('details','Network details')
  if vn.get('instance_ip_back_refs'):
   print tmpl.format('interfaces','Interfaces')
  if vn.get('floating_ip_pools'):
   # create a list of floating-ips
   fipool = ",".join(map(lambda x: x.get('uuid'), vn.get('floating_ip_pools')))
   print tmpl.format('floating-ip&fipool=%s'%fipool,'Floating IPs')
  print "</DIV>"
  print "<ARTICLE STYLE='overflow:auto;' ID=div_os_info>"
  dict2html(vn,"{} ({})".format(name,id))
  print "</ARTICLE>"

 elif op == 'details':
  vn = controller.call("8082","virtual-network/{}".format(id))['data']['virtual-network']
  name = vn['display_name']
  dict2html(vn,"{} ({})".format(name,id))

 elif op == 'interfaces':
  vn = controller.call("8082","virtual-network/{}".format(id))['data']['virtual-network']
  print "<DIV CLASS=table STYLE='width:auto'><DIV CLASS=thead><DIV CLASS=th>IP</DIV><DIV CLASS=th>MAC</DIV><DIV CLASS=th>Interface</DIV></DIV>"
  print "<DIV CLASS=tbody>"
  for ip in vn['instance_ip_back_refs']:
   iip = controller.href(ip['href'])['data']['instance-ip']
   vmi = controller.href(iip['virtual_machine_interface_refs'][0]['href'])['data']['virtual-machine-interface']
   print "<DIV CLASS=tr>"
   print "<! -- {} -->".format(ip['href'])
   print "<! -- {} -->".format(iip['virtual_machine_interface_refs'][0]['href'])
   if vmi.get('virtual_machine_refs'):
    print "<DIV CLASS=td><A CLASS='z-op' DIV=div_content_right SPIN=true URL=sdcp.cgi?call=nova_action&id={0}>{1}</A></DIV>".format(vmi['virtual_machine_refs'][0]['uuid'],iip['instance_ip_address'])
   else:
    print "<DIV CLASS=td>{}</DIV>".format(iip['instance_ip_address'])
   print "<DIV CLASS=td>{}</DIV>".format(vmi['virtual_machine_interface_mac_addresses']['mac_address'][0])
   if   vmi.get('virtual_machine_interface_bindings'):
    host = vmi['virtual_machine_interface_bindings']['key_value_pair']
    for kvp in host:
     if kvp['key'] == 'host_id':
      print "<DIV CLASS=td>{}</DIV>".format(kvp['value'])
   elif vmi.get('logical_interface_back_refs'):
    li = vmi['logical_interface_back_refs'][0]
    interface = li['to'][1] + "-" + li['to'][3]
    print "<DIV CLASS=td><A CLASS='z-op' DIV=div_os_info SPIN=true URL=sdcp.cgi?call=neutron_action&op=print&id={}>{}</A></DIV>".format(li['href'],interface)
   else:
    print "<!-- {} -->".format(vmi['href'])
    print "<DIV CLASS=td>{}</DIV>".format(vmi['virtual_machine_interface_device_owner'])
   print "</DIV>"
  print "</DIV></DIV>"

 ############################################# Floating IP ##############################################
 #
 #
 elif op == 'floating-ip':
  fipools = aWeb['fipool'].split(',')
  print "<DIV CLASS=table STYLE='width:500px'><DIV CLASS=thead><DIV CLASS=th>Pool</DIV><DIV CLASS=th>Floating IP</DIV><DIV CLASS=th>Fixed IP</DIV><DIV CLASS=th>Fixed Network</DIV><DIV CLASS=th>Operations</DIV></DIV>"
  print "<DIV CLASS=tbody>"
  for fipool in fipools:
   pool  = controller.call("8082","floating-ip-pool/{}".format(fipool))['data']['floating-ip-pool']
   for fips in pool['floating_ips']:
    fip = controller.href(fips['href'])['data']['floating-ip']
    fixed =  fip.get('floating_ip_fixed_ip_address')
    print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV>".format(pool['display_name'],fip['floating_ip_address'])
    if fixed:
     # Do we select one or many VMI:s?
     print "<!-- {} -->".format(fip)
     vmi = controller.href(fip['virtual_machine_interface_refs'][0]['href'])['data']['virtual-machine-interface']
     print "<DIV CLASS=td><A TITLE='VM info' CLASS='z-op' DIV=div_content_right  URL=sdcp.cgi?call=nova_action&op=info&id={0} SPIN=true>{1}</A></DIV>".format(vmi['virtual_machine_refs'][0]['to'][0],fixed)
     print "<DIV CLASS=td><A TITLE='Network info' CLASS='z-op' DIV=div_content_right  URL=sdcp.cgi?call=neutron_action&op=info&id={0} SPIN=true>{1}</A></DIV>".format(vmi['virtual_network_refs'][0]['uuid'],vmi['virtual_network_refs'][0]['to'][2])
     print "<DIV CLASS=td>"
     print aWeb.button('info',  DIV='div_os_info', URL='sdcp.cgi?call=neutron_action&op=print&id=%s'%fip['href'])
     print aWeb.button('remove',DIV='div_os_info', URL='sdcp.cgi?call=neutron_action&op=fi_disassociate&id=%s'%fip['uuid'], MSG='Are you sure?', SPIN='true')
     print "&nbsp;</DIV>"
    else:
     print "<DIV CLASS=td></DIV>"
     print "<DIV CLASS=td></DIV>"
     print "<DIV CLASS=td>"
     print aWeb.button('info', DIV='div_os_info', URL='sdcp.cgi?call=neutron_action&op=print&id=%s'%fip['href'])
     print aWeb.button('add',  DIV='div_os_info', URL='sdcp.cgi?call=neutron_action&op=fi_associate_choose_vm&id=%s'%fip['uuid'])
     print "</DIV>"
    print "</DIV>"
  print "</DIV></DIV>" 

 elif op == 'print':
  from json import dumps
  print "<PRE>{}</PRE>".format(dumps(controller.href(id)['data'],indent=4))

 elif op == 'remove':
  res = controller.call("8082","virtual-network/{}".format(id), method='DELETE')['data']
  print "<ARTICLE>{}</ARTICLE>".format(res)

 elif op == 'fi_disassociate':
  fip = {'floating-ip':{'virtual_machine_interface_refs':None,'floating_ip_fixed_ip_address':None }}
  try:
   res = controller.call("8082","floating-ip/{}".format(id),args=fip,method='PUT')['data']
   print "Floating IP association removed"
  except Exception as e:
   print "Error - [%s]"%str(e)

 elif op == 'fi_associate_choose_vm':
  vms = controller.call(cookie.get('os_nova_port'),cookie.get('os_nova_url') + "/servers")['data']['servers']
  print "<FORM ID=frm_fi_assoc_vm><INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(id)
  print "VM: <SELECT STYLE='width:auto; height:22px;' NAME=vm>"
  for vm in vms:
   print "<OPTION VALUE={0}#{1}>{0}</OPTION>".format(vm['name'],vm['id'])
  print "</SELECT></FORM>"
  print aWeb.button('next', DIV='div_os_info', FRM='frm_fi_assoc_vm', URL='sdcp.cgi?call=neutron_action&op=fi_associate_choose_interface')

 elif op == 'fi_associate_choose_interface':
  vm_name,_,vm_id = aWeb['vm'].partition('#')
  vmis = controller.call("8082","virtual-machine/{}".format(vm_id))['data']['virtual-machine']['virtual_machine_interface_back_refs']
  print "<FORM ID=frm_fi_assoc_vmi>"
  print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(id)
  print "<INPUT TYPE=HIDDEN NAME=vm VALUE={}>".format(vm_id)
  print "VM: <INPUT STYLE='width:auto;' TYPE=TEXT VALUE={} disabled> Interface:<SELECT STYLE='width:auto; height:22px;' NAME=vmi>".format(vm_name)
  for vmi in vmis:
   uuid = vmi['uuid']
   vmi = controller.href(vmi['href'])['data']['virtual-machine-interface']
   iip = controller.href(vmi['instance_ip_back_refs'][0]['href'])['data']['instance-ip']
   print "<OPTION VALUE={0}#{1}>{2} ({1})</OPTION>".format(uuid,iip['instance_ip_address'],iip['virtual_network_refs'][0]['to'][2])
  print "</SELECT></FORM>"
  print aWeb.button('back', DIV='div_os_info', URL='sdcp.cgi?call=neutron_action&op=fi_associate_choose_vm&id=%s'%id, TITLE='Change VM')
  print aWeb.button('next', DIV='div_os_info', URL='sdcp.cgi?call=neutron_action&op=fi_associate', FRM='frm_fi_assoc_vmi', TITLE='Commit')

 elif op == 'fi_associate':
  from json import dumps
  vmid  = aWeb['vm']
  vmiid,_,ip = aWeb['vmi'].partition('#')
  vmi = controller.call("8082","virtual-machine-interface/{}".format(vmiid))['data']['virtual-machine-interface']
  fip = { 'floating-ip':{ 'floating_ip_fixed_ip_address':ip, 'virtual_machine_interface_refs':[ {'href':vmi['href'],'attr':None,'uuid':vmi['uuid'],'to':vmi['fq_name'] } ] } }
  try:
   res = controller.call("8082","floating-ip/{}".format(id),args=fip,method='PUT')
   print "Floating IP association created"
  except Exception as e:
   print "Error - [%s]"%str(e)
