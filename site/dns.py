"""HTML5 Ajax DNS module"""
__author__= "Zacharias El Banna"

############################################ Domains ###########################################
#
#
def domain_list(aWeb):
 domains = aWeb.rest_call("dns/domain_list",{'sync':True if aWeb['sync'] == 'true' else False})
 aWeb.wr("<ARTICLE><P>Domains</P>")
 aWeb.wr(aWeb.button('items', DIV='div_content_left', URL='dns_domain_list',TITLE='List domains'))
 aWeb.wr(aWeb.button('sync',   DIV='div_content_left', URL='dns_domain_list?sync=true',TITLE='Resync cache'))
 aWeb.wr(aWeb.button('add',    DIV='div_content_right',URL='dns_domain_info?id=new',TITLE='Add domain'))
 aWeb.wr(aWeb.button('search', DIV='div_content_right',URL='dns_consistency',TITLE='Check Backend Consistency',SPIN='true'))
 aWeb.wr(aWeb.button('document',DIV='div_content_right',URL='dns_status', SPIN='true'))
 if domains.get('sync'):
  aWeb.wr("<SPAN CLASS='results'>%s</SPAN>"%(domains['sync']))
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Domain</DIV><DIV CLASS=th>Server</DIV><DIV CLASS=th>&nbsp;</DIV></DIV><DIV CLASS=tbody>")
 for dom in domains['domains']:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%(id)s</DIV><DIV CLASS=td>%(name)s</DIV><DIV CLASS=td>%(service)s</DIV><DIV CLASS=td>"%dom)
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
 aWeb.wr("<DIV CLASS=table><DIV CLASS=tbody>")
 if res['id'] == 'new' and res.get('servers'):
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Server</DIV><DIV CLASS=td><SELECT NAME=server_id>")
  for srv in res['servers']:
   aWeb.wr("<OPTION VALUE=%s>%s on %s</OPTION>"%(srv['id'],srv['service'],srv['node']))
  aWeb.wr("</SELECT></DIV></DIV>")
 else:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Node:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=node VALUE=%s READONLY></DIV></DIV>"%(res['infra']['node']))
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Service:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=service VALUE=%s READONLY></DIV></DIV>"%(res['infra']['service']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Name:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=name VALUE=%s></DIV></DIV>"%(data['name']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Master:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=master VALUE=%s></DIV></DIV>"%(data['master']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Type:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=type VALUE=%s></DIV></DIV>"%(data['type']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Serial:</DIV><DIV CLASS=td>%s</DIV></DIV>"%(data['notified_serial']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Foreign ID:</DIV><DIV CLASS=td>%s</DIV></DIV>"%(data['id']))
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("<SPAN CLASS='results' ID=update_results>{}</SPAN>".format("lookup" if not aWeb.get('op') else aWeb['op']))
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=id VALUE=%s>"%(res['id']))
 aWeb.wr("</FORM>")
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
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>Content</DIV><DIV CLASS=th>Type</DIV><DIV CLASS=th>TTL</DIV><DIV CLASS=th>&nbsp;</DIV></DIV><DIV CLASS=tbody>")
 for rec in dns['records']:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%i</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>"%(rec['id'],rec['name']))
  aWeb.wr(rec['content'] if not rec['type'] == 'A' else "<A CLASS=z-op DIV=div_content_right URL='device_info?ip=%s'>%s</A>"%(rec['content'],rec['content']))
  aWeb.wr("</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>"%(rec['type'],rec['ttl']))
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
 aWeb.wr("<DIV CLASS=table><DIV CLASS=tbody>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td TITLE='E.g. A:FQDN, PTR:x.y.z.in-addr.arpa'>Name:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=name VALUE={}></DIV></DIV>".format(data['name']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td TITLE='E.g. A:IP, PTR:FQDN'>Content:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=content VALUE='{}'></DIV></DIV>".format(data['content']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>TTL:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=ttl VALUE={}></DIV></DIV>".format(data['ttl']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Type:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=type VALUE={}></DIV></DIV>".format(data['type']))
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("<SPAN CLASS='results' ID=update_results></SPAN>")
 aWeb.wr("</FORM>")
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

#
#
def record_correct(aWeb):
 args = aWeb.args()
 res = aWeb.rest_call("dns/record_device_correct",args)
 aWeb.wr("Updated device %s - Results:%s"%(aWeb['device_id'],str(res)))

#
#
def record_create(aWeb):
 args = aWeb.args()
 res = aWeb.rest_call("dns/record_device_create",args)
 aWeb.wr("Create result:%s"%str(res))

############################################ Tools ###########################################
#
# Cleanup duplicate entries
#
def sync(aWeb):
 dns = aWeb.rest_call("dns/sync")
 aWeb.wr("<ARTICLE><P>Duplicate Removal</P>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Node</DIV><DIV CLASS=th>Service</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>Content</DIV></DIV><DIV CLASS=tbody>")
 for node_service,res in dns.items():
  node,service = node_service.split('_')
  for row in res:
   aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV></DIV>"%(node,service,row['name'],row['content']))
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</ARTICLE>")


def status(aWeb):
 dns = aWeb.rest_call("dns/status")
 aWeb.wr("<ARTICLE STYLE='float:left; width:49%;'><P>Top looked up FQDN</P>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Node</DIV><DIV CLASS=th>Service</DIV><DIV CLASS=th>Hit</DIV><DIV CLASS=th>FQDN</DIV></DIV><DIV CLASS=tbody>")
 for node_service,res in dns['top'].items():
  node,service = node_service.split('_')
  for row in res:
   aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV></DIV>"%(node,service,row['count'],row['fqdn']))
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</ARTICLE>")
 aWeb.wr("<ARTICLE STYLE='float:left; width:49%;'><P>Top looked up FQDN per Client</P>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Node</DIV><DIV CLASS=th>Service</DIV><DIV CLASS=th>Hit</DIV><DIV CLASS=th>Who</DIV><DIV CLASS=th>FQDN</DIV></DIV><DIV CLASS=tbody>")
 for node_service,res in dns['who'].items():
  node,service = node_service.split('_')
  for row in res:
   aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td TITLE='%s'>%s</DIV><DIV CLASS=td>%s</DIV></DIV>"%(node,service,row['count'],row['who'],row['hostname'],row['fqdn']))
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</ARTICLE>")

#
#
def consistency(aWeb):
 data = aWeb.rest_call("dns/consistency_check")
 aWeb.wr("<ARTICLE><P>DNS Consistency</P><SPAN CLASS='results' ID=span_dns>&nbsp;</SPAN>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Key</DIV><DIV CLASS=th>Type</DIV><DIV CLASS=th>Value</DIV><DIV CLASS=th>Rec Id</DIV><DIV CLASS=th>Dev Id</DIV><DIV CLASS=th>Dev Record</DIV><DIV CLASS=th>Dev FQDN</DIV><DIV CLASS=th>&nbsp;</DIV></DIV><DIV CLASS=tbody>")
 for rec in data['records']:
  aWeb.wr("<DIV CLASS=tr>")
  aWeb.wr("<DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV>"%(rec['name'],rec['type'],rec['content'],rec['id']))
  aWeb.wr("<DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV>"%(rec['device_id'],rec['record_id'],rec['fqdn']))
  aWeb.wr("<DIV CLASS=td>")
  aWeb.wr(aWeb.button('delete',DIV='span_dns',MSG='Delete record?',URL='dns_record_delete?domain_id=%s&id=%s'%(rec['domain_id'],rec['id'])))
  if rec['device_id']:
   aWeb.wr(aWeb.button('reload',DIV='span_dns',MSG='Update device info?',URL='dns_record_correct?&domain_id=%s&record_id=%s&device_id=%s&type=%s'%(rec['domain_id'],rec['id'],rec['device_id'],rec['type'])))
  aWeb.wr("</DIV></DIV>")
 for dev in data['devices']:
  aWeb.wr("<DIV CLASS=tr>")
  aWeb.wr("<DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>-</DIV><DIV CLASS=td>-</DIV>"%(dev['ip'],dev['type']))
  aWeb.wr("<DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL='device_info?id=%s'>%s</A></DIV>"%(dev['device_id'],dev['record_id'],dev['device_id'],dev['fqdn']))
  aWeb.wr("<DIV CLASS=td>")
  aWeb.wr(aWeb.button('add',DIV='span_dns',URL='dns_record_create?type={}&device_id={}&ip={}&fqdn={}&domain_id={}'.format(dev['type'],dev['device_id'],dev['ip'],dev['fqdn'],dev['domain_id'])))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</ARTICLE>")
