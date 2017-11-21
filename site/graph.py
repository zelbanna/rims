"""Module docstring.

HTML5 Ajax Graph calls module

"""
__author__= "Zacharias El Banna"                     
__version__ = "17.11.01GA"
__status__= "Production"

############################################ GRAPHS ##########################################
#
def list(aWeb):
 from sdcp.core.dbase import DB
 id    = aWeb['id']
 state = aWeb['state']
 target= aWeb['target']
 arg   = aWeb['arg']

 with DB() as db:
  if id and state:
   db.do("UPDATE devices SET graph_update = '{1}' WHERE id = '{0}'".format(id,1 if state == '0' else 0))
  if not target or not arg:
   tune = ""
  elif target:
   if target == 'rack_id' and not arg == 'NULL':
    tune = "INNER JOIN rackinfo ON rackinfo.device_id = devices.id WHERE rackinfo.rack_id = '{}'".format(arg)
   elif target == 'vm' and not arg == 'NULL':
    tune = "WHERE vm = {}".format(arg)
   else: 
    tune = "WHERE {0} is NULL".format(target)
  db.do("SELECT devices.id, INET_NTOA(ip) as ip, hostname, INET_NTOA(graph_proxy) AS proxy ,graph_update, domains.name AS domain FROM devices INNER JOIN domains ON devices.a_dom_id = domains.id {} ORDER BY hostname".format(tune))
  rows = db.get_rows()
 print "<ARTICLE><P>Graphing</P>"
 print aWeb.button('reload',DIV='div_content_left',  URL='sdcp.cgi?call=graph_list&%s'%(aWeb.get_args_except(['call','id','state'])))
 print aWeb.button('save'  ,DIV='div_content_right', URL='sdcp.cgi?call=graph_save')
 print aWeb.button('search',DIV='div_content_right', URL='sdcp.cgi?call=graph_discover', SPIN='true')
 print "<DIV CLASS=table>"
 print "<DIV CLASS=thead><DIV CLASS=th>FQDN</DIV><DIV CLASS=th>Proxy</DIV><DIV CLASS=th TITLE='Include in graphing?'>Include</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for row in rows:
  print "<DIV CLASS=tr>"
  if row['graph_update']:
   print "<DIV CLASS=td><A CLASS=z-op TITLE='Show graphs for {1}' DIV=div_content_right URL='/munin-cgi/munin-cgi-html/{0}/{1}/index.html'>{1}.{0}</A></DIV>".format(row['domain'],row['hostname'])
   print "<DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL=sdcp.cgi?call=graph_set_proxy&id={0}&proxy={1}&ip={2}>{1}</A></DIV>".format(row['id'],row['proxy'],row['ip'])
  else:
   print "<DIV CLASS=td>{0}.{1}</DIV>".format(row['hostname'],row['domain'])
   print "<DIV CLASS=td>{0}</A></DIV>".format(row['proxy'])
  print "<DIV CLASS=td TITLE='Include in graphing?'>&nbsp;"
  print aWeb.button("shutdown" if row['graph_update'] else "start", DIV='div_content_left', URL='sdcp.cgi?call=graph_list&{}&id={}&state={}'.format(aWeb.get_args_except(['call','id','state']),row['id'],row['graph_update']))
  print "</DIV></DIV>"
 print "</DIV></DIV>"
 print "</ARTICLE>"

#
# Modify proxy
#
def set_proxy(aWeb):
 id    = aWeb['id']
 proxy = aWeb['proxy']
 ip    = aWeb['ip']
 op = aWeb['op']
 if op == 'update':
  from sdcp.core.dbase import DB
  with DB() as db:
   db.do("UPDATE devices SET graph_proxy = INET_ATON('{0}') WHERE id = '{1}'".format(proxy,id))
 print "<ARTICLE><P>Update Proxy for {}</DIV>".format(ip)
 print "<FORM ID=graph_proxy_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(id)
 print "<INPUT TYPE=HIDDEN NAME=ip VALUE={}>".format(ip)
 print "<DIV CLASS=table STYLE='width:auto'><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Proxy:</DIV><DIV CLASS=td><INPUT CLASS='border' TYPE=TEXT NAME=proxy STYLE='width:200px;' VALUE='{}'></DIV></DIV>".format(proxy)
 print "</DIV></DIV>"
 print "</FORM>"
 print aWeb.button('save',DIV='div_content_right', URL='sdcp.cgi?call=graph_set_proxy&op=update', FRM='graph_proxy_form')
 print "</ARTICLE>"

#
# Find graphs
#
def discover(aWeb):
 from sdcp.tools.munin import discover as graph_discover
 graph_discover()

#
# Generate output for munin, until we have other types
#
def save(aWeb):
 from sdcp.core.dbase import DB
 from sdcp import PackageContainer as PC
 with DB() as db:
  db.do("SELECT hostname, INET_NTOA(graph_proxy) AS proxy, domains.name AS domain FROM devices INNER JOIN domains ON domains.id = devices.a_dom_id WHERE graph_update = 1")
  rows = db.get_rows()
 with open(PC.sdcp['graph']['file'],'w') as output:
  for row in rows:
   output.write("[{}.{}]\n".format(row['hostname'],row['domain']))
   output.write("address {}\n".format(row['proxy']))
   output.write("update yes\n\n")
 print "<ARTICLE>Done updating devices' graphing to conf file [{}]</ARTICLE>".format(PC.sdcp['graph']['file'])

#
# Weathermap Link
#
def wm(aWeb):
 indx = aWeb['index']
 name = aWeb['hostname']
 snmpname = name.replace('-','_')
 dom  = aWeb['domain']
 desc = aWeb.get('desc',"LNK"+indx)
 gstr = "munin-cgi/munin-cgi-graph/{1}/{0}.{1}/snmp_{2}_{1}_if_{3}-day.png".format(name,dom,snmpname,indx)
 print "<ARTICLE><PRE STYLE='font-size:10px;'>"
 print "LINK {}-{}".format(name,desc)
 print "\tINFOURL " +  gstr
 print "\tOVERLIBGRAPH " + gstr
 print "\tBWLABEL bits"
 print "\tTARGET {1}/{0}.{1}-snmp_{2}_{1}_if_{3}-recv-d.rrd {1}/{0}.{1}-snmp_{2}_{1}_if_{3}-send-d.rrd:-:42".format(name,dom,snmpname,indx)
 print "</CODE></ARTICLE>"
