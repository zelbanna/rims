"""Module docstring.

Ajax ESXi calls module

"""
__author__= "Zacharias El Banna"                     
__version__ = "17.11.01GA"
__status__= "Production"


def hypervisors(aWeb):
 from sdcp.core.dbase import DB
 with DB() as db:
  db.do("SELECT devices.id, INET_NTOA(ip) AS ipasc, hostname, devicetypes.base as type_base, devicetypes.name as type_name FROM devices LEFT JOIN devicetypes ON devices.type_id = devicetypes.id WHERE devicetypes.base = 'hypervisor' ORDER BY type_name,hostname")
  rows = db.get_rows() 
 print "<DIV CLASS=z-navbar ID=div_navbar>"
 print "&nbsp;</DIV>"    
 print "<DIV CLASS=z-content ID=div_content>"
 print "<DIV CLASS=z-content-left ID=div_content_left>"
 print "<DIV CLASS=z-frame><DIV CLASS=z-table>"
 print "<DIV CLASS=thead><DIV CLASS=th>Type</DIV><DIV CLASS=th>Hostname</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for row in rows:
  print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><DIV CLASS=td>".format(row['type_name'])
  if   row['type_name'] == 'esxi':
   print "<A CLASS=z-op DIV=div_main_cont URL='sdcp.cgi?call=esxi_main&id={}'>{}</A>".format(row['id'],row['hostname'])
  elif row['type_name'] == 'vcenter':
   print "<A TARGET=_blank HREF='https://{}:9443/vsphere-client/'>{}</A>".format(row['ipasc'],row['hostname'])
  print "</DIV></DIV>"
 print "</DIV></DIV></DIV>"
 print "</DIV>"
 print "</DIV>"

########################################## ESXi Operations ##########################################
#
#
#
def main(aWeb):
 from sdcp.core.dbase import DB
 id = aWeb['id']
 with DB() as db:
  db.do("SELECT hostname, INET_NTOA(ip) as ipasc, domains.name AS domain FROM devices INNER JOIN domains ON domains.id = devices.a_dom_id WHERE devices.id = '{}'".format(id))
  data = db.get_row() 
 print "<DIV CLASS=z-navbar ID=div_navbar>"
 print "<A CLASS='z-warning z-op' DIV=div_esxi_op MSG='Really shut down?' URL='sdcp.cgi?call=esxi_op&nstate=poweroff&id={}'>Shutdown</A>".format(id)
 print "<A CLASS=z-op DIV=div_content_right  URL=sdcp.cgi?call=esxi_graph&hostname={0}&domain={1}>Stats</A>".format(data['hostname'],data['domain'])
 print "<A CLASS=z-op DIV=div_content_right  URL=sdcp.cgi?call=esxi_logs&hostname={0}&domain={1}>Logs</A>".format(data['hostname'],data['domain'])
 print "<A CLASS=z-op HREF=https://{0}/ui     target=_blank>UI</A>".format(data['ipasc'])
 print "<A CLASS='z-op z-reload' DIV=div_main_cont URL='sdcp.cgi?{}'></A>".format(aWeb.get_args())
 print "<SPAN CLASS='z-right z-navinfo'>{}</SPAN>".format(data['hostname'])
 print "</DIV>"
 print "<DIV CLASS=z-content ID=div_content>"
 print "<DIV CLASS=z-content-left ID=div_content_left>"
 list(aWeb,data['ipasc'])
 print "</DIV>" 
 print "<DIV CLASS=z-content-right ID=div_content_right></DIV>"
 print "</DIV>"        

