"""Module docstring.

HTML5 Ajax DNS calls module

"""
__author__= "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__= "Production"

from sdcp import PackageContainer as PC
from sdcp.core.dbase import DB

############################################ Domains ###########################################
#
#
def list(aWeb):
 domains = aWeb.rest_call(PC.dns['url'], "sdcp.rest.{}_domains".format(PC.dns['type']))['data']
 with DB() as db:
  db.do("SELECT id, name FROM domains")
  local = db.get_dict('id')
 print "<ARTICLE><P>Domains</P>"
 print "<DIV CLASS='controls'>"
 print aWeb.button('reload',DIV='div_content_left',URL='sdcp.cgi?call=dns_list')
 print aWeb.button('add',DIV='div_content_right',URL='sdcp.cgi?call=dns_domain_info&id=new',TITLE='Add domain')
 print aWeb.button('search',DIV='div_content_right',URL='sdcp.cgi?call=dns_discrepancy',TITLE='Check Backend Discrepancy',SPIN='true')
 print aWeb.button('delete',DIV='div_content_right',URL='sdcp.cgi?call=dns_dedup',TITLE='Find Duplicates',SPIN='true')
 print "</DIV>"
 print "<DIV CLASS=table>"
 print "<DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Domain</DIV><DIV CLASS=th>Serial</DIV><DIV CLASS=th>&nbsp;</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for dom in domains['domains']:
  print "<DIV CLASS=tr><!-- {} -->".format(dom)
  print "<DIV CLASS=td>{}</DIV><DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL=sdcp.cgi?call=dns_records&type={}&id={}>{}</A></DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>&nbsp;".format(dom['id'],"a" if not 'arpa' in dom['name'] else "ptr",dom['id'],dom['name'],dom['notified_serial'])
  print aWeb.button('info',DIV='div_content_right',URL='sdcp.cgi?call=dns_domain_info&id=%s'%(dom['id']))
  if not local.pop(dom['id'],None):
   print aWeb.button('add',DIV='div_content_right',URL='sdcp.cgi?call=dns_domain_cache_add&id={}&name={}'.format(dom['id'],dom['name']))
  print "</DIV></DIV>"
 for dom in local.values():
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
  data = aWeb.get_args2dict_except(['call','op'])
  res = aWeb.rest_call(PC.dns['url'], "sdcp.rest.{}_domain_update".format(PC.dns['type']),data)['data']
  data['id'] = res['id']
 else:
  res = aWeb.rest_call(PC.dns['url'], "sdcp.rest.{}_domain_lookup".format(PC.dns['type']),{'id':aWeb['id']})['data']
  data = res['data']
 lock = "readonly" if not data['id'] == 'new' else ""
 print "<ARTICLE CLASS=info><P>Domain Info{}</P>".format(" (new)" if data['id'] == 'new' else "")
 print "<!-- {} -->".format(res)
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
 print "<SPAN CLASS='results' ID=update_results>{}/{}</SPAN>".format("lookup" if not aWeb.get('op') else aWeb['op'],res['result'])
 print "</ARTICLE>"

#
#
def domain_transfer(aWeb):
 domains = aWeb.rest_call(PC.dns['url'], "sdcp.rest.{}_domains".format(PC.dns['type']))['data']
 print "<ARTICLE>"
 print "<FORM ID=dns_transfer><INPUT TYPE=HIDDEN NAME=id VALUE=%s>"%(aWeb['id'])
 print "Transfer all records to <SELECT NAME=transfer>"
 for domain in domains['domains']:
  if (str(domain['id']) == aWeb['id']):
   old = domain['name']
  else:
   if not "arpa" in domain['name']:
    print "<OPTION VALUE={}>{}</OPTION>".format(domain['id'],domain['name'])
 print "</SELECT> from previous domain ({})".format(old)
 print aWeb.button('back',DIV='div_content_right',URL='sdcp.cgi?call=dns_domain_info&id=%s'%(aWeb['id']))
 print aWeb.button('next',DIV='div_content_right',URL='sdcp.cgi?call=dns_domain_delete',FRM='dns_transfer')
 print "</ARTICLE>"

