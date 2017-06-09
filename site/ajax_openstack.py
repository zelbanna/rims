"""Module docstring.

Ajax Openstack calls module

"""
__author__= "Zacharias El Banna"
__version__ = "17.6.1GA"
__status__= "Production"


############################### Openstack #############################
#
# Assume we've created a token from the pane, so auth is done and we should pick up cookie template .. now username is the final thing .. before proper cookies in web reader
#
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

##################################### Heatstack ##################################
#
def heat_list(aWeb):
 cookie = aWeb.get_cookie()
 token  = cookie.get('os_user_token')
 if not token:
  print "Not logged in"
  return
 controller = OpenstackRPC(cookie.get('os_controller'),token)

 port  = cookie.get('os_heat_port')
 url   = cookie.get('os_heat_url')
 name = aWeb.get_value('name')
 id   = aWeb.get_value('id')
 op   = aWeb.get_value('op','info')

 ret = controller.call(cookie.get('os_heat_port'),cookie.get('os_heat_url') + "/stacks") 
 if not ret['result'] == "OK":
  print "Error retrieving heat stacks ({})".format(ret['code'])
  return

 print "<DIV CLASS='z-table' style='width:394px'><TABLE style='width:99%'>"
 print "<THEAD style='height:20px'><TH COLSPAN=3><CENTER>Heat Stacks</CENTER></TH></THEAD>"
 print "<TR style='height:20px'><TD COLSPAN=3>"
 print "<A TITLE='Reload List' CLASS='z-btn z-small-btn z-op' OP=load DIV=div_navleft URL='ajax.cgi?call=openstack_heat_list'><IMG SRC='images/btn-reboot.png'></A>"
 print "<A TITLE='Add service' CLASS='z-btn z-small-btn z-op' OP=load DIV=div_navcont URL='ajax.cgi?call=openstack_heat_choose_template'><IMG SRC='images/btn-add.png'></A>"
 print "</TR>"
 print "<THEAD><TH>Name</TH><TH>Status</TH><TH>Operations</TH></THEAD>"
 for stack in ret['data'].get('stacks',None):
  print "<TR>"
  print "<TD>{}</TD>".format(stack['stack_name'])
  print "<TD>{}</TD>".format(stack['stack_status'])
  print "<TD>"
  tmpl = "<A TITLE='{}' CLASS='z-btn z-op z-small-btn' DIV=div_navcont URL=ajax.cgi?call=openstack_heat_action&name=" + stack['stack_name'] + "&id=" + stack['id'] + "&op={} OP=load SPIN=true>{}</A>"
  print tmpl.format('Stack info','info','<IMG SRC=images/btn-info.png>')
  if stack['stack_status'] == "CREATE_COMPLETE" or stack['stack_status'] == "CREATE_FAILED":
   print tmpl.format('Remove stack','remove','<IMG SRC=images/btn-remove.png>')
  print "</TD>"
  print "</TR>"
 print "</TABLE>"
 print "</DIV>"

######################### HEAT ADD ######################
#
# Add instantiation
#
def heat_choose_template(aWeb):
 print "<DIV CLASS='z-table' style='display:inline-block; padding:6px'>"
 print "<FORM ID=frm_heat_choose_template>"
 try:
  print "Add solution from template:<SELECT NAME=template style='height:22px;'>"
  from os import listdir
  for file in listdir("os_templates/"):
   name = file.partition('.')[0]
   print "<OPTION VALUE={}>{}</OPTION>".format(file,name)
  print "</SELECT>"
 except Exception as err:
  print "openstack_choose_template: error finding template files in 'os_templates/' [{}]".format(str(err))
 print "</FORM>"
 print "<A TITLE='Enter parameters' CLASS='z-btn z-small-btn z-op' OP=post FRM=frm_heat_choose_template DIV=div_os_info URL='ajax.cgi?call=openstack_heat_enter_parameters'><IMG SRC='images/btn-document.png'></A>"
 print "<A TITLE='View template'    CLASS='z-btn z-small-btn z-op' OP=post FRM=frm_heat_choose_template DIV=div_os_info URL='ajax.cgi?call=openstack_heat_action&op=templateview'><IMG SRC='images/btn-info.png'></A>"
 print "</DIV>"
 print "<DIV ID=div_os_info></DIV>"

