"""Module docstring.

HTML5 Ajax DNS module

"""
__author__= "Zacharias El Banna"
__version__ = "18.04.07GA"
__status__= "Production"

############################################ Servers ###########################################
def server_list(aWeb):
 res = aWeb.rest_call("dns_server_list")
 print "<ARTICLE><P>Domains</P><DIV CLASS='controls'>"
 print aWeb.button('reload',DIV='div_content_left',URL='sdcp.cgi?dns_server_list')
 print aWeb.button('add',DIV='div_content_right',URL='sdcp.cgi?dns_server_info&id=new',TITLE='Add domain')
 print "</DIV><DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Node</DIV><DIV CLASS=th>Server</DIV><DIV CLASS=th>&nbsp;</DIV></DIV><DIV CLASS=tbody>"
 for srv in res['servers']:
  print "<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td><DIV CLASS=controls>"%(srv['id'],srv['node'],srv['server'])
  print aWeb.button('info',DIV='div_content_right',URL='sdcp.cgi?dns_server_info&id=%s'%(srv['id']))
  print "</DIV></DIV></DIV>"
 print "</DIV></DIV>"
 print "</ARTICLE>"

#
#
def server_info(aWeb):
 args = aWeb.get_args2dict()
 res  = aWeb.rest_call("dns_server_info",args)
 data = res['data']
 print "<ARTICLE CLASS=info><P>Server</P>"
 print "<FORM ID=server_info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE=%s>"%(data['id'])
 print "<DIV CLASS=table STYLE='float:left; width:auto;'><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Node:</DIV><DIV CLASS=td><SELECT NAME=node>"
 for node in res['nodes']:
  extra = " selected" if (data['node'] == node['node']) else ""
  print "<OPTION VALUE=%s %s>%s</OPTION>"%(node['node'],extra,node['node'])
 print "</SELECT></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td>Server:</DIV><DIV CLASS=td><SELECT NAME=server>"
 for srv in res['servers']:
  extra = " selected" if (data['server'] == srv['server']) else ""
  print "<OPTION VALUE=%s %s>%s</OPTION>"%(srv['server'],extra,srv['server'])
 print "</SELECT></DIV></DIV>"
 print "</DIV></DIV>"
 print "</FORM><DIV CLASS=controls>"
 print aWeb.button('save',    DIV='div_content_right', URL='sdcp.cgi?dns_server_info&op=update', FRM='server_info_form')
 if data['id'] != 'new':
  print aWeb.button('trash', DIV='div_content_right', URL='sdcp.cgi?dns_server_delete&id=%s'%(data['id']), MSG='Delete server?')
 print "</DIV></ARTICLE>"

#
#
def server_delete(aWeb):
 res = aWeb.rest_call("dns_server_delete",{'id':aWeb['id']})
 print "<ARTICLE>%s</ARTICLE>"%str(res)


############################################ Domains ###########################################
#
#
def domain_list(aWeb):
 domains = aWeb.rest_call("dns_domain_list",{'sync':aWeb['sync']})
 print "<ARTICLE><P>Domains</P><DIV CLASS='controls'>"
 print aWeb.button('reload',DIV='div_content_left',URL='sdcp.cgi?dns_domain_list&sync=true',TITLE='Resync cache')
 print aWeb.button('add',DIV='div_content_right',URL='sdcp.cgi?dns_domain_info&id=new',TITLE='Add domain')
 print aWeb.button('search',DIV='div_content_right',URL='sdcp.cgi?dns_consistency',TITLE='Check Backend Consistency',SPIN='true')
 print aWeb.button('delete',DIV='div_content_right',URL='sdcp.cgi?dns_dedup',TITLE='Find Duplicates',SPIN='true')
 print aWeb.button('document',DIV='div_content_right',URL='sdcp.cgi?dns_top', SPIN='true')
 print "</DIV><DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Domain</DIV><DIV CLASS=th>Server</DIV><DIV CLASS=th>&nbsp;</DIV></DIV><DIV CLASS=tbody>"
 for dom in domains['domains']:
  print "<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL=sdcp.cgi?dns_record_list&type=%s&domain_id=%s>%s</A></DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td><DIV CLASS=controls>"%(dom['id'],"a" if not 'arpa' in dom['name'] else "ptr",dom['id'],dom['name'],dom['server'])
  print aWeb.button('info',DIV='div_content_right',URL='sdcp.cgi?dns_domain_info&id=%s'%(dom['id']))
  print "</DIV></DIV></DIV>"
 print "</DIV></DIV>"
 if domains.get('sync'):
  print "<SPAN>Added: %s, Removed: %s</SPAN>"%(domains['sync']['added'],domains['sync']['deleted'])
 print "</ARTICLE>"

