"""Module docstring.

HTML5 Ajax DNS calls module

"""
__author__= "Zacharias El Banna"
__version__ = "18.02.09GA"
__status__= "Production"

############################################ Domains ###########################################
#
#
def list(aWeb):
 domains = aWeb.rest_call("sdcpdns_domains")
 print "<ARTICLE><P>Domains</P>"
 print "<DIV CLASS='controls'>"
 print aWeb.button('reload',DIV='div_content_left',URL='sdcp.cgi?call=dns_list')
 print aWeb.button('add',DIV='div_content_right',URL='sdcp.cgi?call=dns_domain_info&id=new',TITLE='Add domain')
 print aWeb.button('search',DIV='div_content_right',URL='sdcp.cgi?call=dns_consistency',TITLE='Check Backend Consistency',SPIN='true')
 print aWeb.button('delete',DIV='div_content_right',URL='sdcp.cgi?call=dns_dedup',TITLE='Find Duplicates',SPIN='true')
 print "</DIV>"
 print "<DIV CLASS=table>"
 print "<DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Domain</DIV><DIV CLASS=th>Serial</DIV><DIV CLASS=th>&nbsp;</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for dom in domains['domains']:
  print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL=sdcp.cgi?call=dns_records&type={}&id={}>{}</A></DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>&nbsp;".format(dom['id'],"a" if not 'arpa' in dom['name'] else "ptr",dom['id'],dom['name'],dom['notified_serial'])
  print aWeb.button('info',DIV='div_content_right',URL='sdcp.cgi?call=dns_domain_info&id=%s'%(dom['id']))
  print "</DIV></DIV>"
 print "</DIV></DIV>"
 print "</ARTICLE>"

#
# Domain info
def domain_info(aWeb):
 if aWeb['op'] == 'update':
  data = aWeb.get_args2dict(['call','op'])
  res = aWeb.rest_call("sdcpdns_domain_update",data)
  data['id'] = res['id']
 else:
  res = aWeb.rest_call("sdcpdns_domain_lookup",{'id':aWeb['id']})
  data = res['data']
 lock = "readonly" if not data['id'] == 'new' else ""
 print "<ARTICLE CLASS=info><P>Domain Info{}</P>".format(" (new)" if data['id'] == 'new' else "")
 print "<FORM ID=dns_info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(data['id'])
 print "<DIV CLASS=table><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Name:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=name VALUE={}></DIV></DIV>".format(data['name'])
 print "<DIV CLASS=tr><DIV CLASS=td>Master:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=master VALUE={}></DIV></DIV>".format(data['master'])
 print "<DIV CLASS=tr><DIV CLASS=td>Type:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=type VALUE={}></DIV></DIV>".format(data['type'])
 print "</DIV></DIV>"
 print "<SPAN CLASS='results' ID=update_results>{}</SPAN>".format("lookup" if not aWeb.get('op') else aWeb['op'])
 print "</FORM><DIV CLASS=controls>"
 print aWeb.button('reload',DIV='div_content_right',URL='sdcp.cgi?call=dns_domain_info&id={}'.format(data['id']))
 if data['id'] == 'new':
  print aWeb.button('save',DIV='div_content_right',URL='sdcp.cgi?call=dns_domain_info&op=update',FRM='dns_info_form')
 else:
  if not "arpa" in data['name']:
   print aWeb.button('delete',DIV='div_content_right',URL='sdcp.cgi?call=dns_domain_transfer&id={}'.format(data['id']))
  else:
   print aWeb.button('delete',DIV='div_content_right',URL='sdcp.cgi?call=dns_domain_delete&id={}'.format(data['id']))
 print "</DIV></ARTICLE>"

#
#
def domain_transfer(aWeb):
 domains = aWeb.rest_call("sdcpdns_domains",{"filter":"arpa","exclude":aWeb['id']})
 print "<ARTICLE STYLE='display:inline-block'>"
 print "<FORM ID=dns_transfer><INPUT TYPE=HIDDEN NAME=id VALUE=%s>"%(aWeb['id'])
 print "Transfer all records to <SELECT NAME=transfer>"
 for domain in domains['domains']:
  print "<OPTION VALUE={}>{}</OPTION>".format(domain['id'],domain['name'])
 print "</SELECT>"
 print "</FORM><DIV CLASS=controls>"
 print aWeb.button('back',DIV='div_content_right',URL='sdcp.cgi?call=dns_domain_info&id=%s'%(aWeb['id']))
 print aWeb.button('next',DIV='div_content_right',URL='sdcp.cgi?call=dns_domain_delete',FRM='dns_transfer')
 print "</DIV></ARTICLE>"

