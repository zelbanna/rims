"""Module docstring.

HTML5 Ajax DNS calls module

"""
__author__= "Zacharias El Banna"
__version__ = "18.02.09GA"
__status__= "Production"

from .. import SettingsContainer as SC

############################################ Domains ###########################################
#
#
def list(aWeb):
 domains = aWeb.rest_generic(SC.dns['url'], "%s_domains"%SC.dns['type'])
 local   = aWeb.rest_call("sdcpdns_domains",{'index':'id'})
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
  print "<DIV CLASS=tr><!-- {} -->".format(dom)
  print "<DIV CLASS=td>{}</DIV><DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL=sdcp.cgi?call=dns_records&type={}&id={}>{}</A></DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>&nbsp;".format(dom['id'],"a" if not 'arpa' in dom['name'] else "ptr",dom['id'],dom['name'],dom['notified_serial'])
  print aWeb.button('info',DIV='div_content_right',URL='sdcp.cgi?call=dns_domain_info&id=%s'%(dom['id']))
  if not local['domains'].pop(str(dom['id']),None):
   print aWeb.button('add',DIV='div_content_right',URL='sdcp.cgi?call=dns_domain_cache_add&id={}&name={}'.format(dom['id'],dom['name']))
  print "</DIV></DIV>"
 for dom in local['domains'].values():
  print "<DIV CLASS=tr><!-- {} -->".format(dom)
  print "<DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>&nbsp;</DIV><DIV CLASS=td>&nbsp;".format(dom['id'],dom['name'])
  print aWeb.button('delete',DIV='div_content_right',URL='sdcp.cgi?call=dns_domain_cache_delete&id={}'.format(dom['id']))
  print "</DIV></DIV>"
 print "</DIV></DIV>"
 print "</ARTICLE>"

#
# Domain info
def domain_info(aWeb):
 if aWeb['op'] == 'update':
  data = aWeb.get_args2dict(['call','op'])
  res = aWeb.rest_generic(SC.dns['url'], "{}_domain_update".format(SC.dns['type']),data)
  data['id'] = res['id']
 else:
  res = aWeb.rest_generic(SC.dns['url'], "{}_domain_lookup".format(SC.dns['type']),{'id':aWeb['id']})
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
 print "</FORM>"
 print aWeb.button('reload',DIV='div_content_right',URL='sdcp.cgi?call=dns_domain_info&id={}'.format(data['id']))
 if data['id'] == 'new':
  print aWeb.button('save',DIV='div_content_right',URL='sdcp.cgi?call=dns_domain_info&op=update',FRM='dns_info_form')
 else:
  if not "arpa" in data['name']:
   print aWeb.button('delete',DIV='div_content_right',URL='sdcp.cgi?call=dns_domain_transfer&id={}'.format(data['id']))
  else:
   print aWeb.button('delete',DIV='div_content_right',URL='sdcp.cgi?call=dns_domain_delete&id={}'.format(data['id']))
 print "<SPAN CLASS='results' ID=update_results>{}</SPAN>".format("lookup" if not aWeb.get('op') else aWeb['op'])
 print "</ARTICLE>"

#
#
def domain_transfer(aWeb):
 domains = aWeb.rest_generic(SC.dns['url'], "{}_domains".format(SC.dns['type']),{"filter":"arpa"})
 print "<ARTICLE>"
 print "<FORM ID=dns_transfer><INPUT TYPE=HIDDEN NAME=id VALUE=%s>"%(aWeb['id'])
 print "Transfer all records to <SELECT NAME=transfer>"
 for domain in domains['domains']:
  if (str(domain['id']) == aWeb['id']):
   old = domain['name']
  else:
   print "<OPTION VALUE={}>{}</OPTION>".format(domain['id'],domain['name'])
 print "</SELECT> from previous domain ({})".format(old)
 print aWeb.button('back',DIV='div_content_right',URL='sdcp.cgi?call=dns_domain_info&id=%s'%(aWeb['id']))
 print aWeb.button('next',DIV='div_content_right',URL='sdcp.cgi?call=dns_domain_delete',FRM='dns_transfer')
 print "</ARTICLE>"

#
#
def domain_delete(aWeb):
 print "<ARTICLE>"
 cache = aWeb.rest_call("sdcpdns_domain_delete",{'from':aWeb['id'],'to':aWeb['transfer']})
 if cache['result'] == 'OK': 
  dns = aWeb.rest_generic(SC.dns['url'], "{}_domain_delete".format(SC.dns['type']),{'id':aWeb['id']})
  print "Removed domain [%s,%s]" % (cache,dns)
 else:
  print "Error removing domain cache and transfer"
 print "</ARTICLE>"

#
#
def domain_cache_add(aWeb):
 res = aWeb.rest_call("sdcpdns_domain_add",{'id':aWeb['id'],'name':aWeb['name']})
 print "<ARTICLE>Inserted (%s:%s): %i</ARTICLE>"%(aWeb['id'],aWeb['name'],res['xist'])

#
#
def domain_cache_delete(aWeb):
 res = aWeb.rest_call("sdcpdns_domain_delete",{'id':aWeb['id']})
 print "<ARTICLE>Delete %s: %i</ARTICLE>"%(aWeb['id'],res['xist'])

############################################ Records ###########################################
#
#
def records(aWeb):
 dns = aWeb.rest_generic(SC.dns['url'], "{}_records".format(SC.dns['type']),{'domain_id':aWeb['id']})
 print "<ARTICLE><P>Records</P>"
 print aWeb.button('reload',DIV='div_content_right',URL='sdcp.cgi?call=dns_records&id=%s'%(aWeb['id']))
 print aWeb.button('add',DIV='div_content_right',URL='sdcp.cgi?call=dns_record_info&id=new&domain_id=%s'%(aWeb['id']))
 print "<SPAN CLASS='results' ID=span_dns>&nbsp;</SPAN>"
 print "<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>Content</DIV><DIV CLASS=th>Type</DIV><DIV CLASS=th>TTL</DIV><DIV CLASS=th>&nbsp;</DIV></DIV>"
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