def heat_enter_parameters(aWeb):
 from json import load,dumps
 template = aWeb.get_value('template')
 with open("os_templates/"+template) as f:
  data = load(f)
 print "<DIV CLASS='z-table' style='display:inline-block; padding:6px'>"
 print "<FORM ID=frm_heat_template_parameters>"
 print "<INPUT TYPE=hidden NAME=template VALUE={}>".format(template)
 print "<TABLE>"
 print "<THEAD><TH>Parameter</TH><TH style='min-width:300px'>Value</TH></THEAD>"
 print "<TR><TD><B>Unique Name</B></TD><TD><INPUT CLASS='z-input' TYPE=text NAME=name PLACEHOLDER='change-this-name'></TD></TR>"
 for key,value in data['parameters'].iteritems():
  print "<TR><TD>{0}</TD><TD><INPUT CLASS='z-input' TYPE=TEXT NAME=param_{0} PLACEHOLDER={1}></TD></TR>".format(key,value)
 print "</TABLE>"
 print "</FORM>"
 print "<A TITLE='Create' CLASS='z-btn z-small-btn z-op' style='float:right;' OP=post SPIN=true FRM=frm_heat_template_parameters DIV=div_navcont URL='ajax.cgi?call=openstack_heat_action&op=create'><IMG SRC='images/btn-start.png'></A>"
 print "</DIV>"

#
# Heat Actions
#
def heat_action(aWeb):
 cookie = aWeb.get_cookie()
 token  = cookie.get('os_user_token')
 if not token:
  print "Not logged in"
  return
 controller = OpenstackRPC(cookie.get('os_controller'),token)

 port  = cookie.get('os_heat_port')
 url   = cookie.get('os_heat_url')
 name = aWeb.get_value('name')
 id   = aWeb.get_value('id')
 op   = aWeb.get_value('op','info')

 aWeb.log_msg("openstack_heat_action - id:{} name:{} op:{} for project:{}".format(id,name,op,cookie.get('os_project_name')))

 if   op == 'info':
  tmpl = "<A TITLE='{}' CLASS='z-btn z-op' DIV=div_os_info URL=ajax.cgi?call=openstack_heat_action&name=" + name + "&id=" + id+ "&op={} OP=load SPIN=true>{}</A>"
  print "<DIV>"
  print tmpl.format('Stack Details','details','Details')
  print tmpl.format('Stack Parameters','events','Events')
  print tmpl.format('Stack Template','template','Template')
  print tmpl.format('Stack Parameters','parameters','Parameters')
  print "</DIV>"
  print "<DIV CLASS='z-table' style='overflow:auto' ID=div_os_info>"
  ret = controller.call(port,url + "/stacks/{}/{}".format(name,id))
  print "<H2>{}</H2>".format(name)
  _print_info(ret['data']['stack'])
  print "</DIV>"

 elif op == 'events':
  from json import dumps
  ret = controller.call(port,url + "/stacks/{}/{}/events".format(name,id))
  print "<TABLE>"
  for event in ret['data']['events']:
   print "<TR><TD>{}</TD><TD>{}</TD><TD>{}</TD><TD>{}</TD></TR>".format(event['resource_name'],event['logical_resource_id'],event['resource_status'],event['resource_status_reason'])
  print "</TABLE>"

 elif op == 'details':
  ret = controller.call(port,url + "/stacks/{}/{}".format(name,id))
  print "<H2>{}</H2>".format(name)
  _print_info(ret['data']['stack'])

 elif op == 'remove':
  ret = controller.call(port,url + "/stacks/{}/{}".format(name,id), method='DELETE')
  print "<DIV CLASS='z-table'>"
  print "<H3>Removing {}</H3>".format(name)
  if ret['code'] == 204:
   print "Stack removed"
  else:
   print "Error code: {}".format(ret['code'])
  print "</DIV>"

 elif op == 'template':
  from json import dumps
  ret = controller.call(port,url + "/stacks/{}/{}/template".format(name,id))
  print "<PRE>" + dumps(ret['data'], indent=4) + "</PRE>"

 elif op == 'parameters':
  from json import dumps
  ret = controller.call(port,url + "/stacks/{}/{}".format(name,id))
  data = ret['data']['stack']['parameters']
  data.pop('OS::project_id')
  data.pop('OS::stack_name')
  data.pop('OS::stack_id')
  print "<PRE>" + dumps(data, indent=4) + "</PRE>"

 elif op == 'create':
  template = aWeb.get_value('template')
  if name and template:
   from json import load,dumps
   with open("os_templates/"+template) as f:
    data = load(f)
   data['stack_name'] = name
   params  = aWeb.get_args2dict_except(['op','call','template','name'])
   for key,value in params.iteritems():
    data['parameters'][key[6:]] = value
   ret = controller.call(port,url + "/stacks",arg=data)
   if ret['code'] == 201:
    print "<DIV CLASS='z-table'>"
    print "<H2>Successful instantiation of '{}' solution</H2>".format(template.partition('.')[0])
    print "Name: {}<BR>Id:{}".format(name,ret['data']['stack']['id'])
    print "</DIV>"
   else:
    print "<PRE>Error instantiating stack:" + str(ret) + "</PRE>"
  else:
   print "Error - need to provide a name for the instantiation"

 if op == 'templateview':
  template = aWeb.get_value('template')
  from json import load,dumps
  with open("os_templates/"+template) as f:
   data = load(f)
  data['stack_name'] = name if name else "Need_to_specify_name"
  print "<DIV CLASS='z-table'><PRE>"
  print dumps(data, indent=4, sort_keys=True)
  print "</PRE></DIV>"