#
#
def domain_delete(aWeb):
 res = aWeb.rest_call("sdcpdns_domain_delete",{'from':aWeb['id'],'to':aWeb['transfer']})
 print "<ARTICLE>%s</ARTICLE>"%res

############################################ Records ###########################################
#
#
def records(aWeb):
 dns = aWeb.rest_call("sdcpdns_records",{'domain_id':aWeb['id']})
 print "<ARTICLE><P>Records</P><DIV CLASS=controls>"
 print aWeb.button('reload',DIV='div_content_right',URL='sdcp.cgi?call=dns_records&id=%s'%(aWeb['id']))
 print aWeb.button('add',DIV='div_content_right',URL='sdcp.cgi?call=dns_record_info&id=new&domain_id=%s'%(aWeb['id']))
 print "<SPAN CLASS='results' ID=span_dns>&nbsp;</SPAN>"
 print "</DIV><DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>Content</DIV><DIV CLASS=th>Type</DIV><DIV CLASS=th>TTL</DIV><DIV CLASS=th>&nbsp;</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for rec in dns['records']:
  print "<DIV CLASS=tr><DIV CLASS=td>%i</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>"%(rec['id'],rec['name'])
  print rec['content'] if not rec['type'] == 'A' else "<A CLASS=z-op DIV=div_content_right URL=sdcp.cgi?call=device_info&ip=%s>%s</A>"%(rec['content'],rec['content'])
  print "</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>&nbsp;"%(rec['type'],rec['ttl'])
  print aWeb.button('info',DIV='div_content_right',URL='sdcp.cgi?call=dns_record_info&id=%i&domain_id=%s'%(rec['id'],aWeb['id']))
  if rec['type'] in ['A','CNAME','PTR']:
   print aWeb.button('delete',DIV='span_dns',URL='sdcp.cgi?call=dns_record_delete&id=%i'%(rec['id']))
  print "</DIV></DIV>"
 print "</DIV></DIV>"
 print "</ARTICLE>"

#
#
def record_info(aWeb):
 if aWeb['op'] == 'update':
  data = aWeb.get_args2dict(['call','op'])
  res = aWeb.rest_call("sdcpdns_record_update",data)
  data['id'] = res['id']
 else:
  res = aWeb.rest_call("sdcpdns_record_lookup",{'id':aWeb['id'],'domain_id':aWeb['domain_id']})
  data = res['data']
 lock = "readonly" if not data['id'] == 'new' else ""
 print "<ARTICLE CLASS=info><P>Record Info {} (Domain {})</P>".format("(new)" if data['id'] == 'new' else "",data['domain_id'])
 print "<!-- {} -->".format(res)
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
 print aWeb.button('reload',DIV='div_content_right',URL='sdcp.cgi?call=dns_record_info&id={}&domain_id={}'.format(data['id'],data['domain_id']))
 print aWeb.button('save',DIV='div_content_right',URL='sdcp.cgi?call=dns_record_info&op=update',FRM='dns_info_form')
 if not data['id'] == 'new':
  print aWeb.button('delete',DIV='div_content_right',URL='sdcp.cgi?call=dns_record_delete&id={}'.format(data['id']))
 print "</DIV></ARTICLE>"

#
#
def record_delete(aWeb):
 res = aWeb.rest_call("sdcpdns_record_delete",{'id': aWeb['id']})
 print "<ARTICLE>Remove {} - Results:{}</ARTICLE>".format(aWeb['id'],res)

#
#
def record_create(aWeb):
 res = aWeb.rest_call("sdcpdns_record_auto_create",{'type':aWeb['type'],'domain_id':aWeb['domain_id'],'fqdn':aWeb['fqdn'],'ip':aWeb['ip'],'id':aWeb['id']})
 print "Create result:%s"%str(res)

#
#
def record_transfer(aWeb):
 res = aWeb.rest_call("device_update",{'id':aWeb['dev'],'devices_%s_id'%aWeb['type']:aWeb['id']})
 print "Updated device %s - Results:%s"%(aWeb['dev'],str(res))

############################################ Tools ###########################################
#
#
def load_cache(aWeb):
 res = aWeb.rest_call("sdcpdns_domains",{'sync':True})
 print "<ARTICLE>Added:%s Removed:%s</ARTICLE>"%(res['added'],res['deleted'])