#
# Domain info
def domain_info(aWeb):
 args = aWeb.get_args2dict()
 res  = aWeb.rest_call("dns_domain_info",args)
 data = res['data']
 print "<ARTICLE CLASS=info><P>Domain Info (%s)</P>"%data['id']
 print "<FORM ID=dns_info_form>"
 print "<DIV CLASS=table><DIV CLASS=tbody>"
 if data['id'] == 'new':
  print "<DIV CLASS=tr><DIV CLASS=td>Server</DIV><DIV CLASS=td><SELECT NAME=server_id>"
  for srv in res['servers']:
   print "<OPTION VALUE=%s>%s on %s</OPTION>"%(srv['id'],srv['server'],srv['node'])
  print "</SELECT></DIV></DIV>"
 else:
  print "<DIV CLASS=tr><DIV CLASS=td>Node:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=node VALUE=%s READONLY></DIV></DIV>"%(res['infra']['node'])
  print "<DIV CLASS=tr><DIV CLASS=td>Server:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=server VALUE=%s READONLY></DIV></DIV>"%(res['infra']['server'])
 print "<DIV CLASS=tr><DIV CLASS=td>Name:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=name VALUE=%s></DIV></DIV>"%(data['name'])
 print "<DIV CLASS=tr><DIV CLASS=td>Master:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=master VALUE=%s></DIV></DIV>"%(data['master'])
 print "<DIV CLASS=tr><DIV CLASS=td>Type:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=type VALUE=%s></DIV></DIV>"%(data['type'])
 print "<DIV CLASS=tr><DIV CLASS=td>Serial:</DIV><DIV CLASS=td>%s</DIV></DIV>"%(data['notified_serial'])
 print "</DIV></DIV>"
 print "<SPAN CLASS='results' ID=update_results>{}</SPAN>".format("lookup" if not aWeb.get('op') else aWeb['op'])
 print "<INPUT TYPE=HIDDEN NAME=id VALUE=%s>"%(data['id'])
 print "</FORM><DIV CLASS=controls>"
 print aWeb.button('reload',DIV='div_content_right',URL='sdcp.cgi?dns_domain_info&id=%s'%(data['id']))
 if data['id'] == 'new':
  print aWeb.button('save',DIV='div_content_right',URL='sdcp.cgi?dns_domain_info&op=update',FRM='dns_info_form')
 else:
  print aWeb.button('trash',DIV='div_content_right',URL='sdcp.cgi?dns_domain_%s&id=%s'%("transfer" if not "arpa" in data['name'] else "delete",data['id']))
 print "</DIV></ARTICLE>"

#
#
def domain_transfer(aWeb):
 domains = aWeb.rest_call("dns_domain_list",{"filter":"arpa","exclude":aWeb['id']})
 print "<ARTICLE STYLE='display:inline-block'>"
 print "<FORM ID=dns_transfer>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE=%s>"%(aWeb['id'])
 print "Transfer all records to <SELECT NAME=transfer>"
 for domain in domains['domains']:
  print "<OPTION VALUE=%s>%s</OPTION>"%(domain['id'],domain['name'])
 print "</SELECT>"
 print "</FORM><DIV CLASS=controls>"
 print aWeb.button('back',DIV='div_content_right',URL='sdcp.cgi?dns_domain_info',FRM='dns_transfer')
 print aWeb.button('forward',DIV='div_content_right',URL='sdcp.cgi?dns_domain_delete',FRM='dns_transfer')
 print "</DIV></ARTICLE>"

#
#
def domain_delete(aWeb):
 res = aWeb.rest_call("dns_domain_delete",{'from':aWeb['id'],'to':aWeb['transfer']})
 print "<ARTICLE>%s</ARTICLE>"%res

