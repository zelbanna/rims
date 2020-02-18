"""HTML5 Ajax System function module"""
__author__= "Zacharias El Banna"

#
#
def main(aWeb):
 cookie = aWeb.cookie('rims')
 data = aWeb.rest_call("master/inventory",{'node':aWeb.node(),'user_id':cookie['id']})
 svcs = aWeb.rest_call("system/service_list")['services']
 tools = data.get('tools',[])
 aWeb.wr("<NAV><UL>")
 if aWeb.node() == 'master':
  aWeb.wr("<LI><A CLASS=z-op DIV=div_content URL='node_list'>Nodes</A></LI>")
  aWeb.wr("<LI><A CLASS=z-op DIV=div_content URL='server_list'>Servers</A></LI>")
  aWeb.wr("<LI><A CLASS=z-op TARGET=_blank   HREF='infra/erd.pdf'>ERD</A></LI>")
  aWeb.wr("<LI><A CLASS=z-op DIV=div_content URL='user_list'>Users</A></LI>")
 if data.get('logs'):
  aWeb.wr("<LI CLASS='dropdown'><A>Logs</A><DIV CLASS='dropdown-content'>")
  for node in data['logs']:
   aWeb.wr("<A CLASS=z-op DIV=div_content URL=system_logs_show?node=%s>%s</A>"%(node,node))
  aWeb.wr("</DIV></LI>")
 aWeb.wr("<LI CLASS='dropdown'><A>Reports</A><DIV CLASS='dropdown-content'>")
 if aWeb.node() == 'master':
  aWeb.wr("<A CLASS=z-op DIV=div_content URL='activity_report'>Activities</A>")
  aWeb.wr("<A CLASS=z-op DIV=div_content URL='reservation_report'>Reservations</A>")
  aWeb.wr("<A CLASS=z-op DIV=div_content URL='device_report'>Devices</A>")
  aWeb.wr("<A CLASS=z-op DIV=div_content URL='inventory_report'>Inventory</A>")
 aWeb.wr("<A CLASS=z-op DIV=div_content URL='system_task_report'>Tasks</A>")
 aWeb.wr("<A CLASS=z-op DIV=div_content URL='system_report'>System</A>")
 aWeb.wr("</DIV></LI>")
 aWeb.wr("<LI><A CLASS=z-op DIV=div_content URL='system_rest_explore'>REST</A></LI>")
 if len(tools) > 0 or len(svcs) > 0:
  aWeb.wr("<LI CLASS='dropdown'><A>Tools</A><DIV CLASS='dropdown-content'>")
  for tool in tools:
   aWeb.wr("<A CLASS=z-op DIV=div_content URL='%s'>%s</A>"%(tool['href'],tool['title']))
  for svc in svcs:
   aWeb.wr("<A CLASS=z-op DIV=div_content URL='system_services_info?service=%s'>%s</A>"%(svc['service'],svc['name']))
 aWeb.wr("</DIV></LI>")
 if aWeb.node() == 'master':
  aWeb.wr("<LI><A CLASS='z-op' DIV=div_content URL='system_controls'>Controls</A></LI>")
 aWeb.wr("<LI><A CLASS='z-op reload' DIV=main URL='system_main'></A></LI>")
 if data.get('navinfo'):
  for info in data['navinfo']:
   aWeb.wr("<LI CLASS='right navinfo'><A>%s</A></LI>"%info)
 aWeb.wr("</UL></NAV>")
 aWeb.wr("<SECTION CLASS=content ID=div_content></SECTION>")

#
#
def report(aWeb):
 info = aWeb.rest_full("%s/system/report"%aWeb.url(), aDataOnly = True)
 analytics = info.pop('analytics',{})
 keys = sorted(info.keys())
 aWeb.wr("<ARTICLE><P>System</P>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV>Information</DIV><DIV>Value</DIV></DIV><DIV CLASS=tbody>")
 for i in keys:
  aWeb.wr("<DIV><DIV>%s</DIV><DIV>%s</DIV></DIV>"%(i,info[i]))
 for x in ['modules','files']:
  for k,v in analytics.get(x,{}).items():
   aWeb.wr("<DIV><DIV>%s: %s</DIV><DIV>%s</DIV></DIV>"%(x.title(),k,v))
 aWeb.wr("</DIV></DIV></ARTICLE>")

