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
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV>ID</DIV><DIV>Network</DIV><DIV>Description</DIV><DIV>DHCP</DIV><DIV>&nbsp;</DIV></DIV><DIV CLASS=tbody>")
 for net in res['data']:
  aWeb.wr("<DIV><DIV>%(id)s</DIV><DIV>%(netasc)s</DIV><DIV STYLE='max-width:120px; overflow:hidden;'>%(description)s</DIV><DIV>%(service)s</DIV><DIV STYLE='width:80px'>"%net)
  aWeb.wr(aWeb.button('info',  DIV='div_content_right', URL='ipam_network_layout?id=%i'%net['id']))
  aWeb.wr(aWeb.button('items', DIV='div_content_right', URL='ipam_address_list?network_id=%i'%net['id']))
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
 aWeb.wr("<ARTICLE CLASS=info><P>Network Info</P>")
 aWeb.wr("<FORM ID='rims_data_form'>")
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=id VALUE='%s'>"%(data['id']))
 aWeb.wr("<DIV CLASS='info col2'>")
 aWeb.wr("<LABEL for='id'>ID:</LABEL><SPAN id='id'>%(id)s</SPAN>"%data)
 aWeb.wr("<label for='description'>Description:</label><INPUT id='description' TYPE=TEXT NAME=description VALUE='{}'>".format(data['description']))
 aWeb.wr("<label for='network'>Network:</label><INPUT id='network' TYPE=TEXT NAME=network  VALUE='{}' '{}'>".format(data['network'],lock))
 aWeb.wr("<label for='mask'>Mask:</label><INPUT id='mask' TYPE=TEXT NAME=mask VALUE='{}' '{}'>".format(data['mask'],lock))
 aWeb.wr("<label for='gateway'>Gateway:</label><INPUT id='gateway' TYPE=TEXT NAME=gateway VALUE='{}'>".format(data['gateway']))
 aWeb.wr("<label for='server_id'>Server</label><SELECT id='server_id' NAME=server_id>")
 for srv in res['servers']:
  extra = "selected='selected'" if srv['id'] == data['server_id'] or srv['id'] == 'NULL' and data['server_id'] == None else ""
  aWeb.wr("<OPTION VALUE='%s' %s>%s@%s</OPTION>"%(srv['id'],extra,srv['service'],srv['node']))
 aWeb.wr("</SELECT>")
 aWeb.wr("<label for='reverse_zone_id'>Reverse Zone:</label><SELECT id='reverse_zone_id' NAME=reverse_zone_id>")
 for dom in res['domains']:
  extra = "selected" if (dom['id'] == data['reverse_zone_id']) or (not data['reverse_zone_id'] and dom['id'] == 'NULL') else ''
  aWeb.wr("<OPTION VALUE='%s' %s>%s (%s)</OPTION>"%(dom['id'],extra,dom['server'],dom['name']))
 aWeb.wr("</SELECT>")
 aWeb.wr("</DIV>")
 aWeb.wr("</FORM>")
 aWeb.wr(aWeb.button('reload',DIV='div_content_right',URL='ipam_network_info?id=%s'%data['id']))
 aWeb.wr(aWeb.button('save'  ,DIV='div_content_right',URL='ipam_network_info?op=update', FRM='rims_data_form'))
 if not data['id'] == 'new':
  aWeb.wr(aWeb.button('trash',DIV='div_content_right',URL='ipam_network_delete?id=%s'%data['id'],MSG='Are you really sure'))
 aWeb.wr("<SPAN CLASS='results' ID=update_results></SPAN>")
 aWeb.wr("</ARTICLE>")

#
#
def network_delete(aWeb):
 data = aWeb.rest_call("ipam/network_delete",{'id':aWeb['id']})
 aWeb.wr("<ARTICLE>%s</ARTICLE"%(data))

#
#
def network_layout(aWeb):
 data = aWeb.rest_call("ipam/address_list",{'network_id':aWeb['id'],'dict':'ip_integer','extra':['device_id']})
 startn  = int(data['start'])
 starta  = int(data['network'].split('.')[3])
 addresses = data['data']
 green = "<A CLASS='z-op btn small ipam green' TITLE='New' DIV=div_content_right URL='device_new?ipam_network_id="+ aWeb['id'] +"&ipint={}'>{}</A>"
 red   = "<A CLASS='z-op btn small ipam red'   TITLE='Used' DIV=div_content_right URL='device_info?id={}'>{}</A>"
 blue  = "<A CLASS='z-op btn small ipam blue'  TITLE='{}'>{}</A>"
 aWeb.wr("<ARTICLE><P>%s/%s</P>"%(data['network'],data['mask']))
 aWeb.wr(blue.format('network',starta % 256))
 for cnt in range(1,int(data['size'])-1):
  ip = addresses.get(str(cnt + startn))
  if ip:
   aWeb.wr(red.format(ip['device_id'],(cnt + starta) % 256))
  else:
   aWeb.wr(green.format(cnt + startn,(cnt + starta) % 256))
 aWeb.wr(blue.format('broadcast',(starta + int(data['size'])-1)% 256))
 aWeb.wr("</ARTICLE>")

########################################## Server #########################################
#
#
def server_leases(aWeb):
 leases = aWeb.rest_call("ipam/server_leases",{'type':'active'})
 aWeb.wr("<ARTICLE><P>Leases (%s)</P>"%(aWeb['type']))
 aWeb.wr("<DIV CLASS=table><DIV class=thead><DIV>Ip</DIV><DIV>Mac</DIV><DIV>Hostname</DIV><DIV>OUI</DIV><DIV>Starts</DIV><DIV>Ends</DIV></DIV>")
 aWeb.wr("<DIV CLASS=tbody>")
 for data in leases['data']:
  aWeb.wr("<DIV><DIV>%s</DIV><DIV>%s</DIV><DIV>%s</DIV><DIV>%s</DIV><DIV>%s</DIV><DIV>%s</DIV></DIV>"%(data['ip'],data['mac'],data.get('hostname',"None"),data['oui'],data['starts'],data['ends']))
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</ARTICLE>")

