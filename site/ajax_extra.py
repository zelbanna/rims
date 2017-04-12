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
 from json import loads, dumps
 res = {}    
 op  = aWeb.get_value('op')
 args= aWeb.get_value('args')
 arg = loads(args)
 module = op.partition('_')[0]
 if   module == 'ddi':
  import sdcp.core.ddi as mod
 else:
  mod = None

 try:
  fun = getattr(mod,op,None)
  res = fun(arg)
 except Exception as err:
  res['err'] = str(err)
 # aWeb.log_msg("remote_json - op_result: " + str(res))
 print dumps(res,sort_keys = True)     
