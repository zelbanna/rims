"""Module docstring.

HTML5 Ajax Openstack HEAT module

"""
__author__= "Zacharias El Banna"
__version__ = "5.0GA"
__status__= "Production"

##################################### Heatstack ##################################
#
def list(aWeb):
 cookie = aWeb.cookie('openstack')
 token  = cookie.get('token')
 if not token:
  aWeb.wr("Not logged in")
  return
 res = aWeb.rest_call("openstack_call",{'token':cookie['token'],'service':'heat','call':"stacks"})
 if not res['result'] == 'OK':
  aWeb.wr("<ARTICLE>Error retrieving heat stacks: %s</ARTICLE>"%str(e))
  return
 data = res['data']
 aWeb.wr("<SECTION CLASS=content-left ID=div_content_left><ARTICLE><P>Heat Stacks</P>")
 aWeb.wr(aWeb.button('reload',DIV='div_content',URL='heat_list'))
 aWeb.wr(aWeb.button('add',   DIV='div_content_right',URL='heat_choose_template'))
 aWeb.wr("<DIV CLASS=table>")
 aWeb.wr("<DIV CLASS=thead><DIV CLASS=th>Name</DIV><DIV CLASS=th STYLE='width:150px;'>Status</DIV><DIV CLASS=th STYLE='width:50px;'>&nbsp;</DIV></DIV>")
 aWeb.wr("<DIV CLASS=tbody>")
 for stack in data.get('stacks'):
  aWeb.wr("<DIV CLASS=tr>")
  aWeb.wr("<DIV CLASS=td>{}</DIV>".format(stack['stack_name']))
  aWeb.wr("<DIV CLASS=td>{}</DIV>".format(stack['stack_status']))
  aWeb.wr("<DIV CLASS=td>")
  aWeb.wr(aWeb.button('info',DIV='div_content_right', SPIN='true', URL='heat_action?name=%s&id=%s&op=info'%(stack['stack_name'],stack['id'])))
  if stack['stack_status'] == "CREATE_COMPLETE" or stack['stack_status'] == "CREATE_FAILED" or stack['stack_status'] == "DELETE_FAILED":
   aWeb.wr(aWeb.button('delete', DIV='div_content_right', SPIN='true', URL='heat_action?name=%s&id=%s&op=remove'%(stack['stack_name'],stack['id']), MSG='Are you sure?'))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</ARTICLE></SECTION>")
 aWeb.wr("<SECTION CLASS=content-right ID=div_content_right></SECTION>")

######################### HEAT ADD ######################
#
# Add instantiation
#
def choose_template(aWeb):
 cookie = aWeb.cookie('openstack')
 token  = cookie.get('token')
 templates = aWeb.rest_call("openstack_heat_templates",{'token':token})['templates']
 aWeb.wr("<ARTICLE CLASS=info STYLE='width:auto; display:inline-block; padding:6px'>")
 aWeb.wr("<FORM ID=frm_heat_choose_template>")
 aWeb.wr("Add solution from template:<SELECT NAME=template STYLE='height:22px; width:auto;'>")
 for tmpl in templates:
  aWeb.wr("<OPTION VALUE={0}>{0}</OPTION>".format(tmpl))
 aWeb.wr("</SELECT>")
 aWeb.wr("</FORM>")
 aWeb.wr(aWeb.button('document', DIV='div_os_info', URL='heat_enter_parameters',   FRM='frm_heat_choose_template', TITLE='Enter parameters'))
 aWeb.wr(aWeb.button('info', DIV='div_os_info', URL='heat_action?op=templateview', FRM='frm_heat_choose_template', TITLE='View Template'))
 aWeb.wr(aWeb.button('add', DIV='div_os_info', URL='heat_add_template', TITLE='Add a new template'))
 aWeb.wr("<BR><DIV ID=div_os_info></DIV>")
 aWeb.wr("</DIV></ARTICLE>")

def enter_parameters(aWeb):
 cookie = aWeb.cookie('openstack')
 token  = cookie.get('token')
 template = aWeb['template']
 data = aWeb.rest_call("openstack_heat_content",{'template':template,'token':token})['template']
 aWeb.wr("<FORM ID=frm_heat_template_parameters>")
 aWeb.wr("<INPUT TYPE=hidden NAME=template VALUE={}>".format(template))
 aWeb.wr("<DIV CLASS=table>")
 aWeb.wr("<DIV CLASS=thead><DIV CLASS=th>Parameter</DIV><DIV CLASS=th STYLE='min-width:300px'>Value</DIV></DIV>")
 aWeb.wr("<DIV CLASS=tbody>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS='td green'>Unique Name</DIV><DIV CLASS=td><INPUT TYPE=text NAME=name PLACEHOLDER='change-this-name'></DIV></DIV>")
 for key,value in data['parameters'].items():
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>{0}</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=param_{0} PLACEHOLDER={1}></DIV></DIV>".format(key,value))
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</FORM>")
 aWeb.wr(aWeb.button('forward',DIV='div_content_right', URL='heat_action?op=create',FRM='frm_heat_template_parameters', SPIN='true'))

