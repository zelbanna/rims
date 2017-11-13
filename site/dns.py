"""Module docstring.

Ajax DNS calls module

"""
__author__= "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__= "Production"

from sdcp import PackageContainer as PC
from sdcp.core.dbase import DB
from sdcp.core.rest import call as rest_call

############################################ Domains ###########################################
#
#
def domains(aWeb):
 domains = rest_call(PC.dns['url'], "sdcp.rest.{}_domains".format(PC.dns['type']))
 with DB() as db:
  db.do("SELECT id, name FROM domains")
  local = db.get_dict('id')
 print "<DIV CLASS=z-frame>"
 print "<DIV CLASS=title>Domains</DIV>"
 print aWeb.button('reload',DIV='div_content_left',URL='sdcp.cgi?call=dns_domains')
 print aWeb.button('add',DIV='div_content_right',URL='sdcp.cgi?call=dns_domain_info&id=new')
 print "<DIV CLASS=z-table>"
 print "<DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Domain</DIV><DIV CLASS=th>Serial</DIV><DIV CLASS=th>&nbsp;</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for dom in domains['domains']:
  print "<DIV CLASS=tr><!-- {} -->".format(dom)
  print "<DIV CLASS=td>{}</DIV><DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL=sdcp.cgi?call=dns_domain_info&id={}>{}</A></DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>&nbsp;".format(dom['id'],dom['id'],dom['name'],dom['notified_serial'])
  print aWeb.button('info',DIV='div_content_right',URL='sdcp.cgi?call=dns_records&type={}&id={}'.format("a" if not 'arpa' in dom['name'] else "ptr",dom['id']))
  if not local.pop(dom['id'],None):
   print aWeb.button('reload',DIV='div_content_right',URL='sdcp.cgi?call=dns_load&id={}'.format(dom['id']))
  print "</DIV></DIV>"
 print "</DIV></DIV>"
 print "<SPAN>Remaining:{}</SPAN>".format(len(local))
 print "</DIV>"

#
# Domain info
def domain_info(aWeb):
 if aWeb['op'] == 'update':
  data = aWeb.get_args2dict_except(['call','op'])
  res = rest_call(PC.dns['url'], "sdcp.rest.{}_domain_update".format(PC.dns['type']),data)
  data['id'] = res['id']
 else:
  res = rest_call(PC.dns['url'], "sdcp.rest.{}_domain_lookup".format(PC.dns['type']),{'id':aWeb['id']})
  data = res['data']
 lock = "readonly" if not data['id'] == 'new' else ""
 print "<DIV CLASS='z-frame z-info' STYLE='height:200px;'>"
 print "<DIV CLASS=title>Domain Info {}</DIV>".format("(new)" if data['id'] == 'new' else "")
 print "<!-- {} -->".format(res)
 print "<FORM ID=dns_info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(data['id'])
 print "<DIV CLASS=z-table><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Name:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=name VALUE={}></DIV></DIV>".format(data['name'])
 print "<DIV CLASS=tr><DIV CLASS=td>Master:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=master VALUE={}></DIV></DIV>".format(data['master'])
 print "<DIV CLASS=tr><DIV CLASS=td>Type:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=type VALUE={}></DIV></DIV>".format(data['type'])
 print "</DIV></DIV>"
 print "</FORM>"
 print aWeb.button('reload',DIV='div_content_right',URL='sdcp.cgi?call=dns_domain_info&id={}'.format(data['id']))
 print aWeb.button('save',DIV='div_content_right',URL='sdcp.cgi?call=dns_domain_info&op=update',FRM='dns_info_form')
 if not data['id'] == 'new':
  print aWeb.button('delete',DIV='div_content_right',URL='sdcp.cgi?call=dns_domain_delete&id={}'.format(data['id']))
 print "<SPAN style='float:right; font-size:9px;'ID=update_results>{}/{}</SPAN>".format("lookup" if not aWeb.get('op') else aWeb['op'],res['res'])

#
#
def domain_delete(aWeb):
 domains = rest_call(PC.dns['url'], "sdcp.rest.{}_domains".format(PC.dns['type']))
 print "<DIV CLASS=z-frame>"
 print "<FORM ID=dns_transfer><INPUT TYPE=HIDDEN NAME=from VALUE=%s>"%(aWeb['id'])
 print "Transfer all records to <SELECT STYLE='border:none; overflow:visible; background-color:transparent; color:black;' NAME=to>"
 for domain in domains['domains']:
  if (str(domain['id']) == aWeb['id']):
   old = domain['name']
  else:
   if not "arpa" in domain['name']:
    print "<OPTION VALUE={}>{}</OPTION>".format(domain['id'],domain['name'])
 print "</SELECT> from previous domain ({})".format(old)
 print aWeb.button('back',DIV='div_content_right',URL='sdcp.cgi?call=dns_domain_info&id=%s'%(aWeb['id']))
 print aWeb.button('next',DIV='div_content_right',URL='sdcp.cgi?call=dns_domain_transfer',FRM='dns_transfer')
 print "</DIV>"

