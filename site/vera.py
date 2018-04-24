"""Module docstring.

HTML5 Ajax Vera Z-wave controller calls module

"""
__author__= "Zacharias El Banna"
__version__ = "18.04.07GA"
__status__ = "Production"

##### ToDo #####
#
# - list categories in vera inventory
# - dimmable switch object in vera
# - use nodes :-)

#
#
def portal(aWeb):
 aWeb.put_html('Vera','lights')
 res = aWeb.rest_call("vera_infra&node=master",{'node':'vera'})
 print "<MAIN STYLE='top:0px;' ID=main>"
 print "<ARTICLE CLASS='mobile'>"
 print "<DIV CLASS=table><DIV CLASS=tbody>"
 for scen in res['scenes'].values():
  id = scen['id']
  name = scen['name'].replace('_',' ')
  print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL=sdcp.cgi?call=vera_scene_info&node=vera&scene=%s>%s</A></DIV>"%(id,name)
  print "<DIV CLASS=td><DIV CLASS=controls ID=scene_%s>"%id
  print aWeb.button('start' if scen['active'] == 0 else 'stop',URL='sdcp.cgi?call=vera_scene_state&node=vera&scene=%s&op=%s'%(id,"run" if scen['active'] == 0 else "off"),DIV='scene_%s'%id)
  print "</DIV></DIV></DIV>"
 print "</DIV></DIV></ARTICLE>"
 print "</MAIN>"

########################################## Vera Operations ##########################################
#
#
def manage(aWeb):
 if aWeb['node']:
  node = aWeb['node']
 elif aWeb['id']:
  node = aWeb.rest_call("device_to_node",{'id':aWeb['id']})['node']
 ui = aWeb.rest_call("vera_node_to_ui",{'node':node}).get('ui','#')
 print "<NAV><UL>"
 print "<LI><A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=vera_status&node=%s>Status</A></LI>"%node
 print "<LI><A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=vera_devices&node=%s>Devices</A></LI>"%node
 print "<LI><A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=vera_rooms&node=%s>Rooms</A></LI>"%node
 print "<LI><A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=vera_scenes&node=%s>Scenes</A></LI>"%node
 print "<LI><A CLASS='z-op reload' DIV=main URL='sdcp.cgi?call=vera_manage&node=%s'></A></LI>"%node
 print "<LI CLASS='right navinfo'><A CLASS=z-op TARGET=_blank HREF='%s'>UI</A></LI>"%(ui)
 print "<LI CLASS='right'><A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=tools_rest_main&node=%s>REST</A></LI>"%node
 print "</UL></NAV>"
 print "<SECTION CLASS=content ID=div_content></SECTION>"

#
#
def status(aWeb):
 res = aWeb.rest_call("vera_status&node=master",{'node':aWeb['node']})
 print "<ARTICLE>"
 print "<DIV CLASS=table style='width:auto'><DIV CLASS=thead><DIV CLASS=th>Key</DIV><DIV CLASS=th>Value</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for key,value in res.iteritems():
  print "<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV></DIV>"%(key,value)
 print "</DIV></DIV></ARTICLE>"

#
#
def devices(aWeb):
 args = aWeb.get_args2dict(['call'])
 res = aWeb.rest_call("vera_devices&node=master",args)
 print "<SECTION CLASS=content-left ID=div_content_left>"
 print "<ARTICLE>"
 print "<DIV CLASS=table>"
 print "<DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>Type</DIV><DIV CLASS=th>Room</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for dev in res['devices']:
   print "<DIV CLASS=tr>"
   print "<DIV CLASS=td>%s</DIV>"%dev['id']
   print "<DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL=sdcp.cgi?call=vera_device_info&node=%s&id=%s>%s</A></DIV>"%(aWeb['node'],dev['id'],dev['name'])
   print "<DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV>"%(res['categories'].get(str(dev['category'])),res['rooms'].get(str(dev['room']),'Unassigned'))
   print "</DIV>"
 print "</DIV></DIV></ARTICLE></SECTION>"
 print "<SECTION CLASS=content-right ID=div_content_right></SECTION>"

#
#
def device_info(aWeb):
 res = aWeb.rest_call("vera_device_info&node=master",{'node':aWeb['node'],'device':aWeb['id']})
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
 res = aWeb.rest_call("vera_infra&node=master",{'node':aWeb['node']})
 print "<SECTION CLASS=content-left ID=div_content_left><ARTICLE>"
 print "<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>Section</DIV></DIV><DIV CLASS=tbody>"
 for room in res['rooms'].values():
  print "<DIV CLASS=tr><DIV CLASS=td>%s</DIV>"%room['id']
  print "<DIV CLASS=td><A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=vera_devices&node=%s&room=%s>%s</A></DIV>"%(aWeb['node'],room['id'],room['name'])
  print "<DIV CLASS=td>%s</DIV></DIV>"%(res['sections'][str(room['section'])])
 print "</DIV></DIV></ARTICLE></SECTION>"
 print "<SECTION CLASS=content-right ID=div_content_right></SECTION>"

#
#
def scenes(aWeb):
 res = aWeb.rest_call("vera_infra&node=master",{'node':aWeb['node']})
 print "<SECTION CLASS=content-left ID=div_content_left>"
 print "<ARTICLE>"
 print "<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>&nbsp;</DIV></DIV><DIV CLASS=tbody>"
 for scen in res['scenes'].values():
  id = scen['id']
  print "<DIV CLASS=tr><DIV CLASS=td>%s</DIV>"%id
  print "<DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL=sdcp.cgi?call=vera_scene_info&node=%s&scene=%s>%s</A></DIV>"%(aWeb['node'],id,scen['name'])
  print "<DIV CLASS=td><DIV CLASS=controls ID=scene_%s>"%id
  print aWeb.button('start' if scen['active'] == 0 else 'stop',URL='sdcp.cgi?call=vera_scene_state&node=%s&scene=%s&op=%s'%(aWeb['node'],id,"run" if scen['active'] == 0 else "off"),DIV='scene_%s'%id)
  print "</DIV></DIV></DIV>"
 print "</DIV></DIV></ARTICLE></SECTION>"
 print "<SECTION CLASS=content-right ID=div_content_right></SECTION>"

#
#
def scene_state(aWeb):
 res = aWeb.rest_call("vera_scene&node=master",{'node':aWeb['node'],'scene':aWeb['scene'],'op':aWeb['op']})
 print aWeb.button('stop' if aWeb['op'] == "run" else 'start',URL='sdcp.cgi?call=vera_scene_state&node=%s&scene=%s&op=%s'%(aWeb['node'],aWeb['scene'],"run" if aWeb['op'] == "off" else "off"),DIV='div_scene_%s'%aWeb['id'])

#
#
def scene_info(aWeb):
 pass
