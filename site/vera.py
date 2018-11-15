"""HTML5 Ajax Vera Z-wave controller module"""
__author__= "Zacharias El Banna"

##### ToDo #####
#
# - list categories in vera inventory
# - dimmable switch object in vera
# - use nodes :-)

#
#
def portal(aWeb):
 cookie = aWeb.cookie('rims')
 aWeb.put_html(aTitle = 'Vera', aIcon = 'lights', aTheme = cookie.get('theme'))
 res = aWeb.rest_call("vera/infra?node=master",{'node':'vera'})
 aWeb.wr("<MAIN STYLE='top:0px;' ID=main>")
 aWeb.wr("<ARTICLE CLASS='mobile'>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=tbody>")
 for scen in res['scenes'].values():
  id = scen['id']
  name = scen['name'].replace('_',' ')
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL=vera_scene_info?node=vera&scene=%s>%s</A></DIV>"%(id,name))
  aWeb.wr("<DIV CLASS=td><DIV ID=scene_%s>"%id)
  aWeb.wr("<A CLASS='z-op btn mobile' DIV='scene_{0}' URL='vera_scene_state?node=vera&scene={0}&op={1}'><IMG SRC='../images/btn-{2}.png' /></A>".format(id,"run" if scen['active'] == 0 else "off",'start' if scen['active'] == 0 else 'stop'))
  aWeb.wr("</DIV></DIV></DIV>")
 aWeb.wr("</DIV></DIV></ARTICLE>")
 aWeb.wr("</MAIN>")

########################################## Vera Operations ##########################################
#
#
def manage(aWeb):
 node = aWeb['node']
 aWeb.wr("<NAV><UL>")
 aWeb.wr("<LI><A CLASS=z-op DIV=div_content URL=vera_status?node=%s>Status</A></LI>"%node)
 aWeb.wr("<LI><A CLASS=z-op DIV=div_content URL=vera_devices?node=%s>Devices</A></LI>"%node)
 aWeb.wr("<LI><A CLASS=z-op DIV=div_content URL=vera_rooms?node=%s>Rooms</A></LI>"%node)
 aWeb.wr("<LI><A CLASS=z-op DIV=div_content URL=vera_scenes?node=%s>Scenes</A></LI>"%node)
 aWeb.wr("<LI><A CLASS='z-op reload' DIV=main URL='vera_manage?node=%s'></A></LI>"%node)
 aWeb.wr("<LI CLASS='right'><A CLASS=z-op DIV=div_content URL=tools_rest_main?node=%s>REST</A></LI>"%node)
 aWeb.wr("</UL></NAV>")
 aWeb.wr("<SECTION CLASS=content ID=div_content></SECTION>")

#
#
def status(aWeb):
 res = aWeb.rest_call("vera/status?node=master",{'node':aWeb['node']})
 aWeb.wr("<ARTICLE>")
 aWeb.wr("<DIV CLASS=table style='width:auto'><DIV CLASS=thead><DIV CLASS=th>Key</DIV><DIV CLASS=th>Value</DIV></DIV>")
 aWeb.wr("<DIV CLASS=tbody>")
 for key,value in res.items():
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV></DIV>"%(key,value))
 aWeb.wr("</DIV></DIV></ARTICLE>")

#
#
def devices(aWeb):
 args = aWeb.args()
 res = aWeb.rest_call("vera/devices?node=master",args)
 aWeb.wr("<SECTION CLASS=content-left ID=div_content_left>")
 aWeb.wr("<ARTICLE>")
 aWeb.wr("<DIV CLASS=table>")
 aWeb.wr("<DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>Type</DIV><DIV CLASS=th>Room</DIV></DIV>")
 aWeb.wr("<DIV CLASS=tbody>")
 for dev in res['devices']:
   aWeb.wr("<DIV CLASS=tr>")
   aWeb.wr("<DIV CLASS=td>%s</DIV>"%dev['id'])
   aWeb.wr("<DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL=vera_device_info?node=%s&category=%s&id=%s>%s</A></DIV>"%(aWeb['node'],dev['category'],dev['id'],dev['name']))
   aWeb.wr("<DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV>"%(res['categories'].get(str(dev['category'])),res['rooms'].get(str(dev['room']),'Unassigned')))
   aWeb.wr("</DIV>")
 aWeb.wr("</DIV></DIV></ARTICLE></SECTION>")
 aWeb.wr("<SECTION CLASS=content-right ID=div_content_right></SECTION>")

