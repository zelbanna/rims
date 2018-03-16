"""Module docstring.

HTML5 Ajax Openstack HEAT calls module

"""
__author__= "Zacharias El Banna"
__version__ = "18.03.16"
__status__= "Production"

##################################### Heatstack ##################################
#
def list(aWeb):
 cookie = aWeb.cookie_unjar('openstack')
 token  = cookie.get('token')
 if not token:
  print "Not logged in"
  return
 res = aWeb.rest_call("openstack_call",{'token':cookie['token'],'service':'heat','call':"stacks"})
 if not res['result'] == 'OK':
  print "<ARTICLE>Error retrieving heat stacks: %s</ARTICLE>"%str(e)
  return
 data = res['data']
 print "<SECTION CLASS=content-left ID=div_content_left><ARTICLE><P>Heat Stacks</P><DIV CLASS=controls>"
 print aWeb.button('reload',DIV='div_content',URL='sdcp.cgi?call=heat_list')
 print aWeb.button('add',   DIV='div_content_right',URL='sdcp.cgi?call=heat_choose_template')
 print "</DIV>"
 print "<DIV CLASS=table>"
 print "<DIV CLASS=thead><DIV CLASS=th>Name</DIV><DIV CLASS=th STYLE='width:150px;'>Status</DIV><DIV CLASS=th STYLE='width:50px;'>&nbsp;</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for stack in data.get('stacks'):
  print "<DIV CLASS=tr>"
  print "<DIV CLASS=td>{}</DIV>".format(stack['stack_name'])
  print "<DIV CLASS=td>{}</DIV>".format(stack['stack_status'])
  print "<DIV CLASS='td controls'>"
  print aWeb.button('info',DIV='div_content_right', SPIN='true', URL='sdcp.cgi?call=heat_action&name=%s&id=%s&op=info'%(stack['stack_name'],stack['id']))
  if stack['stack_status'] == "CREATE_COMPLETE" or stack['stack_status'] == "CREATE_FAILED" or stack['stack_status'] == "DELETE_FAILED":
   print aWeb.button('delete', DIV='div_content_right', SPIN='true', URL='sdcp.cgi?call=heat_action&name=%s&id=%s&op=remove'%(stack['stack_name'],stack['id']), MSG='Are you sure?')
  print "&nbsp;</DIV></DIV>"
 print "</DIV></DIV>"
 print "</ARTICLE></SECTION>"
 print "<SECTION CLASS=content-right ID=div_content_right></SECTION>"

######################### HEAT ADD ######################
#
# Add instantiation
#
def choose_template(aWeb):
 print "<ARTICLE CLASS=info STYLE='width:auto; display:inline-block; padding:6px'>"
 print "<FORM ID=frm_heat_choose_template>"
 print "Add solution from template:<SELECT NAME=template STYLE='height:22px; width:auto;'>"
 templates = aWeb.rest_call("openstack_heat_templates")['templates']
 for tmpl in templates:
  print "<OPTION VALUE={0}>{0}</OPTION>".format(tmpl)
 print "</SELECT>"
 print "</FORM><DIV CLASS=controls>"
 print aWeb.button('document', DIV='div_os_info', URL='sdcp.cgi?call=heat_enter_parameters',   FRM='frm_heat_choose_template', TITLE='Enter parameters')
 print aWeb.button('info', DIV='div_os_info', URL='sdcp.cgi?call=heat_action&op=templateview', FRM='frm_heat_choose_template', TITLE='View Template')
 print aWeb.button('add', DIV='div_os_info', URL='sdcp.cgi?call=heat_add_template', TITLE='Add Template')
 print "</DIV><BR><DIV ID=div_os_info></DIV>"
 print "</DIV></ARTICLE>"

def enter_parameters(aWeb):
 template = aWeb['template']
 data = aWeb.rest_call("openstack_heat_content",{'template':template})['template']
 print "<FORM ID=frm_heat_template_parameters>"
 print "<INPUT TYPE=hidden NAME=template VALUE={}>".format(template)
 print "<DIV CLASS=table>"
 print "<DIV CLASS=thead><DIV CLASS=th>Parameter</DIV><DIV CLASS=th STYLE='min-width:300px'>Value</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS='td green'>Unique Name</DIV><DIV CLASS=td><INPUT TYPE=text NAME=name PLACEHOLDER='change-this-name'></DIV></DIV>"
 for key,value in data['parameters'].iteritems():
  print "<DIV CLASS=tr><DIV CLASS=td>{0}</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=param_{0} PLACEHOLDER={1}></DIV></DIV>".format(key,value)
 print "</DIV></DIV>"
 print "</FORM><DIV CLASS=controls>"
 print aWeb.button('next',DIV='div_content_right', URL='sdcp.cgi?call=heat_action&op=create',FRM='frm_heat_template_parameters', SPIN='true')
 print "</DIV>"

