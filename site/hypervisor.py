"""HTML5 Ajax Hypervisors module"""
__author__= "Zacharias El Banna"

def main(aWeb):
 hypervisors = aWeb.rest_call("device/list",{'field':'base','search':'hypervisor','extra':['type','functions','url'],'sort':'hostname'})['data']
 aWeb.wr("<NAV><UL>&nbsp;</UL></NAV>")
 aWeb.wr("<SECTION CLASS=content ID=div_content>")
 aWeb.wr("<SECTION CLASS=content-left ID=div_content_left>")
 aWeb.wr("<ARTICLE><P>Hypervisors</P>")
 aWeb.wr(aWeb.button('sync',DIV='div_content_right', URL='hypervisor_sync'))
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV>Hostname</DIV><DIV>Type</DIV><DIV>&nbsp;</DIV><DIV>&nbsp;</DIV></DIV><DIV CLASS=tbody>")
 for row in hypervisors:
  aWeb.wr("<DIV><DIV>%(hostname)s</DIV><DIV>%(type_name)s</DIV>"%row)
  aWeb.wr("<DIV><DIV CLASS='state %s' /></DIV><DIV>"%aWeb.state_ascii(row['state']))
  if row['state'] == 'up':
   if row['type_functions'] == 'manage':
    aWeb.wr(aWeb.button('info', DIV='main', URL='%s_manage?id=%s'%(row['type_name'],row['id']), TITLE='Management'))
   if row['url']:
    aWeb.wr(aWeb.button('ui', TARGET='_blank', HREF=row['url'], TITLE='UI'))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</DIV></DIV></ARTICLE>")
 aWeb.wr("</SECTION><SECTION CLASS=content-right ID=div_content_right></SECTION>")
 aWeb.wr("</SECTION>")

def sync(aWeb):
 res = aWeb.rest_call("device/vm_mapping")
 aWeb.wr("<ARTICLE>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV>Status</DIV><DIV>Host</DIV><DIV>Device</DIV><DIV>VM Name</DIV><DIV>Device UUID</DIV><DIV>Config</DIV></DIV><DIV CLASS=tbody>")
 for type in ['existing','inventory','discovered','database']:
  for row in res.get(type):
   aWeb.wr("<DIV><DIV>%s</DIV><DIV>%s</DIV><DIV>%s</DIV><DIV>%s</DIV><DIV>%s</DIV><DIV>%s</DIV></DIV>"%(type.upper(),row['host_id'],row.get('device_id','-'),row['vm'],row['device_uuid'],row['config']))
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</ARTICLE>")
