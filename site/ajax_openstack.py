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
 print "Service: <SELECT CLASS='z-select' style='width:auto; height:22px;' NAME=os_service>"
 for service in ['contrail','heat','nova','neutron']:
  print "<OPTION VALUE={0}>{0}</OPTION>".format(service)
 print "</SELECT> Method: <SELECT CLASS='z-select' style='width:auto; height:22px;' NAME=os_method>"
 for method in ['GET','POST','DELETE','PUT']:
  print "<OPTION VALUE={0}>{0}</OPTION>".format(method)
 print "</SELECT> API Call: <INPUT style='width:500px;' TYPE=TEXT NAME=os_call>"
 print "<A CLASS='z-btn z-small-btn z-op' DIV=div_os_info URL=ajax.cgi?call=openstack_rest FRM=frm_os_debug><IMG SRC=images/btn-start.png></A><BR>"
 print "Arguments/Body"
 print "<TEXTAREA style='width:100%; height:100px;' NAME=os_args></TEXTAREA>"
 print "</FORM>"
 print "</DIV>"
 print "<DIV ID=div_os_info></DIV>"

def rest(aWeb):
 if not aWeb.get_value('os_call'):
  return
 cookie = aWeb.get_cookie()
 token  = cookie.get('os_user_token')
 if not token:
  print "Not logged in"
  return
 controller = OpenstackRPC(cookie.get('os_controller'),token)
 service = aWeb.get_value('os_service')
 if service == 'contrail':
  port = "8082"
  url = ""
 else:
  port = cookie.get("os_{}_port".format(service))
  url  = cookie.get("os_{}_url".format(service))

 from json import dumps,loads
 ret = controller.call(port,url + aWeb.get_value('os_call'), method=aWeb.get_value('os_method'))
 print "<DIV CLASS='z-table'>"
 print "<!-- {} -->".format(aWeb.get_value('os_args'))
 print "<TABLE style=' width:100%;'>"
 print "<TR><TD>Result</TD><TD>{}</TD></TR>".format(ret['result'])
 print "<TR><TD>Header</TD><TD>{}</TD></TR>".format(ret['header'])
 print "<TR><TD>Code</TD><TD>{}</TD></TR>".format(ret['code'])
 print "</TABLE>"
 print "<DIV style='border:solid 1px black; background:#FFFFFF'>"
 print "<PRE>{}</PRE>".format(dumps(ret['data'],indent=4, sort_keys=True))
 print "</DIV>"
 print "</DIV>"
