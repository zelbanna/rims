"""HTML5 Ajax AWX module"""
__author__= "Zacharias El Banna"

#
#
def manage(aWeb):
 aWeb.wr("<NAV><UL>")
 aWeb.wr("<LI><A CLASS=z-op DIV=div_content_left URL='awx_inventory_list?node=%s'>Inventories</A></LI>"%aWeb['node'])
 aWeb.wr("<LI CLASS='right navinfo'><A>%s</A></LI>"%(aWeb['node']))
 aWeb.wr("</UL></NAV>")
 aWeb.wr("<SECTION CLASS=content ID=div_content>")
 aWeb.wr("<SECTION CLASS=content-left ID=div_content_left></SECTION>")
 aWeb.wr("<SECTION CLASS=content-right ID=div_content_right></SECTION>")
 aWeb.wr("</SECTION>")

#
#
def inventory_list(aWeb):
 data = aWeb.rest_call("awx/inventory_list",{'node':aWeb['node']})
 aWeb.wr("<ARTICLE><P>Inventories</P>")
 if data.get('exception'):
  aWeb.wr("Error: %s"%(data['exception']))
 else:
  aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV>ID</DIV><DIV>Name</DIV><DIV>&nbsp;</DIV></DIV><DIV CLASS=tbody>")
  for row in data['inventories']:
   aWeb.wr("<DIV><DIV>%s</DIV><DIV CLASS='maxed'>%s</DIV><DIV>"%(row['id'],row['name']))
   aWeb.wr(aWeb.button('items',DIV='div_content_right', URL='awx_inventory_info?node=%s&id=%s'%(aWeb['node'],row['id']), SPIN='true', TITLE='Hosts list'))
   aWeb.wr(aWeb.button('trash',DIV='div_content_right', URL='awx_inventory_delete?node=%s&id=%s'%(aWeb['node'],row['id']), SPIN='true', TITLE='Delete inventory', MSG='Really delete inventory?'))
   aWeb.wr("</DIV></DIV>")
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</ARTICLE>")

#
#
def inventory_info(aWeb):
 args = aWeb.args()
 if aWeb['op'] == 'delete_list':
  opres = aWeb.rest_call("awx/inventory_delete_hosts",args)
 else:
  opres = ""
 res = aWeb.rest_call("awx/inventory_info",args)
 aWeb.wr("<ARTICLE><P>Hosts</P>")
 aWeb.wr(aWeb.button('reload', DIV='div_content_right', URL='awx_inventory_info?node=%s&id=%s'%(aWeb['node'],aWeb['id']), SPIN='true'))
 aWeb.wr(aWeb.button('add',    DIV='div_content_right', URL='awx_inventory_device_search?node=%s&id=%s'%(aWeb['node'],aWeb['id']), TITLE='Sync with AWX'))
 aWeb.wr(aWeb.button('trash',  DIV='div_content_right', URL='awx_inventory_info?node=%s&id=%s&op=delete_list'%(aWeb['node'],aWeb['id']), MSG='Delete hosts?', FRM='awx_inventory_info_form', SPIN='true'))
 aWeb.wr("<SPAN CLASS=results>%s</SPAN><FORM ID=awx_inventory_info_form>"%(opres))
 aWeb.wr("</DIV><DIV CLASS=table><DIV CLASS=thead><DIV>ID</DIV><DIV>Name</DIV><DIV>Description</DIV><DIV>Groups</DIV><DIV>&nbsp;</DIV></DIV><DIV CLASS=tbody>")
 for row in res['hosts']:
  name = "<A CLASS=z-op DIV=div_content_right URL='device_info?id=%s'>%s</A>"%(row['instance_id'],row['name']) if row['instance_id'] != "" else row['name']
  aWeb.wr("<DIV><DIV>%s</DIV><DIV>%s</DIV><DIV>%s</DIV><DIV>%s</DIV><DIV>"%(row['id'],name,row['description'],",".join(k['name'] for k in row['groups'])))
  aWeb.wr("<INPUT TYPE=CHECKBOX VALUE=%(id)s NAME='host_%(id)s'>"%row)
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</DIV></DIV></DIV>")
 aWeb.wr("</FORM></ARTICLE>")

