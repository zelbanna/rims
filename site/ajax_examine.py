"""Module docstring.

Ajax Generic calls module

"""
__author__= "Zacharias El Banna"                     
__version__ = "17.6.1GA"
__status__= "Production"

######################################## Examine pane - logs ########################################
#
#
#

def clear_logs(aWeb, aClear = True):
 domain  = aWeb.get_value('domain')
 try:
  from subprocess import check_output
  import sdcp.PackageContainer as PC
  import sdcp.core.GenLib as GL
  if aClear:
   open("/var/log/network/"+ domain +".log",'w').close()
   open(PC.generic_logformat,'w').close()
   GL.log_msg("Emptied logs")
  netlogs = check_output("tail -n 15 /var/log/network/{}.log | tac".format(domain), shell=True)
  print "<DIV CLASS='z-logs'><H1>Network Logs</H1><PRE>{}</PRE></DIV>".format(netlogs)
  print "<BR>"
  syslogs = check_output("tail -n 15 " + PC.generic_logformat + " | tac", shell=True)
  print "<DIV CLASS='z-logs'><H1>System Logs</H1><PRE>{}</PRE></DIV>".format(syslogs)
 except Exception as err:
  print "<DIV CLASS='z-error'>{}</DIV>".format(str(err))

def log(aWeb):
 try:
  from subprocess import check_output
  import sdcp.PackageContainer as PC
  logfile = aWeb.get_value('logfile',PC.generic_logformat)
  syslogs = check_output("tail -n 15 " + logfile + " | tac", shell=True)
  print "<PRE>{}</PRE>".format(syslogs)
 except Exception as err:
  print "<PRE>{}</PRE>".format(str(err))      
