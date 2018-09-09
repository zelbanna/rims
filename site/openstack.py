"""Module docstring.

HTML5 Ajax Openstack Generic module

- left and right divs frames (div_content_left/right) needs to be created by ajax call
"""
__author__= "Zacharias El Banna"
__version__ = "1.0GA"
__status__= "Production"

############################################## Openstack ###############################################
#
#
# Openstack Portal - New "Window"/Pane
#
def portal(aWeb):
 cookie = aWeb.cookie('openstack')

 aWeb.put_html("Openstack Portal")
 if not cookie.get('authenticated'):
  (pid,pname) = aWeb.get('project','none_none').split('_')
  res = aWeb.rest_call("openstack_authenticate",{'node':cookie['node'],'project_name':pname,'project_id':pid, 'username':aWeb['username'],'password':aWeb['password']})
  if res['authenticated'] == "OK":
   cookie.update({'authenticated':'OK','token':res['token'],'username':aWeb['username'],'project_id':pid})
   aWeb.put_cookie('openstack',cookie,res['expires'])
  else:
   aWeb.wr("Error logging in - please try login again")
   return

 aWeb.wr("<MAIN CLASS='background' STYLE='top:0px;' ID=main>")
 aWeb.wr("<NAV><UL>")
 aWeb.wr("<LI><A CLASS=z-op           DIV=div_content URL='heat_list'>Orchestration</A></LI>")
 aWeb.wr("<LI><A CLASS=z-op           DIV=div_content URL='neutron_list'>Virtual Networks</A></LI>")
 aWeb.wr("<LI><A CLASS=z-op           DIV=div_content URL='nova_list'>Virtual Machines</A></LI>")
 aWeb.wr("<LI><A CLASS=z-op SPIN=true DIV=div_content URL='appformix_list'>Usage Report</A></LI>")
 aWeb.wr("<LI><A CLASS='z-op reload' OP=redirect URL='openstack_portal'></A></LI>")
 aWeb.wr("<LI CLASS='right'><A CLASS='z-op warning' OP=logout COOKIE=openstack URL='system_login?application=openstack&node={}&name={}&appformix={}'>Log out</A></LI>".format(cookie['node'],cookie.get('name'),cookie.get('appformix')))
 aWeb.wr("<LI CLASS='dropdown right'><A>Debug</A><DIV CLASS=dropdown-content>")
 aWeb.wr("<A CLASS='z-op'  DIV=div_content URL='openstack_info'>Info</A>")
 aWeb.wr("<A CLASS='z-op'  DIV=div_content URL='openstack_api'>REST</A>")
 aWeb.wr("<A CLASS='z-op'  DIV=div_content URL='openstack_fqname'>FQDN</A>")
 aWeb.wr("</DIV></LI>")
 aWeb.wr("</UL></NAV>")
 aWeb.wr("<SECTION CLASS=content ID=div_content></SECTION>")
 aWeb.wr("</MAIN>")

############################################## Formatting ##############################################
#
# Assume div_os_info
#
def dict2html(aData,aTitle=None):
 aWeb.wr("<H2>{}</H2>".format(aTitle) if aTitle else "<!-- No title -->")
 data2html(aData)

def data2html(aData):
 if isinstance(aData,dict):
  aWeb.wr("<DIV CLASS=table STYLE='width:auto'><DIV CLASS=tbody>")
  for k,v in aData.iteritems():
   aWeb.wr("<DIV CLASS=tr><DIV CLASS=td STYLE='padding:0px;'><I>{}</I>:</DIV><DIV CLASS=td STYLE='white-space:normal; overflow:auto; width:100%'>".format(k))
   if 'href' in k:
    aWeb.wr("<A CLASS=z-op DIV=div_content URL='openstack_result?method=GET&os_href={0}'>{0}</A>".format(v))
   else:
    data2html(v)
   aWeb.wr("</DIV></DIV>")
  aWeb.wr("</DIV></DIV>")
 elif isinstance(aData,list):
  aWeb.wr("<DIV CLASS=table STYLE='width:100%;'><DIV CLASS=tbody>")
  for v in aData:
   aWeb.wr("<DIV CLASS=tr><DIV CLASS=td STYLE='padding:0px;'>")
   data2html(v)
   aWeb.wr("</DIV></DIV>")
  aWeb.wr("</DIV></DIV>")
 else:
  aWeb.wr(aData)