#
#
def domain_delete(aWeb):
 print "<ARTICLE>"
 with DB() as db:
  if aWeb['transfer']:
   exist = db.do("UPDATE devices SET a_dom_id = %s WHERE a_dom_id = %s"%(aWeb['transfer'],aWeb['id']))
   print "Transfered %i devices. "%(exist)
  dbase   = db.do("DELETE FROM domains WHERE id = %s"%(aWeb['id']))
 res = aWeb.rest_call(PC.dns['url'], "sdcp.rest.{}_domain_delete".format(PC.dns['type']),{'id':aWeb['id']})['data']
 print "Removed domain [%s,%s]" % ("removed cache" if dbase > 0 else "not in cache",str(res))
 print "</ARTICLE>"

#
#
def domain_cache_add(aWeb):
 print "<ARTICLE>"
 with DB() as db:
  xist = db.do("INSERT INTO domains SET id = %s, name = '%s'"%(aWeb['id'],aWeb['name']))
  print "Inserted (%s:%s): %i"%(aWeb['id'],aWeb['name'],xist)
 print "</ARTICLE>"

#
#
def domain_cache_delete(aWeb):
 print "<ARTICLE>"
 with DB() as db:
  xist = db.do("DELETE FROM domains WHERE id = %s"%(aWeb['id']))
  print "Delete %s: %i"%(aWeb['id'],xist)
 print "</ARTICLE>"

############################################ Records ###########################################
#
#
def records(aWeb):
 dns = aWeb.rest_call(PC.dns['url'], "sdcp.rest.{}_records".format(PC.dns['type']),{'domain_id':aWeb['id']})['data']
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
  data = aWeb.get_args2dict_except(['call','op'])
  res = aWeb.rest_call(PC.dns['url'], "sdcp.rest.{}_record_update".format(PC.dns['type']),data)['data']
  data['id'] = res['id']
 else:
  res = aWeb.rest_call(PC.dns['url'], "sdcp.rest.{}_record_lookup".format(PC.dns['type']),{'id':aWeb['id'],'domain_id':aWeb['domain_id']})['data']
  data = res['data']
 lock = "readonly" if not data['id'] == 'new' else ""
 print "<ARTICLE CLASS=info><P>Record Info {} (Domain {})</P>".format("(new)" if data['id'] == 'new' else "",data['domain_id'])
 print "<!-- {} -->".format(res)
 print "<FORM ID=dns_info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id        VALUE={}>".format(data['id'])
 print "<INPUT TYPE=HIDDEN NAME=domain_id VALUE={}>".format(data['domain_id'])
 print "<DIV CLASS=table><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td TITLE='E.g. A:FQDN, PTR:x.y.z.in-addr.arpa'>Name:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=name VALUE={}></DIV></DIV>".format(data['name'])
 print "<DIV CLASS=tr><DIV CLASS=td TITLE='E.g. A:IP, PTR:FQDN'>Content:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=content VALUE={}></DIV></DIV>".format(data['content'])
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
 res = aWeb.rest_call(PC.dns['url'],"sdcp.rest.{}_record_delete".format(PC.dns['type']),{'id': aWeb['id']})['data']
 print "Remove {} - Results:{}".format(aWeb['id'],res)

def record_transfer(aWeb):
 res = aWeb.rest_call("http://127.0.0.1/rest.cgi","sdcp.rest.device_update",{'id':aWeb['dev'],'devices_%s_id'%aWeb['type']:aWeb['id']})['data']
 print "Updated device %s - Results:%s"%(aWeb['dev'],str(res))