#
#
def inventory_delete(aWeb):
 args = aWeb.args()
 res = aWeb.rest_call("awx/inventory_delete",args)
 aWeb.wr("<ARTICLE>Delete result: %s</ARTICLE>"%res)

#
#
def inventory_device_search(aWeb):
 aWeb.wr("<ARTICLE STYLE='display:inline-block'>")
 aWeb.wr("<FORM ID=awx_inventory_device_search_form>")
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=id VALUE=%s>"%(aWeb['id']))
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=node VALUE=%s>"%(aWeb['node']))
 aWeb.wr("<SPAN>Sync devices matching field:</SPAN><SELECT CLASS='background' ID='field' NAME='field'><OPTION VALUE='hostname'>Hostname</OPTION><OPTION VALUE='type'>Type</OPTION><OPTION VALUE='ip'>IP</OPTION><OPTION VALUE='mac'>MAC</OPTION><OPTION VALUE='id'>ID</OPTION></SELECT>")
 aWeb.wr("<INPUT CLASS='background' TYPE=TEXT ID='search' NAME='search' STYLE='width:200px' REQUIRED>")
 aWeb.wr("</FORM><DIV CLASS='inline'>")
 aWeb.wr(aWeb.button('back',DIV='div_content_right',URL='awx_inventory_info?id=%s&node=%s'%(aWeb['id'],aWeb['node'])))
 aWeb.wr(aWeb.button('forward',DIV='div_content_right',URL='awx_inventory_device_choose',FRM='awx_inventory_device_search_form', SPIN='true'))
 aWeb.wr("</DIV></ARTICLE>")

#
#
def inventory_device_choose(aWeb):
 args = aWeb.args()
 res = aWeb.rest_call("device/list",args)
 aWeb.wr("<ARTICLE STYLE='display:inline-block'>")
 aWeb.wr("<FORM ID=awx_inventory_device_choose_form>")
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=id VALUE=%s>"%(aWeb['id']))
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=node VALUE=%s>"%(aWeb['node']))
 aWeb.wr("</DIV><DIV CLASS=table><DIV CLASS=thead><DIV>Id</DIV><DIV>FQDN</DIV><DIV>&nbsp;</DIV></DIV><DIV CLASS=tbody>")
 for row in res['data']:
  aWeb.wr("<DIV><DIV>%(id)s</DIV><DIV>%(hostname)s.%(domain)s</DIV><DIV><INPUT TYPE=CHECKBOX VALUE=%(id)s NAME=device_%(id)s></DIV></DIV>"%row)
 aWeb.wr("</DIV></DIV></FORM>")
 aWeb.wr(aWeb.button('back',DIV='div_content_right',URL='awx_inventory_device_search?id=%s&node=%s'%(aWeb['id'],aWeb['node'])))
 aWeb.wr(aWeb.button('forward',DIV='div_content_right',URL='awx_inventory_device_sync',FRM='awx_inventory_device_choose_form', SPIN='true'))
 aWeb.wr("</ARTICLE>")

#
#
def inventory_device_sync(aWeb):
 args = aWeb.args()
 res = aWeb.rest_call("awx/inventory_sync",args)
 aWeb.wr("<ARTICLE><P>Synced Devices</P>")
 aWeb.wr(aWeb.button('forward', DIV='div_content_right', URL='awx_inventory_info?node=%s&id=%s'%(aWeb['node'],aWeb['id'])))
 aWeb.wr("<DIV CLASS=table><DIV CLASS=tbody>")
 for row in res['devices']:
  aWeb.wr("<DIV><DIV>%s</DIV><DIV>%s.%s</DIV><DIV>%s</DIV><DIV>%s</DIV></DIV>"%(row['id'],row['hostname'],row['domain'],row['ip'],row['awx']))
 aWeb.wr("</DIV>")
 aWeb.wr("</ARTICLE>")