#
#
def list(aWeb,aIP = None):
 from sdcp.devices.esxi import Device
 ip     = aWeb.get('ip',aIP)
 sort   = aWeb.get('sort','name')
 esxi   = Device(ip)
 print "<DIV CLASS=z-frame>"
 print "<A TITLE='Reload List' CLASS='z-btn z-small-btn z-op' DIV=div_content_left URL='sdcp.cgi?call=esxi_list&ip={}&sort={}'><IMG SRC='images/btn-reload.png'></A>".format(ip,sort)
 print "<DIV CLASS=z-table>"
 print "<DIV CLASS=thead><DIV CLASS=th><A CLASS=z-op DIV=div_content_left URL='sdcp.cgi?call=esxi_op&ip=" + ip + "&sort=" + ("id" if sort == "name" else "name") + "'>VM</A></DIV><DIV CLASS=th>Operations</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 statelist = esxi.get_vms(sort)
 for vm in statelist:
  print "<DIV CLASS=tr style='padding:0px;' ID=div_vm_{}>".format(vm[0])
  _vm_options(ip,vm[0],vm[1],vm[2],False)
  print "</DIV>"
 print "</DIV></DIV></DIV>"

#
#
def _vm_options(aIP,aVMid,aVMname,aState,aHighlight):
 template="<A CLASS='z-btn z-small-btn z-op' TITLE='{2}' DIV=div_vm_"+aVMid+" SPIN=div_content_left URL='sdcp.cgi?call=esxi_vmop&ip=" + aIP + "&nstate={0}&vmname="+aVMname+"&vmid="+aVMid+"'><IMG SRC=images/btn-{1}.png></A>"
 print "<DIV CLASS=td style='padding:0px;'>{}</DIV><DIV CLASS=td style='width:150px'>&nbsp;".format("<B>{}</B>".format(aVMname) if aHighlight else aVMname)
 if int(aState) == 1:
  print template.format('vmsvc-power.shutdown','shutdown', "Soft shutdown")
  print template.format('vmsvc-power.reboot','reboot', "Soft reboot")
  print template.format('vmsvc-power.suspend','suspend', "Suspend")
  print template.format('vmsvc-power.off','off', "Hard power off")
 elif int(aState) == 3:
  print template.format('vmsvc-power.on','start', "Start")
  print template.format('vmsvc-power.off','off', "Hard power off")
 elif int(aState) == 2:
  print template.format('vmsvc-power.on','start', "Start")
  print template.format('vmsvc-snapshot.create','snapshot', "Snapshot")
  print "<A CLASS='z-op z-btn z-small-btn' DIV=div_content_right SPIN=true TITLE='Snapshot - Info' URL=sdcp.cgi?call=esxi_snapshot&ip={}&vmid={}><IMG SRC='images/btn-info.png'></A>".format(aIP,aVMid)
 else:
  print "Unknown state [{}]".format(aState)
 print "</DIV>"

#
#
def vmop(aWeb):
 from sdcp.devices.esxi import Device
 from time import sleep
 ip     = aWeb.get('ip')
 nstate = aWeb['nstate']
 vmid   = aWeb.get('vmid','-1')
 name   = aWeb['vmname'] 
 userid = aWeb.cookie.get('sdcp_id')
 if not userid:
  print "<SCRIPT>location.replace('index.cgi')</SCRIPT>"
  return
 esxi   = Device(ip)
 try:
  if nstate == 'vmsvc-snapshot.create':
   from time import strftime
   with esxi:
    esxi.ssh_send("vim-cmd vmsvc/snapshot.create {} 'Portal Snapshot' '{}'".format(vmid,strftime("%Y%m%d")),userid)
  elif "vmsvc-" in nstate:
   vmop = nstate.partition('-')[2]
   with esxi:
    esxi.ssh_send("vim-cmd vmsvc/{} {}".format(vmop,vmid),userid)
    sleep(4)
  elif nstate == 'poweroff':
   with esxi:
    esxi.ssh_send("poweroff",userid)
 except Exception as err:
  aWeb.log("esxi: nstate error [{}]".format(str(err)))
 _vm_options(ip,vmid,name,esxi.get_state_vm(vmid),True)

