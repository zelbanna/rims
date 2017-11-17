"""Module docstring.

HTML5 Ajax IPAM calls module

"""
__author__= "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__= "Production"

#
#
def list(aWeb):
 from sdcp.rest import sdcpipam
 res = sdcpipam.list(None)
 print "<ARTICLE><P>Subnets</P>"
 print aWeb.button('reload', DIV='div_content_left',  URL='sdcp.cgi?call=ipam_list')
 print aWeb.button('add',    DIV='div_content_right', URL='sdcp.cgi?call=ipam_info&id=new')
 print "<DIV CLASS=z-table>"
 print "<DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Subnet</DIV><DIV CLASS=th>Description</DIV><DIV CLASS=th>&nbsp;</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for net in res['subnets']:
  print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><DIV CLASS=td><A CLASS='z-op' DIV=div_content_right URL='sdcp.cgi?call=ipam_info&id={}'>{}</A></DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>&nbsp;".format(net['id'],net['id'],net['subnet'],net['description'])
  print aWeb.button('info', DIV='div_content_right', URL='sdcp.cgi?call=ipam_layout&id=%i'%net['id'])
  print "</DIV></DIV>"
 print "</DIV></DIV></ARTICLE>"

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

 print "<ARTICLE CLASS=info><P>Subnet Info {}</P>".format("(new)" if data['id'] == 'new' else "")
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
 print aWeb.button('reload',DIV='div_content_right',URL='sdcp.cgi?call=ipam_info&id=%s'%data['id'])
 print aWeb.button('save'  ,DIV='div_content_right',URL='sdcp.cgi?call=ipam_info&op=update', FRM='ipam_info_form')
 if not data['id'] == 'new':
  print aWeb.button('delete',DIV='div_content_right',URL='sdcp.cgi?call=ipam_delete&id=%s'%data['id'],MSG='Are you really sure')
 print "<SPAN CLASS='results' ID=update_results></SPAN>"
 print "</ARTICLE>"

#
#
def layout(aWeb):
 from sdcp.rest import sdcpipam
 print "<ARTICLE>"
 ret = sdcpipam.allocation({'id':aWeb['id']})
 startn  = int(ret['start'])
 starta  = int(ret['subnet'].split('.')[3])
 devices = ret['devices']
 green = "<A CLASS='z-op z-btn ipam-icon' STYLE='background-color:#00cc66!important' TITLE='New' DIV=div_content_right URL=sdcp.cgi?call=device_new&subnet_id="+ aWeb['id'] +"&ipint={}>{}</A>"
 red   = "<A CLASS='z-op z-btn ipam-icon' STYLE='background-color:#df3620!important' TITLE='{}' DIV=div_content_right URL=sdcp.cgi?call=device_info&id={}>{}</A>"
 blue  = "<A CLASS='z-op z-btn ipam-icon' STYLE='background-color:#33CAFF!important' TITLE='{}'>{}</A>"
 print blue.format('network',starta % 256)
 for cnt in range(1,int(ret['no'])-1):
  dev = devices.get(cnt + startn)
  if dev:
   print red.format(dev['hostname'],dev['id'],(cnt + starta) % 256)
  else:
   print green.format(cnt + startn,(cnt + starta) % 256)
 print blue.format('broadcast',(starta + int(ret['no'])-1)% 256)
 print "</ARTICLE>"

#
#
def delete(aWeb):
 from sdcp.rest import sdcpipam
 print "<ARTICLE>%s</ARTICLE"%(sdcpipam.remove({'id':aWeb['id']}))
