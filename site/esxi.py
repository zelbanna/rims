"""Module docstring.

HTML5 Ajax ESXi calls module

"""
__author__= "Zacharias El Banna"
__version__ = "18.03.16"
__status__ = "Production"
__icon__ = 'images/icon-servers.png'
__type__ = 'menuitem'

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
 data = aWeb.rest_call("device_basics",{'id':id})
 print "<NAV><UL>"
 print "<LI CLASS=warning><A CLASS=z-op DIV=div_content MSG='Really shut down?' URL='sdcp.cgi?call=esxi_op&ip=%s&next-state=poweroff&id=%s'>Shutdown</A></LI>".format(data['ip'],id)
 print "<LI><A CLASS=z-op DIV=div_content_right  URL=sdcp.cgi?call=esxi_graph&hostname={0}&domain={1}>Stats</A></LI>".format(data['hostname'],data['domain'])
 print "<LI><A CLASS=z-op DIV=div_content_right  URL=sdcp.cgi?call=esxi_logs&hostname={0}&domain={1}>Logs</A></LI>".format(data['hostname'],data['domain'])
 print "<LI><A CLASS=z-op HREF=https://{0}/ui     target=_blank>UI</A></LI>".format(data['ip'])
 print "<LI><A CLASS='z-op reload' DIV=main URL='sdcp.cgi?call=esxi_manage&id=%s'></A></LI>".format(id)
 print "<LI CLASS='right navinfo'><A>{}</A></LI>".format(data['hostname'])
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
 print "<DIV CLASS=thead><DIV CLASS=th><A CLASS=z-op DIV=div_content_left URL='sdcp.cgi?call=esxi_list&ip=%s&sort=%s'>VM</A></DIV><DIV CLASS=th>Operations</DIV></DIV>"%(ip,"id" if sort == "name" else "name")
 print "<DIV CLASS=tbody>"
 for vm in statelist:
  print "<DIV CLASS=tr STYLE='padding:0px;'><DIV CLASS=td STYLE='padding:0px;'>%s</DIV><DIV CLASS='td controls' ID=div_vm_%s STYLE='width:120px'>"%(vm['name'],vm['id'])
  _vm_options(aWeb,ip,vm,False)
  print "</DIV></DIV>"
 print "</DIV></DIV></ARTICLE>"

#
#
def op(aWeb):
 cookie = aWeb.cookie_unjar('system')
 args = aWeb.get_args2dict(['call'])
 args['user_id'] = cookie['id']
 res = aWeb.rest_call("esxi_op",args)
 if aWeb['output'] == 'div':
  print "<ARTICLE>Carried out '{}' on '{}@{}'</ARTICLE>".format(aWeb['next-state'],aWeb['id'],aWeb['ip'])
 else:
  _vm_options(aWeb,aWeb['ip'],res,True)

#
#
def _vm_options(aWeb,aIP,aVM,aHighlight):
 div = "div_vm_%s"%aVM['id']
 url = "sdcp.cgi?call=esxi_op&ip=%s&next-state={}&id=%s"%(aIP,aVM['id'])
 if aHighlight:
  print "<DIV CLASS='border'>"
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
  print aWeb.button('info',    DIV='div_content_right',SPIN='true',URL='sdcp.cgi?call=esxi_snapshot&ip={}&id={}'.format(aIP,aVM['id']), TITLE='Snapshot info')
 else:
  print "Unknown state [{}]".format(aVM['state_id'])
 if aHighlight:
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
 res = aWeb.rest_call("esxi_logs",{'hostname':aWeb['hostname']})
 print "<ARTICLE><P>%s operation logs</P><P CLASS='machine-text'>%s</P></ARTICLE>"%(aWeb['hostname'],"<BR>".join(res['data']))

#
#
def snapshot(aWeb):
 cookie = aWeb.cookie_unjar('system')
 res = aWeb.rest_call("esxi_snapshots",{'ip':aWeb['ip'],'id':aWeb['id'],'user_id':cookie['id']}) 
 print "<ARTICLE><P>Snapshots (%s) Highest ID:%s</P>"%(aWeb['id'],res['highest'])
 print "<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Name</DIV><DIV CLASS=th>Id</DIV><DIV CLASS=th>Description</DIV><DIV CLASS=th>Created</DIV><DIV CLASS=th>State</DIV><DIV CLASS=th>&nbsp;</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for snap in res['data']:
  print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS='td controls'>".format(snap['name'],snap['id'],snap['desc'],snap['created'],snap['state'])
  print aWeb.button('revert', TITLE='Revert', DIV='div_content_right',SPIN='true', URL='sdcp.cgi?call=esxi_op&ip=%s&id=%s&next-state=vmsvc-snapshot.revert&snapshot=%s&output=div'%(aWeb['ip'],aWeb['id'],snap['id']))
  print aWeb.button('delete', TITLE='Delete', DIV='div_content_right',SPIN='true', URL='sdcp.cgi?call=esxi_op&ip=%s&id=%s&next-state=vmsvc-snapshot.remove&snapshot=%s&output=div'%(aWeb['ip'],aWeb['id'],snap['id']))
  print "</DIV></DIV>"
 print "</DIV></DIV>"