def record_create(aWeb):
 operation = {'type':aWeb['type'],'dns':None,'device':None}
 if aWeb['type'] == 'a':
  data = {'id':'new','type':aWeb['type'],'domain_id':aWeb['dom_id'],'name':aWeb['fqdn'],'content':aWeb['ip']}
 else:
  from sdcp.core import genlib as GL
  data = {'id':'new','type':aWeb['type'],'domain_id':aWeb['dom_id'],'content':aWeb['fqdn'],'name':GL.ip2ptr(aWeb['ip'])}
 res = aWeb.rest_call(PC.dns['url'],"sdcp.rest.{}_record_update".format(PC.dns['type']),data)
 operation['dns'] = res['data']
 if res['data']['result'] == 'OK':
  res = aWeb.rest_call("http://127.0.0.1/rest.cgi","sdcp.rest.device_update",{'id':aWeb['id'],'devices_%s_id'%aWeb['type']:res['data']['id']})
  operation['device'] = res['data']
 print "Created record result: %s"%str(operation)

############################################ Tools ###########################################
#
#
def load(aWeb):
 dns_domains  = aWeb.rest_call(PC.dns['url'], "sdcp.rest.{}_domains".format(PC.dns['type']))['data']
 added = 0
 print "<ARTICLE>"
 with DB() as db:
  db.do("SELECT id,name FROM domains")
  sdcp_domains = db.get_dict('id')
  for dom in dns_domains['domains']:
   exist = sdcp_domains.pop(dom['id'],None)
   if not exist:
    added += 1
    print "Added: {}".format(dom)
   db.do("INSERT INTO domains(id,name) VALUES ({0},'{1}') ON DUPLICATE KEY UPDATE name = '{1}'".format(dom['id'],dom['name']))
  print "<SPAN>Domains - Inserted:{}, New:{}, Old:{}</SPAN><BR>".format(len(dns_domains['domains']),added,len(sdcp_domains))
  for dom,entry in sdcp_domains.iteritems():
   print "Delete {} -> {}<BR>".format(dom,entry)
   db.do("DELETE FROM domains WHERE id = '{}'".format(dom))
 print "</ARTICLE>"

#
#
#
def discrepancy(aWeb):
 print "<ARTICLE><P>DNS Consistency</P><SPAN CLASS='results' ID=span_dns>&nbsp;</SPAN>"
 print "<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Value</DIV><DIV CLASS=th>Type</DIV><DIV CLASS=th>Key</DIV><DIV CLASS=th>Id</DIV><DIV CLASS=th>Id (Dev)</DIV><DIV CLASS=th>Hostname (Dev)</DIV><DIV CLASS=th>&nbsp;</DIV></DIV><DIV CLASS=tbody>"
 for type in ['a','ptr']:
  dns = aWeb.rest_call(PC.dns['url'],"sdcp.rest.{}_records".format(PC.dns['type']),{'type':type})['data']
  tid = "{}_id".format(type)
  with DB() as db:
   db.do("SELECT devices.id, ip, INET_NTOA(ip) as ipasc, {0}_id, CONCAT(devices.hostname,'.',domains.name) as fqdn, a_dom_id FROM devices LEFT JOIN domains ON devices.a_dom_id = domains.id ORDER BY ip".format(type))
   devs = db.get_dict("ipasc" if type == 'a' else "fqdn")
   db.do("SELECT id,name FROM domains")
   domains = db.get_dict('name')
  for rec in dns['records']:
   dev = devs.pop(rec['content'],None)
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
  if len(devs) > 0:
   from sdcp.core import genlib as GL
   for key,value in  devs.iteritems():
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
 from sdcp.core import extras as EXT
 dnstop = aWeb.rest_call(PC.dns['url'], "sdcp.rest.{}_top".format(PC.dns['type']), {'count':20})['data']
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
 dns = aWeb.rest_call(PC.dns['url'], "sdcp.rest.{}_dedup".format(PC.dns['type']))['data']
 print "<ARTICLE><P>Duplicate Removal</P>"
 xist = len(dns['removed'])
 if xist > 0:
  from sdcp.core import extras as EXT
  EXT.dict2table(dns['removed'])
 print "</ARTICLE>"

