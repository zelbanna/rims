"""Module docstring.

HTML5 Ajax Openstack Neutron/Contrail module

"""
__author__= "Zacharias El Banna"
__version__ = "5.0GA"
__status__= "Production"

############################### Neutron ##############################
#
def list(aWeb):
 cookie = aWeb.cookie('openstack')
 token  = cookie.get('token')
 if not token:
  aWeb.wr("Not logged in")
  return
 data = aWeb.rest_call("openstack_call",{'token':token,'service':'contrail','call':"virtual-networks?fields=name,display_name,virtual_network_properties,network_ipam_refs"})['data']

 aWeb.wr("<SECTION CLASS=content-left ID=div_content_left>")
 aWeb.wr("<ARTICLE STYLE='overflow-x:hidden;'><P>Contrail VNs</P>")
 aWeb.wr(aWeb.button('reload',DIV='div_content',  URL='neutron_list'))
 aWeb.wr("<DIV CLASS=table>")
 aWeb.wr("<DIV CLASS=thead><DIV CLASS=th>Network</DIV><DIV CLASS=th>Subnet</DIV><DIV CLASS=th STYLE='width:50px;'>&nbsp;</DIV></DIV>")
 aWeb.wr("<DIV CLASS=tbody>")
 for net in data['virtual-networks']:
  if not net.get('display_name'):
   continue
  aWeb.wr("<DIV CLASS=tr>")
  aWeb.wr("<!-- {} -->".format(net.get('href')))
  aWeb.wr("<DIV CLASS=td STYLE='max-width:175px;'><A TITLE='Info {1}' CLASS='z-op' DIV=div_content_right URL='neutron_action?id={0}&op=info' SPIN=true>{1}</A></DIV>".format(net['uuid'],net['display_name']))
  aWeb.wr("<DIV CLASS=td STYLE='max-width:175px;'>")
  if net.get('network_ipam_refs'):
   for ipam in net['network_ipam_refs']:
    for sub in ipam['attr']['ipam_subnets']:
     aWeb.wr("{}/{}".format(sub['subnet']['ip_prefix'],sub['subnet']['ip_prefix_len']))
  aWeb.wr("</DIV>")
  aWeb.wr("<DIV CLASS=td>")
  aWeb.wr(aWeb.button('delete',DIV='div_content_right', SPIN='true', URL='neutron_action?name=%s&id=%s&op=remove'%(net['display_name'],net['uuid']), MSG='Delete network?'))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</DIV></DIV></ARTICLE></SECTION>")
 aWeb.wr("<SECTION CLASS=content-right ID=div_content_right></SECTION>")