######################################### Addresses #######################################
#
#
def address_list(aWeb):
 data = aWeb.rest_call("ipam/address_list",{'network_id':aWeb['network_id'],'extra':['a_id','ptr_id','hostname','a_domain_id','device_id']})
 aWeb.wr("<ARTICLE><P>Allocated IP Addresses</P>")
 aWeb.wr(aWeb.button('reload',DIV='div_content_right',URL='ipam_address_list?network_id=%s'%(aWeb['network_id'])))
 aWeb.wr(aWeb.button('add',   DIV='div_content_right',URL='ipam_address_info?id=new&network_id=%s'%(aWeb['network_id'])))
 aWeb.wr("<SPAN CLASS=results ID=ipam_address_operation>&nbsp;</SPAN><DIV CLASS=table><DIV CLASS=thead><DIV>Id</DIV><DIV>IP</DIV><DIV>Hostname</DIV><DIV>Domain</DIV><DIV>A_id</DIV><DIV>PTR_id</DIV><DIV>&nbsp;</DIV></DIV><DIV CLASS=tbody>")
 for row in data['data']:
  aWeb.wr("<DIV><DIV>%(id)i</DIV><DIV>%(ip)s</DIV><DIV>%(hostname)s</DIV><DIV>%(domain)s</DIV><DIV>%(a_id)s</DIV><DIV>%(ptr_id)s</DIV>"%row)
  aWeb.wr("<DIV><DIV CLASS='state %s' /></DIV><DIV>"%aWeb.state_ascii(row['state']))
  aWeb.wr(aWeb.button('info', DIV='div_content_right', URL='ipam_address_info?id=%(id)i'%row))
  aWeb.wr(aWeb.button('delete', DIV='ipam_address_operation', URL='ipam_address_delete?id=%(id)i&ip=%(ip)s'%row))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</DIV></DIV></ARTICLE>")

#
#
def address_info(aWeb):
 args = aWeb.args()
 div = args.pop('vpl','div_content_right')
 data = aWeb.rest_call("ipam/address_info",args)
 domains = aWeb.rest_call("dns/domain_list",{'filter':'forward'})['data']
 aWeb.wr("<ARTICLE CLASS='info'><P>Address Info</P>")
 aWeb.wr("<SPAN CLASS=results ID=ipam_address_operation>%(status)s %(info)s&nbsp;</SPAN>"%(data))
 aWeb.wr("<FORM ID=ipam_address_form>")
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=id VALUE='%s'>"%data['data']['id'])
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=network_id VALUE='%s'>"%(data['data']['network_id']))
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=vpl VALUE='%s'>"%(div))
 aWeb.wr("<DIV CLASS='info col2'>")
 aWeb.wr("<label for='id'>ID:</label><span id='id'>%s</span>"%(data['data']['id']))
 aWeb.wr("<label for='state'>State:</label><DIV id='state' CLASS='state %s' />"%(aWeb.state_ascii(data['data']['state'])))
 aWeb.wr("<label for='network'>Network:</label><span id='network'>%s</span>"%(data['extra']['network']))
 aWeb.wr("<label for='ip'>IP:</label><INPUT id='ip' TYPE=TEXT NAME=ip       VALUE='%s'>"%(data['data']['ip']))
 aWeb.wr("<label for='a_id'>A_id:</label><INPUT id='a_id' TYPE=TEXT NAME=a_id     VALUE='%s'>"%(data['data']['a_id']))
 aWeb.wr("<label for='ptr_id'>PTR_id:</label><INPUT id='ptr_id' TYPE=TEXT NAME=ptr_id   VALUE='%s'>"%(data['data']['ptr_id']))
 aWeb.wr("<label for='hostname'>Hostname:</label><INPUT id='hostname' TYPE=TEXT NAME=hostname VALUE='%s'>"%(data['data']['hostname']))
 aWeb.wr("<label for='a_domain_id'>Domain:</label><SELECT id='a_domain_id' NAME=a_domain_id>")
 for dom in domains:
  extra = " selected" if data['data']['a_domain_id'] == dom['id'] or data['data']['a_domain_id'] is None and dom['id'] == 0 else ""
  aWeb.wr("<OPTION VALUE='%s' %s>%s</OPTION>"%(dom['id'],extra,dom['name']))
 aWeb.wr("</SELECT>")
 aWeb.wr("</DIV>")
 aWeb.wr("</FORM>")
 aWeb.wr(aWeb.button('reload', DIV=div, URL='ipam_address_info', FRM='ipam_address_form'))
 if data['data']['id'] != 'new':
  aWeb.wr(aWeb.button('save',  DIV=div, URL='ipam_address_info?op=update', FRM='ipam_address_form'))
  aWeb.wr(aWeb.button('trash', DIV=div, URL='ipam_address_delete', FRM='ipam_address_form', MSG='Are you really sure you want to delete address?'))
 else:
  aWeb.wr(aWeb.button('save',  DIV=div, URL='ipam_address_info?op=insert', FRM='ipam_address_form'))
 aWeb.wr("</ARTICLE>")

#
#
def address_delete(aWeb):
 res = aWeb.rest_call("ipam/address_delete",{'id':aWeb['id']})
 aWeb.wr("Deleted: %(status)s"%res)
