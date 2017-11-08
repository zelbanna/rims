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
 print "<A TITLE='Reload List' CLASS='z-btn z-small-btn z-op' DIV=div_content_left  URL='sdcp.cgi?call=ipam_list'><IMG SRC='images/btn-reboot.png'></A>"
 print "<A TITLE='Add Subnet'  CLASS='z-btn z-small-btn z-op' DIV=div_content_right URL='sdcp.cgi?call=ipam_info&id=new'><IMG SRC='images/btn-add.png'></A>"
 print "<DIV CLASS=z-table>"
 print "<DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Subnet</DIV><DIV CLASS=th>Gateway</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for net in res['subnets']:
  print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><DIV CLASS=td><A CLASS='z-op' DIV=div_content_right URL='sdcp.cgi?call=ipam_info&id={}'>{}</A></DIV><DIV CLASS=td>{}</DIV></DIV>".format(net['id'],net['id'],net['subnet'],net['gateway'])
 print "</DIV></DIV></DIV>"

#
#
def info(aWeb):
 from sdcp.rest import sdcpipam
 if aWeb['op'] == 'update':
  data = aWeb.get_args2dict()
  res = sdcpipam.update(data)
  data['gateway'] = res['gateway']
  data['id']      = res['id']
 else:
  res = sdcpipam.subnet({'id':aWeb['id']})
  data = res['data']
 lock = "readonly" if not data['id'] == 'new' else ""

 print "<DIV CLASS=z-frame style='resize: horizontal; margin-left:0px; width:420px; z-index:101; height:200px;'>"
 print "<DIV CLASS=title>Subnet Info {}</DIV>".format("(new)" if id == 'new' else "")
 print "<!-- {} -->".format(res)
 print "<FORM ID=ipam_info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(data['id'])
 print "<DIV CLASS=z-table><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Description:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=description VALUE={}></DIV></DIV>".format(data['description'])
 print "<DIV CLASS=tr><DIV CLASS=td>Subnet:</DIV><DIV CLASS=td><INPUT  TYPE=TEXT NAME=subnet  VALUE={} {}></DIV></DIV>".format(data['subnet'],lock)
 print "<DIV CLASS=tr><DIV CLASS=td>Mask:</DIV><DIV CLASS=td><INPUT    TYPE=TEXT NAME=mask    VALUE={} {}></DIV></DIV>".format(data['mask'],lock)
 print "<DIV CLASS=tr><DIV CLASS=td>Gateway:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=gateway VALUE={}></DIV></DIV>".format(data['gateway'])
 print "</DIV></DIV>"
 print "</FORM>"
 print "<A TITLE='Reload info' CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=sdcp.cgi?call=ipam_info&id={}><IMG SRC='images/btn-reboot.png'></A>".format(data['id'])
 print "<A TITLE='Update unit' CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=sdcp.cgi?call=ipam_info&op=update FRM=ipam_info_form><IMG SRC='images/btn-save.png'></A>"
 if not data['id'] == 'new':
  print "<A TITLE='Remove unit' CLASS='z-btn z-op z-small-btn' DIV=div_content_right MSG='Are you really sure' URL=sdcp.cgi?call=ipam_remove&id={}><IMG SRC='images/btn-remove.png'></A>".format(data['id'])
 print "<SPAN style='float:right; font-size:9px;'ID=update_results></SPAN>"
 print "</DIV></DIV>"

#
#
def remove(aWeb):
 from sdcp.rest import sdcpipam
 print "<DIV CLASS=z-frame>"
 print sdcpipam.remove({'id':aWeb['id']})
 print "</DIV>"