############################### Neutron ##############################
#
def neutron_list(aWeb):
 cookie = aWeb.get_cookie()
 token  = cookie.get('os_user_token')
 if not token:
  print "Not logged in"
  return
 controller = OpenstackRPC(cookie.get('os_controller'),token)
 pname = cookie.get("os_project_name")

 ret = controller.call(cookie.get('os_neutron_port'), cookie.get('os_neutron_url')+"/v2.0/networks")
 if not ret['result'] == "OK":
  print "Error retrieving list"
  return

 print "<DIV CLASS='z-table' style='width:394px'><TABLE style='width:99%'>"
 print "<THEAD style='height:20px'><TH COLSPAN=3><CENTER>Contrail VNs</CENTER></TH></THEAD>"
 print "<TR style='height:20px'><TD COLSPAN=3>"
 print "<A TITLE='Reload List' CLASS='z-btn z-small-btn z-op' OP=load DIV=div_navleft URL='ajax.cgi?call=openstack_neutron_list'><IMG SRC='images/btn-reboot.png'></A>"
 print "</TR>"
 print "<THEAD><TH>Owner</TH><TH>Network</TH><TH>Operations</TH></THEAD>"
 for net in ret['data']['networks']:
  if net['tenant_id'] == cookie.get('os_project_id'):
   print "<TR><TD>{}</TD><TD>{}</TD>".format(pname,net['name'])
   print "<TD>"
   tmpl = "<A TITLE='{}' CLASS='z-btn z-op z-small-btn' DIV=div_navcont URL=ajax.cgi?call=openstack_neutron_action&name=" + net['name'] + "&id=" + net['id'] + "&op={} OP=load SPIN=true>{}</A>"
   print tmpl.format('Network info','info','<IMG SRC=images/btn-info.png>')  
   print "</TD>"
   print "</TR>"
 print "</TABLE>"
 print "</DIV>"

def neutron_action(aWeb):
 cookie = aWeb.get_cookie()
 token  = cookie.get('os_user_token')
 if not token:
  print "Not logged in"
  return
 controller = OpenstackRPC(cookie.get('os_controller'),token)

 port  = cookie.get('os_neutron_port')
 url   = cookie.get('os_neutron_url')
 name = aWeb.get_value('name')
 id   = aWeb.get_value('id')
 op   = aWeb.get_value('op','info')

 if   op == 'info':
  print "<DIV CLASS='z-table' style='overflow:auto' ID=div_os_info>"
  ret = controller.call("8082","virtual-network/{}".format(id))
  print "<H2>{} ({})</H2>".format(name,id)
  _print_info(ret['data']['virtual-network'])
  print "</DIV>"


