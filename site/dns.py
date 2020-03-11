"""HTML5 Ajax DNS module"""
__author__= "Zacharias El Banna"

############################################ Domains ###########################################
#
#
def domain_list(aWeb):
 domains = aWeb.rest_call("dns/domain_list",{'sync':True if aWeb['sync'] == 'true' else False})
 aWeb.wr("<ARTICLE><P>Domains</P>")
 aWeb.wr(aWeb.button('reload', DIV='div_content_left', URL='dns_domain_list',TITLE='List domains'))
 aWeb.wr(aWeb.button('sync',   DIV='div_content_left', URL='dns_domain_list?sync=true',TITLE='Resync cache'))
 aWeb.wr(aWeb.button('add',    DIV='div_content_right',URL='dns_domain_info?id=new',TITLE='Add domain'))
 aWeb.wr(aWeb.button('document',DIV='div_content_right',URL='dns_status', SPIN='true'))
 if domains.get('sync'):
  aWeb.wr("<SPAN CLASS='results'>%s</SPAN>"%(domains['sync']))
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV>ID</DIV><DIV>Domain</DIV><DIV>Server</DIV><DIV>&nbsp;</DIV></DIV><DIV CLASS=tbody>")
 for dom in domains['data']:
  aWeb.wr("<DIV><DIV>%(id)s</DIV><DIV>%(name)s</DIV><DIV>%(service)s</DIV><DIV>"%dom)
  aWeb.wr(aWeb.button('info', DIV='div_content_right',URL='dns_domain_info?id=%s'%(dom['id'])))
  aWeb.wr(aWeb.button('items',DIV='div_content_right',URL='dns_record_list?domain_id=%s'%(dom['id'])))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</ARTICLE>")

#
# Domain info
def domain_info(aWeb):
 args = aWeb.args()
 res  = aWeb.rest_call("dns/domain_info",args)
 data = res['data']
 aWeb.wr("<ARTICLE CLASS=info><P>Domain Info (%s)</P>"%res['id'])
 aWeb.wr("<FORM ID=dns_domain_info_form>")
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=id VALUE=%s>"%(res['id']))
 aWeb.wr("<DIV CLASS='info col2'>")
 if res['id'] == 'new' and res.get('servers'):
  aWeb.wr("<label for='server_id'>Server</label><SELECT id='server_id' NAME=server_id>")
  for srv in res['servers']:
   aWeb.wr("<OPTION VALUE=%s>%s on %s</OPTION>"%(srv['id'],srv['service'],srv['node']))
  aWeb.wr("</SELECT>")
 else:
  aWeb.wr("<label for='node'>Node:</label><span id='node'>%s</span>"%(res['infra']['node']))
  aWeb.wr("<label for='service'>Service:</label><span id='service'>%s</span>"%(res['infra']['service']))
 aWeb.wr("<label for='name'>Name:</label><INPUT id='name' TYPE=TEXT NAME=name VALUE=%s>"%(data['name']))
 aWeb.wr("<label for='master'>Master:</label><INPUT id='master' TYPE=TEXT NAME=master VALUE=%s>"%(data['master']))
 aWeb.wr("<label for='type'>Type:</label><INPUT id='type' TYPE=TEXT NAME=type VALUE=%s>"%(data['type']))
 aWeb.wr("<label for='notified_serial'>Serial:</label><span id='notified_serial'>%s</span>"%(data['notified_serial']))
 if not res['id'] == 'new':
  aWeb.wr("<label for='foreign_id'>Foreign ID:</label><span id='foreign_id'>%s</span>"%(data['id']))
 aWeb.wr("</DIV>")
 aWeb.wr("</FORM>")
 aWeb.wr("<SPAN CLASS='results' ID=update_results>{}</SPAN>".format("lookup" if not aWeb.get('op') else aWeb['op']))
 if res['id'] == 'new':
  aWeb.wr(aWeb.button('save',DIV='div_content_right',URL='dns_domain_info?op=update',FRM='dns_domain_info_form'))
 else:
  aWeb.wr(aWeb.button('reload',DIV='div_content_right',URL='dns_domain_info?id=%s'%(res['id'])))
  aWeb.wr(aWeb.button('trash',DIV='div_content_right',URL='dns_domain_delete?id=%s'%res['id']))
 aWeb.wr("</ARTICLE>")

