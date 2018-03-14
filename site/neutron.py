"""Module docstring.

HTML5 Ajax Openstack Neutron/Contrail calls module

"""
__author__= "Zacharias El Banna"
__version__ = "18.03.14GA"
__status__= "Production"

############################### Neutron ##############################
#
def list(aWeb):
 cookie = aWeb.cookie_unjar('openstack')
 token  = cookie.get('token')
 if not token:
  print "Not logged in"
  return
 data = aWeb.rest_call("openstack_call",{'token':token,'service':'contrail','call':"virtual-networks?fields=name,display_name,virtual_network_properties,network_ipam_refs"})['data']

 print "<SECTION CLASS=content-left ID=div_content_left>"
 print "<ARTICLE STYLE='overflow-x:hidden;'><P>Contrail VNs</P>"
 print aWeb.button('reload',DIV='div_content',  URL='sdcp.cgi?call=neutron_list')
 print "<DIV CLASS=table>"
 print "<DIV CLASS=thead><DIV CLASS=th>Network</DIV><DIV CLASS=th>Subnet</DIV><DIV CLASS=th STYLE='width:50px;'>&nbsp;</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for net in data['virtual-networks']:
  if not net.get('display_name'):
   continue
  print "<DIV CLASS=tr>"
  print "<!-- {} -->".format(net.get('href'))
  print "<DIV CLASS=td STYLE='max-width:175px;'><A TITLE='Info {1}' CLASS='z-op' DIV=div_content_right URL=sdcp.cgi?call=neutron_action&id={0}&op=info SPIN=true>{1}</A></DIV>".format(net['uuid'],net['display_name'])
  print "<DIV CLASS=td STYLE='max-width:175px;'>"
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
 from ..site.openstack import dict2html
 cookie = aWeb.cookie_unjar('openstack')
 token  = cookie.get('token')
 if not token:
  print "Not logged in"
  return
 args = {'token':token,'service':'contrail'}
 id   = aWeb['id']
 op   = aWeb['op']

 if   op == 'info':
  args['call'] = 'virtual-network/%s'%(id)
  vn = aWeb.rest_call("openstack_call",args)['data']['virtual-network']
  name = vn['display_name']
  tmpl = "<BUTTON CLASS='z-op' DIV=div_os_info URL=sdcp.cgi?call=neutron_action&name=%s&id=%s&op={} SPIN=true>{}</BUTTON>"%(name,id)
  print "<DIV>"
  print tmpl.format('details','Network details')
  if vn.get('instance_ip_back_refs'):
   print tmpl.format('interfaces','Interfaces')
  if vn.get('floating_ip_pools'):
   print tmpl.format('floating-ip&id=%s'%id,'Floating IPs')
  print "</DIV>"
  print "<ARTICLE STYLE='overflow:auto;' ID=div_os_info>"
  dict2html(vn,"{} ({})".format(name,id))
  print "</ARTICLE>"

 elif op == 'details':
  args['call'] = 'virtual-network/%s'%(id)
  vn = aWeb.rest_call("openstack_call",args)['data']['virtual-network']
  name = vn['display_name']
  dict2html(vn,"{} ({})".format(name,id))

 elif op == 'interfaces':
  args['virtual_network'] = id
  vn = aWeb.rest_call("openstack_contrail_interfaces",args)
  print "<DIV CLASS=table STYLE='width:auto'><DIV CLASS=thead><DIV CLASS=th>IP</DIV><DIV CLASS=th>MAC</DIV><DIV CLASS=th>Interface</DIV></DIV>"
  print "<DIV CLASS=tbody>"
  for ip in vn['ip_addresses']:
   print "<DIV CLASS=tr>"
   if ip.get('vm_uuid'):
    print "<DIV CLASS=td><A CLASS='z-op' DIV=div_content_right SPIN=true URL=sdcp.cgi?call=nova_action&id={0}>{1}</A></DIV>".format(ip['vm_uuid'],ip['ip_address'])
   else:
    print "<DIV CLASS=td>{}</DIV>".format(ip['ip_address'])
   print "<DIV CLASS=td>{}</DIV>".format(ip['mac_address'])
   if ip.get('vm_binding'):
    print "<DIV CLASS=td>{}</DIV>".format(ip['vm_binding'])
   elif ip.get('logical_interface'):
    print "<DIV CLASS=td><A CLASS='z-op' DIV=div_os_info SPIN=true URL=sdcp.cgi?call=neutron_action&op=print&id={}>{}</A></DIV>".format(ip['logical_interface_uuid'],ip['logical_interface'])
   else:
    print "<DIV CLASS=td>{}</DIV>".format(vmi['vm_interface_owner'])
   print "</DIV>"
  print "</DIV></DIV>"

 ############################################# Floating IP ##############################################
 #
 #
 elif op == 'floating-ip':
  args['virtual_network'] = id
  fips = aWeb.rest_call("openstack_contrail_floating_ips",args)
  print "<DIV CLASS=table STYLE='width:500px'><DIV CLASS=thead><DIV CLASS=th>Pool</DIV><DIV CLASS=th>Floating IP</DIV><DIV CLASS=th>Fixed IP</DIV><DIV CLASS=th>Fixed Network</DIV><DIV CLASS=th>Operations</DIV></DIV>"
  print "<DIV CLASS=tbody>"
  for fip in fips['ip_addresses']:
   fixed = fip.get('vm_ip_address')
   print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV>".format(fip['pool_name'],fip['ip_address'])
   if fixed:
    # Do we select one or many VMI:s?
    print "<DIV CLASS=td><A TITLE='VM info' CLASS='z-op' DIV=div_content_right  URL=sdcp.cgi?call=nova_action&op=info&id={0} SPIN=true>{1}</A></DIV>".format(fip['vm_interface'],fixed)
    print "<DIV CLASS=td><A TITLE='Network info' CLASS='z-op' DIV=div_content_right  URL=sdcp.cgi?call=neutron_action&op=info&id={0} SPIN=true>{1}</A></DIV>".format(fip['vm_network_uuid'],fip['vm_network_name'])
    print "<DIV CLASS=td>"
    print aWeb.button('info',  DIV='div_os_info', URL='sdcp.cgi?call=neutron_action&op=print&id=%s'%fip['uuid'])
    print aWeb.button('delete',DIV='div_os_info', URL='sdcp.cgi?call=neutron_action&op=fi_disassociate&id=%s'%fip['uuid'], MSG='Are you sure?', SPIN='true')
    print "&nbsp;</DIV>"
   else:
    print "<DIV CLASS=td></DIV>"
    print "<DIV CLASS=td></DIV>"
    print "<DIV CLASS=td>"
    print aWeb.button('info', DIV='div_os_info', URL='sdcp.cgi?call=neutron_action&op=print&id=%s'%fip['uuid'])
    print aWeb.button('add',  DIV='div_os_info', URL='sdcp.cgi?call=neutron_action&op=fi_associate_choose_vm&id=%s'%fip['uuid'])
    print "</DIV>"
   print "</DIV>"
  print "</DIV></DIV>"

 elif op == 'print':
  from json import dumps
  args['uuid'] = aWeb['id']
  res = aWeb.rest_call("openstack_contrail_uuid",args)
  print "<PRE>{}</PRE>".format(dumps(res,indent=4))

 elif op == 'remove':
  args['call'] = "virtual-network/{}".format(id)
  args['method'] = 'DELETE'
  res = aWeb.rest_call("openstack_call",args)['data']
  print "<ARTICLE>{}</ARTICLE>".format(res)

 elif op == 'fi_disassociate':
  args['call'] = "floating-ip/{}".format(id)
  args['method'] = 'PUT'
  args['arguments'] = {'floating-ip':{'virtual_machine_interface_refs':None,'floating_ip_fixed_ip_address':None }}
  res = aWeb.rest_call("openstack_call",args)
  print "Floating IP association removed" if res.get('result') == 'OK' else "Error: %s"%res

 elif op == 'fi_associate_choose_vm':
  args['service'] = 'nova'
  args['call'] = "servers"
  vms = aWeb.rest_call("openstack_call",args)['data']['servers']
  print "<FORM ID=frm_fi_assoc_vm><INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(id)
  print "VM: <SELECT STYLE='width:auto; height:22px;' NAME=vm>"
  for vm in vms:
   print "<OPTION VALUE={0}#{1}>{0}</OPTION>".format(vm['name'],vm['id'])
  print "</SELECT></FORM><DIV CLASS=controls>"
  print aWeb.button('next', DIV='div_os_info', FRM='frm_fi_assoc_vm', URL='sdcp.cgi?call=neutron_action&op=fi_associate_choose_interface')
  print "</DIV>"

 elif op == 'fi_associate_choose_interface':
  vm_name,_,vm_id = aWeb['vm'].partition('#')
  args['vm'] = vm_id
  vmis = aWeb.rest_call("openstack_contrail_vm_interfaces",args)
  print "<FORM ID=frm_fi_assoc_vmi>"
  print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(id)
  print "<INPUT TYPE=HIDDEN NAME=vm VALUE={}>".format(vm_id)
  print "VM: <INPUT STYLE='width:auto;' TYPE=TEXT VALUE={} disabled> Interface:<SELECT STYLE='width:auto; height:22px;' NAME=vmi>".format(vm_name)
  for vmi in vmis.get('interfaces',[]):
   print "<OPTION VALUE={0}#{1}>{2} ({1})</OPTION>".format(vmi['uuid'],vmi['ip_address'],vmi['virtual_network'])
  print "</SELECT>"
  print "</FORM><DIV CLASS=controls>"
  print aWeb.button('back', DIV='div_os_info', URL='sdcp.cgi?call=neutron_action&op=fi_associate_choose_vm&id=%s'%id, TITLE='Change VM')
  print aWeb.button('next', DIV='div_os_info', URL='sdcp.cgi?call=neutron_action&op=fi_associate', FRM='frm_fi_assoc_vmi', TITLE='Commit')
  print "</DIV>"

 elif op == 'fi_associate':
  vmid  = aWeb['vm']
  vmiid,_,ip = aWeb['vmi'].partition('#')
  args['vm_interface'] = vmiid
  args['vm_ip_address'] = ip
  args['floating_ip'] = id
  res = aWeb.rest_call("openstack_contrail_vm_associate_fip",args)
  print "Floating IP asssociation created" if res.get('result','NOT_OK') == "OK" else "Failure: %s"%res
