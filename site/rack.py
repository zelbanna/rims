"""Module docstring.

HTML5 Ajax Racks calls module

"""
__author__= "Zacharias El Banna"                     
__version__ = "18.02.09GA"
__status__ = "Production"
__icon__ = 'images/icon-rack.png'

################################################## Basic Rack Info ######################################################

def main(aWeb):
 racks = aWeb.rest_call("racks_list")
 print "<NAV><UL>&nbsp;</UL></NAV>"
 print "<H1 CLASS='centered'>Rack Overview</H1>"
 print "<DIV CLASS='centered'>"
 rackstr = "<DIV STYLE='float:left; margin:6px;'><A TITLE='{1}' CLASS=z-op DIV=main URL=sdcp.cgi?call=device_main&target=rack_id&arg={0}><IMG STYLE='max-height:400px; max-width:200px;' ALT='{1} ({2})' SRC='images/{2}'></A></DIV>"
 print "<DIV STYLE='float:left; margin:6px;'><A CLASS=z-op DIV=main URL=sdcp.cgi?call=device_main&target=vm&arg=1><IMG STYLE='max-height:400px; max-width:200px;' ALT='VMs' SRC='images/hypervisor.png'></A></DIV>"
 for rack in racks:
  print rackstr.format(rack['id'], rack['name'], rack['image_url'])
 print "</DIV>"

#
#
def list(aWeb):
 racks = aWeb.rest_call("racks_list",{"sort":"name"})
 print "<ARTICLE><P>Rack</P>"
 print aWeb.button('reload',DIV='div_content_left',URL='sdcp.cgi?call=rack_list')
 print aWeb.button('add',DIV='div_content_right',URL='sdcp.cgi?call=rack_info&id=new')
 print "<DIV CLASS=table>"
 print "<DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>Size</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for unit in racks:
  print "<DIV CLASS=tr><DIV CLASS=td>{0}</DIV><DIV CLASS=td><A CLASS='z-op' DIV=div_content_right URL='sdcp.cgi?call=rack_info&id={0}'>{1}</A></DIV><DIV CLASS=td>{2}</DIV></DIV>".format(unit['id'],unit['name'],unit['size'])
 print "</DIV></DIV></ARTICLE>"

#
def list_infra(aWeb):
 type = aWeb['type']
 devices = aWeb.rest_call("device_list_type",{'base':type})['data']
 print "<ARTICLE><P>%ss</P>"%type.title()
 print aWeb.button('reload',DIV='div_content_left',  URL='sdcp.cgi?call=rack_list_infra&type=%s'%type)
 print "<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>&nbsp;</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for dev in devices:
  print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL='sdcp.cgi?call=device_info&id=%s'>%s</DIV><DIV CLASS=td><A CLASS=z-op DIV=div_content_left URL='sdcp.cgi?call=%s_inventory&ip=%s'>%s</A></DIV><DIV CLASS=td>"%(dev['id'],dev['id'],dev['type_name'],dev['ipasc'],dev['hostname'])
  print aWeb.button('info',DIV='main',URL='sdcp.cgi?call=%s_manage&id=%s&ip=%s&hostname=%s'%(dev['type_name'],dev['id'],dev['ipasc'],dev['hostname']))
  print "</DIV></DIV>"
 print "</DIV></DIV></ARTICLE>"

#
#
def inventory(aWeb):
 data = aWeb.rest_call("racks_devices",{"id":aWeb['rack']})
 size = data['size']
 print "<DIV STYLE='display:grid; justify-items:stretch; align-items:stretch; margin:10px; grid: repeat({}, 20px)/20px 220px 20px 20px 20px 220px 20px;'>".format(size)
 # Create rack and some text, then place devs
 print "<DIV STYLE='grid-column:1/4; grid-row:1; justify-self:center; font-weight:bold; font-size:14px;'>Front</DIV>"
 print "<DIV STYLE='grid-column:5/8; grid-row:1; justify-self:center; font-weight:bold; font-size:14px;'>Back</DIV>"
 print "<DIV STYLE='grid-column:2;   grid-row:2; text-align:center; background:yellow; border: solid 2px grey; font-size:12px;'>Panel</DIV>"
 for idx in range(2,size+2):
  ru = size-idx+2
  print "<DIV CLASS=rack-indx STYLE='grid-column:1; grid-row:%i; border-right:1px solid grey'>%i</DIV>"%(idx,ru)
  print "<DIV CLASS=rack-indx STYLE='grid-column:3; grid-row:%i;  border-left:1px solid grey'>%i</DIV>"%(idx,ru)
  print "<DIV CLASS=rack-indx STYLE='grid-column:5; grid-row:%i; border-right:1px solid grey'>%i</DIV>"%(idx,ru)
  print "<DIV CLASS=rack-indx STYLE='grid-column:7; grid-row:%i;  border-left:1px solid grey'>%i</DIV>"%(idx,ru)

 for dev in data['devices']:
  if dev['rack_unit'] == 0:
   continue
  rowstart = size-abs(dev['rack_unit'])+2
  rowend   = rowstart + dev['rack_size']
  col = "2" if dev['rack_unit'] > 0 else "6"
  print "<DIV CLASS='rack-data centered' STYLE='grid-column:{0}; grid-row:{1}/{2}; background:{3};'>".format(col,rowstart,rowend,"#00cc66" if not dev.get('user_id') else "#df3620")
  print "<A CLASS='z-op' TITLE='Show device info for {0}' DIV='div_content_right' URL='sdcp.cgi?call=device_info&id={1}'>{0}</A></CENTER>".format(dev['hostname'],dev['id'])
  print "</DIV>"
 print "</DIV>"

