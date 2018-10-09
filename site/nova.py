"""Module docstring.

HTML5 Ajax Openstack NOVA module

- left and right divs frames (div_content_left/right) needs to be created by ajax call
"""
__author__= "Zacharias El Banna"
__version__ = "5.1GA"
__status__= "Production"

################################# Nova ###############################
#
def list(aWeb):
 from zdcp.core.genlib import get_quote
 cookie = aWeb.cookie('openstack')
 token  = cookie.get('token')
 if not token:
  aWeb.wr("Not logged in")
  return
 data = aWeb.rest_call("openstack_call",{'token':cookie['token'],'service':"nova",'call':"servers/detail"})['data']
 aWeb.wr("<SECTION CLASS=content-left ID=div_content_left><ARTICLE><P>Nova Servers</P>")
 aWeb.wr(aWeb.button('reload', DIV='div_content', URL='nova_list'))
 aWeb.wr(aWeb.button('add', DIV='div_content_right', URL='nova_select_parameters'))
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Name</DIV><DIV CLASS=th STYLE='width:135px;'>&nbsp;</DIV></DIV>")
 aWeb.wr("<DIV CLASS=tbody>")
 for server in data.get('servers'):
  aWeb.wr("<DIV CLASS=tr>")
  aWeb.wr("<!-- {} - {} -->".format(server['status'],server['OS-EXT-STS:task_state']))
  aWeb.wr("<DIV CLASS=td STYLE='max-width:200px'><A CLASS='z-op' TITLE='VM info' DIV=div_content_right URL='nova_action?id={}&op=info' SPIN=true>{}</A></DIV>".format(server['id'],server['name']))
  aWeb.wr("<DIV CLASS=td>")
  qserver = get_quote(server['name'])
  actionurl = 'nova_action?name=%s&id=%s&op={}'%(qserver,server['id'])
  aWeb.wr(aWeb.button('term', TARGET='_blank', HREF='nova_console?name=%s&id=%s'%(qserver,server['id']), TITLE='New window console'))
  aWeb.wr(aWeb.button('term-frame', DIV='div_content_right', URL='nova_console?inline=yes&id=%s'%server['id'], TITLE='Embedded console'))
  aWeb.wr(aWeb.button('delete', DIV='div_content_right', URL=actionurl.format('remove'), MSG='Are you sure you want to delete VM?', SPIN='true'))
  if not server['OS-EXT-STS:task_state']:
   if   server['status'] == 'ACTIVE':
    aWeb.wr(aWeb.button('stop', DIV='div_content_right', URL=actionurl.format('stop'), SPIN='true', TITLE='Stop VM'))
    aWeb.wr(aWeb.button('reload', DIV='div_content_right', URL=actionurl.format('reboot'), SPIN='true', TITLE='Reboot'))
   elif server['status'] == 'SHUTOFF':
    aWeb.wr(aWeb.button('start', DIV='div_content_right', URL=actionurl.format('start'), SPIN='true', TITLE='Start VM'))
  else:
   aWeb.wr(aWeb.button('info', DIV='div_content_right', URL=actionurl.format('info'), SPIN='true', TITLE='VM info'))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</ARTICLE></SECTION>")
 aWeb.wr("<SECTION CLASS=content-right ID=div_content_right></SECTION>")

def select_parameters(aWeb):
 cookie = aWeb.cookie('openstack')
 token  = cookie.get('token')
 if not token:
  aWeb.wr("Not logged in")
  return
 resources = aWeb.rest_call("openstack_vm_resources",{'token':token})
 aWeb.wr("<SCRIPT>dragndrop();</SCRIPT>")
 aWeb.wr("<ARTICLE CLASS='info'><P>New VM parameters</P>")
 aWeb.wr("<FORM ID=frm_os_create_vm>")
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=os_network ID=os_network>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=tbody>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Name</DIV><DIV CLASS=td><INPUT NAME=os_name PLACEHOLDER='Unique Name'></DIV></DIV>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Image</DIV><DIV CLASS=td><SELECT NAME=os_image>")
 for img in resources['images']:
  aWeb.wr("<OPTION VALUE={}>{} (Min Ram: {}Mb)</OPTION>".format(img['id'],img['name'],img['min_ram']))
 aWeb.wr("</SELECT></DIV></DIV>")

 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Flavor</DIV><DIV CLASS='table-val td'><SELECT NAME=os_flavor>")
 for fl in resources['flavors']:
  aWeb.wr("<OPTION VALUE={}>{} (Ram: {}Mb, vCPUs: {}, Disk: {}Gb</OPTION>".format(fl['id'],fl['name'],fl['ram'],fl['vcpus'],fl['disk']))
 aWeb.wr("</SELECT></DIV></DIV>")
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("<DIV CLASS='border'><UL CLASS='drop vertical' ID=ul_network DEST=os_network></UL></DIV>")
 aWeb.wr("</FORM>")
 aWeb.wr(aWeb.button('start',DIV='div_content_right', URL='nova_action?id=new&op=add',FRM='frm_os_create_vm', SPIN='true'))
 aWeb.wr("<DIV CLASS='border'><UL CLASS='drop vertical' ID=ul_avail>")
 for net in resources['networks']:
  if net.get('contrail:subnet_ipam'):
   aWeb.wr("<LI ID=net_%s CLASS='drag'>%s (%s)</LI>"%(net['id'],net['name'],net['contrail:subnet_ipam'][0]['subnet_cidr']))
 aWeb.wr("</UL></DIV>")
 aWeb.wr("</ARTICLE>")