#
# DNS top
#
def top(aWeb):
 dnstop = aWeb.rest_call("sdcpdns_top", {'count':20})
 print "<ARTICLE STYLE='float:left; width:49%;'><P>Top looked up FQDN</P>"
 if len(dnstop['top']) > 0:
  print "<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Count</DIV><DIV CLASS=th>FQDN</DIV></DIV><DIV CLASS=tbody>"
  for row in dnstop['top']:
   print "<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV></DIV>"%(row['count'],row['fqdn'])
  print "</DIV></DIV>"
 print "</ARTICLE>"
 print "<ARTICLE STYLE='float:left; width:49%;'><P>Top looked up FQDN per Client</P>"
 if len(dnstop['who']) > 0:
  print "<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Count</DIV><DIV CLASS=th>FQDN</DIV><DIV CLASS=th>Who</DIV><DIV CLASS=th>Hostname</DIV></DIV><DIV CLASS=tbody>"
  for row in dnstop['who']:
   print "<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV></DIV>"%(row['count'],row['fqdn'],row['who'],row['hostname'])
  print "</DIV></DIV>"
 print "</ARTICLE>"

#
# Cleanup duplicate entries
#
def dedup(aWeb):
 dns = aWeb.rest_call("sdcpdns_dedup")
 print "<ARTICLE><P>Duplicate Removal</P>"
 if len(dns['removed']) > 0:
  print "<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Name</DIV><DIV CLASS=th>Content</DIV></DIV><DIV CLASS=tbody>"
  for row in dns['removed']:
   print "<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV></DIV>"%(row['name'],row['content'])
  print "</DIV></DIV>"
 print "</ARTICLE>"

#
#
def consistency(aWeb):
 print "<ARTICLE><P>DNS Consistency</P><SPAN CLASS='results' ID=span_dns>&nbsp;</SPAN>"
 print "<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Value</DIV><DIV CLASS=th>Type</DIV><DIV CLASS=th>Key</DIV><DIV CLASS=th>Id</DIV><DIV CLASS=th>Id (Dev)</DIV><DIV CLASS=th>Hostname (Dev)</DIV><DIV CLASS=th>&nbsp;</DIV></DIV><DIV CLASS=tbody>"
 domains = aWeb.rest_call("sdcpdns_domains_cache",{'dict':'name'})['domains']
 for type in ['a','ptr']:
  records = aWeb.rest_call("sdcpdns_records",{'type':type})['records']
  tid = "{}_id".format(type)
  devices = aWeb.rest_call("device_list",{"dict":"ipasc" if type == 'a' else "fqdn"})['data']
  for rec in records:
   dev = devices.pop(rec['content'],None)
   if not dev or dev[tid] != rec['id']:
    print "<DIV CLASS=tr>"
    print "<!-- %s -->"%str(rec)
    print "<!-- %s -->"%str(dev)
    print "<DIV CLASS=td>{}</DIV>".format(rec['content'])
    print "<DIV CLASS=td>{}</DIV>".format(rec['type'])
    print "<DIV CLASS=td>{}</DIV>".format(rec['name'])
    print "<DIV CLASS=td>{}</DIV>".format(rec['id'])
    if dev:
     print "<DIV CLASS=td>{}</DIV>".format(dev[tid])
     print "<DIV CLASS=td>{0}</DIV>".format(dev['fqdn'])
    else:
     print "<DIV CLASS=td>-</DIV><DIV CLASS=td>-</DIV>"
    print "<DIV CLASS=td>&nbsp;" + aWeb.button('delete',DIV='span_dns',MSG='Delete record?',URL='sdcp.cgi?call=dns_record_delete&id={}'.format(rec['id']))
    if dev:
     print aWeb.button('reload',DIV='span_dns',MSG='Update device info?',URL='sdcp.cgi?call=dns_record_transfer&id={}&dev={}&type={}'.format(rec['id'],dev['id'],type))
    print "</DIV></DIV>"

  if len(devices) > 0:
   from ..core import genlib as GL
   for key,value in  devices.iteritems():
    print "<DIV CLASS=tr>"
    print "<!-- %s -> %s -->"%(key,value)
    print "<DIV CLASS=td>{}</DIV><DIV CLASS=td>-</DIV>".format(key)
    print "<DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL=sdcp.cgi?call=device_info&id={0}>{1}</A></DIV><DIV CLASS=td>-</DIV><DIV CLASS=td>{0}</DIV><DIV CLASS=td>{1}</DIV>".format(value['id'],value['fqdn'] if type == 'a' else value['ipasc'])
    print "<DIV CLASS=td>&nbsp;" + aWeb.button('add',DIV='span_dns',URL='sdcp.cgi?call=dns_record_create&type={}&id={}&ip={}&fqdn={}&domain_id={}'.format(type,value['id'],value['ipasc'],value['fqdn'],value['a_dom_id'] if type == 'a' else domains[GL.ip2arpa(value['ipasc'])]['id'] )) + "</DIV>"
    print "</DIV>"
 print "</DIV></DIV>"

 print "</ARTICLE>"