#
#
def device_info(aWeb):
 args = aWeb.args()
 res = aWeb.rest_call("vera/device_info?node=master",args)
 aWeb.wr("<ARTICLE><DIV CLASS=title>Device %s</DIV>"%aWeb['id'])
 if aWeb['category'] == '2':
  load  = res['urn:upnp-org:serviceId:Dimming1']['LoadLevelStatus']
  state = res['urn:upnp-org:serviceId:SwitchPower1']['Status']
  aWeb.wr("<FORM ID=device_state>")
  aWeb.wr("<INPUT TYPE=HIDDEN NAME='node' VALUE='%s'>"%(aWeb['node']))
  aWeb.wr("<INPUT TYPE=HIDDEN NAME='id' VALUE='%s'>"%(aWeb['id']))
  aWeb.wr("<INPUT TYPE=HIDDEN NAME='service' VALUE='urn:upnp-org:serviceId:Dimming1'>")
  aWeb.wr("<INPUT TYPE=HIDDEN NAME='category' VALUE='%s'>"%(aWeb['category']))
  aWeb.wr("<INPUT TYPE=RANGE MIN=0 MAX=100 VALUE='%s' CLASS='slider' NAME='value' HTML='output'><SPAN ID='output'>%s</SPAN></FORM>"%(load,load))
  aWeb.wr("<INPUT TYPE=RADIO ID='on' NAME='state' VALUE='on' %s><LABEL FOR='on'>On</LABEL> <INPUT TYPE=RADIO ID='off' NAME='state' VALUE='off' %s><LABEL FOR='off'>Off</LABEL>"%("checked" if state == "1" else "","checked" if state == "0" else ""))
  aWeb.wr(aWeb.button('start',DIV='div_content_right', URL='vera_device_info?op=update&variable=LoadLevelTarget', FRM='device_state'))
  if res['op']:
   aWeb.wr("<DIV CLASS=table><DIV CLASS=tbody>")
   aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Response</DIV><DIV CLASS=td>%s</DIV></DIV>"%(res['op']['response']))
   aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Job</DIV><DIV CLASS=td>%s</DIV></DIV>"%(res['op'].get('job')))
   aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Result</DIV><DIV CLASS=td>%s</DIV></DIV>"%(res['op'].get('status')))
   aWeb.wr("</DIV></DIV>")
 else:
  res.pop('op',None)
  aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Service</DIV><DIV CLASS=th>Variable</DIV><DIV CLASS=th>Value</DIV></DIV><DIV CLASS=tbody>")
  for svc,entry in res.items():
   for var,val in entry.items():
    aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV></DIV>"%(svc,var,val))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</ARTICLE>")

#
#
def rooms(aWeb):
 res = aWeb.rest_call("vera/infra?node=master",{'node':aWeb['node']})
 aWeb.wr("<SECTION CLASS=content-left ID=div_content_left><ARTICLE>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>Section</DIV></DIV><DIV CLASS=tbody>")
 for room in res['rooms'].values():
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%s</DIV>"%room['id'])
  aWeb.wr("<DIV CLASS=td><A CLASS=z-op DIV=div_content URL=vera_devices?node=%s&room=%s>%s</A></DIV>"%(aWeb['node'],room['id'],room['name']))
  aWeb.wr("<DIV CLASS=td>%s</DIV></DIV>"%(res['sections'][str(room['section'])]))
 aWeb.wr("</DIV></DIV></ARTICLE></SECTION>")
 aWeb.wr("<SECTION CLASS=content-right ID=div_content_right></SECTION>")

#
#
def scenes(aWeb):
 res = aWeb.rest_call("vera/infra?node=master",{'node':aWeb['node']})
 aWeb.wr("<SECTION CLASS=content-left ID=div_content_left>")
 aWeb.wr("<ARTICLE>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>&nbsp;</DIV></DIV><DIV CLASS=tbody>")
 for scen in res['scenes'].values():
  id = scen['id']
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%s</DIV>"%id)
  aWeb.wr("<DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL=vera_scene_info?node=%s&scene=%s>%s</A></DIV>"%(aWeb['node'],id,scen['name']))
  aWeb.wr("<DIV CLASS=td><DIV ID=scene_%s>"%id)
  aWeb.wr(aWeb.button('start' if scen['active'] == 0 else 'stop',URL='vera_scene_state?node=%s&scene=%s&op=%s'%(aWeb['node'],id,"run" if scen['active'] == 0 else "off"),DIV='scene_%s'%id))
  aWeb.wr("</DIV></DIV></DIV>")
 aWeb.wr("</DIV></DIV></ARTICLE></SECTION>")
 aWeb.wr("<SECTION CLASS=content-right ID=div_content_right></SECTION>")

#
#
def scene_state(aWeb):
 res = aWeb.rest_call("vera/scene?node=master",{'node':aWeb['node'],'scene':aWeb['scene'],'op':aWeb['op']})
 aWeb.wr(aWeb.button('stop' if aWeb['op'] == "run" else 'start',URL='vera_scene_state?node=%s&scene=%s&op=%s'%(aWeb['node'],aWeb['scene'],"run" if aWeb['op'] == "off" else "off"),DIV='div_scene_%s'%aWeb['id']))

#
#
def scene_info(aWeb):
 args = aWeb.args()
 res = aWeb.rest_call("vera/scene",args)
 aWeb.wr("<ARTICLE>")
 aWeb.wr("<DIV CLASS=table style='width:auto'><DIV CLASS=thead><DIV CLASS=th>Key</DIV><DIV CLASS=th>Value</DIV></DIV>")
 aWeb.wr("<DIV CLASS=tbody>")
 for key,value in res.items():
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV></DIV>"%(key,value))
 aWeb.wr("</DIV></DIV></ARTICLE>")
