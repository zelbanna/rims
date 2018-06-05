"""Module docstring.

HTML5 Ajax IPAM module

"""
__author__= "Zacharias El Banna"
__version__ = "18.05.31GA"
__status__= "Production"

#
#
def list(aWeb):
 res = aWeb.rest_call("ipam_list")
 print "<ARTICLE><P>Networks</P><DIV CLASS='controls'>"
 print aWeb.button('reload', DIV='div_content_left',  URL='sdcp.cgi?ipam_list', TITLE='Reload list')
 print aWeb.button('add',    DIV='div_content_right', URL='sdcp.cgi?ipam_info&id=new', TITLE='New network')
 if res['dhcp']:
  print aWeb.button('save',   DIV='div_content_right', URL='sdcp.cgi?dhcp_update&node=%s&type=%s'%(res['dhcp']['node']['value'],res['dhcp']['type']['value']), SPIN='true', TITLE='Update DHCP server')
 print "</DIV><DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Network</DIV><DIV CLASS=th>Description</DIV><DIV CLASS=th>&nbsp;</DIV></DIV><DIV CLASS=tbody>"
 for net in res['subnets']:
  print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><DIV CLASS=td><A CLASS='z-op' DIV=div_content_right URL='sdcp.cgi?ipam_layout&id={}'>{}</A></DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td><DIV CLASS=controls>".format(net['id'],net['id'],net['subasc'],net['description'])
  print aWeb.button('info', DIV='div_content_right', URL='sdcp.cgi?ipam_info&id=%i'%net['id'])
  print "</DIV></DIV></DIV>"
 print "</DIV></DIV></ARTICLE>"

#
#
def info(aWeb):
 args = aWeb.get_args2dict()
 data = aWeb.rest_call("ipam_info",args)['data']
 lock = "readonly" if not data['id'] == 'new' else ""
 print "<ARTICLE CLASS=info><P>Subnet Info (%s)</P>"%(data['id'])
 print "<FORM ID=ipam_info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE='%s'>"%(data['id'])
 print "<DIV CLASS=table><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Description:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=description VALUE='{}'></DIV></DIV>".format(data['description'])
 print "<DIV CLASS=tr><DIV CLASS=td>Subnet:</DIV><DIV CLASS=td><INPUT  TYPE=TEXT NAME=subnet  VALUE='{}' '{}'></DIV></DIV>".format(data['subnet'],lock)
 print "<DIV CLASS=tr><DIV CLASS=td>Mask:</DIV><DIV CLASS=td><INPUT    TYPE=TEXT NAME=mask    VALUE='{}' '{}'></DIV></DIV>".format(data['mask'],lock)
 print "<DIV CLASS=tr><DIV CLASS=td>Gateway:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=gateway VALUE='{}'></DIV></DIV>".format(data['gateway'])
 print "</DIV></DIV>"
 print "</FORM><DIV CLASS=controls>"
 print aWeb.button('reload',DIV='div_content_right',URL='sdcp.cgi?ipam_info&id=%s'%data['id'])
 print aWeb.button('save'  ,DIV='div_content_right',URL='sdcp.cgi?ipam_info&op=update', FRM='ipam_info_form')
 if not data['id'] == 'new':
  print aWeb.button('trash',DIV='div_content_right',URL='sdcp.cgi?ipam_delete&id=%s'%data['id'],MSG='Are you really sure')
 print "</DIV>"
 print "<SPAN CLASS='results' ID=update_results></SPAN>"
 print "</ARTICLE>"

#
#
def layout(aWeb):
 data = aWeb.rest_call("ipam_inventory",{'network':aWeb['id']})
 startn  = int(data['start'])
 starta  = int(data['subnet'].split('.')[3])
 devices = data['devices']
 green = "<A CLASS='z-op btn small ipam green' TITLE='New' DIV=div_content_right URL=sdcp.cgi?device_new&ipam_id="+ aWeb['id'] +"&ipint={}>{}</A>"
 red   = "<A CLASS='z-op btn small ipam red'   TITLE='{}' DIV=div_content_right URL=sdcp.cgi?device_info&id={}>{}</A>"
 blue  = "<A CLASS='z-op btn small ipam blue'  TITLE='{}'>{}</A>"
 print "<ARTICLE><P>%s/%s</P><DIV CLASS=controls"%(data['subnet'],data['mask'])
 print blue.format('network',starta % 256)
 for cnt in range(1,int(data['no'])-1):
  dev = devices.get(str(cnt + startn))
  if dev:
   print red.format(dev['hostname'],dev['id'],(cnt + starta) % 256)
  else:
   print green.format(cnt + startn,(cnt + starta) % 256)
 print blue.format('broadcast',(starta + int(data['no'])-1)% 256)
 print "</DIV></ARTICLE>"

#
#
def delete(aWeb):
 data = aWeb.rest_call("ipam_delete",{'network':aWeb['id']})
 print "<ARTICLE>%s</ARTICLE"%(data)