#
#
def domain_delete(aWeb):
 res = aWeb.rest_call("dns/domain_delete",{'id':aWeb['id']})
 aWeb.wr("<ARTICLE>%s</ARTICLE>"%res)

#
#
def domain_save(aWeb):
 args = aWeb.args()
 res = aWeb.rest_call("dns/domain_save",args)
 aWeb.wr("Save result:%s"%str(res))


############################################ Records ###########################################
#
#
def record_list(aWeb):
 dns = aWeb.rest_call("dns/record_list",{'domain_id':aWeb['domain_id']})
 aWeb.wr("<ARTICLE><P>Records</P>")
 aWeb.wr(aWeb.button('reload',DIV='div_content_right',URL='dns_record_list?domain_id=%s'%(aWeb['domain_id'])))
 aWeb.wr(aWeb.button('save',  DIV='div_content_right',URL='dns_domain_save?id=%s'%(aWeb['domain_id'])))
 aWeb.wr(aWeb.button('add',   DIV='div_content_right',URL='dns_record_info?id=new&domain_id=%s'%(aWeb['domain_id'])))
 aWeb.wr("<SPAN CLASS='results' ID=span_dns>&nbsp;</SPAN>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV>ID</DIV><DIV>Name</DIV><DIV>Content</DIV><DIV>Type</DIV><DIV>TTL</DIV><DIV>&nbsp;</DIV></DIV><DIV CLASS=tbody>")
 for rec in dns['records']:
  aWeb.wr("<DIV><DIV>%(id)s</DIV><DIV>%(name)s</DIV><DIV>%(content)s</DIV><DIV>%(type)s</DIV><DIV>%(ttl)s</DIV><DIV>"%rec)
  aWeb.wr(aWeb.button('info',DIV='div_content_right',URL='dns_record_info?id=%i&domain_id=%s'%(rec['id'],aWeb['domain_id'])))
  if rec['type'] in ['A','CNAME','PTR']:
   aWeb.wr(aWeb.button('delete',DIV='span_dns',URL='dns_record_delete?id=%s&domain_id=%s'%(rec['id'],aWeb['domain_id'])))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</ARTICLE>")

#
#
def record_info(aWeb):
 args = aWeb.args()
 res = aWeb.rest_call("dns/record_info",args)
 data = res['data']
 aWeb.wr("<ARTICLE CLASS=info><P>Record Info (%s)</P>"%(data['id']))
 aWeb.wr("<FORM ID=dns_record_info_form>")
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=id        VALUE={}>".format(data['id']))
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=domain_id VALUE={}>".format(data['domain_id']))
 aWeb.wr("<DIV CLASS='info col2'>")
 aWeb.wr("<label for='name' TITLE='E.g. A:FQDN, PTR:x.y.z.in-addr.arpa'>Name:</label><INPUT id='name' TYPE=TEXT NAME=name VALUE={}>".format(data['name']))
 aWeb.wr("<label for='content' TITLE='E.g. A:IP, PTR:FQDN'>Content:</label><INPUT id='content' TYPE=TEXT NAME=content VALUE='{}'>".format(data['content']))
 aWeb.wr("<label for='ttl'>TTL:</label><INPUT id='ttl' TYPE=TEXT NAME=ttl VALUE={}>".format(data['ttl']))
 aWeb.wr("<label for='type'>Type:</label><INPUT id='type' TYPE=TEXT NAME=type VALUE={}>".format(data['type']))
 aWeb.wr("</DIV>")
 aWeb.wr("</FORM>")
 aWeb.wr("<SPAN CLASS='results' ID=update_results></SPAN>")
 aWeb.wr(aWeb.button('reload',DIV='div_content_right',URL='dns_record_info?id=%s&domain_id=%s'%(data['id'],data['domain_id'])))
 aWeb.wr(aWeb.button('save',DIV='div_content_right',URL='dns_record_info?op=update',FRM='dns_record_info_form'))
 if not data['id'] == 'new':
  aWeb.wr(aWeb.button('delete',DIV='div_content_right',URL='dns_record_delete?id=%s&domain_id=%s'%(data['id'],data['domain_id'])))
 aWeb.wr("</ARTICLE>")

#
#
def record_delete(aWeb):
 res = aWeb.rest_call("dns/record_delete",{'id': aWeb['id'],'domain_id': aWeb['domain_id']})
 aWeb.wr("<ARTICLE>Remove {} - Results:{}</ARTICLE>".format(aWeb['id'],res))

