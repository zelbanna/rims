"""HTML5 Ajax IPAM module"""
__author__= "Zacharias El Banna"

#
#
def network_list(aWeb):
 res = aWeb.rest_call("ipam/network_list")
 aWeb.wr("<ARTICLE><P>Networks</P>")
 aWeb.wr(aWeb.button('reload',  DIV='div_content_left',  URL='ipam_network_list', TITLE='Reload list'))
 aWeb.wr(aWeb.button('add',     DIV='div_content_right', URL='ipam_network_info?id=new', TITLE='New network'))
 aWeb.wr(aWeb.button('document',DIV='div_content_right', URL='ipam_server_leases', SPIN='true'))
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Network</DIV><DIV CLASS=th>Description</DIV><DIV CLASS=th>DHCP</DIV><DIV CLASS=th>&nbsp;</DIV></DIV><DIV CLASS=tbody>")
 for net in res['networks']:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%(id)s</DIV><DIV CLASS=td>%(netasc)s</DIV><DIV CLASS=td STYLE='max-width:120px; overflow:hidden;'>%(description)s</DIV><DIV CLASS=td>%(service)s</DIV><DIV CLASS=td STYLE='width:80px'>"%net)
  aWeb.wr(aWeb.button('info',  DIV='div_content_right', URL='ipam_network_layout?id=%i'%net['id']))
  aWeb.wr(aWeb.button('items', DIV='div_content_right', URL='ipam_network_entries?id=%i'%net['id']))
  aWeb.wr(aWeb.button('edit',  DIV='div_content_right', URL='ipam_network_info?id=%i'%net['id']))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</DIV></DIV></ARTICLE>")

#
#
def network_info(aWeb):
 args = aWeb.args()
 res  = aWeb.rest_call("ipam/network_info",args)
 data = res['data']
 lock = "readonly" if not data['id'] == 'new' else ""
 aWeb.wr("<ARTICLE CLASS=info><P>Network Info (%s)</P>"%(data['id']))
 aWeb.wr("<FORM ID='rims_data_form'>")
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=id VALUE='%s'>"%(data['id']))
 aWeb.wr("<DIV CLASS=table><DIV CLASS=tbody>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Description:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=description VALUE='{}'></DIV></DIV>".format(data['description']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Network:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=network  VALUE='{}' '{}'></DIV></DIV>".format(data['network'],lock))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Mask:</DIV><DIV CLASS=td><INPUT    TYPE=TEXT NAME=mask    VALUE='{}' '{}'></DIV></DIV>".format(data['mask'],lock))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Gateway:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=gateway VALUE='{}'></DIV></DIV>".format(data['gateway']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Server</DIV><DIV CLASS=td><SELECT NAME=server_id>")
 for srv in res['servers']:
  extra = "selected='selected'" if srv['id'] == data['server_id'] or srv['id'] == 'NULL' and data['server_id'] == None else ""
  aWeb.wr("<OPTION VALUE='%s' %s>%s@%s</OPTION>"%(srv['id'],extra,srv['service'],srv['node']))
 aWeb.wr("</SELECT></DIV></DIV>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Reverse Zone:</DIV><DIV CLASS=td><SELECT NAME=reverse_zone_id>")
 for dom in res['domains']:
  extra = "selected" if (dom['id'] == data['reverse_zone_id']) or (not data['reverse_zone_id'] and dom['id'] == 'NULL') else ''
  aWeb.wr("<OPTION VALUE='%s' %s>%s (%s)</OPTION>"%(dom['id'],extra,dom['server'],dom['name']))
 aWeb.wr("</SELECT></DIV></DIV>")
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</FORM>")
 aWeb.wr(aWeb.button('reload',DIV='div_content_right',URL='ipam_network_info?id=%s'%data['id']))
 aWeb.wr(aWeb.button('save'  ,DIV='div_content_right',URL='ipam_network_info?op=update', FRM='rims_data_form'))
 if not data['id'] == 'new':
  aWeb.wr(aWeb.button('trash',DIV='div_content_right',URL='ipam_network_delete?id=%s'%data['id'],MSG='Are you really sure'))
 aWeb.wr("<SPAN CLASS='results' ID=update_results></SPAN>")
 aWeb.wr("</ARTICLE>")