def add_template(aWeb):
 print "<FORM ID=frm_heat_template_parameters>"
 print "<DIV CLASS=table><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Name:</DIV><DIV CLASS=td><INPUT CLASS='border white' TYPE=TEXT NAME=os_name REQUIRED></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td>Template:</DIV><DIV CLASS=td><TEXTAREA STYLE='width:100%; height:100px;' NAME=os_template></TEXTAREA></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td>Parameters:</DIV><DIV CLASS=td><TEXTAREA STYLE='width:100%; height:100px;' NAME=os_parameters></TEXTAREA></DIV></DIV>"
 print "</DIV></DIV>"
 print "</FORM><DIV CLASS=controls>"
 print aWeb.button('start',DIV='div_content_right', URL='sdcp.cgi?call=heat_action&op=add_template',FRM='frm_heat_template_parameters', SPIN='true')
 print "</DIV>"
#
# Heat Actions
#
def action(aWeb):
 from ..site.openstack import dict2html
 from json import dumps
 cookie = aWeb.cookie_unjar('openstack')
 token  = cookie.get('token')
 if not token:
  print "Not logged in"
  return
 args = {'token':cookie['token'],'service':'heat'}
 name = aWeb['name']
 id   = aWeb['id']
 op   = aWeb.get('op','info')

 if   op == 'info':
  tmpl = "<BUTTON CLASS='z-op' TITLE='{}' DIV=div_os_info URL=sdcp.cgi?call=heat_action&name=%s&id=%s&op={} SPIN=true>{}</BUTTON>"%(name,id)
  print "<DIV>"
  print tmpl.format('Stack Details','details','Stack Details')
  print tmpl.format('Stack Parameters','events','Events')
  print tmpl.format('Stack Template','template','Template')
  print tmpl.format('Stack Parameters','parameters','Parameters')
  print "</DIV>"
  print "<ARTICLE STYLE='overflow:auto;' ID=div_os_info>"
  args['call'] = "stacks/{}/{}".format(name,id)
  data = aWeb.rest_call("openstack_call",args)['data']
  dict2html(data['stack'],name)
  print "</ARTICLE>"

 elif op == 'details':
  args['call'] = "stacks/{}/{}".format(name,id)
  data = aWeb.rest_call("openstack_call",args)['data']
  dict2html(data['stack'],name)

 elif op == 'events':
  args['call'] = "stacks/{}/{}/events".format(name,id)
  data = aWeb.rest_call("openstack_call",args)['data']
  print "<!-- {} -->".format("stacks/{}/{}/events".format(name,id) )
  print "<DIV CLASS=table>"
  print "<DIV CLASS=thead><DIV CLASS=th>Time</DIV><DIV CLASS=th>Resource</DIV><DIV CLASS=th>Id</DIV><DIV CLASS=th>Status</DIV><DIV CLASS=th>Reason</DIV></DIV>"
  print "<DIV CLASS=tbody>"
  for event in data['events']:
   print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV></DIV>".format(event['event_time'].replace("T"," "),event['resource_name'],event['physical_resource_id'],event['resource_status'],event['resource_status_reason'])
  print "</DIV></DIV>"

 elif op == 'template':
  args['call'] = "stacks/{}/{}/template".format(name,id)
  data = aWeb.rest_call("openstack_call",args)['data']
  print "<PRE>%s</PREE>"%(dumps(data, indent=4))

 elif op == 'parameters':
  args['call'] = "stacks/{}/{}".format(name,id)
  data = aWeb.rest_call("openstack_call",args)['data']['stack']['parameters']
  data.pop('OS::project_id')
  data.pop('OS::stack_name')
  data.pop('OS::stack_id')
  print "<PRE>%s</PRE>"%(dumps(data, indent=4))

 elif op == 'create':
  print "<ARTICLE>"
  if name and aWeb['template']:
   args['name'] = name
   args['template'] = aWeb['template']
   args['parameters'] = {}
   params  = aWeb.get_args2dict(['op','call','template','name'])
   for key,value in params.iteritems():
    args['parameters'][key[6:]] = value
   ret = aWeb.rest_call("openstack_heat_instantiate",args)
   if ret['code'] == 201:
    print "<H2>Starting instantiation of '{}' solution</H2>".format(aWeb['template'].partition('.')[0])
    print "Name: {}<BR>Id:{}".format(name,ret['data']['stack']['id'])
   else:
    print "<PRE>Error instantiating stack:" + str(ret) + "</PRE>"
  else:
   print "Error - need to provide a name for the instantiation"
  print "</ARTICLE>"

 elif op == 'remove':
  args['call'] = "stacks/{}/{}".format(name,id)
  args['method'] = 'DELETE'
  ret = aWeb.rest_call("openstack_call",args)
  print "<ARTICLE><P>Removing {}</P>".format(name)
  print "Removing stack" if ret['code'] == 204 else "Error code: %s"%ret['code']
  print "</ARTICLE>"

 elif op == 'templateview':
  template = aWeb['template']
  data = aWeb.rest_call("openstack_heat_content",{'template':template})['template']
  data['stack_name'] = name if name else "Need_to_specify_name"
  print "<PRE>{}</PRE>".format(dumps(data, indent=4, sort_keys=True))

 elif op == 'add_template':
  res = aWeb.rest_call("openstack_heat_create_template",aWeb.get_args2dict(['call','op']))
  print res
