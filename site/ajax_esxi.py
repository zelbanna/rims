"""Module docstring.

Ajax ESXi calls module

"""
__author__= "Zacharias El Banna"                     
__version__ = "17.6.1GA"
__status__= "Production"

########################################## ESXi Operations ##########################################
#
# ESXi operations
#
def op(aWeb, aEsxi = None):
 excpt  = aWeb.get_value('except','-1')
 nstate = aWeb.get_value('nstate')
 vmid   = aWeb.get_value('vmid','-1')
 sort   = aWeb.get_value('sort','name')

 if not aEsxi:
  from sdcp.devices.ESXi import ESXi
  host   = aWeb.get_value('host')
  domain = aWeb.get_value('domain')
  aEsxi   = ESXi(host,domain)

 if nstate:
  from subprocess import check_call, check_output
  import sdcp.PackageContainer as PC
  try:
   PC.log_msg("ESXi: {} got command {}".format(aEsxi._fqdn,nstate))
   if nstate == 'vmsvc-snapshot.create':
    from time import strftime
    with aEsxi:
     aEsxi.ssh_send("vim-cmd vmsvc/snapshot.create {} 'Portal Snapshot' '{}'".format(vmid,strftime("%Y%m%d")))
   elif nstate == 'vmsvc-snapshot.revert':
    with aEsxi:
     data = aEsxi.ssh_send("vim-cmd vmsvc/snapshot.get {} ".format(vmid))
     s_last = 0
     for line in data.splitlines():
      if "Snapshot Id" in line:
       s_id = int(line.split()[3])
       s_last = s_last if s_last > s_id else s_id
     if s_last > 0:
      aEsxi.ssh_send("vim-cmd vmsvc/snapshot.revert {} {} suppressPowerOff".format(vmid,s_last))
   elif "vmsvc-" in nstate:
    vmop = nstate.partition('-')[2]
    with aEsxi:
     aEsxi.ssh_send("vim-cmd vmsvc/{} {}".format(vmop,vmid))
   elif nstate == 'poweroff':
    with aEsxi:
     aEsxi.ssh_send("poweroff")
   elif nstate == 'vmsoff':
    excpt = "" if vmid == '-1' else vmid
    check_call("/usr/local/sbin/ups-operations shutdown " + aEsxi._hostname + " " + excpt + " &", shell=True)
  except Exception as err:
   PC.log_msg("ESXi: nstate error [{}]".format(str(err)))

 statelist = aEsxi.get_vms(sort)
 # Formatting template (command, btn-xyz, vm-id, hover text)
 template="<A CLASS='z-btn z-small-btn z-op' TITLE='{3}' SPIN=true OP=load DIV=div_esxi_op URL='ajax.cgi?call=esxi_op&domain=" +  aEsxi._domain + "&host="+ aEsxi._hostname + "&nstate={0}&vmid={2}&sort=" + sort + "'><IMG SRC=images/btn-{1}.png></A>"
 if not nstate:
  print "<DIV CLASS=title>{}</DIV>".format(aEsxi._fqdn)
 else:
  print "<DIV CLASS=title>{} <SPAN style='font-size:12px'>{}:{}</SPAN></DIV>".format(aEsxi._fqdn,vmid, nstate.split('-')[1])
 print "<DIV CLASS=z-table>"
 print "<DIV CLASS=thead><DIV CLASS=th><A CLASS='z-op' OP=load DIV=div_esxi_op URL='ajax.cgi?call=esxi_op&domain=" +  aEsxi._domain + "&host="+ aEsxi._hostname + "&sort=" + ("id" if sort == "name" else "name") + "'>VM</A></DIV><DIV CLASS=th>Operations</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>"
 if nstate and nstate == 'vmsoff':
  print "<B>SHUTDOWN ALL VMs!</B>"
 else:
  print "SHUTDOWN ALL VMs!"
 print "</DIV><DIV CLASS=td><CENTER>" + template.format('vmsoff','shutdown',excpt, "Shutdown all VMs") + "&nbsp;</CENTER></DIV></DIV>"
 for vm in statelist:
  print "<DIV CLASS=tr><DIV CLASS=td>"
  print "<B>{}</B>".format(vm[1]) if vm[0] == vmid else vm[1]
  print "</DIV><DIV CLASS=td>"
  if vm[2] == "1":
   print template.format('vmsvc-power.shutdown','shutdown', vm[0], "Soft shutdown")
   print template.format('vmsvc-power.reboot','reboot', vm[0], "Soft reboot")
   print template.format('vmsvc-power.suspend','suspend', vm[0], "Suspend")
   print template.format('vmsvc-power.off','off', vm[0], "Hard power off")
  elif vm[2] == "3":
   print template.format('vmsvc-power.on','start', vm[0], "Start")
   print template.format('vmsvc-power.off','off', vm[0], "Hard power off")
  else:
   print template.format('vmsvc-power.on','start', vm[0], "Start")
   print template.format('vmsvc-snapshot.create','snapshot', vm[0], "Snapshot")
   print template.format('vmsvc-snapshot.revert','revert', vm[0], "Snapshot revert to last")
  print "</DIV></DIV>"
 print "</DIV></DIV>"
