"""Module docstring.

HTML5 Ajax Vera Z-wave controller calls module

"""
__author__= "Zacharias El Banna"
__version__ = "18.02.09GA"
__status__ = "Production"

##### ToDo #####
#
# - list categories in vera inventory
# - dimmable switch object in vera
# - use nodes :-)


########################################## Vera Operations ##########################################
#
#
def manage(aWeb):
 host = aWeb['ip'] if aWeb['ip'] else aWeb.rest_call("device_basics",{'id':aWeb['id']})['ip']
 print "<NAV><UL>"
 print "<LI><A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=vera_status&host=%s>Status</A></LI>"%host
 print "<LI><A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=vera_devices&host=%s>Devices</A></LI>"%host
 print "<LI><A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=vera_rooms&host=%s>Rooms</A></LI>"%host
 print "<LI><A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=vera_scenes&host=%s>Scenes</A></LI>"%host
 print "<LI><A CLASS='z-op reload' DIV=main URL='sdcp.cgi?%s'></A></LI>"%(aWeb.get_args())
 print "<LI CLASS='right navinfo'><A CLASS=z-op TARGET=_blank HREF='http://%s/cmh/'>UI</A></LI>"%(host)
 print "<LI CLASS='right'><A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=vera_rest_main&host=%s>REST</A></LI>"%host
 print "</UL></NAV>"
 print "<SECTION CLASS=content ID=div_content></SECTION>"

#
#
def rest_main(aWeb):
 print "<ARTICLE><P>REST API inspection</P>"
 print "<FORM ID=frm_rest><INPUT TYPE=hidden NAME=host VALUE='%s'>"%aWeb['host']
 print "Enter API: <INPUT CLASS='white' STYLE='width:500px;' TYPE=TEXT NAME=api><BR>"
 print "Call 'Method': <SELECT STYLE='width:70px; height:22px;' NAME=method>"
 for method in ['GET','POST','DELETE','PUT']:
  print "<OPTION VALUE={0}>{0}</OPTION>".format(method)
 print "</SELECT>"
 print "<BR>Arguments/Body<BR><TEXTAREA STYLE='width:100%; height:70px;' NAME=args></TEXTAREA>"
 print "</FORM><DIV CLASS=controls>"
 print aWeb.button('start',  DIV='div_rest_info', URL='sdcp.cgi?call=vera_rest_execute', FRM='frm_rest')
 print aWeb.button('delete', DIV='div_rest_info', OP='empty', TITLE='Clear results view')
 print "</DIV></ARTICLE>"
 print "<DIV ID=div_rest_info></DIV>"

#
#
def rest_execute(aWeb):
 from json import loads,dumps
 parameters = aWeb.get_args2dict(['call'])
 try:    parameters['args'] = loads(aWeb['args'])
 except: parameters['args'] = None
 res = aWeb.rest_call("vera_rest",parameters)
 data = res.pop('data',None)
 print "<ARTICLE STYLE='width:auto'>"
 print "<DIV CLASS='border'>"    
 print "<!-- %s -->"%(res.keys())  
 print "<DIV CLASS=table STYLE='table-layout:fixed; width:100%; '><DIV CLASS=tbody>"
 for key,value in res.iteritems():
  print "<DIV CLASS=tr><DIV CLASS=td STYLE='width:100px'>{}</DIV><DIV CLASS=td STYLE='white-space:normal'>{}</DIV></DIV>".format(key.upper(),value)                 
 print "</DIV></DIV>" 
 print "<PRE CLASS='white'>%s</PRE>"%dumps(data,indent=4, sort_keys=True)
 print "</DIV></ARTICLE>"

#
#
def status(aWeb):
 res = aWeb.rest_call("vera_status",{'host':aWeb['host']})
 print "<ARTICLE>"
 print "<DIV CLASS=table style='width:auto'><DIV CLASS=thead><DIV CLASS=th>Key</DIV><DIV CLASS=th>Value</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for key,value in res.iteritems():
  print "<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV></DIV>"%(key,value)
 print "</DIV></DIV></ARTICLE>"

