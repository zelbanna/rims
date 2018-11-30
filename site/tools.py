"""HTML5 Ajax Tools module"""
__author__= "Zacharias El Banna"
__icon__ = 'icon-config.png'
__type__ = 'menuitem'

############################################ Options ##############################################
#
def main(aWeb):
 cookie = aWeb.cookie('rims')
 data = aWeb.rest_call("system/inventory",{'node':aWeb.node(),'user_id':cookie['id']})
 aWeb.wr("<NAV><UL>")
 if data.get('node'):
  aWeb.wr("<LI><A CLASS=z-op DIV=div_content URL='servers_list'>Servers</A></LI>")
  aWeb.wr("<LI><A CLASS=z-op DIV=div_content URL='nodes_list'>Nodes</A></LI>")
 if data.get('users'):
  aWeb.wr("<LI><A CLASS=z-op DIV=div_content URL='users_list'>Users</A></LI>")
 tools = data.get('tools',[])
 svcs  = data.get('services',[])
 if len(tools) > 0 and len(svcs) > 0:
  aWeb.wr("<LI CLASS='dropdown'><A>Tools</A><DIV CLASS='dropdown-content'>")
  for tool in data.get('tools',[]):
   aWeb.wr("<A CLASS=z-op DIV=div_content URL='%s'>%s</A>"%(tool['href'],tool['title']))
  for svc in data.get('services',[]):
   aWeb.wr("<A CLASS=z-op DIV=div_content URL='tools_services_info?node=%s&service=%s'>%s</A>"%(aWeb.node(),svc['service'],svc['name']))
 aWeb.wr("</DIV></LI>")
 aWeb.wr("<LI CLASS=dropdown><A>REST</A><DIV CLASS='dropdown-content'>")
 aWeb.wr("<A CLASS=z-op DIV=div_content URL='tools_rest_main?node=%s'>Debug</A>"%aWeb['node'])
 aWeb.wr("<A CLASS=z-op DIV=div_content URL='tools_logs_show?name=rest&node=%s'>Logs</A>"%aWeb['node'])
 aWeb.wr("<A CLASS=z-op DIV=div_content URL='tools_rest_explore'>Explore</A>")
 aWeb.wr("</DIV></LI>")
 aWeb.wr("<LI><A CLASS='z-op reload' DIV=main URL='tools_main?node=%s'></A></LI>"%aWeb['node'])
 if data.get('navinfo'):
  for info in data['navinfo']:
   aWeb.wr("<LI CLASS='right navinfo'><A>%s</A></LI>"%info)
 aWeb.wr("</UL></NAV>")
 aWeb.wr("<SECTION CLASS=content ID=div_content></SECTION>")

#
#
def install(aWeb):
 res = aWeb.rest_call("tool/install?node=%s"%aWeb['node'])
 aWeb.wr("<ARTICLE CLASS='info'><P>Install results</P>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=tbody>")
 for i in res.items():
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV></DIV>"%i)
 aWeb.wr("</DIV></DIV></ARTICLE>")

############################################# REST ###############################################
#
#
def rest_main(aWeb):
 nodes = aWeb.rest_call("system/node_list")['data']
 aWeb.wr("<ARTICLE><P>REST API inspection</P>")
 aWeb.wr("<FORM ID=frm_rest>")
 aWeb.wr("Choose host and enter API:<SELECT CLASS=background STYLE='height:22px;' NAME=node>")
 for node in nodes:
  aWeb.wr("<OPTION VALUE='%s' %s>%s</A>"%(node['id'],"selected" if aWeb['node'] == node['node'] else "",node['node']))
 aWeb.wr("</SELECT> <INPUT CLASS=background STYLE='width:500px;' TYPE=TEXT NAME=api><BR>")
 aWeb.wr("Call 'Method': <SELECT CLASS=background STYLE='width:70px; height:22px;' NAME=method>")
 for method in ['GET','POST','DELETE','PUT']:
  aWeb.wr("<OPTION VALUE={0}>{0}</OPTION>".format(method))
 aWeb.wr("</SELECT> Debug:")
 aWeb.wr("<INPUT NAME=debug TYPE=RADIO VALUE=0 checked=checked>no")
 aWeb.wr("<INPUT NAME=debug TYPE=RADIO VALUE=1>yes")
 aWeb.wr("<BR>Arguments/Body<BR><TEXTAREA STYLE='width:100%; height:70px;' NAME=arguments></TEXTAREA>")
 aWeb.wr("</FORM>")
 aWeb.wr(aWeb.button('start',  DIV='div_rest_info', URL='tools_rest_execute', FRM='frm_rest'))
 aWeb.wr(aWeb.button('delete', DIV='div_rest_info', OP='empty', TITLE='Clear results view'))
 aWeb.wr("</ARTICLE>")
 aWeb.wr("<DIV ID=div_rest_info></DIV>")

