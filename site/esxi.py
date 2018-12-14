"""HTML5 Ajax ESXi module"""
__author__= "Zacharias El Banna"

########################################## ESXi Operations ##########################################
#
#
#
def manage(aWeb):
 id = aWeb['id']
 data = aWeb.rest_call("device/management",{'id':id})
 aWeb.wr("<NAV><UL>")
 aWeb.wr("<LI><A CLASS=z-op DIV=div_content_right  URL='device_logs?id=%s'>Logs</A></LI>"%id)
 if data['data']['url']:
  aWeb.wr("<LI><A CLASS=z-op HREF='%s'     target=_blank>UI</A></LI>"%(data['data']['url']))
 aWeb.wr("<LI><A CLASS='z-op reload' DIV=main URL='esxi_manage?id=%s'></A></LI>"%(id))
 aWeb.wr("<LI CLASS='right navinfo'><A>{}</A></LI>".format(data['data']['hostname']))
 aWeb.wr("</UL></NAV>")
 aWeb.wr("<SECTION CLASS=content ID=div_content>")
 aWeb.wr("<SECTION CLASS=content-left ID=div_content_left>")
 list(aWeb)
 aWeb.wr("</SECTION>")
 aWeb.wr("<SECTION CLASS=content-right ID=div_content_right></SECTION>")
 aWeb.wr("</SECTION>")

#
#
def list(aWeb):
 sort = aWeb.get('sort','name')
 res = aWeb.rest_call("esxi/list",{'id':aWeb['id'],'sort':sort})
 statelist = res['data']
 aWeb.wr("<ARTICLE>")
 aWeb.wr(aWeb.button('reload',TITLE='Reload List',DIV='div_content_left',URL='esxi_list?id=%s&sort=%s'%(aWeb['id'],sort)))
 aWeb.wr("<DIV CLASS=table>")
 aWeb.wr("<DIV CLASS=thead><DIV CLASS=th><A CLASS=z-op DIV=div_content_left URL='esxi_list?id=%s&sort=%s'>VM</A></DIV><DIV CLASS=th>Operations</DIV></DIV>"%(aWeb['id'],"id" if sort == "name" else "name"))
 aWeb.wr("<DIV CLASS=tbody>")
 for vm in statelist:
  aWeb.wr("<DIV CLASS=tr STYLE='padding:0px;'><DIV CLASS=td STYLE='padding:0px;'>%s</DIV><DIV CLASS=td ID=div_vm_%s STYLE='width:120px'>"%(vm['name'],vm['id']))
  _vm_options(aWeb,vm,False)
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</DIV></DIV></ARTICLE>")

