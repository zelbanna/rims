"""Module docstring.

Ajax Openstack Generic calls module

- left and right divs frames (div_content_left/right) needs to be created by ajax call
"""
__author__= "Zacharias El Banna"
__version__ = "17.10.4"
__status__= "Production"

############################################## Openstack ###############################################
#
#
# Openstack Portal - New "Window"/Pane
#
def portal(aWeb):
 from json import dumps
 from sdcp.devices.openstack import OpenstackRPC
 from sdcp import PackageContainer as PC
 ctrl = aWeb.cookie.get('os_controller')
 utok = aWeb.cookie.get('os_user_token')

 if not utok:
  username = aWeb.get_value('username')
  password = aWeb.get_value('password')
  project  = aWeb.get_value('project','none_none')
  (pid,pname) = project.split('_')
  openstack = OpenstackRPC(ctrl,None)
  res = openstack.auth({'project':pname, 'username':username,'password':password })
  if not res['result'] == "OK":
   aWeb.put_html("Openstack Portal")
   PC.log_msg("openstack_portal - error during login for {}@{}".format(username,ctrl))
   print "Error logging in - please try login again"
   return
  utok = openstack.get_token()
  aWeb.add_cookie('os_user_token',utok)
  aWeb.add_cookie('os_user_name',username)
  aWeb.add_cookie("os_project_id",pid)
  aWeb.add_cookie("os_project_name",pname)
  aWeb.add_cookie("os_services",",".join(['heat','nova','neutron','glance']))
  for service in ['heat','nova','neutron','glance']:
   base = "os_" + service
   port,url,id = openstack.get_service(service,'public')
   aWeb.add_cookie(base + "_port",port)
   aWeb.add_cookie(base + "_url",url)
   aWeb.add_cookie(base + "_id",id)

  PC.log_msg("openstack_portal - successful login and catalog init for {}@{}".format(username,ctrl))
 else:
  username = aWeb.cookie.get("os_user_name")
  pid      = aWeb.cookie.get("os_project_id")
  pname    = aWeb.cookie.get("os_project_name")
  PC.log_msg("openstack_portal - using existing token for {}@{}".format(username,ctrl))
  openstack = OpenstackRPC(ctrl,utok)

 aWeb.put_html("Openstack Portal")
 print "<DIV CLASS=z-content-head ID=div_content_head>"
 print "<DIV CLASS=z-content-head-info ID=div_content_head_info>"
 print "<DIV CLASS=z-table style='width:auto; display:inline; float:left; margin:5px 100px 0px 10px;'><DIV CLASS=tbody>"
 print "<DIV CLASS=tr style='background:transparent'><DIV CLASS=td><B>Identity:</B></DIV><DIV CLASS=td><I>{}</I></DIV><DIV CLASS=td>&nbsp;<B>Id:</B></DIV><DIV CLASS=td><I>{}</I></DIV></DIV>".format(pname,pid)
 print "<DIV CLASS=tr style='background:transparent'><DIV CLASS=td><B>Username:</B></DIV><DIV CLASS=td><I>{}</I></DIV><DIV CLASS=td>&nbsp;<B>Token:</B></DIV><DIV CLASS=td><I>{}</I></DIV></DIV>".format(username,utok)
 print "</DIV></DIV>"
 print "<A CLASS='z-btn z-op' OP=logout URL='sdcp.cgi?call=front_openstack&headers=no&controller={}&name={}&appformix={}' style='float:right; background-color:red!important; margin-right:20px;'>Log out</A>".format(ctrl,aWeb.cookie.get('os_demo_name'),aWeb.cookie.get('af_controller'))
 print "</DIV>"
 print "<DIV CLASS='z-navbar' style='top:60px; z-index:1001' ID=div_navbar>"
 print "<A CLASS=z-op           DIV=div_content URL='sdcp.cgi?call=heat_list'>Orchestration</A>"
 print "<A CLASS=z-op           DIV=div_content URL='sdcp.cgi?call=neutron_list'>Virtual Networks</A>"
 print "<A CLASS=z-op           DIV=div_content URL='sdcp.cgi?call=nova_list'>Virtual Machines</A>"
 print "<A CLASS=z-op SPIN=true DIV=div_content URL='sdcp.cgi?call=appformix_report'>Usage Report</A>"
 print "<A CLASS='z-reload z-op'  OP=redirect URL='sdcp.cgi?call=openstack_portal&headers=no'></A>"
 if username == 'admin':
  print "<A CLASS='z-op z-right'  DIV=div_content URL=sdcp.cgi?call=openstack_fqname>FQDN</A>"
  print "<A CLASS='z-op z-right'  DIV=div_content URL=sdcp.cgi?call=openstack_api>API Debug</A>"
 print "</DIV>"
 print "</DIV>"
 print "<DIV CLASS=z-content ID=div_content style='top:94px;'></DIV>"