def domain_transfer(aWeb):
 with DB() as db:
  updates = db.do("UPDATE devices SET a_dom_id = %s WHERE a_dom_id = %s"%(aWeb['to'],aWeb['from']))
  dbase   = db.do("DELETE FROM domains WHERE id = %s"%(aWeb['from']))
 res = rest_call(PC.dns['url'], "sdcp.rest.{}_domain_delete".format(PC.dns['type']),{'id':aWeb['from']})
 print "<DIV CLASS=z-frame>"
 print "Updated [%i] devices and removed domain [%s,%s]" % (updates,"OK" if dbase > 0 else "NOT_OK",str(res))
 print "</DIV>"


############################################ Records ###########################################
#
#
def records(aWeb):
 dns = rest_call(PC.dns['url'], "sdcp.rest.{}_records".format(PC.dns['type']),{'domain_id':aWeb['id']})
 print "<DIV CLASS=z-frame>"
 print "<DIV CLASS=title>Records</DIV><SPAN ID=span_dns STYLE='font-size:9px;'>&nbsp;</SPAN>"
 print aWeb.button('reload',DIV='div_content_right',URL='sdcp.cgi?call=dns_records&id=%s'%(aWeb['id']))
 print aWeb.button('add',DIV='div_content_right',URL='sdcp.cgi?call=dns_record_info&id=new&domain_id=%s'%(aWeb['id']))
 print "<DIV CLASS=z-table><DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>Content</DIV><DIV CLASS=th>Type</DIV><DIV CLASS=th>TTL</DIV><DIV CLASS=th>&nbsp;</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for rec in dns['records']:
  print "<DIV CLASS=tr><!-- {} -->".format(rec)
  print "<DIV CLASS=td>%i</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>&nbsp;"%(rec['id'],rec['name'],rec['content'],rec['type'],rec['ttl'])
  print aWeb.button('info',DIV='div_content_right',URL='sdcp.cgi?call=dns_record_info&id=%i&domain_id=%s'%(rec['id'],aWeb['id']))
  if rec['type'] in ['A','CNAME','PTR']:
   print aWeb.button('delete',DIV='span_dns',URL='sdcp.cgi?call=dns_record_remove&id=%i'%(rec['id']))
  print "</DIV></DIV>"
 print "</DIV></DIV>"
 print "</DIV>"


def record_info(aWeb):
 if aWeb['op'] == 'update':
  data = aWeb.get_args2dict_except(['call','op'])
  res = rest_call(PC.dns['url'], "sdcp.rest.{}_record_update".format(PC.dns['type']),data)
  data['id'] = res['id']
 else:
  res = rest_call(PC.dns['url'], "sdcp.rest.{}_record_lookup".format(PC.dns['type']),{'id':aWeb['id'],'domain_id':aWeb['domain_id']})
  data = res['data']
 lock = "readonly" if not data['id'] == 'new' else ""
 print "<DIV CLASS='z-frame z-info' STYLE='height:200px;'>"
 print "<DIV CLASS=title>Record Info {} (Domain {})</DIV>".format("(new)" if data['id'] == 'new' else "",data['domain_id'])
 print "<!-- {} -->".format(res)
 print "<FORM ID=dns_info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(data['id'])
 print "<DIV CLASS=z-table><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Name:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=name VALUE={}></DIV></DIV>".format(data['name'])
 print "<DIV CLASS=tr><DIV CLASS=td>Content:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=content VALUE={}></DIV></DIV>".format(data['content'])
 print "<DIV CLASS=tr><DIV CLASS=td>TTL:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=ttl VALUE={}></DIV></DIV>".format(data['ttl'])
 print "<DIV CLASS=tr><DIV CLASS=td>Type:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=type VALUE={}></DIV></DIV>".format(data['type'])
 print "<DIV CLASS=tr><DIV CLASS=td>Domain (id):</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=domain_id VALUE={}></DIV></DIV>".format(data['domain_id'])
 print "</DIV></DIV>"
 print "</FORM>"
 print aWeb.button('reload',DIV='div_content_right',URL='sdcp.cgi?call=dns_record_info&id={}'.format(data['id']))
 print aWeb.button('save',DIV='div_content_right',URL='sdcp.cgi?call=dns_record_info&op=update',FRM='dns_info_form')
 if not data['id'] == 'new':
  print aWeb.button('delete',DIV='div_content_right',URL='sdcp.cgi?call=dns_record_remove&id={}'.format(data['id']))
 print "<SPAN style='float:right; font-size:9px;'ID=update_results></SPAN>"