def record_info(aWeb):
 if aWeb['op'] == 'update':
  data = aWeb.get_args2dict(['call','op'])
  res = aWeb.rest_generic(SC.dns['url'], "{}_record_update".format(SC.dns['type']),data)
  data['id'] = res['id']
 else:
  res = aWeb.rest_generic(SC.dns['url'], "{}_record_lookup".format(SC.dns['type']),{'id':aWeb['id'],'domain_id':aWeb['domain_id']})
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
 print "</FORM>"
 print aWeb.button('reload',DIV='div_content_right',URL='sdcp.cgi?call=dns_record_info&id={}&domain_id={}'.format(data['id'],data['domain_id']))
 print aWeb.button('save',DIV='div_content_right',URL='sdcp.cgi?call=dns_record_info&op=update',FRM='dns_info_form')
 if not data['id'] == 'new':
  print aWeb.button('delete',DIV='div_content_right',URL='sdcp.cgi?call=dns_record_delete&id={}'.format(data['id']))
 print "<SPAN CLASS='results' ID=update_results></SPAN>"
 print "</ARTICLE>"

#
#
def record_delete(aWeb):
 res = aWeb.rest_generic(SC.dns['url'],"{}_record_delete".format(SC.dns['type']),{'id': aWeb['id']})
 print "Remove {} - Results:{}".format(aWeb['id'],res)

def record_transfer(aWeb):
 res = aWeb.rest_call("device_update",{'id':aWeb['dev'],'devices_%s_id'%aWeb['type']:aWeb['id']})
 print "Updated device %s - Results:%s"%(aWeb['dev'],str(res))

def record_create(aWeb):
 operation = {'type':aWeb['type'],'dns':None,'device':None}
 if aWeb['type'] == 'a':
  data = {'id':'new','type':'a','domain_id':aWeb['dom_id'],'name':aWeb['fqdn'],'content':aWeb['ip']}
 else:
  from ..core import genlib as GL
  data = {'id':'new','type':'ptr','domain_id':aWeb['dom_id'],'content':aWeb['fqdn'],'name':GL.ip2ptr(aWeb['ip'])}
 operation['dns'] = aWeb.rest_generic(SC.dns['url'],"{}_record_update".format(SC.dns['type']),data)
 if operation['dns']['xist'] == 1:
  operation['device'] = aWeb.rest_call("device_update",{'id':aWeb['id'],'devices_%s_id'%aWeb['type']:operation['dns']['id']})
 print "Created record result: %s"%str(operation)

############################################ Tools ###########################################
#
#
def load(aWeb):
 dns = aWeb.rest_generic(SC.dns['url'], "{}_domains".format(SC.dns['type'])) 
 res = aWeb.rest_call("sdcpdns_load",{'domains':dns['domains']})
 print "<ARTICLE>%s</ARTICLE>"%(res)

#
#
def consistency(aWeb):
 print "<ARTICLE><P>DNS Consistency</P><SPAN CLASS='results' ID=span_dns>&nbsp;</SPAN>"
 print "<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Value</DIV><DIV CLASS=th>Type</DIV><DIV CLASS=th>Key</DIV><DIV CLASS=th>Id</DIV><DIV CLASS=th>Id (Dev)</DIV><DIV CLASS=th>Hostname (Dev)</DIV><DIV CLASS=th>&nbsp;</DIV></DIV><DIV CLASS=tbody>"
 domains = aWeb.rest_call("sdcpdns_domains",{'index':'name'})['domains']
 for type in ['a','ptr']:
  records = aWeb.rest_generic(SC.dns['url'],"{}_records".format(SC.dns['type']),{'type':type})['records']
  tid = "{}_id".format(type)
  devices = aWeb.rest_call("device_list",{"index":"ipasc" if type == 'a' else "fqdn"})['data']
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
    print "<DIV CLASS=td>&nbsp;" + aWeb.button('add',DIV='span_dns',URL='sdcp.cgi?call=dns_record_create&type={}&id={}&ip={}&fqdn={}&dom_id={}'.format(type,value['id'],value['ipasc'],value['fqdn'],value['a_dom_id'] if type == 'a' else domains[GL.ip2arpa(value['ipasc'])]['id'] )) + "</DIV>"
    print "</DIV>"
 print "</DIV></DIV>"

 print "</ARTICLE>"

#
# DNS top
#
def top(aWeb):
 from ..core import extras as EXT
 dnstop = aWeb.rest_generic(SC.dns['url'], "{}_top".format(SC.dns['type']), {'count':20})
 print "<ARTICLE STYLE='float:left; width:49%;'><P>Top looked up FQDN</P>"
 EXT.dict2table(dnstop['top'])
 print "</ARTICLE>"
 print "<ARTICLE STYLE='float:left; width:49%;'><P>Top looked up FQDN per Client</P>"
 EXT.dict2table(dnstop['who'])
 print "</ARTICLE>"

#
# Cleanup duplicate entries
#
def dedup(aWeb):
 dns = aWeb.rest_generic(SC.dns['url'], "{}_dedup".format(SC.dns['type']))
 print "<ARTICLE><P>Duplicate Removal</P>"
 xist = len(dns['removed'])
 if xist > 0:
  from ..core import extras as EXT
  EXT.dict2table(dns['removed'])
 print "</ARTICLE>"