#
#
def reload(aWeb):
 """ Map node to URL and call reload """
 api = aWeb.rest_call("system/node_to_api",{'node':aWeb['node']})['url']
 res = aWeb.rest_full("%s/system/reload"%api, aDataOnly = True)
 aWeb.wr("<ARTICLE><P>Module</P>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=tbody>")
 for x in res['modules']:
  aWeb.wr("<DIV><DIV>%s</DIV></DIV>"%x)
 aWeb.wr("</DIV></DIV></ARTICLE>")

######################################### Tasks ######################################
#
#
def task_report(aWeb):
 res = aWeb.rest_call("master/task_list",{'node':aWeb.node()})
 aWeb.wr("<ARTICLE><P>Tasks</P>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV>Node</DIV><DIV>Frequency</DIV><DIV>Module</DIV><DIV>Function</DIV><DIV>Args</DIV></DIV><DIV CLASS=tbody>")
 for task in res['tasks']:
  aWeb.wr("<DIV><DIV>%(node)s</DIV><DIV>%(frequency)s</DIV><DIV>%(module)s</DIV><DIV>%(function)s</DIV><DIV>%(args)s</DIV></DIV>"%task)
 aWeb.wr("</DIV></DIV></ARTICLE>")

############################################ Options ##############################################
#
#
#
def rest_explore(aWeb):
 res = aWeb.rest_call("system/rest_explore")
 aWeb.wr("<SECTION CLASS=content-left  ID=div_content_left>")
 aWeb.wr("<ARTICLE>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV>API</DIV><DIV>Function</DIV></DIV><DIV CLASS=tbody>")
 for item in res['data']:
  for fun in item['functions']:
   aWeb.wr("<DIV><DIV>%s</DIV><DIV><A CLASS=z-op DIV=div_content_right URL=system_rest_information?api=%s&function=%s>%s</A></DIV></DIV>"%(item['api'],item['api'],fun,fun))
 aWeb.wr("</DIV></DIV></ARTICLE>")
 aWeb.wr("</SECTION>")
 aWeb.wr("<SECTION CLASS=content-right ID=div_content_right></SECTION>")

#
#
def rest_information(aWeb):
 res = aWeb.rest_call("system/rest_information",{'api':aWeb['api'],'function':aWeb['function']})
 aWeb.wr("<ARTICLE>")
 aWeb.wr("<H1>API: %s</H1>"%(aWeb['api']))
 aWeb.wr("<BR>".join(res['module']))
 aWeb.wr("<H1>Function: %s</H1>"%(aWeb['function']))
 aWeb.wr("<BR>".join(res['information']))
 aWeb.wr("</ARTICLE>")

#
#
def rest_execute(aWeb):
 from json import dumps, loads
 args = loads(aWeb['arguments']) if 'arguments' in aWeb.args() else None
 data = aWeb.rest_full("%s/api/%s"%(aWeb.url(),aWeb['api']), aArgs = args, aTimeOut=300, aDataOnly = True)
 aWeb.wr("<ARTICLE><PRE CLASS='white'>%s</PRE></ARTICLE>"%dumps(data,indent=4, sort_keys=True))


############################################### Logs ###############################################

#
#
def logs_clear(aWeb):
 args = aWeb.args()
 node = args.pop('node',None)
 args['count'] = 18
 res = aWeb.rest_call('system/logs_clear%s'%('?node=%s'%node if node else ''),args)
 aWeb.wr("<ARTICLE><P>%s</P>"%res['node'])
 for i in res['file'].items():
  aWeb.wr("%s: %s<BR>"%i)
 aWeb.wr("</ARTICLE>"%(res))

#
#
def logs_show(aWeb):
 args = aWeb.args()
 node = args.pop('node',None)
 args['count'] = 18
 res = aWeb.rest_call('system/logs_get%s'%('?node=%s'%node if node else ''),args)
 aWeb.wr("<ARTICLE>")
 for file,logs in res.items():
  aWeb.wr("<P STYLE='font-weight:bold; text-align:center;'>%s</P><P CLASS='machine-text'>%s</P>"%(file,"<BR>".join(logs)))
 aWeb.wr("</ARTICLE>")