#
# VM info
def info(aWeb):
 args = aWeb.args()
 res  = aWeb.rest_call("esxi/info",args)
 info = res['data']
 aWeb.wr("<ARTICLE CLASS='info'><P>VM info</P>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=tbody>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>VM Name:</DIV><DIV CLASS=td>%s</DIV></DIV>"%info['name'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Hostname:</DIV><DIV CLASS=td>%s</DIV></DIV>"%info.get('device_name','-'))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>SNMP ID:</DIV><DIV CLASS=td>%s</DIV></DIV>"%info.get('snmp_id','-'))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>UUID:</DIV><DIV CLASS=td>%s</DIV></DIV>"%info.get('device_uuid','-'))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>State:</DIV><DIV CLASS=td><DIV CLASS='state %s' /></DIV></DIV>"%aWeb.state_ascii(info['state_id']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>System ID:</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>"%info.get('device_id','-'))
 if info.get('device_id'):
  aWeb.wr(aWeb.button('forward', DIV='div_content_right', URL='device_info?id=%s'%info['device_id']))
 aWeb.wr(aWeb.button('configure', DIV='div_content_right', URL='esxi_map?device_uuid=%s'%info['device_uuid']))
 aWeb.wr("</DIV></DIV>")
 if info.get('host_id'):
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Host ID:</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>"%info.get('host_id','-'))
  aWeb.wr(aWeb.button('forward', DIV='div_content_right', URL='device_info?id=%s'%info['host_id']))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Config file</DIV><DIV CLASS=td STYLE='max-width:360px'>%s</DIV></DIV>"%info.get('config','-'))
 for k,v in info.get('interfaces').items():
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Interface %s</DIV><DIV CLASS=td>%s - %s - %s</DIV></DIV>"%(k,v['name'],v['mac'],v['port']))
 aWeb.wr("</DIV></DIV>")
 aWeb.wr(aWeb.button('sync', DIV='div_content_right',  URL='esxi_info?id=%s&vm_id=%s&op=update'%(args['id'],args['vm_id']), TITLE='Resync database with VM info'))
 aWeb.wr("<SPAN CLASS='results' ID=update_results>%s</SPAN>"%str(res.get('update','')))
 aWeb.wr("</ARTICLE>")

#
#
def map(aWeb):
 args = aWeb.args()
 res = aWeb.rest_call('esxi/map',args)
 aWeb.wr("<ARTICLE><FORM ID=esxi_map_form><INPUT TYPE=HIDDEN NAME='device_uuid' VALUE='%(device_uuid)s'>ESXi VM to device mapping:<INPUT CLASS=TEXT NAME='device_id' VALUE='%(device_id)s'></FORM>"%res)
 aWeb.wr(aWeb.button('save', DIV='div_content_right', URL='esxi_map?op=update', FRM='esxi_map_form'))
 aWeb.wr('</ARTICLE>')

#
#
def control(aWeb):
 args = aWeb.args()
 res = aWeb.rest_call("esxi/control",args)
 if aWeb['output'] == 'div':
  aWeb.wr("<ARTICLE>Carried out '{}' on '{}'</ARTICLE>".format(aWeb['op'],aWeb['id']))
 else:
  _vm_options(aWeb,res,True)

#
#
def _vm_options(aWeb,aVM,aHighlight):
 div = "div_vm_%s"%aVM['id']
 url = 'esxi_control?id=%s&op={}&vm_id=%s'%(aWeb['id'],aVM['id'])
 if aHighlight:
  aWeb.wr("<DIV CLASS='border'>")
 aWeb.wr(aWeb.button('info',     DIV='div_content_right', URL='esxi_info?id=%s&vm_id=%s'%(aWeb['id'],aVM['id'])))
 if aVM['state_id'] == 1:
  aWeb.wr(aWeb.button('stop',    DIV=div, SPIN='div_content_left', URL=url.format('shutdown'), TITLE='Soft shutdown'))
  aWeb.wr(aWeb.button('reload',  DIV=div, SPIN='div_content_left', URL=url.format('reboot'), TITLE='Soft reboot'))
  aWeb.wr(aWeb.button('suspend', DIV=div, SPIN='div_content_left', URL=url.format('suspend'),TITLE='Suspend'))
  aWeb.wr(aWeb.button('off',     DIV=div, SPIN='div_content_left', URL=url.format('off'), TITLE='Hard power off'))
  # Change to get IP when proper REACT
  # aWeb.wr(aWeb.button('term',    HREF="https://%s/ui/#/console/%s"%(aIP,aVM['id']),  TARGET='_blank', TITLE='vSphere Console'))
 elif aVM['state_id'] == 3:
  aWeb.wr(aWeb.button('start',   DIV=div, SPIN='div_content_left', URL=url.format('on'), TITLE='Start'))
  aWeb.wr(aWeb.button('off',     DIV=div, SPIN='div_content_left', URL=url.format('off'), TITLE='Hard power off'))
 elif aVM['state_id'] == 2:
  aWeb.wr(aWeb.button('start',   DIV=div, SPIN='div_content_left', URL=url.format('on'), TITLE='Start'))
  aWeb.wr(aWeb.button('snapshot',DIV=div, SPIN='div_content_left', URL=url.format('create'), TITLE='Snapshot'))
  aWeb.wr(aWeb.button('info',    DIV='div_content_right',SPIN='true',URL='esxi_snapshot?id={}&vm_id={}'.format(aWeb['id'],aVM['id']), TITLE='Snapshot info'))
 else:
  aWeb.wr("Unknown state [{}]".format(aVM['state_id']))
 if aHighlight:
  aWeb.wr("</DIV>")

#
#
def snapshot(aWeb):
 res = aWeb.rest_call("esxi/control",{'id':aWeb['id'],'vm_id':aWeb['vm_id'],'op':'list'})
 aWeb.wr("<ARTICLE><P>Snapshots (%s) Highest ID:%s</P>"%(aWeb['vm_id'],res['highest']))
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Name</DIV><DIV CLASS=th>Id</DIV><DIV CLASS=th>Description</DIV><DIV CLASS=th>Created</DIV><DIV CLASS=th>State</DIV><DIV CLASS=th>&nbsp;</DIV></DIV>")
 aWeb.wr("<DIV CLASS=tbody>")
 for snap in res['snapshots']:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>".format(snap['name'],snap['id'],snap['desc'],snap['created'],snap['state']))
  aWeb.wr(aWeb.button('revert', TITLE='Revert', DIV='div_content_right',SPIN='true', URL='esxi_control?id=%s&vm_id=%s&op=revert&snapshot=%s&output=div'%(aWeb['id'],aWeb['vm_id'],snap['id'])))
  aWeb.wr(aWeb.button('delete', TITLE='Delete', DIV='div_content_right',SPIN='true', URL='esxi_control?id=%s&vm_id=%s&op=remove&snapshot=%s&output=div'%(aWeb['id'],aWeb['vm_id'],snap['id'])))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</DIV></DIV>")
