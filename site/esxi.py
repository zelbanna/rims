"""HTML5 Ajax ESXi module"""
__author__= "Zacharias El Banna"
__icon__ = '../images/icon-servers.png'
__type__ = 'menuitem'

def main(aWeb):
 rows = aWeb.rest_call("device/list",{'field':'base','search':'hypervisor','extra':['type','url'],'sort':'hostname'})['data']
 aWeb.wr("<NAV><UL>&nbsp;</UL></NAV>")
 aWeb.wr("<SECTION CLASS=content ID=div_content>")
 aWeb.wr("<SECTION CLASS=content-left ID=div_content_left>")
 aWeb.wr("<ARTICLE><DIV CLASS=table>")
 aWeb.wr("<DIV CLASS=thead><DIV CLASS=th>Hostname</DIV><DIV CLASS=th>Type</DIV><DIV CLASS=th>&nbsp;</DIV></DIV>")
 aWeb.wr("<DIV CLASS=tbody>")
 for row in rows:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%(hostname)s</DIV><DIV CLASS=td>%(type_name)s</DIV><DIV CLASS=td>"%row)
  if row['type_name'] == 'esxi':
   aWeb.wr(aWeb.button('info', DIV='main', URL='esxi_manage?id=%s'%row['id'], TITLE='Management'))
  if row['url']:
   aWeb.wr(aWeb.button('ui', TARGET='_blank', HREF=row['url'], TITLE='UI'))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</DIV></DIV></ARTICLE>")
 aWeb.wr("</SECTION>")
 aWeb.wr("</SECTION>")

########################################## ESXi Operations ##########################################
#
#
#
def manage(aWeb):
 id = aWeb['id']
 data = aWeb.rest_call("device/info",{'id':id,'op':'basics'})
 aWeb.wr("<NAV><UL>")
 aWeb.wr("<LI CLASS=warning><A CLASS=z-op DIV=div_content MSG='Really shut down?' URL='esxi_op?ip=%s&next-state=poweroff&id=%s'>Shutdown</A></LI>".format(data['ip'],id))
 aWeb.wr("<LI><A CLASS=z-op DIV=div_content_right  URL='esxi_logs?ip=%s'>Logs</A></LI>"%data['ip'])
 if data['info']['url']:
  aWeb.wr("<LI><A CLASS=z-op HREF='%s'     target=_blank>UI</A></LI>"%(data['info']['url']))
 aWeb.wr("<LI><A CLASS='z-op reload' DIV=main URL='esxi_manage?id=%s'></A></LI>"%(id))
 aWeb.wr("<LI CLASS='right navinfo'><A>{}</A></LI>".format(data['info']['hostname']))
 aWeb.wr("</UL></NAV>")
 aWeb.wr("<SECTION CLASS=content ID=div_content>")
 aWeb.wr("<SECTION CLASS=content-left ID=div_content_left>")
 list(aWeb,data['ip'])
 aWeb.wr("</SECTION>")
 aWeb.wr("<SECTION CLASS=content-right ID=div_content_right></SECTION>")
 aWeb.wr("</SECTION>")

#
#
def list(aWeb,aIP = None):
 ip   = aWeb.get('ip',aIP)
 sort = aWeb.get('sort','name')
 res = aWeb.rest_call("esxi/list",{'ip':ip,'sort':sort})
 statelist = res['data']
 aWeb.wr("<ARTICLE>")
 aWeb.wr(aWeb.button('reload',TITLE='Reload List',DIV='div_content_left',URL='esxi_list?ip=%s&sort=%s'%(ip,sort)))
 aWeb.wr("<DIV CLASS=table>")
 aWeb.wr("<DIV CLASS=thead><DIV CLASS=th><A CLASS=z-op DIV=div_content_left URL='esxi_list?ip=%s&sort=%s'>VM</A></DIV><DIV CLASS=th>Operations</DIV></DIV>"%(ip,"id" if sort == "name" else "name"))
 aWeb.wr("<DIV CLASS=tbody>")
 for vm in statelist:
  aWeb.wr("<DIV CLASS=tr STYLE='padding:0px;'><DIV CLASS=td STYLE='padding:0px;'>%s</DIV><DIV CLASS=td ID=div_vm_%s STYLE='width:120px'>"%(vm['name'],vm['id']))
  _vm_options(aWeb,ip,vm,False)
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</DIV></DIV></ARTICLE>")

