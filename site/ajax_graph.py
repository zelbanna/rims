"""Module docstring.

Ajax Graph calls module

"""
__author__= "Zacharias El Banna"                     
__version__ = "17.6.1GA"
__status__= "Production"

############################################ GRAPHS ##########################################

def list(aWeb):
 from sdcp.tools.Grapher import Grapher
 node  = aWeb.get_value('node')
 state = aWeb.get_value('state')
 graph = Grapher()
 graph.load_conf()
 if node and state:
  nstate = "yes" if state == "no" else "no"
  graph.update_entry(node, nstate)
 print "<DIV CLASS=z-frame><DIV CLASS=z-table style='width:99%'>"
 print "<DIV CLASS=thead><DIV CLASS=th>Node</DIV><DIV CLASS=th>Handler</DIV><DIV CLASS=th TITLE='Include in graphing?'>Include</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 keys = graph.get_keys()
 for key in keys:
  entry = graph.get_entry(key)
  gdomain = key.partition(".")[2]
  print "<DIV CLASS=tr>"
  if entry['update'] == 'yes':
   print "<DIV CLASS=td><A CLASS=z-op TITLE='Show graphs for {1}' DIV=div_content_right URL='/munin-cgi/munin-cgi-html/{0}/{1}/index.html'>{1}</A></DIV>".format(gdomain,key)
  else:
   print "<DIV CLASS=td>{0}</DIV>".format(key)
  print "<DIV CLASS=td>"+ entry['handler'] +"</DIV>"
  print "<DIV CLASS=td TITLE='Include in graphing?'><A CLASS='z-btn z-small-btn z-op' DIV=div_content_left URL='ajax.cgi?call=graph_list&node=" + key + "&state=" + entry['update'] + "'><IMG SRC=images/btn-{}.png></A>&nbsp;</DIV>".format("start" if entry['update'] == "no" else "shutdown")
  print "</DIV>"
 print "</DIV></DIV></DIV>"

#
# Find graphs
#
def find(aWeb):
 from sdcp.tools.Grapher import Grapher
 try:
  graph = Grapher() 
  graph.discover()
  print "<B>Done discovering graphs</B>"
 except Exception as err:
  print "<B>Error: {}</B>".format(str(err))


#
# Sync graphs and devices
#
def sync(aWeb):
 import sdcp.core.GenLib as GL
 import sdcp.PackageContainer as PC
 from sdcp.tools.Grapher import Grapher
 try:
  db = GL.DB()
  db.connect()
  db.do("SELECT devices.id, hostname, domains.name AS domain FROM devices LEFT JOIN domains on domains.id = devices.a_dom_id")
  rows = db.get_all_rows()
  graph = Grapher()
  graphdevices = graph.get_keys()
  sql = "UPDATE devices SET graphed = 'yes' WHERE id = '{}'"
  for row in rows:
   fqdn = row['hostname'] + "." + row['domain']
   if fqdn in graphdevices:
    db.do(sql.format(row['id']))
  db.commit()
  db.close()
  print "<B>Done syncing devices' graphing</B>"
  PC.log_msg("graph_sync: Done syncing devices' graphing")
 except Exception as err:
  print "<B>Error: {}</B>".format(str(err))

#
# Add graphs
#
def add(aWeb):
 node   = aWeb.get_value('node',None)
 name   = aWeb.get_value('name',None)
 domain = aWeb.get_value('domain',None)
 if name and domain:
  fqdn   = name + "." + domain
  from sdcp.tools.Grapher import Grapher
  graph = Grapher()
  entry = graph.get_entry(fqdn)
  if entry:
   print "<B>Entry existed</B>"
  else:
   graph.add_entry(fqdn,'no')
   print "<B>Added graphing for node {0} ({1})</B>".format(node, fqdn)

#
# Weathermap Link
#
def wm(aWeb):
 indx = aWeb.get_value('index')
 name = aWeb.get_value('hostname')
 snmpname = name.replace('-','_')
 dom  = aWeb.get_value('domain')
 desc = aWeb.get_value('desc',"LNK"+indx)
 gstr = "munin-cgi/munin-cgi-graph/{1}/{0}.{1}/snmp_{2}_{1}_if_{3}-day.png".format(name,dom,snmpname,indx)
 print "<DIV CLASS=z-frame><PRE style='font-size:10px;'>"
 print "LINK {}-{}".format(name,desc)
 print "\tINFOURL " +  gstr
 print "\tOVERLIBGRAPH " + gstr
 print "\tBWLABEL bits"
 print "\tTARGET {1}/{0}.{1}-snmp_{2}_{1}_if_{3}-recv-d.rrd {1}/{0}.{1}-snmp_{2}_{1}_if_{3}-send-d.rrd:-:42".format(name,dom,snmpname,indx)
 print "</PRE></DIV>"
