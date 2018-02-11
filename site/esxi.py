"""Module docstring.

HTML5 Ajax ESXi calls module

"""
__author__= "Zacharias El Banna"
__version__ = "18.02.09GA"
__status__ = "Production"
__icon__ = 'images/icon-servers.png'

def main(aWeb):
 rows = aWeb.rest_call("device_list_type",{'base':'hypervisor'})['data']
 print "<NAV><UL>&nbsp;</UL></NAV>"
 print "<SECTION CLASS=content ID=div_content>"
 print "<SECTION CLASS=content-left ID=div_content_left>"
 print "<ARTICLE><DIV CLASS=table>"
 print "<DIV CLASS=thead><DIV CLASS=th>Type</DIV><DIV CLASS=th>Hostname</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for row in rows:
  print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><DIV CLASS=td>".format(row['type_name'])
  if row['type_name'] == 'esxi':
   print "<A CLASS=z-op DIV=main URL='sdcp.cgi?call=esxi_manage&id={}'>{}</A>".format(row['id'],row['hostname'])
  elif row['type_name'] == 'vcenter':
   print "<A TARGET=_blank HREF='https://{}:9443/vsphere-client/'>{}</A>".format(row['ipasc'],row['hostname'])
  print "</DIV></DIV>"
 print "</DIV></DIV></ARTICLE>"
 print "</SECTION>"
 print "</SECTION>"

########################################## ESXi Operations ##########################################
#
#
#
def manage(aWeb):
 id = aWeb['id']
 data = aWeb.rest_call("device_info",{'id':id})
 print "<NAV><UL>"
 print "<LI CLASS=warning><A CLASS=z-op DIV=div_content MSG='Really shut down?' URL='sdcp.cgi?call=esxi_op&ip=%s&next-state=poweroff&id=%s&name=esxi'>Shutdown</A></LI>".format(data['ip'],id)
 print "<LI><A CLASS=z-op DIV=div_content_right  URL=sdcp.cgi?call=esxi_graph&hostname={0}&domain={1}>Stats</A></LI>".format(data['info']['hostname'],data['info']['domain'])
 print "<LI><A CLASS=z-op DIV=div_content_right  URL=sdcp.cgi?call=esxi_logs&hostname={0}&domain={1}>Logs</A></LI>".format(data['info']['hostname'],data['info']['domain'])
 print "<LI><A CLASS=z-op HREF=https://{0}/ui     target=_blank>UI</A></LI>".format(data['ip'])
 print "<LI><A CLASS='z-op reload' DIV=main URL='sdcp.cgi?{}'></A></LI>".format(aWeb.get_args())
 print "<LI CLASS='right navinfo'><A>{}</A></LI>".format(data['info']['hostname'])
 print "</UL></NAV>"
 print "<SECTION CLASS=content ID=div_content>"
 print "<SECTION CLASS=content-left ID=div_content_left>"
 list(aWeb,data['ip'])
 print "</SECTION>" 
 print "<SECTION CLASS=content-right ID=div_content_right></SECTION>"
 print "</SECTION>"

#
#
def list(aWeb,aIP = None):
 ip   = aWeb.get('ip',aIP)
 sort = aWeb.get('sort','name') 
 statelist = aWeb.rest_call("esxi_list",{'ip':ip,'sort':sort})
 print "<ARTICLE>"
 print aWeb.button('reload',TITLE='Reload List',DIV='div_content_left',URL='sdcp.cgi?call=esxi_list&ip={}&sort={}'.format(ip,sort))
 print "<DIV CLASS=table>"
 print "<DIV CLASS=thead><DIV CLASS=th><A CLASS=z-op DIV=div_content_left URL='sdcp.cgi?call=esxi_list&ip=" + ip + "&sort=" + ("id" if sort == "name" else "name") + "'>VM</A></DIV><DIV CLASS=th>Operations</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for vm in statelist:
  print "<DIV CLASS=tr STYLE='padding:0px;' ID=div_vm_{}>".format(vm['id'])
  _vm_options(aWeb,ip,vm,False)
  print "</DIV>"
 print "</DIV></DIV></ARTICLE>"

#
#
def op(aWeb):
 if not aWeb.cookies.get('sdcp'):
  print "<SCRIPT>location.replace('index.cgi')</SCRIPT>"
  return
 cookie = aWeb.cookie_unjar('sdcp')
 res = aWeb.rest_call("esxi_op",{'ip':aWeb['ip'],'next-state':aWeb['next-state'], 'id':aWeb['id'],'name':aWeb['name'],'user_id':cookie['id']})
 _vm_options(aWeb,aWeb['ip'],res,True)