############################################## Formatting ##############################################
#
# Assume div_os_info
#
def dict2html(aData,aTitle=None):
 print "<H2>{}</H2>".format(aTitle) if aTitle else "<!-- No title -->"
 data2html(aData)

def data2html(aData):
 if isinstance(aData,dict):
  print "<DIV CLASS=z-table style='width:auto'><DIV CLASS=tbody>"
  for k,v in aData.iteritems():
   print "<DIV CLASS=tr><DIV CLASS=td style='padding:0px;'><I>{}</I>:</DIV><DIV CLASS=td style='white-space:normal; overflow:auto; width:100%'>".format(k)
   if 'href' in k:
    print "<A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=openstack_result&method=GET&os_href={0}>{0}</A>".format(v)
   else:
    data2html(v)
   print "</DIV></DIV>"
  print "</DIV></DIV>"
 elif isinstance(aData,list):
  print "<DIV CLASS=z-table style='width:100%;'><DIV CLASS=tbody>"
  for v in aData:
   print "<DIV CLASS=tr><DIV CLASS=td style='padding:0px;'>"
   data2html(v)
   print "</DIV></DIV>"
  print "</DIV></DIV>"
 else:
  print aData

##################################################### Debugging #######################################################
#
#
#
def api(aWeb):
 print "<DIV CLASS=z-frame ID=div_os_control><FORM ID=frm_os_api>"
 print "<H3>OpenStack REST API inspection</H3>"
 print "Choose Service and enter API call: <SELECT style='overflow: visible; width:auto; height:22px;' NAME=os_service>"
 services = ['contrail']
 services.extend(aWeb.cookie['os_services'].split(','))
 for service in services:
  print "<OPTION VALUE={0}>{0}</OPTION>".format(service)
 print "</SELECT> <INPUT style='width:520px;' TYPE=TEXT NAME=os_call><BR>"
 print "Or enter HREF: <DIV ID=div_href style='display:inline-block;'><INPUT style='width:736px;' TYPE=TEXT NAME=os_href></DIV><BR>"
 print "Call 'Method': <SELECT style='overflow: visible; width:auto; height:22px;' NAME=os_method>"
 for method in ['GET','POST','DELETE','PUT']:
  print "<OPTION VALUE={0}>{0}</OPTION>".format(method)
 print "</SELECT>"
 print "<A CLASS='z-btn z-small-btn z-op' DIV=div_os_info URL=sdcp.cgi?call=openstack_result FRM=frm_os_api TITLE='Go'><IMG SRC=images/btn-start.png></A>"
 print "<A CLASS='z-btn z-small-btn z-op' DIV=div_os_info OP=empty TITLE='Clear results view'><IMG SRC=images/btn-remove.png></A><BR>"
 print "Arguments/Body<BR>"
 print "<TEXTAREA style='width:100%; height:100px;' NAME=os_args></TEXTAREA>"
 print "</FORM>"
 print "</DIV>"
 print "<DIV ID=div_os_info></DIV>"

