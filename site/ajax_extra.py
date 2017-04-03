"""Moduledocstring.

Ajax Generic calls module

"""
__author__= "Zacharias El Banna"                     
__version__= "1.0GA"
__status__= "Production"

######################################## Examine pane - logs ########################################
#
#
#

def examine_clear_logs(aWeb, aClear = True):
 domain  = aWeb.get_value('domain')
 try:
  from subprocess import check_output
  import sdcp.SettingsContainer as SC
  if aClear:
   open("/var/log/network/"+ domain +".log",'w').close()
   open(SC.sdcp_logformat,'w').close()
   aWeb.log_msg("Emptied logs")
  netlogs = check_output("tail -n 15 /var/log/network/{}.log | tac".format(domain), shell=True)
  print "<DIV CLASS='z-logs'><H1>Network Logs</H1><PRE>{}</PRE></DIV>".format(netlogs)
  print "<BR>"
  syslogs = check_output("tail -n 15 " + SC.sdcp_logformat + " | tac", shell=True)
  print "<DIV CLASS='z-logs'><H1>System Logs</H1><PRE>{}</PRE></DIV>".format(syslogs)
 except Exception as err:
  print "<DIV CLASS='z-error'>{}</DIV>".format(str(err))

def examine_log(aWeb):
 try:
  from subprocess import check_output
  import sdcp.SettingsContainer as SC
  logfile = aWeb.get_value('logfile',SC.sdcp_logformat)
  syslogs = check_output("tail -n 15 " + logfile + " | tac", shell=True)
  print "<PRE>{}</PRE>".format(syslogs)
 except Exception as err:
  print "<PRE>{}</PRE>".format(str(err))      

def pdns_lookup_entries(aIP,aName,aDomain):
 from sdcp.core.GenLib import DB, sys_ip2ptr
 import sdcp.SettingsContainer as SC
 ptr     = sys_ip2ptr(aIP)
 fqdn    = aName + "." + aDomain
 retvals = {}
 domains = [ aDomain, ptr.partition('.')[2] ]
 
 db = DB()
 db.connect_details('localhost',SC.dnsdb_username, SC.dnsdb_password, SC.dnsdb_dbname)
 db.do("SELECT id,name, notified_serial from domains")
 domain_db = db.get_all_dict("name")
 domain_id = [ domain_db.get(domains[0],None), domain_db.get(domains[1],None) ] 
 db.do("SELECT id,content FROM records WHERE type = 'A' and domain_id = '{}' and name = '{}'".format(domain_id[0]['id'],fqdn)) 
 a_record = db.get_row()                       
 db.do("SELECT id,content FROM records WHERE type = 'PTR' and domain_id = '{}' and name = '{}'".format(domain_id[1]['id'],ptr)) 
 p_record = db.get_row() 
 if a_record and (a_record.get('content',None) == aIP):
  retvals['dns_a_id'] = a_record.get('id') 
 if p_record and (p_record.get('content',None) == fqdn):
  retvals['dns_ptr_id'] = p_record.get('id')
 db.close() 
 return retvals

def remote_json(aWeb):
 from json import dumps
 res = {}    
 op  = aWeb.get_value('op')
 if op == 'dns_lookup':
  ip   = aWeb.get_value('ip')
  name = aWeb.get_value('hostname')
  dom  = aWeb.get_value('domain')
  res  = pdns_lookup_entries(ip,name,dom)
 else:
  res['res'] = "op_not_found"
 print dumps(res,sort_keys = True)     