#
#
def _vm_options(aWeb,aIP,aVM,aHighlight):
 div = "div_vm_%s"%aVM['id']
 url = "sdcp.cgi?call=esxi_op&ip=%s&next-state={}&name=%s&id=%s"%(aIP,aVM['name'],aVM['id'])
 print "<DIV CLASS=td STYLE='padding:0px;'>{}</DIV><DIV CLASS='td controls' STYLE='width:150px'>&nbsp;".format("<B>{}</B>".format(aVM['name']) if aHighlight else aVM['name'])
 if int(aVM['state_id']) == 1:
  print aWeb.button('shutdown',DIV=div, SPIN='div_content_left', URL=url.format('vmsvc-power.shutdown'), TITLE='Soft shutdown')
  print aWeb.button('reboot',  DIV=div, SPIN='div_content_left', URL=url.format('vmsvc-power.reboot'), TITLE='Soft reboot')
  print aWeb.button('suspend', DIV=div, SPIN='div_content_left', URL=url.format('vmsvc-power.suspend'),TITLE='Suspend')
  print aWeb.button('off',     DIV=div, SPIN='div_content_left', URL=url.format('vmsvc-power.off'), TITLE='Hard power off')
 elif int(aVM['state_id']) == 3:
  print aWeb.button('start',   DIV=div, SPIN='div_content_left', URL=url.format('vmsvc-power.on'), TITLE='Start')
  print aWeb.button('off',     DIV=div, SPIN='div_content_left', URL=url.format('vmsvc-power.off'), TITLE='Hard power off')
 elif int(aVM['state_id']) == 2:
  print aWeb.button('start',   DIV=div, SPIN='div_content_left', URL=url.format('vmsvc-power.on'), TITLE='Start')
  print aWeb.button('snapshot',DIV=div, SPIN='div_content_left', URL=url.format('vmsvc-snapshot.create'), TITLE='Snapshot')
  print aWeb.button('info',    DIV='div_content_right',SPIN='true',URL='sdcp.cgi?call=esxi_snapshot&ip={}&vmid={}'.format(aIP,aVM['id']), TITLE='Snapshot info')
 else:
  print "Unknown state [{}]".format(aVM['state_id'])
 print "</DIV>"


#
# Graphing
#
def graph(aWeb):
 from ..tools.munin import widget_cols
 hostname = aWeb['hostname']
 domain   = aWeb['domain']
 print "<ARTICLE STYLE='overflow-x:auto;'>"
 widget_cols([ "{1}/{0}.{1}/esxi_vm_info".format(hostname,domain), "{1}/{0}.{1}/esxi_cpu_info".format(hostname,domain), "{1}/{0}.{1}/esxi_mem_info".format(hostname,domain) ])
 print "</ARTICLE>"

#
#
def logs(aWeb):
 hostname = aWeb['hostname']
 try:
  from subprocess import check_output
  from ..  import SettingsContainer as SC
  logs = check_output("tail -n 30 " + SC.esxi['logformat'].format(hostname) + " | tac", shell=True)
  print "<ARTICLE><P>%s operation logs</P><P CLASS='machine-text'>%s</P></ARTICLE>"%(hostname,logs.replace('\n','<BR>'))
 except: pass

#
#
def snapshot(aWeb):
 cookie = aWeb.cookie_unjar('sdcp')
 from ..devices.esxi import Device
 ip   = aWeb['ip']
 vmid = aWeb['vmid']
 data = {}
 id   = 0
 print "<ARTICLE><P>Snapshots ({})</P>".format(vmid)
 print "<!-- {}@'vim-cmd vmsvc/snapshot.get {}' -->".format(ip,vmid)
 print "<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Name</DIV><DIV CLASS=th>Id</DIV><DIV CLASS=th>Description</DIV><DIV CLASS=th>Created</DIV><DIV CLASS=th>State</DIV><DIV CLASS=th>&nbsp;</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 with Device(ip) as esxi:
  snapshots = esxi.ssh_send("vim-cmd vmsvc/snapshot.get {} ".format(vmid),cookie['id'])
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
     print aWeb.button('revert', TITLE='Revert', DIV='div_content_right',SPIN='true', URL='sdcp.cgi?call=esxi_snap_op&ip=%s&vmid=%s&op=revert&snapid=%s'%(ip,vmid,data['id']))
     print aWeb.button('delete', TITLE='Delete', DIV='div_content_right',SPIN='true', URL='sdcp.cgi?call=esxi_snap_op&ip=%s&vmid=%s&op=remove&snapid=%s'%(ip,vmid,data['id']))
     print "</DIV></DIV>"
     data = {}
 print "</DIV></DIV>"
 print "<SPAN CLASS='results'>[Highest ID:{}]</SPAN></ARTICLE>".format(id)

#
#
#
def snap_op(aWeb):
 from ..devices.esxi import Device
 cookie = aWeb.cookie_unjar('sdcp')
 ip   = aWeb['ip']
 vmid = aWeb['vmid']
 snap = aWeb['snapid']
 op   = aWeb['op']
 if   op == 'revert':
  template = "vim-cmd vmsvc/snapshot.revert {} {} suppressPowerOff"
 elif op == 'remove':
  template = "vim-cmd vmsvc/snapshot.remove {} {}"
 with Device(ip) as esxi:
  esxi.ssh_send(template.format(vmid,snap),cookie['id'])
 print "<ARTICLE>Carried out '{}' on '{}@{}'</ARTICLE>".format(op,vmid,ip)
