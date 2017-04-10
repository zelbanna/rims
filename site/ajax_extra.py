"""Moduledocstring.

Ajax Generic calls module

"""
__author__= "Zacharias El Banna"                     
__version__ = "10.0GA"
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

def remote_json(aWeb):
 from json import dumps
 res = {}    
 op  = aWeb.get_value('op')
 # Assume DDI
 import sdcp.core.ddi as DDI

 ip   = aWeb.get_value('ip')
 name = aWeb.get_value('hostname')
 dom  = aWeb.get_value('domain')
 if   op == 'ddi_dns_lookup':
  res  = DDI.ddi_dns_lookup(ip,name,dom)
 elif op == 'ddi_dns_domains':
  res  = DDI.ddi_dns_domains()
 elif op == 'ddi_dns_update':
  aid  = aWeb.get_value('dns_a_id')
  pid  = aWeb.get_value('dns_ptr_id')
  res  = DDI.ddi_dns_update(ip,name,dom,aid,pid)
 elif op == 'ddi_dns_remove':
  aid  = aWeb.get_value('dns_a_id')
  pid  = aWeb.get_value('dns_ptr_id')
  res  = DDI.ddi_dns_remove(aid,pid)  
 elif op == 'ddi_ipam_lookup':
  res  = DDI.ddi_ipam_lookup(ip)
 elif op == 'ddi_ipam_update':
  iid  = aWeb.get_value('ipam_id')
  pid  = aWeb.get_value('dns_ptr_id')
  fqdn = aWeb.get_value('fqdn')
  res  = DDI.ddi_ipam_update(ip,iid,pid,fqdn)
 elif op == 'ddi_ipam_remove':
  iid  = aWeb.get_value('ipam_id')
  res  = DDI.ddi_ipam_remove(iid)
 else:
  res['op_result'] = "op_not_found"
 # aWeb.log_msg("remote_json - op_result: " + str(res))
 print dumps(res,sort_keys = True)     
