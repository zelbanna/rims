"""Module docstring.

HTML5 Ajax Racks module

"""
__author__= "Zacharias El Banna"
__version__ = "1.0GA"
__status__ = "Production"
__icon__ = 'images/icon-rack.png'
__type__ = 'menuitem'

################################################## Basic Rack Info ######################################################

def main(aWeb):
 print "<NAV><UL>&nbsp;</UL></NAV>"
 print "<SECTION CLASS=content ID=div_content><SECTION CLASS=content-left ID=div_content_left>"
 list(aWeb)
 print "</SECTION><SECTION CLASS=content-right ID=div_content_right></SECTION></SECTION>"

#
#
def list(aWeb):
 racks = aWeb.rest_call("rack_list",{"sort":"name"})
 print "<ARTICLE><P>Racks</P><DIV CLASS=controls>"
 print aWeb.button('reload',DIV='div_content_left',URL='zdcp.cgi?rack_list')
 print aWeb.button('add',DIV='div_content_right',URL='zdcp.cgi?rack_info&id=new')
 print "</DIV><DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Name</DIV><DIV CLASS=th>Size</DIV><DIV CLASS=th>&nbsp;</DIV></DIV><DIV CLASS=tbody>"
 for unit in racks:
  print "<DIV CLASS=tr><DIV CLASS='td maxed'>%(name)s</DIV><DIV CLASS=td>%(size)s</DIV><DIV CLASS=td><DIV CLASS=controls>"%unit
  print aWeb.button('edit', DIV='div_content_right', URL='zdcp.cgi?rack_info&id=%s'%unit['id'])
  print aWeb.button('show', DIV='main',              URL='zdcp.cgi?device_main&rack=%s'%unit['id'],TITLE='Rack inventory')
  print "</DIV></DIV></DIV>"
 print "</DIV></DIV></ARTICLE>"

#
def list_infra(aWeb):
 type = aWeb['type']
 devices = aWeb.rest_call("device_list",{'field':'base','search':type,'extra':['type']})['data']
 print "<ARTICLE><P>%ss</P><DIV CLASS=controls>"%type.title()
 print aWeb.button('reload',DIV='div_content_left', URL='zdcp.cgi?rack_list_infra&type=%s'%type)
 print "</DIV><DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>&nbsp;</DIV></DIV><DIV CLASS=tbody>"
 for dev in devices:
  print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL='zdcp.cgi?device_info&id=%s'>%s</DIV><DIV CLASS=td><A CLASS=z-op DIV=div_content_left URL='zdcp.cgi?%s_inventory&ip=%s'>%s</A></DIV><DIV CLASS=td><DIV CLASS=controls>"%(dev['id'],dev['id'],dev['type_name'],dev['ip'],dev['hostname'])
  print aWeb.button('info',DIV='main',URL='zdcp.cgi?%s_manage&id=%s&ip=%s&hostname=%s'%(dev['type_name'],dev['id'],dev['ip'],dev['hostname']))
  if dev.get('webpage'):
   print aWeb.button('www', HREF=dev['webpage'], TARGET='_blank', TITLE='UI')
  print "</DIV></DIV></DIV>"
 print "</DIV></DIV></ARTICLE>"

#
#
def inventory(aWeb):
 data = aWeb.rest_call("rack_devices",{"id":aWeb['rack']})
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
  print "<A CLASS='z-op' TITLE='Show device info for {0}' DIV='div_content_right' URL='zdcp.cgi?device_info&id={1}'>{0}</A></CENTER>".format(dev['hostname'],dev['id'])
  print "</DIV>"
 print "</DIV>"

#
#
def info(aWeb):
 args = aWeb.get_args2dict()
 res  = aWeb.rest_call("rack_info",args)
 data = res['data']
 print "<ARTICLE CLASS=info><P>Rack Info (%s)</P>"%(data['id'])
 print "<FORM ID=rack_info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(data['id'])
 print "<DIV CLASS=table><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Name:</DIV><DIV CLASS=td><INPUT NAME=name TYPE=TEXT VALUE='%s'></DIV></DIV>"%(data['name'])
 print "<DIV CLASS=tr><DIV CLASS=td>Size:</DIV><DIV CLASS=td><INPUT NAME=size TYPE=TEXT VALUE='%s'></DIV></DIV>"%(data['size'])
 print "<DIV CLASS=tr><DIV CLASS=td>Console:</DIV><DIV CLASS=td><SELECT NAME=console>"
 for unit in res['consoles']:
  extra = " selected" if (data['console'] == unit['id']) or (not data['console'] and unit['id'] == 'NULL') else ""
  print "<OPTION VALUE={0} {1}>{2}</OPTION>".format(unit['id'],extra,unit['hostname'])
 print "</SELECT></DIV></DIV>"

 for key in ['pdu_1','pdu_2']:
  print "<DIV CLASS=tr><DIV CLASS=td>%s:</DIV><DIV CLASS=td><SELECT NAME=%s>"%(key.capitalize(),key)
  for unit in res['pdus']:
   extra = " selected" if (data[key] == unit['id']) or (not data[key] and unit['id'] == 'NULL') else ""
   print "<OPTION VALUE={0} {1}>{2}</OPTION>".format(unit['id'],extra,unit['hostname'])
  print "</SELECT></DIV></DIV>"

 print "</DIV></DIV>"
 print "<SPAN CLASS='right small-text' ID=update_results></SPAN>"
 print "</FORM><DIV CLASS=controls>"
 print aWeb.button('reload',DIV='div_content_right', URL='zdcp.cgi?rack_info&id={0}'.format(data['id']))
 print aWeb.button('save', DIV='div_content_right', URL='zdcp.cgi?rack_info&op=update', FRM='rack_info_form')
 if not id == 'new':
  print aWeb.button('trash',DIV='div_content_right',URL='zdcp.cgi?rack_delete&id=%s'%(data['id']))
 print "</DIV></ARTICLE>"

#
#
def delete(aWeb):
 res = aWeb.rest_call("rack_delete",{'id':aWeb['id']})
 print "<ARTICLE>Rack %s deleted (%s)</ARTICLE>"%(aWeb['id'],res)