############################################ Records ###########################################
#
#
def record_list(aWeb):
 dns = aWeb.rest_call("dns_record_list",{'domain_id':aWeb['domain_id']})
 print "<ARTICLE><P>Records</P><DIV CLASS=controls>"
 print aWeb.button('reload',DIV='div_content_right',URL='sdcp.cgi?dns_record_list&domain_id=%s'%(aWeb['domain_id']))
 print aWeb.button('add',DIV='div_content_right',URL='sdcp.cgi?dns_record_info&id=new&domain_id=%s'%(aWeb['domain_id']))
 print "<SPAN CLASS='results' ID=span_dns>&nbsp;</SPAN>"
 print "</DIV><DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>Content</DIV><DIV CLASS=th>Type</DIV><DIV CLASS=th>TTL</DIV><DIV CLASS=th>&nbsp;</DIV></DIV><DIV CLASS=tbody>"
 for rec in dns['records']:
  print "<DIV CLASS=tr><DIV CLASS=td>%i</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>"%(rec['id'],rec['name'])
  print rec['content'] if not rec['type'] == 'A' else "<A CLASS=z-op DIV=div_content_right URL=sdcp.cgi?device_info&ip=%s>%s</A>"%(rec['content'],rec['content'])
  print "</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td><DIV CLASS=controls>"%(rec['type'],rec['ttl'])
  print aWeb.button('info',DIV='div_content_right',URL='sdcp.cgi?dns_record_info&id=%i&domain_id=%s'%(rec['id'],aWeb['domain_id']))
  if rec['type'] in ['A','CNAME','PTR']:
   print aWeb.button('delete',DIV='span_dns',URL='sdcp.cgi?dns_record_delete&id=%s&domain_id=%s'%(rec['id'],aWeb['domain_id']))
  print "</DIV></DIV></DIV>"
 print "</DIV></DIV>"
 print "</ARTICLE>"

#
#
def record_info(aWeb):
 args = aWeb.get_args2dict()
 res = aWeb.rest_call("dns_record_info",args)
 data = res['data']
 print "<ARTICLE CLASS=info><P>Record Info (%s)</P>"%(data['id'])
 print "<FORM ID=dns_info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id        VALUE={}>".format(data['id'])
 print "<INPUT TYPE=HIDDEN NAME=domain_id VALUE={}>".format(data['domain_id'])
 print "<DIV CLASS=table><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td TITLE='E.g. A:FQDN, PTR:x.y.z.in-addr.arpa'>Name:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=name VALUE={}></DIV></DIV>".format(data['name'])
 print "<DIV CLASS=tr><DIV CLASS=td TITLE='E.g. A:IP, PTR:FQDN'>Content:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=content VALUE='{}'></DIV></DIV>".format(data['content'])
 print "<DIV CLASS=tr><DIV CLASS=td>TTL:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=ttl VALUE={}></DIV></DIV>".format(data['ttl'])
 print "<DIV CLASS=tr><DIV CLASS=td>Type:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=type VALUE={}></DIV></DIV>".format(data['type'])
 print "<DIV CLASS=tr><DIV CLASS=td>Domain (id):</DIV><DIV CLASS=td>{}</DIV></DIV>".format(data['domain_id'])
 print "</DIV></DIV>"
 print "<SPAN CLASS='results' ID=update_results></SPAN>"
 print "</FORM><DIV CLASS=controls>"
 print aWeb.button('reload',DIV='div_content_right',URL='sdcp.cgi?dns_record_info&id=%s&domain_id=%s'%(data['id'],data['domain_id']))
 print aWeb.button('save',DIV='div_content_right',URL='sdcp.cgi?dns_record_info&op=update',FRM='dns_info_form')
 if not data['id'] == 'new':
  print aWeb.button('delete',DIV='div_content_right',URL='sdcp.cgi?dns_record_delete&id=%s&domain_id=%s'%(data['id'],data['domain_id']))
 print "</DIV></ARTICLE>"

#
#
def record_delete(aWeb):
 res = aWeb.rest_call("dns_record_delete",{'id': aWeb['id'],'domain_id': aWeb['domain_id']})
 print "<ARTICLE>Remove {} - Results:{}</ARTICLE>".format(aWeb['id'],res)

#
#
def record_transfer(aWeb):
 res = aWeb.rest_call("dns_record_transfer",{'device_id':aWeb['device_id'],'type':aWeb['type'],'record_id':aWeb['record_id']})
 print "Updated device %s - Results:%s"%(aWeb['device_id'],str(res))