#
#
def network_layout(aWeb):
 data = aWeb.rest_call("ipam/network_inventory",{'id':aWeb['id'],'dict':'ip_integer'})
 startn  = int(data['start'])
 starta  = int(data['network'].split('.')[3])
 addresses = data['entries']
 green = "<A CLASS='z-op btn small ipam green' TITLE='New' DIV=div_content_right URL='device_new?ipam_network_id="+ aWeb['id'] +"&ipint={}'>{}</A>"
 red   = "<A CLASS='z-op btn small ipam red'   TITLE='Used' DIV=div_content_right URL='device_info?ipam_id={}'>{}</A>"
 blue  = "<A CLASS='z-op btn small ipam blue'  TITLE='{}'>{}</A>"
 aWeb.wr("<ARTICLE><P>%s/%s</P>"%(data['network'],data['mask']))
 aWeb.wr(blue.format('network',starta % 256))
 for cnt in range(1,int(data['size'])-1):
  ip = addresses.get(str(cnt + startn))
  if ip:
   aWeb.wr(red.format(ip['id'],(cnt + starta) % 256))
  else:
   aWeb.wr(green.format(cnt + startn,(cnt + starta) % 256))
 aWeb.wr(blue.format('broadcast',(starta + int(data['size'])-1)% 256))
 aWeb.wr("</ARTICLE>")

#
#
def network_delete(aWeb):
 data = aWeb.rest_call("ipam/network_delete",{'id':aWeb['id']})
 aWeb.wr("<ARTICLE>%s</ARTICLE"%(data))

#
#
def network_entries(aWeb):
 data = aWeb.rest_call("ipam/network_inventory",{'id':aWeb['id'],'extra':['mac','state']})
 aWeb.wr("<ARTICLE><P>Allocated IP Addresses</P><SPAN CLASS=results ID=ipam_address_operation></SPAN><DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Id</DIV><DIV CLASS=th>IP</DIV><DIV CLASS=th>MAC</DIV><DIV CLASS=th>State</DIV></DIV><DIV CLASS=tbody>")
 for row in data['entries']:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%(id)i</DIV><DIV CLASS=td>%(ip)s</DIV><DIV CLASS=td>%(mac)s</DIV>"%row)
  aWeb.wr("<DIV CLASS=td><DIV CLASS='state %s' /></DIV><DIV CLASS=td>"%{0:'grey',1:'green',2:'red'}.get(row['state'],0))
  aWeb.wr(aWeb.button('info', DIV='div_content_right', URL='ipam_address_info?id=%(id)i'%row))
  aWeb.wr(aWeb.button('delete', DIV='ipam_address_operation', URL='ipam_address_delete?id=%(id)i&ip=%(ip)s'%row))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</DIV></DIV></ARTICLE>")

########################################## Server #########################################
#
#
def server_leases(aWeb):
 leases = aWeb.rest_call("ipam/server_leases",{'type':'active'})
 aWeb.wr("<ARTICLE><P>Leases (%s)</P>"%(aWeb['type']))
 aWeb.wr("<DIV CLASS=table><DIV class=thead><DIV class=th>Ip</DIV><DIV class=th>Mac</DIV><DIV class=th>Hostname</DIV><DIV class=th>OUI</DIV><DIV class=th>Starts</DIV><DIV class=th>Ends</DIV></DIV>")
 aWeb.wr("<DIV CLASS=tbody>")
 for data in leases['data']:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV></DIV>"%(data['ip'],data['mac'],data.get('hostname',"None"),data['oui'],data['starts'],data['ends']))
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</ARTICLE>")

######################################### Addresses #######################################
#
#
def address_new(aWeb):
 pass

#
#
def address_info(aWeb):
 args = aWeb.args()
 data = aWeb.rest_call("ipam/address_info",args)['data']
 aWeb.wr("<ARTICLE CLASS='info'><P>Address Info</DIV>")
 aWeb.wr("<FORM ID=ipam_address_form>")
 aWeb.wr("<DIV CLASS=table STYLE='width:auto'><DIV CLASS=tbody>")
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=id VALUE='%s'>"%(aWeb['id']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Network:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=network_id STYLE='min-width:200px;' VALUE='%s' READONLY></DIV></DIV>"%(data['network_id']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>IP:</DIV><DIV CLASS=td><INPUT      TYPE=URL  NAME=ip         STYLE='min-width:200px;' VALUE='%s'></DIV></DIV>"%(data['ip']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>MAC:</DIV><DIV CLASS=td><INPUT     TYPE=TEXT NAME=mac        STYLE='min-width:200px;' VALUE='%s'></DIV></DIV>"%(data['mac']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>State:</DIV><DIV CLASS=td><INPUT   TYPE=TEXT NAME=state      STYLE='min-width:200px;' VALUE='%s'></DIV></DIV>"%(data['state']))
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</FORM>")
 aWeb.wr(aWeb.button('save',   DIV='div_content_right',       URL='ipam_address_info?op=update', FRM='ipam_address_form'))
 aWeb.wr(aWeb.button('trash',  DIV='div_content_right',       URL='ipam_address_delete',         FRM='ipam_address_form', MSG='Are you really sure you want to delete address?'))
 aWeb.wr("</ARTICLE>")

#
#
def address_delete(aWeb):
 res = aWeb.rest_call("ipam/address_delete",{'id':aWeb['id']})
 aWeb.wr("Deleted: %(result)s"%res)