#
#
def op(aWeb):
 args = aWeb.args()
 res = aWeb.rest_call("esxi/op",args)
 if aWeb['output'] == 'div':
  aWeb.wr("<ARTICLE>Carried out '{}' on '{}@{}'</ARTICLE>".format(aWeb['next-state'],aWeb['id'],aWeb['ip']))
 else:
  _vm_options(aWeb,aWeb['ip'],res,True)

#
#
def _vm_options(aWeb,aIP,aVM,aHighlight):
 div = "div_vm_%s"%aVM['id']
 url = 'esxi_op?ip=%s&next-state={}&id=%s'%(aIP,aVM['id'])
 if aHighlight:
  aWeb.wr("<DIV CLASS='border'>")
 if int(aVM['state_id']) == 1:
  aWeb.wr(aWeb.button('stop',    DIV=div, SPIN='div_content_left', URL=url.format('vmsvc-power.shutdown'), TITLE='Soft shutdown'))
  aWeb.wr(aWeb.button('reload',  DIV=div, SPIN='div_content_left', URL=url.format('vmsvc-power.reboot'), TITLE='Soft reboot'))
  aWeb.wr(aWeb.button('suspend', DIV=div, SPIN='div_content_left', URL=url.format('vmsvc-power.suspend'),TITLE='Suspend'))
  aWeb.wr(aWeb.button('off',     DIV=div, SPIN='div_content_left', URL=url.format('vmsvc-power.off'), TITLE='Hard power off'))
  aWeb.wr(aWeb.button('term',    HREF="https://%s/ui/#/console/%s"%(aIP,aVM['id']),  TARGET='_blank', TITLE='vSphere Console'))
 elif int(aVM['state_id']) == 3:
  aWeb.wr(aWeb.button('start',   DIV=div, SPIN='div_content_left', URL=url.format('vmsvc-power.on'), TITLE='Start'))
  aWeb.wr(aWeb.button('off',     DIV=div, SPIN='div_content_left', URL=url.format('vmsvc-power.off'), TITLE='Hard power off'))
 elif int(aVM['state_id']) == 2:
  aWeb.wr(aWeb.button('start',   DIV=div, SPIN='div_content_left', URL=url.format('vmsvc-power.on'), TITLE='Start'))
  aWeb.wr(aWeb.button('snapshot',DIV=div, SPIN='div_content_left', URL=url.format('vmsvc-snapshot.create'), TITLE='Snapshot'))
  aWeb.wr(aWeb.button('info',    DIV='div_content_right',SPIN='true',URL='esxi_snapshot?ip={}&id={}'.format(aIP,aVM['id']), TITLE='Snapshot info'))
 else:
  aWeb.wr("Unknown state [{}]".format(aVM['state_id']))
 if aHighlight:
  aWeb.wr("</DIV>")


#
#
def logs(aWeb):
 res = aWeb.rest_call("esxi/logs",{'ip':aWeb['ip']})
 aWeb.wr("<ARTICLE><P>Operation logs</P><P CLASS='machine-text'>%s</P></ARTICLE>"%("<BR>".join(res['data'])))

#
#
def snapshot(aWeb):
 res = aWeb.rest_call("esxi/snapshots",{'ip':aWeb['ip'],'id':aWeb['id']})
 aWeb.wr("<ARTICLE><P>Snapshots (%s) Highest ID:%s</P>"%(aWeb['id'],res['highest']))
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Name</DIV><DIV CLASS=th>Id</DIV><DIV CLASS=th>Description</DIV><DIV CLASS=th>Created</DIV><DIV CLASS=th>State</DIV><DIV CLASS=th>&nbsp;</DIV></DIV>")
 aWeb.wr("<DIV CLASS=tbody>")
 for snap in res['data']:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>".format(snap['name'],snap['id'],snap['desc'],snap['created'],snap['state']))
  aWeb.wr(aWeb.button('revert', TITLE='Revert', DIV='div_content_right',SPIN='true', URL='esxi_op?ip=%s&id=%s&next-state=vmsvc-snapshot.revert&snapshot=%s&output=div'%(aWeb['ip'],aWeb['id'],snap['id'])))
  aWeb.wr(aWeb.button('delete', TITLE='Delete', DIV='div_content_right',SPIN='true', URL='esxi_op?ip=%s&id=%s&next-state=vmsvc-snapshot.remove&snapshot=%s&output=div'%(aWeb['ip'],aWeb['id'],snap['id'])))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</DIV></DIV>")
