"""Module docstring.

Ajax IPAM calls module

"""
__author__= "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__= "Production"

from sdcp.core.dbase import DB

#
#
def list(aWeb):
 from sdcp.rest import sdcpipam
 res = sdcpipam.list(None)
 print "<DIV CLASS=z-frame>"
 print "<DIV CLASS=title>Subnets</DIV>"
 print "<A TITLE='Reload List' CLASS='z-btn z-small-btn z-op' DIV=div_content_left  URL='sdcp.cgi?call=ipam_list'><IMG SRC='images/btn-reload.png'></A>"
 print "<A TITLE='Add Subnet'  CLASS='z-btn z-small-btn z-op' DIV=div_content_right URL='sdcp.cgi?call=ipam_info&id=new'><IMG SRC='images/btn-add.png'></A>"
 print "<DIV CLASS=z-table>"
 print "<DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Subnet</DIV><DIV CLASS=th>Description</DIV><DIV CLASS=th>&nbsp;</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for net in res['subnets']:
  print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><DIV CLASS=td><A CLASS='z-op' DIV=div_content_right URL='sdcp.cgi?call=ipam_info&id={}'>{}</A></DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>&nbsp;".format(net['id'],net['id'],net['subnet'],net['description'])
  print "<A CLASS='z-op z-btn z-small-btn' DIV=div_content_right URL=sdcp.cgi?call=ipam_layout&id={}><IMG SRC=images/btn-info.png></A>".format(net['id'])
  print "</DIV></DIV>"
 print "</DIV></DIV></DIV>"

#
#
def info(aWeb):
 from sdcp.rest import sdcpipam
 if aWeb['op'] == 'update':
  data = aWeb.get_args2dict()
  if data['ptr'] == 'true' and data['ptr_dom_id'] == 'NULL':
   # Create PTR and 
   print "Add PTR"
  if data['ptr'] =='false' and data['ptr_dom_id'] != 'NULL':
   print "Remove PTR" 
  res = sdcpipam.update(data)
  data['gateway'] = res['gateway']
  data['id']      = res['id']
  # ZEB: Remove when ptr update is working
  data['ptr_dom_id'] = None if data['ptr_dom_id'] == 'NULL' else data['ptr_dom_id']
 else:
  res = sdcpipam.subnet({'id':aWeb['id']})
  data = res['data']
 lock = "readonly" if not data['id'] == 'new' else ""

 print "<DIV CLASS='z-frame z-info' STYLE='height:200px;'>"
 print "<DIV CLASS=title>Subnet Info {}</DIV>".format("(new)" if data['id'] == 'new' else "")
 print "<!-- {} -->".format(res)
 print "<FORM ID=ipam_info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(data['id'])
 print "<INPUT TYPE=HIDDEN NAME=ptr_dom_id VALUE={}>".format(data['ptr_dom_id'] if data['ptr_dom_id'] else 'NULL')
 print "<DIV CLASS=z-table><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Description:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=description VALUE={}></DIV></DIV>".format(data['description'])
 print "<DIV CLASS=tr><DIV CLASS=td>Subnet:</DIV><DIV CLASS=td><INPUT  TYPE=TEXT NAME=subnet  VALUE={} {}></DIV></DIV>".format(data['subnet'],lock)
 print "<DIV CLASS=tr><DIV CLASS=td>Mask:</DIV><DIV CLASS=td><INPUT    TYPE=TEXT NAME=mask    VALUE={} {}></DIV></DIV>".format(data['mask'],lock)
 print "<DIV CLASS=tr><DIV CLASS=td>Gateway:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=gateway VALUE={}></DIV></DIV>".format(data['gateway'])
 print "<DIV CLASS=tr><DIV CLASS=td>PTR Domain:</DIV><DIV CLASS=td>"
 print "Yes<INPUT TYPE=RADIO NAME=ptr VALUE=true STYLE='width:auto' {}>".format("checked" if     data['ptr_dom_id'] else "")
 print "No<INPUT TYPE=RADIO NAME=ptr VALUE=false STYLE='width:auto' {}>".format("checked" if not data['ptr_dom_id'] else "")
 print "</DIV></DIV>"
 print "</DIV></DIV>"
 print "</FORM>"
 print "<A TITLE='Reload info' CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=sdcp.cgi?call=ipam_info&id={}><IMG SRC='images/btn-reload.png'></A>".format(data['id'])
 print "<A TITLE='Update unit' CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=sdcp.cgi?call=ipam_info&op=update FRM=ipam_info_form><IMG SRC='images/btn-save.png'></A>"
 if not data['id'] == 'new':
  print "<A TITLE='Delete unit' CLASS='z-btn z-op z-small-btn' DIV=div_content_right MSG='Are you really sure' URL=sdcp.cgi?call=ipam_remove&id={}><IMG SRC='images/btn-delete.png'></A>".format(data['id'])
 print "<SPAN style='float:right; font-size:9px;'ID=update_results></SPAN>"
 print "</DIV></DIV>"

#
#
def layout(aWeb):
 from sdcp.rest import sdcpipam
 print "<DIV CLASS=z-frame>"
 ret = sdcpipam.allocation({'id':aWeb['id']})
 startn  = int(ret['start'])
 starta  = int(ret['subnet'].split('.')[3])
 devices = ret['devices']
 green = "<A CLASS='z-op z-btn z-small-text' STYLE='float:left; background-color:#00cc66!important' TITLE='New' DIV=div_content_right URL=sdcp.cgi?call=device_new&subnet_id="+ aWeb['id'] +"&ipint={}>{}</A>"
 red   = "<A CLASS='z-op z-btn z-small-text' STYLE='float:left; background-color:#df3620!important' TITLE='{}' DIV=div_content_right URL=sdcp.cgi?call=device_info&id={}>{}</A>"
 blue  = "<A CLASS='z-btn z-small-text'      STYLE='float:left; background-color:#33CAFF!important' TITLE='{}'>{}</A>"
 print blue.format('network',starta % 256)
 for cnt in range(1,int(ret['no'])-1):
  dev = devices.get(cnt + startn)
  if dev:
   print red.format(dev['hostname'],dev['id'],(cnt + starta) % 256)
  else:
   print green.format(cnt + startn,(cnt + starta) % 256)
 print blue.format('broadcast',(starta + int(ret['no'])-1)% 256)
 print "</DIV>"
#
#
def remove(aWeb):
 from sdcp.rest import sdcpipam
 print "<DIV CLASS=z-frame>"
 ret = sdcpipam.remove({'id':aWeb['id']})
 print ret
 print "</DIV>"
