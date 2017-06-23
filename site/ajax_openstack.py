"""Module docstring.

Ajax Openstack Generic calls module

- left and right divs frames (div_os_left/right) needs to be created by ajax call
"""
__author__= "Zacharias El Banna"
__version__ = "17.6.1GA"
__status__= "Production"


############################### Openstack #############################
#
from sdcp.devices.openstack import OpenstackRPC
import sdcp.SettingsContainer as SC

def debug(aWeb):
 print "<DIV CLASS='z-table'><FORM ID=frm_os_debug>"
 print "<H3>OpenStack REST API inspection</H3>"
 print "Choose Service: <SELECT CLASS='z-select' style='width:auto; height:22px;' NAME=os_service>"
 for service in ['contrail','heat','nova','neutron']:
  print "<OPTION VALUE={0}>{0}</OPTION>".format(service)
 print "</SELECT> and API Call: <INPUT style='width:528px;' TYPE=TEXT NAME=os_call><BR>"
 print "Or enter HREF: <DIV ID=div_href style='display:inline-block;'><INPUT style='width:700px;' TYPE=TEXT NAME=os_href></DIV><BR>"
 print "Call 'Method': <SELECT CLASS='z-select' style='width:auto; height:22px;' NAME=os_method>"
 for method in ['GET','POST','DELETE','PUT']:
  print "<OPTION VALUE={0}>{0}</OPTION>".format(method)
 print "</SELECT>"
 print "<A CLASS='z-btn z-small-btn z-op' DIV=div_os_info URL=ajax.cgi?call=openstack_rest FRM=frm_os_debug TITLE='Go'><IMG SRC=images/btn-start.png></A>"
 print "<A CLASS='z-btn z-small-btn z-op' DIV=div_os_info OP=empty TITLE='Clear results view'><IMG SRC=images/btn-remove.png></A><BR>"
 print "Arguments/Body"
 print "<TEXTAREA style='width:100%; height:100px;' NAME=os_args></TEXTAREA>"
 print "</FORM>"
 print "<DIV ID=div_os_info></DIV>"
 print "</DIV>"

def rest(aWeb):
 if not aWeb.get_value('os_call') and not aWeb.get_value('os_href'):
  return
 from json import dumps,loads
 cookie = aWeb.get_cookie()
 token  = cookie.get('os_user_token')
 if not token:
  print "Not logged in"
  return
 controller = OpenstackRPC(cookie.get('os_controller'),token)
 data = None if not aWeb.get_value('os_args') else loads(aWeb.get_value('os_args'))
 ret = {} 
 if aWeb.get_value('os_href'):
  ret = controller.href(aWeb.get_value('os_href'), args = data, method=aWeb.get_value('os_method'))
 else:
  service = aWeb.get_value('os_service')
  if service == 'contrail':
   port = "8082"
   url = ""
  else:
   port = cookie.get("os_{}_port".format(service))
   url  = cookie.get("os_{}_url".format(service))
  ret = controller.call(port,url + aWeb.get_value('os_call'), args = data, method=aWeb.get_value('os_method'))
 print "<TABLE style=' width:100%;'>"
 print "<TR><TD style='width:100px'>Result</TD><TD>{}</TD></TR>".format(ret['result'])
 print "<TR><TD style='width:100px'>HTTP Code</TD><TD>{}</TD></TR>".format(ret['code'])
 print "<TR><TD style='width:100px'>Header</TD><TD>"
 for key,value in ret['header'].iteritems():
  print "{}:{}<BR>".format(key,value)
 print "</TD></TR>"
 print "</TABLE>"
 print "<DIV style='border:solid 1px black; background:#FFFFFF'>"
 print "<PRE>{}</PRE>".format(dumps(ret['data'],indent=4, sort_keys=True))
 print "</DIV>"
