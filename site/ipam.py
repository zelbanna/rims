"""Module docstring.

HTML5 Ajax IPAM module

"""
__author__= "Zacharias El Banna"
__version__ = "1.0GA"
__status__= "Production"

#
#
def network_list(aWeb):
 res = aWeb.rest_call("ipam_network_list")
 print "<ARTICLE><P>Networks</P><DIV CLASS='controls'>"
 print aWeb.button('reload', DIV='div_content_left',  URL='zdcp.cgi?ipam_network_list', TITLE='Reload list')
 print aWeb.button('add',    DIV='div_content_right', URL='zdcp.cgi?ipam_network_info&id=new', TITLE='New network')
 if res['dhcp']:
  print aWeb.button('save',   DIV='div_content_right', URL='zdcp.cgi?dhcp_update&node=%s&type=%s'%(res['dhcp']['node']['value'],res['dhcp']['type']['value']), SPIN='true', TITLE='Update DHCP server')
 print "</DIV><DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Network</DIV><DIV CLASS=th>Description</DIV><DIV CLASS=th>&nbsp;</DIV></DIV><DIV CLASS=tbody>"
 for net in res['networks']:
  print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td><DIV CLASS=controls>".format(net['id'],net['netasc'],net['description'])
  print aWeb.button('configure', DIV='div_content_right', URL='zdcp.cgi?ipam_network_info&id=%i'%net['id'])
  print aWeb.button('info',DIV='div_content_right', URL='zdcp.cgi?ipam_network_layout&id=%i'%net['id'])
  print "</DIV></DIV></DIV>"
 print "</DIV></DIV></ARTICLE>"

#
#
def network_info(aWeb):
 args = aWeb.get_args2dict()
 res  = aWeb.rest_call("ipam_network_info",args)
 data = res['data']
 lock = "readonly" if not data['id'] == 'new' else ""
 print "<ARTICLE CLASS=info><P>Network Info (%s)</P>"%(data['id'])
 print "<FORM ID=ipam_info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE='%s'>"%(data['id'])
 print "<DIV CLASS=table><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Description:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=description VALUE='{}'></DIV></DIV>".format(data['description'])
 print "<DIV CLASS=tr><DIV CLASS=td>Network:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=network  VALUE='{}' '{}'></DIV></DIV>".format(data['network'],lock)
 print "<DIV CLASS=tr><DIV CLASS=td>Mask:</DIV><DIV CLASS=td><INPUT    TYPE=TEXT NAME=mask    VALUE='{}' '{}'></DIV></DIV>".format(data['mask'],lock)
 print "<DIV CLASS=tr><DIV CLASS=td>Gateway:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=gateway VALUE='{}'></DIV></DIV>".format(data['gateway'])
 print "<DIV CLASS=tr><DIV CLASS=td>Reverse Zone:</DIV><DIV CLASS=td><SELECT NAME=reverse_zone_id>"
 for dom in res['domains']:
  extra = "selected" if (dom['id'] == data['reverse_zone_id']) or (not data['reverse_zone_id'] and dom['id'] == 'NULL') else ''
  print "<OPTION VALUE='%s' %s>%s (%s)</OPTION>"%(dom['id'],extra,dom['server'],dom['name'])
 print "</SELECT></DIV></DIV>"
 print "</DIV></DIV>"
 print "</FORM><DIV CLASS=controls>"
 print aWeb.button('reload',DIV='div_content_right',URL='zdcp.cgi?ipam_network_info&id=%s'%data['id'])
 print aWeb.button('save'  ,DIV='div_content_right',URL='zdcp.cgi?ipam_network_info&op=update', FRM='ipam_info_form')
 if not data['id'] == 'new':
  print aWeb.button('trash',DIV='div_content_right',URL='zdcp.cgi?ipam_network_delete&id=%s'%data['id'],MSG='Are you really sure')
 print "</DIV>"
 print "<SPAN CLASS='results' ID=update_results></SPAN>"
 print "</ARTICLE>"

#
#
def network_layout(aWeb):
 data = aWeb.rest_call("ipam_network_inventory",{'id':aWeb['id']})
 startn  = int(data['start'])
 starta  = int(data['network'].split('.')[3])
 addresses = data['addresses']
 green = "<A CLASS='z-op btn small ipam green' TITLE='New' DIV=div_content_right URL=zdcp.cgi?device_new&ipam_network_id="+ aWeb['id'] +"&ipint={}>{}</A>"
 red   = "<A CLASS='z-op btn small ipam red'   TITLE='Used' DIV=div_content_right URL=zdcp.cgi?device_info&ipam_id={}>{}</A>"
 blue  = "<A CLASS='z-op btn small ipam blue'  TITLE='{}'>{}</A>"
 print "<ARTICLE><P>%s/%s</P><DIV CLASS=controls"%(data['network'],data['mask'])
 print blue.format('network',starta % 256)
 for cnt in range(1,int(data['no'])-1):
  ip = addresses.get(str(cnt + startn))
  if ip and ip.get('id'):
   print red.format(ip['id'],(cnt + starta) % 256)
  else:
   print green.format(cnt + startn,(cnt + starta) % 256)
 print blue.format('broadcast',(starta + int(data['no'])-1)% 256)
 print "</DIV></ARTICLE>"

#
#
def network_delete(aWeb):
 data = aWeb.rest_call("ipam_network_delete",{'id':aWeb['id']})
 print "<ARTICLE>%s</ARTICLE"%(data)

#
#
def address_new(aWeb):
 pass

#
#
def address_info(aWeb):
 pass

#
#
def address_delete(aWeb):
 pass

