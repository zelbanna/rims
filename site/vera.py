"""Module docstring.

HTML5 Ajax Vera Z-wave controller module

"""
__author__= "Zacharias El Banna"
__version__ = "1.0GA"
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
  print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL=zdcp.cgi?vera_scene_info&node=vera&scene=%s>%s</A></DIV>"%(id,name)
  print "<DIV CLASS=td><DIV CLASS=controls ID=scene_%s>"%id
  print "<A CLASS='z-op btn mobile' DIV='scene_{0}' URL='zdcp.cgi?vera_scene_state&node=vera&scene={0}&op={1}'><IMG SRC='images/btn-{2}.png' /></A>".format(id,"run" if scen['active'] == 0 else "off",'start' if scen['active'] == 0 else 'stop')
  print "</DIV></DIV></DIV>"
 print "</DIV></DIV></ARTICLE>"
 print "</MAIN>"

########################################## Vera Operations ##########################################
#
#
def manage(aWeb):
 if aWeb['node']:
  args = {'node':aWeb['node']}
 elif aWeb['id']:
  args = {'id':aWeb['id']}
 dev = aWeb.rest_call("device_node_mapping",args)
 node = dev['node']
 ui = dev['webpage']
 print "<NAV><UL>"
 print "<LI><A CLASS=z-op DIV=div_content URL=zdcp.cgi?vera_status&node=%s>Status</A></LI>"%node
 print "<LI><A CLASS=z-op DIV=div_content URL=zdcp.cgi?vera_devices&node=%s>Devices</A></LI>"%node
 print "<LI><A CLASS=z-op DIV=div_content URL=zdcp.cgi?vera_rooms&node=%s>Rooms</A></LI>"%node
 print "<LI><A CLASS=z-op DIV=div_content URL=zdcp.cgi?vera_scenes&node=%s>Scenes</A></LI>"%node
 print "<LI><A CLASS='z-op reload' DIV=main URL='zdcp.cgi?vera_manage&node=%s'></A></LI>"%node
 print "<LI CLASS='right navinfo'><A CLASS=z-op TARGET=_blank HREF='%s'>UI</A></LI>"%(ui)
 print "<LI CLASS='right'><A CLASS=z-op DIV=div_content URL=zdcp.cgi?tools_rest_main&node=%s>REST</A></LI>"%node
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
 args = aWeb.get_args2dict()
 res = aWeb.rest_call("vera_devices&node=master",args)
 print "<SECTION CLASS=content-left ID=div_content_left>"
 print "<ARTICLE>"
 print "<DIV CLASS=table>"
 print "<DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>Type</DIV><DIV CLASS=th>Room</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for dev in res['devices']:
   print "<DIV CLASS=tr>"
   print "<DIV CLASS=td>%s</DIV>"%dev['id']
   print "<DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL=zdcp.cgi?vera_device_info&node=%s&category=%s&id=%s>%s</A></DIV>"%(aWeb['node'],dev['category'],dev['id'],dev['name'])
   print "<DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV>"%(res['categories'].get(str(dev['category'])),res['rooms'].get(str(dev['room']),'Unassigned'))
   print "</DIV>"
 print "</DIV></DIV></ARTICLE></SECTION>"
 print "<SECTION CLASS=content-right ID=div_content_right></SECTION>"