############################################ Tools ###########################################
#
# Cleanup duplicate entries
#
def sync(aWeb):
 dns = aWeb.rest_call("dns/sync")
 aWeb.wr("<ARTICLE><P>Duplicate Removal</P>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV>Node</DIV><DIV>Service</DIV><DIV>Name</DIV><DIV>Content</DIV></DIV><DIV CLASS=tbody>")
 for node_service,res in dns.items():
  node,service = node_service.split('_')
  for row in res:
   aWeb.wr("<DIV><DIV>%s</DIV><DIV>%s</DIV><DIV>%s</DIV><DIV>%s</DIV></DIV>"%(node,service,row['name'],row['content']))
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</ARTICLE>")


def status(aWeb):
 dns = aWeb.rest_call("dns/status")
 aWeb.wr("<ARTICLE STYLE='float:left; width:49%;'><P>Top looked up FQDN</P>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV>Node</DIV><DIV>Service</DIV><DIV>Hit</DIV><DIV>FQDN</DIV></DIV><DIV CLASS=tbody>")
 for node_service,res in dns['top'].items():
  node,service = node_service.split('_')
  for row in res:
   aWeb.wr("<DIV><DIV>%s</DIV><DIV>%s</DIV><DIV>%s</DIV><DIV>%s</DIV></DIV>"%(node,service,row['count'],row['fqdn']))
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</ARTICLE>")
 aWeb.wr("<ARTICLE STYLE='float:left; width:49%;'><P>Top looked up FQDN per Client</P>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV>Node</DIV><DIV>Service</DIV><DIV>Hit</DIV><DIV>Who</DIV><DIV>FQDN</DIV></DIV><DIV CLASS=tbody>")
 for node_service,res in dns['who'].items():
  node,service = node_service.split('_')
  for row in res:
   aWeb.wr("<DIV><DIV>%s</DIV><DIV>%s</DIV><DIV>%s</DIV><DIV TITLE='%s'>%s</DIV><DIV>%s</DIV></DIV>"%(node,service,row['count'],row['who'],row['hostname'],row['fqdn']))
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</ARTICLE>")

#
#
def consistency(aWeb):
 data = aWeb.rest_call("dns/consistency_check")
 aWeb.wr("<ARTICLE><P>DNS Consistency</P><SPAN CLASS='results' ID=span_dns>&nbsp;</SPAN>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV>Key</DIV><DIV>Type</DIV><DIV>Value</DIV><DIV>Rec Id</DIV><DIV>Dev Id</DIV><DIV>Dev Record</DIV><DIV>Dev FQDN</DIV><DIV>&nbsp;</DIV></DIV><DIV CLASS=tbody>")
 for rec in data['records']:
  aWeb.wr("<DIV>")
  aWeb.wr("<DIV>%s</DIV><DIV>%s</DIV><DIV>%s</DIV><DIV>%s</DIV>"%(rec['name'],rec['type'],rec['content'],rec['id']))
  aWeb.wr("<DIV>%s</DIV><DIV>%s</DIV><DIV>%s</DIV>"%(rec['device_id'],rec['record_id'],rec['fqdn']))
  aWeb.wr("<DIV>")
  aWeb.wr(aWeb.button('delete',DIV='span_dns',MSG='Delete record?',URL='dns_record_delete?domain_id=%s&id=%s'%(rec['domain_id'],rec['id'])))
  if rec['device_id']:
   aWeb.wr(aWeb.button('reload',DIV='span_dns',MSG='Update device info?',URL='dns_record_correct?&domain_id=%s&record_id=%s&device_id=%s&type=%s'%(rec['domain_id'],rec['id'],rec['device_id'],rec['type'])))
  aWeb.wr("</DIV></DIV>")
 for dev in data['ip_addresses']:
  aWeb.wr("<DIV>")
  aWeb.wr("<DIV>%s</DIV><DIV>%s</DIV><DIV>-</DIV><DIV>-</DIV>"%(dev['ip'],dev['type']))
  aWeb.wr("<DIV>%s</DIV><DIV>%s</DIV><DIV><A CLASS=z-op DIV=div_content_right URL='device_info?id=%s'>%s</A></DIV>"%(dev['device_id'],dev['record_id'],dev['device_id'],dev['fqdn']))
  aWeb.wr("<DIV></DIV></DIV>")
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</ARTICLE>")