#
#
#
def info(aWeb):
 if aWeb.get('op') == 'save':
  data = {'name':aWeb['name'],'size':aWeb['size'],'pdu_1':aWeb['pdu_1'],'pdu_2':aWeb['pdu_2'],'console':aWeb['console'],'image_url':aWeb['image_url'],'id':aWeb['id']}
  res = aWeb.rest_call("racks_update",data)
  id = res['id']
 else:
  id = aWeb['id']
 info = aWeb.rest_call("racks_infra",{'id':id,'consoles':True,'pdus':True,'images':True,'types':False})
 print "<ARTICLE CLASS=info><P>Rack Info {}</P>".format("(new)" if id == 'new' else "")
 print "<FORM ID=rack_info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(id)
 print "<DIV CLASS=table><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Name:</DIV><DIV CLASS=td><INPUT NAME=name TYPE=TEXT VALUE='%s'></DIV></DIV>"%(info['rack']['name'])
 print "<DIV CLASS=tr><DIV CLASS=td>Size:</DIV><DIV CLASS=td><INPUT NAME=size TYPE=TEXT VALUE='%s'></DIV></DIV>"%(info['rack']['size'])
 print "<DIV CLASS=tr><DIV CLASS=td>Console:</DIV><DIV CLASS=td><SELECT NAME=console>"
 for unit in info['consoles']:
  extra = " selected" if (info['rack']['console'] == unit['id']) or (not info['rack']['console'] and unit['id'] == 'NULL') else ""
  print "<OPTION VALUE={0} {1}>{2}</OPTION>".format(unit['id'],extra,unit['hostname'])
 print "</SELECT></DIV></DIV>"

 for key in ['pdu_1','pdu_2']:
  print "<DIV CLASS=tr><DIV CLASS=td>{0}:</DIV><DIV CLASS=td><SELECT NAME={1}>".format(key.capitalize(),key)
  for unit in info['pdus']:
   extra = " selected" if (info['rack'][key] == unit['id']) or (not info['rack'][key] and unit['id'] == 'NULL') else ""
   print "<OPTION VALUE={0} {1}>{2}</OPTION>".format(unit['id'],extra,unit['hostname'])   
  print "</SELECT></DIV></DIV>"

 print "<DIV CLASS=tr><DIV CLASS=td>Image</DIV><DIV CLASS=td><SELECT NAME=image_url>"
 print "<OPTION VALUE=NULL>No picture</OPTION>"
 for image in info['images']:
  extra = " selected" if (info['rack']['image_url'] == image) or (info['rack']['image_url'] and image == 'NULL') else ""
  print "<OPTION VALUE={0} {1}>{2}</OPTION>".format(image,extra,image[:-4])
 print "</SELECT></DIV></DIV>"

 print "</DIV></DIV>"
 print "</FORM>"
 print aWeb.button('reload',DIV='div_content_right', URL='sdcp.cgi?call=rack_info&id={0}'.format(id))
 print aWeb.button('save', DIV='div_content_right', URL='sdcp.cgi?call=rack_info&op=save', FRM='rack_info_form')
 if not id == 'new':
  print aWeb.button('delete',DIV='div_content_right',URL='sdcp.cgi?call=rack_delete&id=%s'%(id))
 print "<SPAN CLASS='right small-text' ID=update_results></SPAN>"
 print "</ARTICLE>"

#
#
def delete(aWeb):
 res = aWeb.rest_call("racks_delete",{'id':aWeb['id']})
 print "<ARTICLE>Rack %s deleted (%s)</ARTICLE>"%(aWeb['id'],res)