################################# Nova ###############################
#
def nova_list(aWeb):
 cookie = aWeb.get_cookie()
 token  = cookie.get('os_user_token')
 if not token:
  print "Not logged in"
  return
 controller = OpenstackRPC(cookie.get('os_controller'),token)

 port  = cookie.get('os_nova_port')
 url   = cookie.get('os_nova_url')

 ret = controller.call(port,url + "/servers")
 if not ret['result'] == "OK":
  print "Error retrieving list {}".format(str(ret))
  return

 print "<DIV CLASS='z-table' style='width:394px'><TABLE style='width:99%'>"
 print "<THEAD style='height:20px'><TH COLSPAN=3><CENTER>Nova Servers</CENTER></TH></THEAD>"
 print "<TR style='height:20px'><TD COLSPAN=3>"
 print "<A TITLE='Reload List' CLASS='z-btn z-small-btn z-op' OP=load DIV=div_navleft URL='ajax.cgi?call=openstack_nova_list'><IMG SRC='images/btn-reboot.png'></A>"
 print "</TR>"
 print "<THEAD><TH>Name</TH><TH style='width:94px;'>Operations</TH></THEAD>"
 for server in ret['data'].get('servers',None):
  qserver = aWeb.quote(server['name'])
  print "<TR>"
  print "<!-- {} -->".format(server)
  print "<TD>{}</TD>".format(server['name'])
  print "<TD>"
  print "<A TITLE='VM info'   CLASS='z-btn z-op z-small-btn' DIV=div_navcont URL=ajax.cgi?call=openstack_nova_action&name={}&id={}&op=info   OP=load SPIN=true><IMG SRC='images/btn-info.png'></A>".format(qserver,server['id'])
  print "<A TITLE='Remove VM' CLASS='z-btn z-op z-small-btn' DIV=div_navcont URL=ajax.cgi?call=openstack_nova_action&name={}&id={}&op=remove OP=load SPIN=true><IMG SRC='images/btn-remove.png'></A>".format(qserver,server['id'])
  print "<A TITLE='Embedded Console' CLASS='z-btn z-op z-small-btn' DIV=div_navcont URL=ajax.cgi?call=openstack_nova_console&name={}&id={} OP=load><IMG SRC='images/btn-term-frame.png'></A>".format(qserver,server['id'])
  print "<A TITLE='New-tab Console'  CLASS='z-btn z-small-btn'	TARGET=_blank      HREF='pane.cgi?view=openstack_console&name={}&id={}'><IMG SRC='images/btn-term.png'></A>".format(qserver,server['id'])
  print "</TD>"
  print "</TR>"
 print "</TABLE>"
 print "</DIV>"

#
# Actions
# 
def nova_action(aWeb):
 cookie = aWeb.get_cookie()
 token  = cookie.get('os_user_token')
 if not token:
  print "Not logged in"
  return
 controller = OpenstackRPC(cookie.get('os_controller'),token)

 port  = cookie.get('os_nova_port')
 url   = cookie.get('os_nova_url')
 name = aWeb.get_value('name')
 id   = aWeb.get_value('id')
 op   = aWeb.get_value('op','info')

 aWeb.log_msg("openstack_nova_action - id:{} name:{} op:{} for project:{}".format(id,name,op,cookie.get('os_project_name')))

 if   op == 'info':
  tmpl = "<A TITLE='{}' CLASS='z-btn z-op' DIV=div_os_info URL=ajax.cgi?call=openstack_nova_action&name=" + name + "&id=" + id+ "&op={} OP=load SPIN=true>{}</A>"
  print "<DIV>"
  print tmpl.format('Details','details','Details')
  print tmpl.format('Diagnostics','diagnostics','Diagnostics')
  print "</DIV>"

  print "<DIV CLASS='z-table' style='overflow:auto' ID=div_os_info>"
  ret = controller.call(port,url + "/servers/{}".format(id))
  print "<H2>{}</H2>".format(name)
  _print_info(ret['data']['server'])
  print "</DIV>"

 elif op == 'details':
  ret = controller.call(port,url + "/servers/{}".format(id))
  print "<H2>{}</H2>".format(name)
  _print_info(ret['data']['server'])

 elif op == 'diagnostics':
  ret = controller.call(port,url + "/servers/{}/diagnostics".format(id))
  print "<H2>{}</H2>".format(name)
  _print_info(ret['data'])

 elif op == 'remove':
  ret = controller.call(port,url + "/servers/{}".format(id), method='DELETE')
  if not ret['result'] == "OK":
   print "Error performing op {}".format(str(ret))
   return
  print "<DIV CLASS='z-table'>"
  print "<H2>Removing {}</H2>".format(name)
  if ret['code'] == 204:
   print "Server removed"
  else:
   print "Error code: {}".format(ret['code'])
  print "</DIV>"

def nova_console(aWeb):
 # Old school version, before microapi 2.6
 # - after: /servers/{server_id}/remote-consoles , body: { "remote_console": { "protocol": "vnc", "type": "novnc" }
 cookie = aWeb.get_cookie()
 token = cookie.get('os_user_token')
 if not token:
  print "Not logged in"
  return
 id   = aWeb.get_value('id')
 name = aWeb.get_value('name')
 controller = OpenstackRPC(cookie.get('os_controller'),token)
 data = controller.call(cookie.get('os_nova_port'), cookie.get('os_nova_url') + "/servers/" + id + "/action", { "os-getVNCConsole": { "type": "novnc" } } )
 if data['code'] == 200:
  # URL is #@?! inline URL.. remove http:// and replace IP (assume there is a port..) with controller IP
  suffix = data['data']['console']['url'][7:].partition(':')[2]
  print "<iframe id='console_embed' src='{}&title={}' style='width: 100%; height: 100%;'></iframe>".format("http://" + cookie.get('os_controller') + ":" + suffix,name)