def action(aWeb):
 from zdcp.site.openstack import dict2html
 cookie = aWeb.cookie('openstack')
 token  = cookie.get('token')
 if not token:
  aWeb.wr("Not logged in")
  return
 args = {'token':token,'service':'contrail'}
 id   = aWeb['id']
 op   = aWeb['op']

 if   op == 'info':
  args['call'] = 'virtual-network/%s'%(id)
  vn = aWeb.rest_call("openstack_call",args)['data']['virtual-network']
  name = vn['display_name']
  tmpl = "<A CLASS='z-op btn small text' DIV=div_os_info URL='neutron_action?name=%s&id=%s&op={}' SPIN=true>{}</A>"%(name,id)
  aWeb.wr("<DIV>")
  aWeb.wr(tmpl.format('details','Network details'))
  if vn.get('instance_ip_back_refs'):
   aWeb.wr(tmpl.format('interfaces','Interfaces'))
  if vn.get('floating_ip_pools'):
   aWeb.wr(tmpl.format('floating-ip&id=%s'%id,'Floating IPs'))
  aWeb.wr("</DIV>")
  aWeb.wr("<ARTICLE STYLE='overflow:auto;' ID=div_os_info>")
  dict2html(vn,"{} ({})".format(name,id))
  aWeb.wr("</ARTICLE>")

 elif op == 'details':
  args['call'] = 'virtual-network/%s'%(id)
  vn = aWeb.rest_call("openstack_call",args)['data']['virtual-network']
  name = vn['display_name']
  dict2html(vn,"{} ({})".format(name,id))

 elif op == 'interfaces':
  args['virtual_network'] = id
  vn = aWeb.rest_call("openstack_contrail_interfaces",args)
  aWeb.wr("<DIV CLASS=table STYLE='width:auto'><DIV CLASS=thead><DIV CLASS=th>IP</DIV><DIV CLASS=th>MAC</DIV><DIV CLASS=th>Interface</DIV></DIV>")
  aWeb.wr("<DIV CLASS=tbody>")
  for ip in vn['ip_addresses']:
   aWeb.wr("<DIV CLASS=tr>")
   if ip.get('vm_uuid'):
    aWeb.wr("<DIV CLASS=td><A CLASS='z-op' DIV=div_content_right SPIN=true URL='nova_action?id={0}'>{1}</A></DIV>".format(ip['vm_uuid'],ip['ip_address']))
   else:
    aWeb.wr("<DIV CLASS=td>{}</DIV>".format(ip['ip_address']))
   aWeb.wr("<DIV CLASS=td>{}</DIV>".format(ip['mac_address']))
   if ip.get('vm_binding'):
    aWeb.wr("<DIV CLASS=td>{}</DIV>".format(ip['vm_binding']))
   elif ip.get('logical_interface'):
    aWeb.wr("<DIV CLASS=td><A CLASS='z-op' DIV=div_os_info SPIN=true URL='neutron_action?op=print&id={}'>{}</A></DIV>".format(ip['logical_interface_uuid'],ip['logical_interface']))
   else:
    aWeb.wr("<DIV CLASS=td>{}</DIV>".format(vmi['vm_interface_owner']))
   aWeb.wr("</DIV>")
  aWeb.wr("</DIV></DIV>")

 ############################################# Floating IP ##############################################
 #
 #
 elif op == 'floating-ip':
  args['virtual_network'] = id
  fips = aWeb.rest_call("openstack_contrail_floating_ips",args)
  aWeb.wr("<DIV CLASS=table STYLE='width:500px'><DIV CLASS=thead><DIV CLASS=th>Pool</DIV><DIV CLASS=th>Floating IP</DIV><DIV CLASS=th>Fixed IP</DIV><DIV CLASS=th>Fixed Network</DIV><DIV CLASS=th>Operations</DIV></DIV>")
  aWeb.wr("<DIV CLASS=tbody>")
  for fip in fips['ip_addresses']:
   fixed = fip.get('vm_ip_address')
   aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV>".format(fip['pool_name'],fip['ip_address']))
   if fixed:
    # Do we select one or many VMI:s?
    aWeb.wr("<DIV CLASS=td><A TITLE='VM info' CLASS='z-op' DIV=div_content_right  URL='nova_action?op=info&id={0}' SPIN=true>{1}</A></DIV>".format(fip['vm_interface'],fixed))
    aWeb.wr("<DIV CLASS=td><A TITLE='Network info' CLASS='z-op' DIV=div_content_right  URL='neutron_action?op=info&id={0}' SPIN=true>{1}</A></DIV>".format(fip['vm_network_uuid'],fip['vm_network_name']))
    aWeb.wr("<DIV CLASS=td>")
    aWeb.wr(aWeb.button('info',  DIV='div_os_info', URL='neutron_action?op=print&id=%s'%fip['uuid']))
    aWeb.wr(aWeb.button('delete',DIV='div_os_info', URL='neutron_action?op=fi_disassociate&id=%s'%fip['uuid'], MSG='Are you sure?', SPIN='true'))
    aWeb.wr("</DIV>")
   else:
    aWeb.wr("<DIV CLASS=td></DIV><DIV CLASS=td></DIV><DIV CLASS=td>")
    aWeb.wr(aWeb.button('info', DIV='div_os_info', URL='neutron_action?op=print&id=%s'%fip['uuid']))
    aWeb.wr(aWeb.button('add',  DIV='div_os_info', URL='neutron_action?op=fi_associate_choose_vm&id=%s'%fip['uuid']))
    aWeb.wr("</DIV>")
   aWeb.wr("</DIV>")
  aWeb.wr("</DIV></DIV>")

 elif op == 'print':
  from json import dumps
  args['uuid'] = aWeb['id']
  res = aWeb.rest_call("openstack_contrail_uuid",args)
  aWeb.wr("<PRE>{}</PRE>".format(dumps(res,indent=4)))

 elif op == 'remove':
  args['call'] = "virtual-network/{}".format(id)
  args['method'] = 'DELETE'
  res = aWeb.rest_call("openstack_call",args)['data']
  aWeb.wr("<ARTICLE>{}</ARTICLE>".format(res))

 elif op == 'fi_disassociate':
  args['call'] = "floating-ip/{}".format(id)
  args['method'] = 'PUT'
  args['arguments'] = {'floating-ip':{'virtual_machine_interface_refs':None,'floating_ip_fixed_ip_address':None }}
  res = aWeb.rest_call("openstack_call",args)
  aWeb.wr("Floating IP association removed" if res.get('result') == 'OK' else "Error: %s"%res)

 elif op == 'fi_associate_choose_vm':
  args['service'] = 'nova'
  args['call'] = "servers"
  vms = aWeb.rest_call("openstack_call",args)['data']['servers']
  aWeb.wr("<FORM ID=frm_fi_assoc_vm><INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(id))
  aWeb.wr("VM: <SELECT STYLE='width:auto; height:22px;' NAME=vm>")
  for vm in vms:
   aWeb.wr("<OPTION VALUE={0}#{1}>{0}</OPTION>".format(vm['name'],vm['id']))
  aWeb.wr("</SELECT></FORM>")
  aWeb.wr(aWeb.button('forward', DIV='div_os_info', FRM='frm_fi_assoc_vm', URL='neutron_action?op=fi_associate_choose_interface'))

 elif op == 'fi_associate_choose_interface':
  vm_name,_,vm_id = aWeb['vm'].partition('#')
  args['vm'] = vm_id
  vmis = aWeb.rest_call("openstack_contrail_vm_interfaces",args)
  aWeb.wr("<FORM ID=frm_fi_assoc_vmi>")
  aWeb.wr("<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(id))
  aWeb.wr("<INPUT TYPE=HIDDEN NAME=vm VALUE={}>".format(vm_id))
  aWeb.wr("VM: <INPUT STYLE='width:auto;' TYPE=TEXT VALUE={} disabled> Interface:<SELECT STYLE='width:auto; height:22px;' NAME=vmi>".format(vm_name))
  for vmi in vmis.get('interfaces',[]):
   aWeb.wr("<OPTION VALUE={0}#{1}>{2} ({1})</OPTION>".format(vmi['uuid'],vmi['ip_address'],vmi['virtual_network']))
  aWeb.wr("</SELECT>")
  aWeb.wr("</FORM>")
  aWeb.wr(aWeb.button('back', DIV='div_os_info', URL='neutron_action?op=fi_associate_choose_vm&id=%s'%id, TITLE='Change VM'))
  aWeb.wr(aWeb.button('forward', DIV='div_os_info', URL='neutron_action?op=fi_associate', FRM='frm_fi_assoc_vmi', TITLE='Commit'))

 elif op == 'fi_associate':
  vmid  = aWeb['vm']
  vmiid,_,ip = aWeb['vmi'].partition('#')
  args['vm_interface'] = vmiid
  args['vm_ip_address'] = ip
  args['floating_ip'] = id
  res = aWeb.rest_call("openstack_contrail_vm_associate_fip",args)
  aWeb.wr("Floating IP asssociation created" if res.get('result','NOT_OK') == "OK" else "Failure: %s"%res)
