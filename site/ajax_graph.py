"""Moduledocstring.

Ajax Graph calls module

"""
__author__= "Zacharias El Banna"                     
__version__= "5.0GA"
__status__= "Production"

############################################ GRAPHS ##########################################

def graph_list(aWeb):
 from sdcp.core.Grapher import Grapher
 node  = aWeb.get_value('node')
 state = aWeb.get_value('state')
 graph = Grapher()
 graph.load_conf()
 if node and state:
  nstate = "yes" if state == "no" else "no"
  graph.update_entry(node, nstate)
 print "<DIV CLASS='z-framed'><DIV CLASS='z-table'>"
 print "<TABLE WIDTH=330><TR><TH>Node</TH><TH>Handler</TH><TH TITLE='Include in graphing?'>Include</TH></TR>"
 keys = graph.get_keys()
 for key in keys:
  entry = graph.get_entry(key)
  gdomain = key.partition(".")[2]
  print "<TR>"
  if entry['update'] == 'yes':
   print "<TD><A CLASS=z-op TITLE='Show graphs for {1}' OP=load DIV=div_navcont LNK='/munin-cgi/munin-cgi-html/{0}/{1}/index.html'>{1}</A></TD>".format(gdomain,key)
  else:
   print "<TD>{0}</TD>".format(key)
  print "<TD>"+ entry['handler'] +"</TD>"
  print "<TD TITLE='Include in graphing?'><CENTER><A CLASS='z-btn z-small-btn z-op' OP=load DIV=div_navleft LNK='ajax.cgi?call=graph_list&node=" + key + "&state=" + entry['update'] + "'><IMG SRC=images/btn-{}.png></A></CENTER></TD>".format("start" if entry['update'] == "no" else "shutdown")
  print "</TR>"
 print "</TABLE></DIV></DIV>"

#
# Find graphs
#
def graph_find(aWeb):
 from sdcp.core.Grapher import Grapher
 try:
  graph = Grapher() 
  graph.discover()
  print "<B>Done discovering graphs</B>"
  aWeb.log_msg("graph_find: Discovered graphs")
 except Exception as err:
  print "<B>Error: {}</B>".format(str(err))


#
# Sync graphs and devices
#
def graph_sync(aWeb):
 from sdcp.core.GenLib import DB
 from sdcp.core.Grapher import Grapher
 try:
  db = DB()
  db.connect()
  db.do("SELECT id,hostname,domain FROM devices")
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
  aWeb.log_msg("graph_sync: Done syncing devices' graphing")
 except Exception as err:
  print "<B>Error: {}</B>".format(str(err))

#
# Add graphs
#
def graph_add(aWeb):
 node   = aWeb.get_value('node',None)
 name   = aWeb.get_value('name',None)
 domain = aWeb.get_value('domain',None)
 if name and domain:
  fqdn   = name + "." + domain
  from sdcp.core.Grapher import Grapher
  graph = Grapher()
  entry = graph.get_entry(fqdn)
  if entry:
   print "<B>Entry existed</B>"
  else:
   graph.add_entry(fqdn,'no')
   print "<B>Added graphing for node {0} ({1})</B>".format(node, fqdn)
