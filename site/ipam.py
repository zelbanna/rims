"""Module docstring.

Ajax IPAM calls module

"""
__author__= "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__= "Production"

from sdcp.core.dbase import DB

#
#
def list(aWeb):
 from sdcp.rest import sdcpipam
 res = sdcpipam.list(None)  
 print "<DIV CLASS=z-frame>"
 print "<DIV CLASS=title>Subnets</DIV>"
 print "<A TITLE='Reload List' CLASS='z-btn z-small-btn z-op' DIV=div_content_left  URL='sdcp.cgi?call=ipam_list'><IMG SRC='images/btn-reboot.png'></A>"
 print "<A TITLE='Add Subnet'  CLASS='z-btn z-small-btn z-op' DIV=div_content_right URL='sdcp.cgi?call=ipam_info&id=new'><IMG SRC='images/btn-add.png'></A>"
 print "<DIV CLASS=z-table>"
 print "<DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Subnet</DIV><DIV CLASS=th>Gateway</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for net in res['subnets']:
  print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><DIV CLASS=td><A CLASS='z-op' DIV=div_content_right URL='sdcp.cgi?call=ipam_info&id={}'>{}</A></DIV><DIV CLASS=td>{}</DIV></DIV>".format(net['id'],net['id'],net['subnet'],net['gateway'])
 print "</DIV></DIV></DIV>"

#
#
def info(aWeb):
 from sdcp.rest import sdcpipam
 if aWeb['op'] == 'update':
  data = aWeb.get_args2dict()
  res = sdcpipam.update(data)
  data['gateway'] = res['gateway']
  data['id']      = res['id']
 else:
  res = sdcpipam.subnet({'id':aWeb['id']})
  data = res['data']
 lock = "readonly" if not data['id'] == 'new' else ""

 print "<DIV CLASS=z-frame style='resize: horizontal; margin-left:0px; width:420px; z-index:101; height:200px;'>"
 print "<DIV CLASS=title>Subnet Info {}</DIV>".format("(new)" if id == 'new' else "")
 print "<!-- {} -->".format(res)
 print "<FORM ID=ipam_info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(data['id'])
 print "<DIV CLASS=z-table><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Description:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=subnet_description VALUE={}></DIV></DIV>".format(data['subnet_description'])
 print "<DIV CLASS=tr><DIV CLASS=td>Subnet:</DIV><DIV CLASS=td><INPUT  TYPE=TEXT NAME=subnet  VALUE={} {}></DIV></DIV>".format(data['subnet'],lock)
 print "<DIV CLASS=tr><DIV CLASS=td>Mask:</DIV><DIV CLASS=td><INPUT    TYPE=TEXT NAME=mask    VALUE={} {}></DIV></DIV>".format(data['mask'],lock)
 print "<DIV CLASS=tr><DIV CLASS=td>Gateway:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=gateway VALUE={}></DIV></DIV>".format(data['gateway'])
 print "</DIV></DIV>"
 print "</FORM>"
 print "<A TITLE='Reload info' CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=sdcp.cgi?call=ipam_info&id={}><IMG SRC='images/btn-reboot.png'></A>".format(data['id'])
 print "<A TITLE='Update unit' CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=sdcp.cgi?call=ipam_info&op=update FRM=ipam_info_form><IMG SRC='images/btn-save.png'></A>"
 if not data['id'] == 'new':
  print "<A TITLE='Remove unit' CLASS='z-btn z-op z-small-btn' DIV=div_content_right MSG='Are you really sure' URL=sdcp.cgi?call=ipam_remove_net&id={}><IMG SRC='images/btn-remove.png'></A>".format(data['id'])
 print "<SPAN style='float:right; font-size:9px;'ID=update_results></SPAN>"
 print "</DIV></DIV>"

#
#
def remove_net(aWeb):
 from sdcp.rest import sdcpipam
 print "<DIV CLASS=z-frame>"
 print sdcpipam.remove({'id':aWeb['id']})
 print "</DIV>"