#
# Graphing
#
def graph(aWeb):
 from sdcp.tools.munin import widget_cols
 hostname = aWeb['hostname']
 domain   = aWeb['domain']
 print "<DIV CLASS=z-frame style='overflow-x:auto;'>"
 widget_cols([ "{1}/{0}.{1}/esxi_vm_info".format(hostname,domain), "{1}/{0}.{1}/esxi_cpu_info".format(hostname,domain), "{1}/{0}.{1}/esxi_mem_info".format(hostname,domain) ])
 print "</DIV>"

#
#
def logs(aWeb):
 hostname = aWeb['hostname']
 try:
  from subprocess import check_output
  from sdcp import PackageContainer as PC
  logs = check_output("tail -n 30 " + PC.esxi['logformat'].format(hostname) + " | tac", shell=True)
  print "<DIV CLASS='z-logs'><H1>{} operation logs</H1>{}</DIV>".format("{}".format(hostname),logs.replace('\n','<BR>'))
 except: pass

#
#
def snapshot(aWeb):
 from sdcp.devices.esxi import Device
 ip   = aWeb['ip']
 vmid = aWeb['vmid']
 data = {}
 id   = 0
 template="<A CLASS='z-btn z-small-btn z-op' TITLE='{0}' SPIN=true DIV=div_content_right URL='sdcp.cgi?call=esxi_snap_op&ip=" + ip + "&vmid=" + vmid + "&snapid={3}&op={2}'><IMG SRC=images/btn-{1}.png></A>"
 print "<DIV CLASS=z-frame>"
 print "<DIV CLASS=title>Snapshots ({})</DIV>".format(vmid)
 print "<!-- {}@'vim-cmd vmsvc/snapshot.get {}' -->".format(ip,vmid)
 print "<DIV CLASS=z-table><DIV CLASS=thead><DIV CLASS=th>Name</DIV><DIV CLASS=th>Id</DIV><DIV CLASS=th>Description</DIV><DIV CLASS=th>Created</DIV><DIV CLASS=th>State</DIV><DIV CLASS=th>&nbsp;</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 with Device(ip) as esxi:
  snapshots = esxi.ssh_send("vim-cmd vmsvc/snapshot.get {} ".format(vmid),aWeb.cookie.get('sdcp_id'))
  for field in snapshots.splitlines():
   if "Snapshot" in field:
    parts = field.partition(':')
    key = parts[0].strip()
    val = parts[2].strip()
    if key[-4:] == 'Name':
     data['name'] = val
    elif key[-10:] == 'Desciption':
     data['desc'] = val
    elif key[-10:] == 'Created On':
     data['created'] = val
    elif key[-2:] == 'Id':
     data['id'] = val
     if int(val) > id:
      id = int(val)
    elif key[-5:] == 'State':
     # Last!
     data['state'] = val
     print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>".format(data['name'],data['id'],data['desc'],data['created'],data['state'])
     print template.format("Revert","revert","revert",data['id'])
     print template.format("Remove","remove","remove",data['id'])
     print "</DIV></DIV>"
     data = {}
 print "</DIV></DIV><SPAN STYLE='float:right; font-size:12px;'>[Highest ID:{}]</SPAN></DIV>".format(id)

#
#
#
def snap_op(aWeb):
 from sdcp.devices.esxi import Device
 ip   = aWeb['ip']
 vmid = aWeb['vmid']
 snap = aWeb['snapid']
 op   = aWeb['op']
 if   op == 'revert':
  template = "vim-cmd vmsvc/snapshot.revert {} {} suppressPowerOff"
 elif op == 'remove':
  template = "vim-cmd vmsvc/snapshot.remove {} {}"
 with Device(ip) as esxi:
  esxi.ssh_send(template.format(vmid,snap),aWeb.cookie.get('sdcp_id'))
 print "<DIV CLASS=z-frame>Carried out '{}' on '{}@{}'</DIV>".format(op,vmid,ip)