def add_template(aWeb):
 aWeb.wr("<FORM ID=frm_heat_template_parameters>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=tbody>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Name:</DIV><DIV CLASS=td><INPUT CLASS='border white' TYPE=TEXT NAME=os_name REQUIRED></DIV></DIV>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Template:</DIV><DIV CLASS=td><TEXTAREA STYLE='width:100%; height:100px;' NAME=os_template></TEXTAREA></DIV></DIV>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Parameters:</DIV><DIV CLASS=td><TEXTAREA STYLE='width:100%; height:100px;' NAME=os_parameters></TEXTAREA></DIV></DIV>")
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</FORM>")
 aWeb.wr(aWeb.button('start',DIV='div_content_right', URL='heat_action?op=add_template',FRM='frm_heat_template_parameters', SPIN='true'))

#
# Heat Actions
#
def action(aWeb):
 from zdcp.site.openstack import dict2html
 from json import dumps
 cookie = aWeb.cookie('openstack')
 token  = cookie.get('token')
 if not token:
  aWeb.wr("Not logged in")
  return
 args = {'token':cookie['token'],'service':'heat'}
 name = aWeb['name']
 id   = aWeb['id']
 op   = aWeb.get('op','info')

 if   op == 'info':
  tmpl = "<A CLASS='z-op btn small text' TITLE='{}' DIV=div_os_info URL='heat_action?name=%s&id=%s&op={}' SPIN=true>{}</A>"%(name,id)
  aWeb.wr("<DIV>")
  aWeb.wr(tmpl.format('Stack Details','details','Stack Details'))
  aWeb.wr(tmpl.format('Stack Parameters','events','Events'))
  aWeb.wr(tmpl.format('Stack Template','template','Template'))
  aWeb.wr(tmpl.format('Stack Parameters','parameters','Parameters'))
  aWeb.wr("</DIV>")
  aWeb.wr("<ARTICLE STYLE='overflow:auto;' ID=div_os_info>")
  args['call'] = "stacks/{}/{}".format(name,id)
  data = aWeb.rest_call("openstack_call",args)['data']
  dict2html(data['stack'],name)
  aWeb.wr("</ARTICLE>")

 elif op == 'details':
  args['call'] = "stacks/{}/{}".format(name,id)
  data = aWeb.rest_call("openstack_call",args)['data']
  dict2html(data['stack'],name)

 elif op == 'events':
  args['call'] = "stacks/{}/{}/events".format(name,id)
  data = aWeb.rest_call("openstack_call",args)['data']
  aWeb.wr("<!-- {} -->".format("stacks/{}/{}/events".format(name,id) ))
  aWeb.wr("<DIV CLASS=table>")
  aWeb.wr("<DIV CLASS=thead><DIV CLASS=th>Time</DIV><DIV CLASS=th>Resource</DIV><DIV CLASS=th>Id</DIV><DIV CLASS=th>Status</DIV><DIV CLASS=th>Reason</DIV></DIV>")
  aWeb.wr("<DIV CLASS=tbody>")
  for event in data['events']:
   aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV></DIV>".format(event['event_time'].replace("T"," "),event['resource_name'],event['physical_resource_id'],event['resource_status'],event['resource_status_reason']))
  aWeb.wr("</DIV></DIV>")

 elif op == 'template':
  args['call'] = "stacks/{}/{}/template".format(name,id)
  data = aWeb.rest_call("openstack_call",args)['data']
  aWeb.wr("<PRE>%s</PREE>"%(dumps(data, indent=4)))

 elif op == 'parameters':
  args['call'] = "stacks/{}/{}".format(name,id)
  data = aWeb.rest_call("openstack_call",args)['data']['stack']['parameters']
  data.pop('OS::project_id')
  data.pop('OS::stack_name')
  data.pop('OS::stack_id')
  aWeb.wr("<PRE>%s</PRE>"%(dumps(data, indent=4)))

 elif op == 'create':
  aWeb.wr("<ARTICLE>")
  if name and aWeb['template']:
   args['name'] = name
   args['template'] = aWeb['template']
   args['parameters'] = {}
   params  = aWeb.get_args2dict(['op','template','name'])
   for key,value in params.items():
    args['parameters'][key[6:]] = value
   ret = aWeb.rest_call("openstack_heat_instantiate",args)
   if ret['code'] == 201:
    aWeb.wr("<H2>Starting instantiation of '{}' solution</H2>".format(aWeb['template'].partition('.')[0]))
    aWeb.wr("Name: {}<BR>Id:{}".format(name,ret['data']['stack']['id']))
   else:
    aWeb.wr("<PRE>Error instantiating stack:" + str(ret) + "</PRE>")
  else:
   aWeb.wr("Error - need to provide a name for the instantiation")
  aWeb.wr("</ARTICLE>")

 elif op == 'remove':
  args['call'] = "stacks/{}/{}".format(name,id)
  args['method'] = 'DELETE'
  ret = aWeb.rest_call("openstack_call",args)
  aWeb.wr("<ARTICLE><P>Removing {}</P>".format(name))
  aWeb.wr("Removing stack" if ret['code'] == 204 else "Error code: %s"%ret['code'])
  aWeb.wr("</ARTICLE>")

 elif op == 'templateview':
  cookie = aWeb.cookie('openstack')
  token  = cookie.get('token')
  template = aWeb['template']
  data = aWeb.rest_call("openstack_heat_content",{'template':template,'token':token})['template']
  data['stack_name'] = name if name else "Need_to_specify_name"
  aWeb.wr("<PRE>{}</PRE>".format(dumps(data, indent=4, sort_keys=True)))

 elif op == 'add_template':
  res = aWeb.rest_call("openstack_heat_create_template",aWeb.get_args2dict(['op']))
  aWeb.wr(res)