##################################################### Debugging #######################################################
#
#
#
def api(aWeb):
 cookie = aWeb.cookie('openstack')
 if not cookie.get('token'):
  aWeb.wr("<SCRIPT>location.replace('system_login')</SCRIPT>")
  return
 services = aWeb.rest_call("openstack_services",{'token':cookie['token']})['services']
 aWeb.wr("<ARTICLE><P>OpenStack REST API inspection</P>")
 aWeb.wr("<FORM ID=frm_os_api>")
 aWeb.wr("Choose Service and enter API call: <SELECT STYLE='width:auto; height:22px;' NAME=os_service>")
 for service in services:
  aWeb.wr("<OPTION VALUE={0}>{0}</OPTION>".format(service['service']))
 aWeb.wr("</SELECT><INPUT CLASS='background' STYLE='width:500px;' TYPE=TEXT NAME=os_api><BR>")
 aWeb.wr("Or enter HREF: <DIV ID=div_href STYLE='display:inline-block;'><INPUT CLASS='background' STYLE='width:716px;' TYPE=TEXT NAME=os_href></DIV><BR>")
 aWeb.wr("Call 'Method': <SELECT STYLE='width:auto; height:22px;' NAME=os_method>")
 for method in ['GET','POST','DELETE','PUT']:
  aWeb.wr("<OPTION VALUE={0}>{0}</OPTION>".format(method))
 aWeb.wr("</SELECT>")
 aWeb.wr("Arguments/Body<BR>")
 aWeb.wr("<TEXTAREA STYLE='width:100%; height:100px;' NAME=os_args></TEXTAREA>")
 aWeb.wr("</FORM><DIV CLASS=controls>")
 aWeb.wr(aWeb.button('start',  DIV='div_os_info', URL='openstack_result', FRM='frm_os_api'))
 aWeb.wr(aWeb.button('delete', DIV='div_os_info', OP='empty', TITLE='Clear results view'))
 aWeb.wr("</DIV></ARTICLE>")
 aWeb.wr("<DIV ID=div_os_info></DIV>")

#
#
def fqname(aWeb):
 aWeb.wr("<ARTICLE>")
 aWeb.wr("<FORM ID=frm_os_uuid>Contrail UUID:<INPUT CLASS='white' STYLE='width:500px;' TYPE=TEXT NAME=os_uuid VALUE={}></FORM><DIV CLASS=controls>".format(aWeb['os_uuid'] if aWeb['os_uuid'] else ""))
 aWeb.wr(aWeb.button('start',  DIV='div_content', URL='openstack_fqname', FRM='frm_os_uuid'))
 aWeb.wr("</DIV>")
 if aWeb['os_uuid']:
  cookie = aWeb.cookie('openstack')
  token  = cookie.get('token')
  if not token:
   aWeb.wr("Not logged in")
  else:
   res = aWeb.rest_call("openstack_contrail_fqname",{'token':cookie['token'],'uuid':aWeb['os_uuid']})
   if res['result'] == 'OK':
    aWeb.wr("<DIV CLASS=table STYLE='width:100%;'><DIV CLASS=thead><DIV CLASS=th>Type</DIV><DIV CLASS=th>Value</DIV></DIV><DIV CLASS=tbody>")
    aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>FQDN</DIV><DIV CLASS=td>{}</DIV></DIV>".format(".".join(res['data']['fq_name'])))
    aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Type</DIV><DIV CLASS=td><A CLASS='z-op' DIV=div_os_info URL='openstack_result?os_service=contrail&os_api={0}/{1}'>{0}</A></DIV></DIV>".format(res['data']['type'],aWeb['os_uuid']))
    aWeb.wr("</DIV></DIV><BR>")
   else:
    aWeb.wr("<DIV CLASS=table STYLE='width:100%'><DIV CLASS=tbody>")
    for key,value in res.iteritems():
     aWeb.wr("<DIV CLASS=tr><DIV CLASS=td STYLE='width:100px'>{}</DIV><DIV CLASS=td>{}</DIV></DIV>".format(key.upper(),value))
    aWeb.wr("</DIV></DIV>")
 aWeb.wr("</ARTICLE>")
 aWeb.wr("<DIV ID=div_os_info></DIV>")

#
#
def result(aWeb):
 cookie = aWeb.cookie('openstack')
 if (not aWeb['os_api'] and not aWeb['os_href']) or not cookie.get('token'):
  return
 from json import dumps,loads
 try:    arguments = loads(aWeb['os_args'])
 except: arguments = None
 args = {"token":cookie['token'],'arguments':arguments,'method':aWeb['os_method']}
 if aWeb['os_href']:
  args['href'] = aWeb['os_href']
 else:
  args['service'] = aWeb['os_service']
  args['call'] = aWeb['os_api']
 res = aWeb.rest_call("openstack_rest",args)
 aWeb.wr("<ARTICLE CLASS=info STYLE='width:auto; overflow:auto'><DIV CLASS='border'>")
 if res['result'] == 'OK':
  aWeb.wr("<PRE CLASS='white'>%s</PRE>"%dumps(res['data'],indent=4, sort_keys=True))
 else:
  aWeb.wr("<DIV CLASS=table STYLE='width:auto'><DIV CLASS=tbody>")
  for key,value in res.iteritems():
   aWeb.wr("<DIV CLASS=tr><DIV CLASS=td STYLE='width:100px'>{}</DIV><DIV CLASS=td>{}</DIV></DIV>".format(key.upper(),value))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</DIV></ARTICLE>")

#
#
def info(aWeb):
 cookie = aWeb.cookie('openstack')
 data = aWeb.rest_call("openstack_info",{'username':cookie['username']})
 aWeb.wr("<ARTICLE>")
 aWeb.wr("<DIV CLASS=table STYLE='width:auto'><DIV CLASS=thead><DIV CLASS=th>Node</DIV><DIV CLASS=th>Controller</DIV><DIV CLASS=th>Internal ID</DIV><DIV CLASS=th>Token</DIV><DIV CLASS=th>Expires</DIV><DIV CLASS=th>Valid</DIV></DIV><DIV CLASS=tbody>")
 for row in data['data']:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV></DIV>"%(row['node_name'],row['node_url'],row['id'],row['token'],row['expires'],row['valid']))
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</ARTICLE>")