#
#
#
def fqname(aWeb):
 print "<DIV CLASS=z-frame ID=div_os_control>"
 print "<FORM ID=frm_os_uuid>Contrail UUID:<INPUT style='width:500px;' TYPE=TEXT NAME=os_uuid VALUE={}></FORM>".format(aWeb.get_value('os_uuid') if aWeb.get_value('os_uuid') else "")
 print "<A CLASS='z-btn z-small-btn z-op' DIV=div_content URL=sdcp.cgi?call=openstack_fqname FRM=frm_os_uuid TITLE='Go'><IMG SRC=images/btn-start.png></A><BR>"
 if aWeb.get_value('os_uuid'):
  from json import dumps,loads
  cookie = aWeb.cookie
  token  = cookie.get('os_user_token')
  if not token:
   print "Not logged in"
  else:
   from sdcp.devices.openstack import OpenstackRPC
   controller = OpenstackRPC(cookie.get('os_controller'),token)
   argument   = {'uuid':aWeb.get_value('os_uuid')}
   ret  = controller.call("8082","id-to-fqname",args=argument,method='POST')
   data = ret['data']
   if ret['result'] == 'OK':
    print "<DIV CLASS=z-table style='width:100%;'><DIV CLASS=thead><DIV CLASS=th>Type</DIV><DIV CLASS=th>Value</DIV></DIV><DIV CLASS=tbody>"
    print "<DIV CLASS=tr><DIV CLASS=td>FQDN</DIV><DIV CLASS=td>{}</DIV></DIV>".format(".".join(data['fq_name']))
    print "<DIV CLASS=tr><DIV CLASS=td>Type</DIV><DIV CLASS=td><A CLASS='z-op' DIV=div_os_info URL=sdcp.cgi?call=openstack_result&os_service=contrail&os_call={0}/{1}>{0}</A></DIV></DIV>".format(data['type'],argument['uuid'])
    print "</DIV></DIV><BR>"
 print "</DIV>"
 print "<DIV ID=div_os_info></DIV>"

#
#
#
def result(aWeb):
 if not aWeb.get_value('os_call') and not aWeb.get_value('os_href'):
  return
 from sdcp.devices.openstack import OpenstackRPC
 from json import dumps,loads
 cookie = aWeb.cookie
 token  = cookie.get('os_user_token')
 if not token:
  print "Not logged in"
  return
 controller = OpenstackRPC(cookie.get('os_controller'),token)
 try:    arguments = loads(aWeb.get_value('os_args'))
 except: arguments = None
 ret = {} 
 if aWeb.get_value('os_href'):
  ret = controller.href(aWeb.get_value('os_href'), args = arguments, method=aWeb.get_value('os_method'))
 else:
  service = aWeb.get_value('os_service')
  if service == 'contrail':
   port,url = "8082",""
  else:
   port,url = cookie.get("os_{}_port".format(service)),cookie.get("os_{}_url".format(service))
  ret = controller.call(port,url + aWeb.get_value('os_call'), args = arguments, method=aWeb.get_value('os_method'))
 print "<DIV CLASS=z-frame style='overflow:auto;'>"
 print "<DIV CLASS=z-table style='width:100%;'>"
 print "<DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td style='width:100px'>Result</DIV><DIV CLASS=td>{}</DIV></DIV>".format(ret['result'])
 print "<DIV CLASS=tr><DIV CLASS=td style='width:100px'>HTTP Code</DIV><DIV CLASS=td>{}</DIV></DIV>".format(ret['code'])
 print "<DIV CLASS=tr><DIV CLASS=td style='width:100px'>Header</DIV><DIV CLASS=td>"
 for key,value in ret['header'].iteritems():
  print "{}:{}<BR>".format(key,value)
 print "</DIV></DIV>"
 print "</DIV></DIV>"
 print "<DIV style='border:solid 1px black; background:#FFFFFF'>"
 output = dumps(ret['data'],indent=4, sort_keys=True)
 print "<PRE style='margin:0px;'>{}</PRE>".format(output)
 print "</DIV></DIV>"