#
#
def load(aWeb):
 from sdcp.core.rest import call as rest_call
 from sdcp import PackageContainer as PC
 ipam_subnets = rest_call(PC.ipam['url'],"sdcp.rest.{}_subnets".format(PC.ipam['type']))
 added = 0
 print "<DIV CLASS=z-frame>"
 print "<!-- {} -->".format(ipam_subnets)
 with DB() as db:
  db.do("SELECT id,subnet,section_name FROM subnets")
  sdcp_subnets = db.get_dict('id')
  for sub in ipam_subnets['subnets']:
   exist = sdcp_subnets.pop(sub['id'],None)
   if not exist:
    added += 1
    print "Added: {}".format(sub)
   db.do("INSERT INTO subnets(id,subnet,mask,subnet_description,section_id,section_name) VALUES ({0},{1},{2},'{3}',{4},'{5}') ON DUPLICATE KEY UPDATE subnet={1},mask={2}".format(sub['id'],sub['subnet'],sub['mask'],sub['description'],sub['section_id'],sub['section_name']))
  print "<SPAN>Subnets - Inserted:{}, New:{}, Old:{}</SPAN><BR>".format(len(ipam_subnets['subnets']),added,len(sdcp_subnets))
  for sub,entry in sdcp_subnets.iteritems():
   print "Delete {} -> {}<BR>".format(sub,entry)
   db.do("DELETE FROM subnets WHERE id = '{}'".format(sub))
 print "</DIV>"

#
#
def discrepancy(aWeb):
 from sdcp.core.rest import call as rest_call
 from sdcp import PackageContainer as PC
 print "<DIV CLASS=z-frame><DIV CLASS=title>IPAM consistency</DIV><SPAN ID=span_ipam STYLE='font-size:9px;'>&nbsp;</SPAN>"
 print "<DIV CLASS=z-table STYLE='width:auto;'><DIV CLASS=thead><DIV CLASS=th>IP</DIV><DIV CLASS=th>FQDN</DIV><DIV CLASS=th>ID</DIV><DIV CLASS=th>Description</DIV><DIV CLASS=th>&nbsp;</DIV></DIV><DIV CLASS=tbody>"
 ipam = rest_call(PC.ipam['url'],"sdcp.rest.{}_get_addresses".format(PC.ipam['type']))
 with DB() as db:
  db.do("SELECT devices.id, ip, INET_NTOA(ip) as ipasc, CONCAT(hostname,'.',domains.name) AS fqdn FROM devices LEFT JOIN domains ON domains.id = devices.a_dom_id ORDER BY ip")
  devs = db.get_dict('ip')
 for row in ipam['addresses']:
  dev = devs.pop(int(row['ip']),None)
  if not dev or dev.get('fqdn') != row['fqdn']:
   print "<DIV CLASS=tr>"
   print "<!-- {} -->".format(row)
   print "<DIV CLASS=td>{}</DIV>".format(row['ipasc'])
   print "<DIV CLASS=td>{}</DIV>".format(row['fqdn'])
   print "<DIV CLASS=td>{}</DIV>".format(row['id'])
   print "<DIV CLASS=td>{}</DIV>".format(row['description'])
   print "<DIV CLASS=td>&nbsp;"
   print "<A CLASS='z-op z-btn z-small-btn' DIV=span_ipam MSG='Are you sure?' URL='sdcp.cgi?call=ipam_remove&id={}'><IMG SRC=images/btn-remove.png></A>".format(row['id'])
   if row['fqdn']:
    hostname,_,domain = row['fqdn'].partition('.')
    print "<!-- {} -->".format(domain)
    print "<A CLASS='z-op z-btn z-small-btn' DIV=div_content_right URL='sdcp.cgi?call=device_new&ip={}&hostname={}&ipam_id={}&ipam_sub_id={}{}'><IMG SRC=images/btn-add.png></A>".format(row['ipasc'],hostname,row['id'],row['ipam_sub_id'],"&domain={}".format(domain) if domain else "")
   print "</DIV></DIV>"
 if len(devs) > 0:
  for dev in devs:
   print "<DIV CLASS=tr>"
   print "<DIV CLASS=td>{}</DIV>".format(dev['ipasc'])
   print "<DIV CLASS=td>{}</DIV>".format(dev['fqdn'])
   print "<DIV CLASS=td>{}</DIV>".format(dev['id'])
   print "<DIV CLASS=td>&nbsp</DIV>"
   print "<DIV CLASS=td>&nbsp</DIV>"
   print "</DIV>"
 print "</DIV></DIV></DIV>"

#
#
def remove(aWeb):
 from sdcp.core.rest import call as rest_call
 from sdcp import PackageContainer as PC
 res = rest_call(PC.ipam['url'],"sdcp.rest.{}_remove".format(PC.ipam['type']),{'ipam_id':aWeb['id']})
 print "Remove {} - Results:{}".format(aWeb['id'],res)