#
#
def device_info(aWeb):
 args = aWeb.get_args2dict()
 res = aWeb.rest_call("vera_device_info&node=master",args)
 print "<ARTICLE><DIV CLASS=title>Device %s</DIV>"%aWeb['id']
 if aWeb['category'] == '2':
  load  = res['urn:upnp-org:serviceId:Dimming1']['LoadLevelStatus']
  state = res['urn:upnp-org:serviceId:SwitchPower1']['Status']
  print "<FORM ID=device_state>"
  print "<INPUT TYPE=HIDDEN NAME='node' VALUE='%s'>"%(aWeb['node'])
  print "<INPUT TYPE=HIDDEN NAME='id' VALUE='%s'>"%(aWeb['id'])
  print "<INPUT TYPE=HIDDEN NAME='service' VALUE='urn:upnp-org:serviceId:Dimming1'>"
  print "<INPUT TYPE=HIDDEN NAME='category' VALUE='%s'>"%(aWeb['category'])
  print "<INPUT TYPE=RANGE MIN=0 MAX=100 VALUE='%s' CLASS='slider' NAME='value' HTML='output'><SPAN ID='output'>%s</SPAN></FORM><DIV CLASS=controls>"%(load,load)
  print "<INPUT TYPE=RADIO ID='on' NAME='state' VALUE='on' %s><LABEL FOR='on'>On</LABEL> <INPUT TYPE=RADIO ID='off' NAME='state' VALUE='off' %s><LABEL FOR='off'>Off</LABEL>"%("checked" if state == "1" else "","checked" if state == "0" else "")
  print aWeb.button('start',DIV='div_content_right', URL='zdcp.cgi?vera_device_info&op=update&variable=LoadLevelTarget', FRM='device_state')
  print "</DIV>"
  if res['op']:
   print "<DIV CLASS=table><DIV CLASS=tbody>"
   print "<DIV CLASS=tr><DIV CLASS=td>Response</DIV><DIV CLASS=td>%s</DIV></DIV>"%(res['op']['response'])
   print "<DIV CLASS=tr><DIV CLASS=td>Job</DIV><DIV CLASS=td>%s</DIV></DIV>"%(res['op'].get('job'))
   print "<DIV CLASS=tr><DIV CLASS=td>Result</DIV><DIV CLASS=td>%s</DIV></DIV>"%(res['op'].get('result'))
   print "</DIV></DIV>"
 else:
  res.pop('op',None)
  print "<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Service</DIV><DIV CLASS=th>Variable</DIV><DIV CLASS=th>Value</DIV></DIV><DIV CLASS=tbody>"
  for svc,entry in res.iteritems():
   print "<!-- %s -->"%svc
   for var,val in entry.iteritems():
    print "<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV></DIV>"%(svc.encode("utf-8"),var.encode("utf-8"),val.encode("utf-8"))
  print "</DIV></DIV>"
 print "</ARTICLE>"

#
#
def rooms(aWeb):
 res = aWeb.rest_call("vera_infra&node=master",{'node':aWeb['node']})
 print "<SECTION CLASS=content-left ID=div_content_left><ARTICLE>"
 print "<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>Section</DIV></DIV><DIV CLASS=tbody>"
 for room in res['rooms'].values():
  print "<DIV CLASS=tr><DIV CLASS=td>%s</DIV>"%room['id']
  print "<DIV CLASS=td><A CLASS=z-op DIV=div_content URL=zdcp.cgi?vera_devices&node=%s&room=%s>%s</A></DIV>"%(aWeb['node'],room['id'],room['name'])
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
  print "<DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL=zdcp.cgi?vera_scene_info&node=%s&scene=%s>%s</A></DIV>"%(aWeb['node'],id,scen['name'])
  print "<DIV CLASS=td><DIV CLASS=controls ID=scene_%s>"%id
  print aWeb.button('start' if scen['active'] == 0 else 'stop',URL='zdcp.cgi?vera_scene_state&node=%s&scene=%s&op=%s'%(aWeb['node'],id,"run" if scen['active'] == 0 else "off"),DIV='scene_%s'%id)
  print "</DIV></DIV></DIV>"
 print "</DIV></DIV></ARTICLE></SECTION>"
 print "<SECTION CLASS=content-right ID=div_content_right></SECTION>"

#
#
def scene_state(aWeb):
 res = aWeb.rest_call("vera_scene&node=master",{'node':aWeb['node'],'scene':aWeb['scene'],'op':aWeb['op']})
 print aWeb.button('stop' if aWeb['op'] == "run" else 'start',URL='zdcp.cgi?vera_scene_state&node=%s&scene=%s&op=%s'%(aWeb['node'],aWeb['scene'],"run" if aWeb['op'] == "off" else "off"),DIV='div_scene_%s'%aWeb['id'])

#
#
def scene_info(aWeb):
 args = aWeb.get_args2dict()
 res = aWeb.rest_call("vera_scene",args)
 print "<ARTICLE>"
 print "<DIV CLASS=table style='width:auto'><DIV CLASS=thead><DIV CLASS=th>Key</DIV><DIV CLASS=th>Value</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for key,value in res.iteritems():
  print "<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV></DIV>"%(key,value)
 print "</DIV></DIV></ARTICLE>"