######################################## Actions ########################################
#
def action(aWeb):
 from zdcp.site.openstack import dict2html
 cookie = aWeb.cookie('openstack')
 token  = cookie.get('token')
 if not token:
  aWeb.wr("Not logged in")
  return
 args ={'token':cookie['token'],'service':'nova'}
 op   = aWeb.get('op','info')

 if   op == 'info':
  from zdcp.core.genlib import get_quote
  args['call'] = "servers/%s"%aWeb['id']
  server = aWeb.rest_call("openstack_call",args)['data']['server']
  qserver = get_quote(server['name'])
  tmpl = "<A CLASS='z-op btn small text' TITLE='{}' DIV=div_os_info URL='nova_action?id=%s&op={}' SPIN=true>{}</A>"%aWeb['id']
  aWeb.wr("<DIV>")
  aWeb.wr(tmpl.format('Details','details','VM Details'))
  aWeb.wr(tmpl.format('Diagnostics','diagnostics','Diagnostics'))
  aWeb.wr(tmpl.format('Networks','networks','Networks'))
  aWeb.wr("<A CLASS='btn small text' TITLE='New-tab Console' TARGET=_blank HREF='nova_console?name={0}&id={1}'>Console</A>".format(qserver,aWeb['id']))
  aWeb.wr("</DIV>")
  aWeb.wr("<ARTICLE STYLE='overflow:auto;' ID=div_os_info>")
  dict2html(server,server['name'])
  aWeb.wr("</ARTICLE>")

 elif op == 'details':
  args['call'] = "servers/%s"%aWeb['id']
  server = aWeb.rest_call("openstack_call",args)['data']['server']
  dict2html(server,server['name'])

 elif op == 'stop' or op == 'start' or op == 'reboot':
  args['arguments'] = {"os-"+op:None} if op != 'reboot' else {"reboot":{ "type":"SOFT" }}
  args['call'] = "servers/%s/action"%aWeb['id']
  res = aWeb.rest_call("openstack_call",args)
  aWeb.wr("<ARTICLE>")
  if res['code'] == 202:
   aWeb.wr("Command executed successfully [%s]"%(op))
  else:
   aWeb.wr("Error executing command [%s]"%str(res))
  aWeb.wr("</ARTICLE>")

 elif op == 'diagnostics':
  args['call'] = "servers/%s/diagnostics"%aWeb['id']
  data = aWeb.rest_call("openstack_call",args)['data']
  dict2html(data)

 elif op == 'networks':
  from json import dumps
  args['vm']  = aWeb['id']
  data = aWeb.rest_call("openstack_vm_networks",args)

  aWeb.wr("<DIV CLASS=table STYLE='width:auto'>")
  aWeb.wr("<DIV CLASS=thead><DIV CLASS=th>MAC</DIV><DIV CLASS=th>Routing Instance</DIV><DIV CLASS=th>Network</DIV><DIV CLASS=th>IP</DIV><DIV CLASS=th>Floating IP</DIV><DIV CLASS=th>Operation</DIV></DIV><DIV CLASS=tbody>")
  for intf in data['interfaces']:
   aWeb.wr("<DIV CLASS=tr>")
   aWeb.wr("<DIV CLASS=td>{}</DIV>".format(intf['mac_address']))
   aWeb.wr("<DIV CLASS=td>{}</DIV>".format(intf['routing-instance']))
   aWeb.wr("<DIV CLASS=td><A CLASS='z-op' DIV=div_content_right SPIN=true URL='neutron_action?id={0}&op=info'>{1}</A></DIV>".format(intf['network_uuid'],intf['network_fqdn']))
   aWeb.wr("<DIV CLASS=td>{}</DIV>".format(intf['ip_address']))
   if intf.get('floating_ip_address'):
    aWeb.wr("<DIV CLASS=td>{} ({})</DIV><DIV CLASS=td>&nbsp;".format(intf['floating_ip_address'],intf['floating_ip_name']))
    aWeb.wr(aWeb.button('delete',DIV='div_os_info', URL='neutron_action?op=fi_disassociate&id=%s'%intf['floating_ip_uuid'], SPIN='true'))
    aWeb.wr("</DIV>")
   else:
    aWeb.wr("<DIV CLASS=td>&nbsp;</DIV>")
    aWeb.wr("<DIV CLASS=td>&nbsp;</DIV>")
   aWeb.wr("</DIV>")
  aWeb.wr("</DIV></DIV>")

 elif op == 'add':
  aWeb.wr(aWeb)

 elif op == 'remove':
  args['call'] = "servers/{}".format(aWeb['id'])
  args['method'] = 'DELETE'
  res = aWeb.rest_call("openstack_rest",args)
  aWeb.wr("<ARTICLE><P>Removing VM</P>")
  aWeb.wr("VM removed" if res['code'] == 204 else "Error code: %s"%(res['code']))
  aWeb.wr("</ARTICLE>")

def console(aWeb):
 cookie = aWeb.cookie('openstack')
 token  = cookie.get('token')
 res = aWeb.rest_call("openstack_vm_console",{'token':cookie['token'],'vm':aWeb['id']})
 if aWeb['inline']:
  aWeb.wr("<iframe id='console_embed' src='{}' STYLE='width: 100%; height: 100%;'></iframe>".format(res['url']))
 else:
  aWeb.wr("<SCRIPT> window.location.replace('%s&title=%s'); </SCRIPT>"%(res['url'],aWeb['name']))
