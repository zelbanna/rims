"""Moduledocstring.

Ajax ESXi calls module

"""
__author__= "Zacharias El Banna"                     
__version__ = "10.0GA"
__status__= "Production"

########################################## ESXi Operations ##########################################
#
# ESXi operations
#
def op(aWeb, aEsxi = None):
 excpt  = aWeb.get_value('except','-1')
 nstate = aWeb.get_value('nstate')
 vmid   = aWeb.get_value('vmid','-1')

 if not aEsxi:
  from sdcp.devices.ESXi import ESXi
  host   = aWeb.get_value('host')
  domain = aWeb.get_value('domain')
  aEsxi   = ESXi(host,domain)

 if nstate:
  from subprocess import check_call, check_output
  try:
   aWeb.log_msg("ESXi: {} got command {}".format(aEsxi._fqdn,nstate))
   if "vm-" in nstate:
    vmop = nstate.split('-')[1]
    with aEsxi:
     aEsxi.ssh_send("vim-cmd vmsvc/power." + vmop + " " + vmid)
   elif nstate == 'poweroff':
    with aEsxi:
     aEsxi.ssh_send("poweroff")
   elif nstate == 'vmsoff':
    excpt = "" if vmid == '-1' else vmid
    check_call("/usr/local/sbin/ups-operations shutdown " + aEsxi._hostname + " " + excpt + " &", shell=True)
  except Exception as err:
   aWeb.log_msg("ESXi: nstate error [{}]".format(str(err)))

 print "<TABLE>"
 template="<A CLASS='z-btn z-small-btn z-op' TITLE='{3}' OP=load DIV=div_esxi_op LNK='ajax.cgi?call=esxi_op&domain=" +  aEsxi._domain + "&host="+ aEsxi._hostname + "&nstate={0}&vmid={2}'><IMG SRC=images/btn-{1}.png></A>"
 statelist = aEsxi.get_vms()
 if not nstate:
  print "<TR><TH CLASS='z-header' COLSPAN=2>{}</TH></TR>".format(aEsxi._fqdn)
 else:
  print "<TR><TH CLASS='z-header' COLSPAN=2>{} - {}:{}</TH></TR>".format(aEsxi._fqdn,vmid, nstate.split('-')[1])
 print "<TR><TH>VM</TH><TH>Operations</TH></TR><TR>"
 if nstate and nstate == 'vmsoff':
  print "<TD><B>SHUTDOWN ALL VMs!</B></TD>"
 else:
  print "<TD>SHUTDOWN ALL VMs!</TD>"
 print "<TD><CENTER>" + template.format('vmsoff','shutdown',excpt, "Shutdown all VMs") + "</CENTER></TD></TR>"
 for vm in statelist:
  if vm[0] == vmid:
   print "<TR><TD><B>" + vm[1] + "</B></TD>"
  else:
   print "<TR><TD>" + vm[1] + "</TD>"
  print "<TD><CENTER>"
  if vm[2] == "1":
   print template.format('vm-shutdown','shutdown', vm[0], "Soft shutdown")
   print template.format('vm-reboot','reboot', vm[0], "Soft reboot")
   print template.format('vm-suspend','suspend', vm[0], "Suspend")
   print template.format('vm-off','off', vm[0], "Hard power off")
  elif vm[2] == "3":
   print template.format('vm-on','start', vm[0], "Start")
   print template.format('vm-off','off', vm[0], "Hard power off")
  else:
   print template.format('vm-on','start', vm[0], "Start")
  print "</CENTER></TD></TR>"
 print "</TABLE>"