############################################# Services ##############################################
#
#
def services_info(aWeb):
 args = aWeb.args()
 data  = aWeb.rest_call('system/service_info',args)
 state = 'start' if data['state'] == 'inactive' else 'stop'
 aWeb.wr("<ARTICLE STYLE='display:inline-block;'><B>%s</B>: %s (%s)"%(aWeb['service'],data['state'],data['extra']))
 aWeb.wr(aWeb.button(state, DIV='div_content', SPIN='true', URL='system_services_info?service=%s&op=%s'%(args['service'],state)))
 aWeb.wr("</ARTICLE>")

############################################## Files ###############################################
#
#
def file_list(aWeb):
 res = aWeb.rest_call('system/file_list',{'directory':aWeb['directory']})
 if aWeb.get('navigation'):
  aWeb.wr("<NAV><UL>&nbsp;</UL></NAV>")
  aWeb.wr("<SECTION CLASS=content ID=div_content>")
 aWeb.wr("<ARTICLE><P>Files in %s<P>"%res.get('path','directory'))
 import urllib.request, urllib.parse, urllib.error
 for f in res['files']:
  url  = urllib.parse.quote(f)
  aWeb.wr("<P CLASS=machine-text>{0}/<A HREF='{0}/{1}' TARGET=_blank>{2}</A></P>".format(res.get('path','#'),url,f))
 aWeb.wr("</ARTICLE>")
 if aWeb.get('navigation'):
  aWeb.wr("</SECTION>")

#
#
def images(aWeb):
 res = aWeb.rest_call('system/file_list')
 if aWeb.get('navigation'):
  aWeb.wr("<NAV><UL>&nbsp;</UL></NAV>")
  aWeb.wr("<SECTION CLASS=content ID=div_content>")
 aWeb.wr("<ARTICLE><P>Images<P><DIV CLASS=table><DIV CLASS=tbody>")
 for file in res['files']:
  if file[-3:] == 'png':
   aWeb.wr("<DIV><DIV STYLE='max-width:180px'>{0}</DIV><DIV STYLE='width:100%;'><IMG STYLE='max-height:60px;' SRC='{1}/{0}' /></DIV></DIV>".format(file,res['path']))
 aWeb.wr("</DIV></DIV></ARTICLE>")
 if aWeb.get('navigation'):
  aWeb.wr("</SECTION>")

############################################ Controls ##############################################
#
#
def controls(aWeb):
 aWeb.wr("<SECTION CLASS=content-left ID=div_content_left>")
 aWeb.wr("<ARTICLE><DIV CLASS=table><DIV CLASS=tbody>")
 aWeb.wr("<DIV><DIV><A CLASS=z-op DIV=div_content_right SPIN='true' URL='system_rest_execute?api=monitor/ipam_init'>IPAM status check</A></DIV></DIV>")
 aWeb.wr("<DIV><DIV><A CLASS=z-op DIV=div_content_right SPIN='true' URL='system_rest_execute?api=monitor/ipam_events&arguments={\"op\":\"clear\"}'>IPAM clear status logs</A></DIV></DIV>")
 aWeb.wr("<DIV><DIV><A CLASS=z-op DIV=div_content_right SPIN='true' URL='system_rest_execute?api=monitor/interface_init'>Interface status check</A></DIV></DIV>")
 aWeb.wr("<DIV><DIV><A CLASS=z-op DIV=div_content_right SPIN='true' URL='system_rest_execute?api=device/network_info_discover'>Discover system info</A></DIV></DIV>")
 aWeb.wr("<DIV><DIV><A CLASS=z-op DIV=div_content_right SPIN='true' URL='system_rest_execute?api=device/model_sync'>Sync models</A></DIV></DIV>")
 aWeb.wr("<DIV><DIV><A CLASS=z-op DIV=div_content_right SPIN='true' URL='system_rest_execute?api=device/vm_mapping'>VM UUID mapping</A></DIV></DIV>")
 aWeb.wr("<DIV><DIV><A CLASS=z-op DIV=div_content_right SPIN='true' URL='system_rest_execute?api=reservation/expiration_status'>Reservation checks</A></DIV></DIV>")
 aWeb.wr("<DIV><DIV><A CLASS=z-op DIV=div_content_right SPIN='true' URL='system_rest_execute?api=master/oui_fetch'>OUI Database sync</A></DIV></DIV>")
 aWeb.wr("</DIV></DIV></ARTICLE>")
 aWeb.wr("</SECTION>")
 aWeb.wr("<SECTION CLASS=content-right ID=div_content_right></SECTION>")
