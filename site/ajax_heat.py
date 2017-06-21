"""Module docstring.

Ajax Openstack HEAT calls module

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
def list(aWeb):
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
 print "<A TITLE='Reload List' CLASS='z-btn z-small-btn z-op' OP=load DIV=div_navleft URL='ajax.cgi?call=heat_list'><IMG SRC='images/btn-reboot.png'></A>"
 print "<A TITLE='Add service' CLASS='z-btn z-small-btn z-op' OP=load DIV=div_navcont URL='ajax.cgi?call=heat_choose_template'><IMG SRC='images/btn-add.png'></A>"
 print "</TR>"
 print "<THEAD><TH>Name</TH><TH>Status</TH><TH></TH></THEAD>"
 for stack in ret['data'].get('stacks',None):
  print "<TR>"
  print "<TD>{}</TD>".format(stack['stack_name'])
  print "<TD>{}</TD>".format(stack['stack_status'])
  print "<TD>"
  tmpl = "<A TITLE='{}' CLASS='z-btn z-op z-small-btn' DIV=div_navcont URL=ajax.cgi?call=heat_action&name=" + stack['stack_name'] + "&id=" + stack['id'] + "&op={} OP=load SPIN=true>{}</A>"
  print tmpl.format('Stack info','info','<IMG SRC=images/btn-info.png>')
  if stack['stack_status'] == "CREATE_COMPLETE" or stack['stack_status'] == "CREATE_FAILED" or stack['stack_status'] == "DELETE_FAILED":
   print "<A TITLE='Remove stack' CLASS='z-btn z-op z-small-btn' DIV=div_navcont URL=ajax.cgi?call=heat_action&name=" + stack['stack_name'] + "&id=" + stack['id'] + "&op=remove OP=load MSG='Are you sure' SPIN=true><IMG SRC=images/btn-remove.png></A>"
  print "</TD>"
  print "</TR>"
 print "</TABLE>"
 print "</DIV>"

######################### HEAT ADD ######################
#
# Add instantiation
#
def choose_template(aWeb):
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
 print "<A TITLE='Enter parameters' CLASS='z-btn z-small-btn z-op' OP=load FRM=frm_heat_choose_template DIV=div_os_info URL='ajax.cgi?call=heat_enter_parameters'><IMG SRC='images/btn-document.png'></A>"
 print "<A TITLE='View template'    CLASS='z-btn z-small-btn z-op' OP=load FRM=frm_heat_choose_template DIV=div_os_info URL='ajax.cgi?call=heat_action&op=templateview'><IMG SRC='images/btn-info.png'></A>"
 print "</DIV>"
 print "<DIV ID=div_os_info></DIV>"

def enter_parameters(aWeb):
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
 print "<A TITLE='Create' CLASS='z-btn z-small-btn z-op' style='float:right;' OP=load SPIN=true FRM=frm_heat_template_parameters DIV=div_navcont URL='ajax.cgi?call=heat_action&op=create'><IMG SRC='images/btn-start.png'></A>"
 print "</DIV>"

#
# Heat Actions
#
def action(aWeb):
 cookie = aWeb.get_cookie()
 token  = cookie.get('os_user_token')
 if not token:
  print "Not logged in"
  return
 controller = OpenstackRPC(cookie.get('os_controller'),token)

 port = cookie.get('os_heat_port')
 url  = cookie.get('os_heat_url')
 name = aWeb.get_value('name')
 id   = aWeb.get_value('id')
 op   = aWeb.get_value('op','info')

 aWeb.log_msg("heat_action - id:{} name:{} op:{} for project:{}".format(id,name,op,cookie.get('os_project_name')))

 if   op == 'info':
  tmpl = "<A TITLE='{}' CLASS='z-btn z-op' DIV=div_os_info URL=ajax.cgi?call=heat_action&name=" + name + "&id=" + id+ "&op={} OP=load SPIN=true>{}</A>"
  print "<DIV>"
  print tmpl.format('Stack Details','details','Stack Details')
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
   ret = controller.call(port,url + "/stacks",args=data)
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
