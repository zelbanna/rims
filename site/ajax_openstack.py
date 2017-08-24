"""Module docstring.

Ajax Openstack Generic calls module

- left and right divs frames (div_os_left/right) needs to be created by ajax call
"""
__author__= "Zacharias El Banna"
__version__ = "17.6.1GA"
__status__= "Production"

############################### Openstack #############################
#

#
# Assume div_os_info

def dict2html(aData,aTitle=None):
 print "<H2>{}</H2>".format(aTitle) if aTitle else "<!-- No title -->"
 data2html(aData)

def data2html(aData):
 if isinstance(aData,dict):
  print "<DIV CLASS=z-table2><DIV CLASS=z-tbody>"
  for k,v in aData.iteritems():
   print "<DIV CLASS=z-tr><DIV CLASS=z-td style='padding:0px;'><I>{}</I>:</DIV><DIV CLASS=z-td style='white-space:normal; overflow:auto; width:100%'>".format(k)
   if 'href' in k:
    print "<A CLASS=z-op DIV=div_os_frame URL=ajax.cgi?call=openstack_result&method=GET&os_href={0}>{0}</A>".format(v)
   else:
    data2html(v)
   print "</DIV></DIV>"
  print "</DIV></DIV>"
 elif isinstance(aData,list):
  print "<DIV CLASS=z-table2 style='width:100%;'><DIV CLASS=z-tbody>"
  for v in aData:
   print "<DIV CLASS=z-tr><DIV CLASS=z-td style='padding:0px;'>"
   data2html(v)
   print "</DIV></DIV>"
  print "</DIV>"
  print "</DIV>"
 else:
  print aData

def result(aWeb):
 if not aWeb.get_value('os_call') and not aWeb.get_value('os_href'):
  return
 from sdcp.devices.openstack import OpenstackRPC
 from json import dumps,loads
 cookie = aWeb.get_cookie()
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
 print "<DIV CLASS=z-table style='overflow:auto;'>"
 print "<TABLE style=' width:100%;'>"
 print "<TR><TD style='width:100px'>Result</TD><TD>{}</TD></TR>".format(ret['result'])
 print "<TR><TD style='width:100px'>HTTP Code</TD><TD>{}</TD></TR>".format(ret['code'])
 print "<TR><TD style='width:100px'>Header</TD><TD>"
 for key,value in ret['header'].iteritems():
  print "{}:{}<BR>".format(key,value)
 print "</TD></TR>"
 print "</TABLE>"
 print "<DIV style='border:solid 1px black; background:#FFFFFF'>"
 output = dumps(ret['data'],indent=4, sort_keys=True)
 print "<PRE style='margin:0px;'>{}</PRE>".format(output)
 print "</DIV></DIV>"

def api(aWeb):
 print "<DIV CLASS='z-table' ID=div_os_control><FORM ID=frm_os_api>"
 print "<H3>OpenStack REST API inspection</H3>"
 print "Choose Service and enter API call: <SELECT CLASS='z-select' style='width:auto; height:22px;' NAME=os_service>"
 services = ['contrail']
 services.extend(aWeb.get_cookie()['os_services'].split(','))
 for service in services:
  print "<OPTION VALUE={0}>{0}</OPTION>".format(service)
 print "</SELECT> <INPUT style='width:520px;' TYPE=TEXT NAME=os_call><BR>"
 print "Or enter HREF: <DIV ID=div_href style='display:inline-block;'><INPUT style='width:736px;' TYPE=TEXT NAME=os_href></DIV><BR>"
 print "Call 'Method': <SELECT CLASS='z-select' style='width:auto; height:22px;' NAME=os_method>"
 for method in ['GET','POST','DELETE','PUT']:
  print "<OPTION VALUE={0}>{0}</OPTION>".format(method)
 print "</SELECT>"
 print "<A CLASS='z-btn z-small-btn z-op' DIV=div_os_info URL=ajax.cgi?call=openstack_result FRM=frm_os_api TITLE='Go'><IMG SRC=images/btn-start.png></A>"
 print "<A CLASS='z-btn z-small-btn z-op' DIV=div_os_info OP=empty TITLE='Clear results view'><IMG SRC=images/btn-remove.png></A><BR>"
 print "Arguments/Body<BR>"
 print "<TEXTAREA style='width:100%; height:100px;' NAME=os_args></TEXTAREA>"
 print "</FORM>"
 print "</DIV>"
 print "<DIV ID=div_os_info></DIV>"

def fqname(aWeb):
 print "<DIV CLASS=z-table ID=div_os_control>"
 print "<FORM ID=frm_os_uuid>Contrail UUID:<INPUT style='width:500px;' TYPE=TEXT NAME=os_uuid VALUE={}></FORM>".format(aWeb.get_value('os_uuid') if aWeb.get_value('os_uuid') else "")
 print "<A CLASS='z-btn z-small-btn z-op' DIV=div_os_frame URL=ajax.cgi?call=openstack_fqname FRM=frm_os_uuid TITLE='Go'><IMG SRC=images/btn-start.png></A><BR>"
 if aWeb.get_value('os_uuid'):
  from json import dumps,loads
  cookie = aWeb.get_cookie()
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
    print "<TABLE style='width:100%;'><THEAD><TH>Type</TH><TH>Value</TH></THEAD>"
    print "<TR><TD>FQDN</TD><TD>{}</TD></TR>".format(".".join(data['fq_name']))
    print "<TR><TD>Type</TD><TD><A CLASS='z-op' DIV=div_os_info URL=ajax.cgi?call=openstack_result&os_service=contrail&os_call={0}/{1}>{0}</A></TD></TR>".format(data['type'],argument['uuid'])
    print "</TABLE><BR>"
 print "</DIV>"
 print "<DIV ID=div_os_info></DIV>"