#
#
def record_remove(aWeb):
 res = rest_call(PC.dns['url'],"sdcp.rest.{}_record_remove".format(PC.dns['type']),{'id': aWeb['id']})
 print "Remove {} - Results:{}".format(aWeb['id'],res)

############################################ Tools ###########################################
#
#
def load(aWeb):
 dns_domains  = rest_call(PC.dns['url'], "sdcp.rest.{}_domains".format(PC.dns['type']))
 added = 0
 print "<DIV CLASS=z-frame>"
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
 print "</DIV>"

#
#
#
def discrepancy(aWeb):
 print "<DIV CLASS=Z-frame>"
 print "<DIV CLASS=title>DNS Consistency</DIV><SPAN ID=span_dns STYLE='font-size:9px;'>&nbsp;</SPAN>"
 print "<DIV CLASS=z-table STYLE='width:auto;'><DIV CLASS=thead><DIV CLASS=th>Value</DIV><DIV CLASS=th>Type</DIV><DIV CLASS=th>Key</DIV><DIV CLASS=th>Id</DIV><DIV CLASS=th>Id (Dev)</DIV><DIV CLASS=th>Hostname (Dev)</DIV><DIV CLASS=th>&nbsp;</DIV></DIV><DIV CLASS=tbody>"
 for type in ['a','ptr']:
  dns = rest_call(PC.dns['url'],"sdcp.rest.{}_records".format(PC.dns['type']),{'type':type})
  tid = "{}_id".format(type)
  with DB() as db:
   db.do("SELECT devices.id, ip, INET_NTOA(ip) as ipasc, {0}_id, CONCAT(hostname,'.',name) as fqdn FROM devices LEFT JOIN domains ON devices.a_dom_id = domains.id ORDER BY ip".format(type))
   devs = db.get_dict("ipasc" if type == 'a' else "fqdn")
  for rec in dns['records']:
   dev = devs.pop(rec['content'],None)
   if not dev or dev[tid] != rec['id']:
    print "<DIV CLASS=tr>"
    print "<!-- {} --> ".format(rec)
    print "<DIV CLASS=td>{}</DIV>".format(rec['content'])
    print "<DIV CLASS=td>{}</DIV>".format(rec['type'])
    print "<DIV CLASS=td>{}</DIV>".format(rec['name'])
    print "<DIV CLASS=td>{}</DIV>".format(rec['id'])
    if dev:
     print "<DIV CLASS=td>{}</DIV>".format(dev[tid])
     print "<DIV CLASS=td>{0}</DIV>".format(dev['fqdn'])
    else:
     print "<DIV CLASS=td>&nbsp</DIV><DIV CLASS=td>&nbsp</DIV>"
    print "<DIV CLASS=td>&nbsp;" + aWeb.button('delete',DIV='span_dns',MSG='Are you sure?',URL='sdcp.cgi?call=dns_record_remove&id={}'.format(rec['id'])) + "</DIV>"
    print "</DIV>"
  if len(devs) > 0:
   for key,value in  devs.iteritems():
    print "<DIV CLASS=tr>"
    print "<DIV CLASS=td>{}</DIV><DIV CLASS=td>&nbsp;</DIV>".format(key)
    print "<DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL=sdcp.cgi?call=device_info&id={0}>{1}</A></DIV><DIV CLASS=td>{0}</DIV><DIV CLASS=td>{1}</DIV>".format(value['id'],value['fqdn'])
    print "<DIV CLASS=td>&nbsp;</DIV>"
    print "</DIV>"
 print "</DIV></DIV></DIV>"

#
# DNS top
#
def top(aWeb):
 from sdcp.core import extras as EXT
 dnstop = rest_call(PC.dns['url'], "sdcp.rest.{}_top".format(PC.dns['type']), {'count':20})
 print "<DIV CLASS=z-frame STYLE='float:left; width:49%;'><DIV CLASS=title>Top looked up FQDN</DIV>"
 EXT.dict2table(dnstop['top'])
 print "</DIV>"
 print "<DIV CLASS=z-frame STYLE='float:left; width:49%;'><DIV CLASS=title>Top looked up FQDN per Client</DIV>"
 EXT.dict2table(dnstop['who'])
 print "</DIV>"

#
# Cleanup duplicate entries
#
def cleanup(aWeb):
 dnsclean = rest_call(PC.dns['url'], "sdcp.rest.{}_cleanup".format(PC.dns['type']))
 print "<DIV CLASS=z-frame><DIV CLASS=title>Cleanup</DIV>"
 xist = len(dnsclean['removed'])
 if xist > 0:
  from sdcp.core import extras as EXT
  EXT.dict2table(dnsclean['removed'])
 print "</DIV>"