#
#
def rest_execute(aWeb):
 from json import loads,dumps
 from cgi import escape
 try:    arguments = loads(aWeb['arguments'])
 except: arguments = None
 try:
  node = aWeb.rest_call("system/node_info",{'id':aWeb['node']})['data']
  url = "%s/%s/%s"%(node['url'],"debug" if aWeb['debug'] == '1' else "api", aWeb['api']) if node['system'] == 1 else "%s%s"%(node['url'],aWeb['api'])
  ret = aWeb.rest_full(url, aArgs = arguments, aMethod = aWeb['method'], aDataOnly = False)
 except Exception as e:
  ret = e.args[0]
 data = ret.pop('data',None)
 aWeb.wr("<ARTICLE STYLE='width:auto'>")
 aWeb.wr("<DIV CLASS='border'>")
 aWeb.wr("<DIV CLASS=table STYLE='table-layout:fixed; width:100%;'><DIV CLASS=tbody>")
 if ret.get('info'):
  aWeb.wr("<DIV CLASS=tr STYLE=><DIV CLASS=td STYLE='width:100px'>INFO</DIV><DIV CLASS=td STYLE='white-space:normal'>")
  for key,value in ret.pop('info',{}).items():
   aWeb.wr("<DIV CLASS='rest'><DIV>%s</DIV><DIV>%s</DIV></DIV>"%(key,escape(value)))
  aWeb.wr("</DIV></DIV>")
 for key,value in ret.items():
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td STYLE='width:100px'>%s</DIV><DIV CLASS=td STYLE='white-space:normal'>%s</DIV></DIV>"%(key.upper(),value))
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("<PRE CLASS='white'>%s</PRE>"%dumps(data,indent=4, sort_keys=True))
 aWeb.wr("</DIV></ARTICLE>")

#
#
def rest_explore(aWeb):
 res = aWeb.rest_call("tool/rest_explore")
 aWeb.wr("<SECTION CLASS=content-left  ID=div_content_left>")
 aWeb.wr("<ARTICLE><DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>API</DIV><DIV CLASS=th>Function</DIV></DIV><DIV CLASS=tbody>")
 for item in res['data']:
  for fun in item['functions']:
   aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL=tools_rest_information?api=%s&function=%s>%s</A></DIV></DIV>"%(item['api'],item['api'],fun,fun))
 aWeb.wr("</DIV></DIV></ARTICLE>")
 aWeb.wr("</SECTION>")
 aWeb.wr("<SECTION CLASS=content-right ID=div_content_right></SECTION>")

#
#
def rest_information(aWeb):
 res = aWeb.rest_call("tool/rest_information",{'api':aWeb['api'],'function':aWeb['function']})
 aWeb.wr("<ARTICLE>")
 aWeb.wr("<H1>API: %s</H1>"%(aWeb['api']))
 aWeb.wr("<BR>".join(res['module']))
 aWeb.wr("<H1>Function: %s</H1>"%(aWeb['function']))
 aWeb.wr("<BR>".join(res['information']))
 aWeb.wr("</ARTICLE>")

############################################### Logs ###############################################

#
#
def logs_clear(aWeb):
 args = aWeb.args()
 node = args.pop('node',None)
 args['count'] = 18
 res = aWeb.rest_call('tool/logs_clear?node=%s'%node,args)
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
 res = aWeb.rest_call('tool/logs_get?node=%s'%node,args)
 aWeb.wr("<ARTICLE>")
 for file,logs in res.items():
  aWeb.wr("<P STYLE='font-weight:bold; text-align:center;'>%s</P><P CLASS='machine-text'>%s</P>"%(file,"<BR>".join(logs)))
 aWeb.wr("</ARTICLE>")

############################################# Services ##############################################
#
#
def services_info(aWeb):
 args = aWeb.args()
 node = args.pop('node',None)
 data  = aWeb.rest_call('tool/service_info?node=%s'%node,args)
 state = 'start' if data['state'] == 'inactive' else 'stop'
 aWeb.wr("<ARTICLE STYLE='display:inline-block;'><B>%s</B>: %s (%s)"%(aWeb['service'],data['state'],data['info']))
 aWeb.wr(aWeb.button(state, DIV='div_content', SPIN='true', URL='tools_services_info?service=%s&node=%s&op=%s'%(args['service'],node,state)))
 aWeb.wr("</ARTICLE>")

############################################## Files ###############################################
#
#
def file_list(aWeb):
 res = aWeb.rest_call('tool/file_list',{'directory':aWeb['directory']})
 aWeb.wr("<NAV></NAV><SECTION CLASS=content ID=div_content><ARTICLE><P>Files in %s<P>"%res.get('path','directory'))
 import urllib.request, urllib.parse, urllib.error
 for f in res['files']:
  url  = urllib.parse.quote(f)
  aWeb.wr("<P CLASS=machine-text>{0}/<A HREF='{0}/{1}' TARGET=_blank>{2}</A></P>".format(res.get('path','#'),url,f))
 aWeb.wr("</ARTICLE></SECTION>")

#
#
def images(aWeb):
 res = aWeb.rest_call('tool/file_list')
 aWeb.wr("<NAV></NAV><SECTION CLASS=content ID=div_content><ARTICLE><P>Images<P><DIV CLASS=table><DIV CLASS=tbody>")
 for file in res['files']:
  if file[-3:] == 'png':
   aWeb.wr("<DIV CLASS=tr><DIV CLASS=td STYLE='max-width:180px'>{0}</DIV><DIV CLASS=td STYLE='width:100%;'><IMG STYLE='max-height:60px;' SRC='{1}/{0}' /></DIV></DIV>".format(file,res['path']))
 aWeb.wr("</DIV></DIV></ARTICLE></SECTION>")