#
#
def record_create(aWeb):
 res = aWeb.rest_call("dns_record_device_create",{'type':aWeb['type'],'domain_id':aWeb['domain_id'],'fqdn':aWeb['fqdn'],'ip':aWeb['ip'],'id':aWeb['id']})
 print "Create result:%s"%str(res)

############################################ Tools ###########################################
#
# Cleanup duplicate entries
#
def dedup(aWeb):
 dns = aWeb.rest_call("dns_dedup")
 print "<ARTICLE><P>Duplicate Removal</P>"
 print "<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Node</DIV><DIV CLASS=th>Server</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>Content</DIV></DIV><DIV CLASS=tbody>"
 for node_server,res in dns.iteritems():
  node,server = node_server.split('_')
  for row in res:
   print "<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV></DIV>"%(node,server,row['name'],row['content'])
 print "</DIV></DIV>"
 print "</ARTICLE>"


#
# DNS top
#
def top(aWeb):
 dns = aWeb.rest_call("dns_top")
 print "<ARTICLE STYLE='float:left; width:49%;'><P>Top looked up FQDN</P>"
 print "<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Node</DIV><DIV CLASS=th>Server</DIV><DIV CLASS=th>Hit</DIV><DIV CLASS=th>FQDN</DIV></DIV><DIV CLASS=tbody>"
 for node_server,res in dns['top'].iteritems():
  node,server = node_server.split('_')
  for row in res:
   print "<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV></DIV>"%(node,server,row['count'],row['fqdn'])
  print "</DIV></DIV>"
 print "</ARTICLE>"
 print "<ARTICLE STYLE='float:left; width:49%;'><P>Top looked up FQDN per Client</P>"
 print "<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Node</DIV><DIV CLASS=th>Server</DIV><DIV CLASS=th>Hit</DIV><DIV CLASS=th>Who</DIV><DIV CLASS=th>FQDN</DIV></DIV><DIV CLASS=tbody>"
 for node_server,res in dns['who'].iteritems():
  node,server = node_server.split('_')
  for row in res:
   print "<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td TITLE='%s'>%s</DIV><DIV CLASS=td>%s</DIV></DIV>"%(node,server,row['count'],row['who'],row['hostname'],row['fqdn'])
  print "</DIV></DIV>"
 print "</ARTICLE>"

#
#
def consistency(aWeb):
 data = aWeb.rest_call("dns_consistency")
 print "<ARTICLE><P>DNS Consistency</P><SPAN CLASS='results' ID=span_dns>&nbsp;</SPAN>"
 print "<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Key</DIV><DIV CLASS=th>Type</DIV><DIV CLASS=th>Value</DIV><DIV CLASS=th>Id</DIV><DIV CLASS=th>Id (Dev)</DIV><DIV CLASS=th>Hostname (Dev)</DIV><DIV CLASS=th>&nbsp;</DIV></DIV><DIV CLASS=tbody>"
 for rec in data['records']:
  print "<DIV CLASS=tr>"
  print "<DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV>"%(rec['name'],rec['type'],rec['content'],rec['id'])
  print "<DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV>"%(rec['dns_id'],rec['fqdn'])
  print "<DIV CLASS=td><DIV CLASS=controls>" + aWeb.button('delete',DIV='span_dns',MSG='Delete record?',URL='sdcp.cgi?dns_record_delete&id=%s'%(rec['id']))
  if rec['fqdn']:
   print aWeb.button('reload',DIV='span_dns',MSG='Update device info?',URL='sdcp.cgi?dns_record_transfer&record_id=%s&device_id=%s&type=%s'%(rec['id'],rec['device_id'],rec['type']))
  print "</DIV></DIV></DIV>"
 for dev in data['devices']:
  print "<DIV CLASS=tr>"
  print "<DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>-</DIV><DIV CLASS=td>-</DIV>"%(dev['ipasc'],dev['type'])
  print "<DIV CLASS=td>%s</DIV><DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL=sdcp.cgi?device_info&id=%s>%s</A></DIV>"%(dev['dns_id'],dev['device_id'],dev['fqdn'])
  print "<DIV CLASS=td>&nbsp;" + aWeb.button('add',DIV='span_dns',URL='sdcp.cgi?dns_record_create&type={}&id={}&ip={}&fqdn={}&domain_id={}'.format(dev['type'],dev['device_id'],dev['ipasc'],dev['fqdn'],dev['domain_id']))
  print "</DIV></DIV>"
 print "</DIV></DIV>"
 print "</ARTICLE>"