#
#
def devices(aWeb):
 res = aWeb.rest_call("vera_devices",{'host':aWeb['host']})
 print "<SECTION CLASS=content-left ID=div_content_left>"
 print "<ARTICLE>"
 print "<DIV CLASS=table>"
 print "<DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>Type</DIV><DIV CLASS=th>Room</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for dev in res['devices']:
   print "<DIV CLASS=tr>"
   print "<DIV CLASS=td>%s</DIV>"%dev['id']
   print "<DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL=sdcp.cgi?call=vera_device_info&host=%s&id=%s>%s</A></DIV>"%(aWeb['host'],dev['id'],dev['name'])
   print "<DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV>"%(res['categories'].get(dev['category']),res['rooms'].get(dev['room'],'Unassigned'))
   print "</DIV>"
 print "</DIV></DIV></ARTICLE></SECTION>"
 print "<SECTION CLASS=content-right ID=div_content_right></SECTION>"

#
#
def device_info(aWeb):
 res = aWeb.rest_call("vera_device_info",{'host':aWeb['host'],'device':aWeb['id']})
 print "<ARTICLE>"
 print "<DIV CLASS=title>Device %s</DIV>"%aWeb['id']
 print "<DIV CLASS=table>"
 print "<DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Variable</DIV><DIV CLASS=th>Service</DIV><DIV CLASS=th>Value</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for row in res['states']:
  print "<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV></DIV>"%(row['id'],row['variable'],row['service'],row['value'])
 print "</DIV></DIV></ARTICLE>"

#
#
def rooms(aWeb):
 res = aWeb.rest_call("vera_infra",{'host':aWeb['host']})
 print "<SECTION CLASS=content-left ID=div_content_left>"
 print "<ARTICLE>"
 print "<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>Section</DIV></DIV><DIV CLASS=tbody>"
 for room in res['rooms'].values():
  print "<DIV CLASS=tr><DIV CLASS=td>%s</DIV>"%room['id']
  print "<DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL=sdcp.cgi?call=vera_room_info&host=%s&id=%s>%s</A></DIV>"%(aWeb['host'],room['id'],room['name'])
  print "<DIV CLASS=td>%s</DIV></DIV>"%(res['sections'][str(room['section'])])
 print "</DIV></DIV></ARTICLE></SECTION>"
 print "<SECTION CLASS=content-right ID=div_content_right></SECTION>"

#
#
def scenes(aWeb):
 res = aWeb.rest_call("vera_infra",{'host':aWeb['host']})
 print "<SECTION CLASS=content-left ID=div_content_left>"
 print "<ARTICLE>"
 print "<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>&nbsp;</DIV></DIV><DIV CLASS=tbody>"
 for scen in res['scenes'].values():
  id = scen['id']
  print "<DIV CLASS=tr><DIV CLASS=td>%s</DIV>"%id
  print "<DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL=sdcp.cgi?call=vera_scene_info&host=%s&scene=%s>%s</A></DIV>"%(aWeb['host'],id,scen['name'])
  print "<DIV CLASS=td ID=div_scene_%s>"%id
  print aWeb.button('start' if scen['active'] == 0 else 'shutdown',URL='sdcp.cgi?call=vera_scene_state&host=%s&scene=%s&op=%s'%(aWeb['host'],id,"run" if scen['active'] == 0 else "off"),DIV='div_scene_%s'%id)
  print "</DIV></DIV>"
 print "</DIV></DIV></ARTICLE></SECTION>"
 print "<SECTION CLASS=content-right ID=div_content_right></SECTION>"

def scene_state(aWeb):
 res = aWeb.rest_call("vera_scene",{'host':aWeb['host'],'scene':aWeb['scene'],'op':aWeb['op']})
 print "<!-- %s -->"%str(res)
 print aWeb.button('shutdown' if aWeb['op'] == "run" else 'start',URL='sdcp.cgi?call=vera_scene_state&host=%s&scene=%s&op=%s'%(aWeb['host'],aWeb['scene'],"run" if aWeb['op'] == "off" else "off"),DIV='div_scene_%s'%aWeb['id'])
