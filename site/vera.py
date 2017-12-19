"""Module docstring.

HTML5 Ajax Vera Z-wave controller calls module

"""
__author__= "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__ = "Production"

########################################## ESXi Operations ##########################################
#
#
#
def inventory(aWeb):
 from sdcp.rest.device import info as rest_info
 id = aWeb['id']
 data = rest_info({'id':id})
 print "<NAV><UL>"
 print "<LI CLASS=warning><A CLASS=z-op DIV=div_content MSG='Really shut down?' URL='sdcp.cgi?call=vera_op&nstate=poweroff&ip=%s'>Shutdown</A></LI>"%(id)
 print "<LI><A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=vera_status&ip=%s>Status</A></LI>"%(data['ip'])
 print "<LI><A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=vera_devices&ip=%s>Devices</A></LI>"%(data['ip'])
 print "<LI><A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=vera_rooms&ip=%s>Rooms</A></LI>"%(data['ip'])
 print "<LI><A CLASS='z-op reload' DIV=main URL='sdcp.cgi?%s'></A></LI>"%(aWeb.get_args())
 print "<LI CLASS='right navinfo'><A>%s</A></LI>"%data['info']['hostname']
 print "<LI CLASS='right'><A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=vera_rest_main&ip=%s>REST</A></LI>"%data['ip']

 print "</UL></NAV>"
 print "<SECTION CLASS=content ID=div_content></SECTION>"

#
#
def rest_main(aWeb):
 print "<ARTICLE><P>REST API inspection</P>"
 print "<FORM ID=frm_vera_rest><INPUT TYPE=hidden NAME=vera_host VALUE='%s'>"%aWeb['ip']
 print "Enter API: <INPUT CLASS='white' STYLE='width:500px;' TYPE=TEXT NAME=vera_api><BR>"
 print "Call 'Method': <SELECT STYLE='width:70px; height:22px;' NAME=vera_method>"
 for method in ['GET','POST','DELETE','PUT']:
  print "<OPTION VALUE={0}>{0}</OPTION>".format(method)
 print "</SELECT>"
 print aWeb.button('start',  DIV='div_rest_info', URL='sdcp.cgi?call=vera_rest_execute', FRM='frm_vera_rest')
 print aWeb.button('remove', DIV='div_rest_info', OP='empty', TITLE='Clear results view')
 print "<BR>Arguments/Body<BR><TEXTAREA STYLE='width:100%; height:100px;' NAME=vera_args></TEXTAREA>"
 print "</FORM>"
 print "</ARTICLE>"
 print "<DIV ID=div_rest_info></DIV>"

#
#
def rest_execute(aWeb):
 from sdcp.devices.vera import Device
 from json import loads,dumps
 try:    arguments = loads(aWeb['vera_args'])
 except: arguments = None
 ctrl = Device(aWeb['vera_host'])
 print "<ARTICLE>"
 try:
  ret = ctrl.call(3480,aWeb['vera_api'],arguments,aWeb['vera_method'])
  print "<DIV CLASS='border'><!-- %s -->"%(ret.keys())
  print "<DIV CLASS=table style='width:auto'><DIV CLASS=tbody>"
  print "<DIV CLASS=tr><DIV CLASS=td>Code</DIV><DIV CLASS=td>%s</DIV></DIV>"%(ret['code'])
  print "<DIV CLASS=tr><DIV CLASS=td>Result</DIV><DIV CLASS=td>%s</DIV></DIV>"%(ret['result'])
  print "<DIV CLASS=tr><DIV CLASS=td>Header</DIV><DIV CLASS=td>%s</DIV></DIV>"%(ret['header'])
  print "</DIV></DIV>"
  print "<PRE CLASS='white'>%s</PRE>"%dumps(ret['data'],indent=4, sort_keys=True)
  print "</DIV>"
 except Exception,e:
  print "<DIV CLASS='border'><PRE>%s</PRE></DIV>"%str(e)
 print "</ARTICLE>"

#
#
def status(aWeb):
 from sdcp.devices.vera import Device
 ctrl = Device(aWeb['ip'])
 data = ctrl.call(3480,"id=sdata")['data']
 print "<ARTICLE>"
 print "<DIV CLASS=table style='width:auto'><DIV CLASS=thead><DIV CLASS=th>Key</DIV><DIV CLASS=th>Value</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for key,value in res['data'].iteritems():
  print "<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV></DIV>"%(key,value)
 print "</DIV></DIV></ARTICLE>"

#
#
def devices(aWeb):
 from sdcp.devices.vera import Device
 ip   = aWeb.get('ip')
 ctrl = Device(ip)
 res  = ctrl.call(3480,"id=sdata")
 devs = res['data']['devices']
 cats = { data['id']: data['name'] for data in res['data']['categories'] }
 rooms= { data['id']: data['name'] for data in res['data']['rooms'] }
 print "<SECTION CLASS=content-left ID=div_content_left>"
 print "<ARTICLE>"
 print "<DIV CLASS=table>"
 print "<DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>Type</DIV><DIV CLASS=th>Room</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for dev in devs:
   print "<DIV CLASS=tr><!-- %s -->"%(dev.keys())
   print "<DIV CLASS=td>%s</DIV>"%dev['id']
   print "<DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL=sdcp.cgi?call=vera_device_info&ip=%s&id=%s>%s</A></DIV>"%(ip,dev['id'],dev['name'])
   print "<DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV>"%(cats.get(dev['category']),rooms.get(dev['room'],'Unassigned'))
   print "</DIV>"
 print "</DIV></DIV></ARTICLE></SECTION>"
 print "<SECTION CLASS=content-right ID=div_content_right></SECTION>"

def device_info(aWeb):
 from sdcp.devices.vera import Device
 from json import dumps
 ip   = aWeb.get('ip')
 ctrl = Device(ip)
 res  = ctrl.call(3480,"id=status&DeviceNum=%s"%aWeb['id'])
 print "<ARTICLE>"
 print "<PRE>%s</PRE>"%(dumps(res['data'],indent=4))
 print "</ARTICLE>"


#
#
def rooms(aWeb):
 from sdcp.devices.vera import Device
 ip   = aWeb.get('ip')
 ctrl = Device(ip)
 res  = ctrl.call(3480,"id=sdata")
 print "<SECTION CLASS=content-left ID=div_content_left>"
 print "<ARTICLE>"
 print "<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>Section</DIV></DIV><DIV CLASS=tbody>"
 for room in res['data']['rooms']:
   print "<DIV CLASS=tr><DIV CLASS=td>%s</DIV>"%room['id']
   print "<DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL=sdcp.cgi?call=vera_room_info&ip=%s&id=%s>%s</A></DIV>"%(ip,room['id'],room['name'])
   print "<DIV CLASS=td>%s</DIV></DIV>"%(room['section'])
 print "</DIV></DIV></ARTICLE></SECTION>"
 print "<SECTION CLASS=content-right ID=div_content_right></SECTION>"
