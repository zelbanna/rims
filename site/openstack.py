"""Module docstring.

HTML5 Ajax Openstack Generic calls module

- left and right divs frames (div_content_left/right) needs to be created by ajax call
"""
__author__= "Zacharias El Banna"
__version__ = "18.02.09GA"
__status__= "Production"

############################################## Openstack ###############################################
#
#
# Openstack Portal - New "Window"/Pane
#
def portal(aWeb):
 cookie = aWeb.cookie_unjar('openstack')

 if not cookie.get('authenticated'):
  (pid,pname) = aWeb.get('project','none_none').split('_')
  res = aWeb.rest_call("openstack_authenticate",{'host':cookie['controller'],'project_name':pname,'project_id':pid, 'username':aWeb['username'],'password':aWeb['password']})
  if res['authenticated'] == "OK":
   cookie.update(res)
   aWeb.cookie_jar('openstack',cookie,3000)
  else:
   print "Error logging in - please try login again"
   return
 else:
  aWeb.log("openstack_portal - using existing %s for %s"%(cookie.get('token'),cookie['controller']))

 aWeb.put_html("Openstack Portal")
 print "<HEADER CLASS='background'>"
 print "<DIV CLASS=table STYLE='width:auto; display:inline; float:left; margin:5px 100px 0px 10px;'><DIV CLASS=tbody>"
 print "<DIV CLASS=tr STYLE='background:transparent'><DIV CLASS=td><B>Identity:</B></DIV><DIV CLASS=td><I>{}</I></DIV><DIV CLASS=td>&nbsp;<B>Id:</B></DIV><DIV CLASS=td><I>{}</I></DIV></DIV>".format(cookie['project_name'],cookie['project_id'])
 print "<DIV CLASS=tr STYLE='background:transparent'><DIV CLASS=td><B>Username:</B></DIV><DIV CLASS=td><I>{}</I></DIV><DIV CLASS=td>&nbsp;<B>Token:</B></DIV><DIV CLASS=td><I>{}</I></DIV></DIV>".format(cookie['username'],cookie['token'])
 print "</DIV></DIV>"
 print "<BUTTON CLASS='z-op right menu warning' OP=logout COOKIE=openstack URL='sdcp.cgi?call=sdcp_login&application=openstack&controller={}&name={}&appformix={}' STYLE='margin-right:20px;'>Log out</BUTTON>".format(cookie['controller'],cookie.get('name'),cookie.get('appformix'))
 print "</HEADER><MAIN CLASS='background' ID=main>"
 print "<NAV><UL>"
 print "<LI><A CLASS=z-op           DIV=div_content URL='sdcp.cgi?call=heat_list'>Orchestration</A></LI>"
 print "<LI><A CLASS=z-op           DIV=div_content URL='sdcp.cgi?call=neutron_list'>Virtual Networks</A></LI>"
 print "<LI><A CLASS=z-op           DIV=div_content URL='sdcp.cgi?call=nova_list'>Virtual Machines</A></LI>"
 print "<LI><A CLASS=z-op SPIN=true DIV=div_content URL='sdcp.cgi?call=appformix_list'>Usage Report</A></LI>"
 print "<LI><A CLASS='z-op reload' OP=redirect URL='sdcp.cgi?call=openstack_portal'></A></LI>"
 print "<LI CLASS='dropdown right'><A>Debug</A><DIV CLASS=dropdown-content>"
 print "<A CLASS='z-op'  DIV=div_content URL=sdcp.cgi?call=openstack_api>REST</A>"
 print "<A CLASS='z-op'  DIV=div_content URL=sdcp.cgi?call=openstack_fqname>FQDN</A>"
 print "</DIV></LI>"
 print "</UL></NAV>"
 print "<SECTION CLASS=content ID=div_content></SECTION></MAIN>"

#
#
def inline(aWeb):
 cookie = aWeb.cookie_unjar('openstack')

 if not cookie.get('authenticated'):
  (pid,pname) = aWeb.get('project','none_none').split('_')
  res = aWeb.rest_call("openstack_authenticate",{'host':cookie['controller'],'project_name':pname,'project_id':pid, 'username':aWeb['username'],'password':aWeb['password']})
  if res['authenticated'] == "OK":
   cookie.update(res)
   aWeb.cookie_jar('openstack',cookie,3000)
  else:
   print "Error logging in - please try login again"
   return
 else:
  aWeb.log("openstack_portal - using existing %s for %s"%(cookie.get('token'),cookie['controller']))

 aWeb.put_cookie()
 print "<NAV><UL>"
 print "<LI><A CLASS=z-op           DIV=div_content URL='sdcp.cgi?call=heat_list'>Orchestration</A></LI>"
 print "<LI><A CLASS=z-op           DIV=div_content URL='sdcp.cgi?call=neutron_list'>Virtual Networks</A></LI>"
 print "<LI><A CLASS=z-op           DIV=div_content URL='sdcp.cgi?call=nova_list'>Virtual Machines</A></LI>"
 print "<LI><A CLASS=z-op SPIN=true DIV=div_content URL='sdcp.cgi?call=appformix_list'>Usage Report</A></LI>"
 print "<LI><A CLASS='z-op reload' DIV=main URL='sdcp.cgi?call=openstack_inline'></A></LI>"
 print "<LI CLASS='right'><A CLASS='z-op warning' OP=logout DIV=main COOKIE=openstack>Logout</A></LI>"
 print "<LI CLASS='right'><A CLASS='z-op green' TARGET=_blank HREF='sdcp.cgi?call=sdcp_login&application=openstack&controller=%s&name=%s&appformix=%s'>Tab</A></LI>"%(cookie['controller'],cookie.get('name'),cookie.get('appformix'))
 print "<LI CLASS='dropdown right'><A>Debug</A><DIV CLASS=dropdown-content>"
 print "<A CLASS='z-op'  DIV=div_content URL=sdcp.cgi?call=openstack_api>REST</A>"
 print "<A CLASS='z-op'  DIV=div_content URL=sdcp.cgi?call=openstack_fqname>FQDN</A>"
 print "</DIV></LI>"
 print "</UL></NAV>"
 print "<SECTION CLASS=content ID=div_content></SECTION></MAIN>"


############################################## Formatting ##############################################
#
# Assume div_os_info
#
def dict2html(aData,aTitle=None):
 print "<H2>{}</H2>".format(aTitle) if aTitle else "<!-- No title -->"
 data2html(aData)

def data2html(aData):
 if isinstance(aData,dict):
  print "<DIV CLASS=table STYLE='width:auto'><DIV CLASS=tbody>"
  for k,v in aData.iteritems():
   print "<DIV CLASS=tr><DIV CLASS=td STYLE='padding:0px;'><I>{}</I>:</DIV><DIV CLASS=td STYLE='white-space:normal; overflow:auto; width:100%'>".format(k)
   if 'href' in k:
    print "<A CLASS=z-op DIV=div_content URL=sdcp.cgi?call=openstack_result&method=GET&os_href={0}>{0}</A>".format(v)
   else:
    data2html(v)
   print "</DIV></DIV>"
  print "</DIV></DIV>"
 elif isinstance(aData,list):
  print "<DIV CLASS=table STYLE='width:100%;'><DIV CLASS=tbody>"
  for v in aData:
   print "<DIV CLASS=tr><DIV CLASS=td STYLE='padding:0px;'>"
   data2html(v)
   print "</DIV></DIV>"
  print "</DIV></DIV>"
 else:
  print aData

##################################################### Debugging #######################################################
#
#
#
def api(aWeb):
 cookie = aWeb.cookie_unjar('openstack')
 if not cookie.get('token'):
  print "<SCRIPT>location.replace('index.cgi')</SCRIPT>"
  return
 services = aWeb.rest_call("openstack_services",{'token':cookie['db_token']})['services']
 print "<ARTICLE><P>OpenStack REST API inspection</P>"
 print "<FORM ID=frm_os_api>"
 print "Choose Service and enter API call: <SELECT CLASS='white' STYLE='width:auto; height:22px;' NAME=os_service>"
 for service in services:
  print "<OPTION VALUE={0}>{0}</OPTION>".format(service['service'])
 print "</SELECT> <INPUT CLASS='white' STYLE='width:500px;' TYPE=TEXT NAME=os_call><BR>"
 print "Or enter HREF: <DIV ID=div_href STYLE='display:inline-block;'><INPUT CLASS='white' STYLE='width:716px;' TYPE=TEXT NAME=os_href></DIV><BR>"
 print "Call 'Method': <SELECT STYLE='width:auto; height:22px;' NAME=os_method>"
 for method in ['GET','POST','DELETE','PUT']:
  print "<OPTION VALUE={0}>{0}</OPTION>".format(method)
 print "</SELECT>"
 print "Arguments/Body<BR>"
 print "<TEXTAREA STYLE='width:100%; height:100px;' NAME=os_args></TEXTAREA>"
 print "</FORM><DIV CLASS=controls>"
 print aWeb.button('start',  DIV='div_os_info', URL='sdcp.cgi?call=openstack_result', FRM='frm_os_api')
 print aWeb.button('delete', DIV='div_os_info', OP='empty', TITLE='Clear results view')
 print "</DIV></ARTICLE>"
 print "<DIV ID=div_os_info></DIV>"

#
#
def fqname(aWeb):
 print "<ARTICLE>"
 print "<FORM ID=frm_os_uuid>Contrail UUID:<INPUT CLASS='white' STYLE='width:500px;' TYPE=TEXT NAME=os_uuid VALUE={}></FORM><DIV CLASS=controls>".format(aWeb['os_uuid'] if aWeb['os_uuid'] else "")
 print aWeb.button('start',  DIV='div_content', URL='sdcp.cgi?call=openstack_fqname', FRM='frm_os_uuid')
 print "</DIV>"
 if aWeb['os_uuid']:
  cookie = aWeb.cookie_unjar('openstack')
  token  = cookie.get('token')
  if not token:
   print "Not logged in"
  else:
   res = aWeb.rest_call("openstack_fqname",{'token':cookie['db_token'],'uuid':aWeb['os_uuid']})
   if res['result'] == 'OK':
    print "<DIV CLASS=table STYLE='width:100%;'><DIV CLASS=thead><DIV CLASS=th>Type</DIV><DIV CLASS=th>Value</DIV></DIV><DIV CLASS=tbody>"
    print "<DIV CLASS=tr><DIV CLASS=td>FQDN</DIV><DIV CLASS=td>{}</DIV></DIV>".format(".".join(res['data']['fq_name']))
    print "<DIV CLASS=tr><DIV CLASS=td>Type</DIV><DIV CLASS=td><A CLASS='z-op' DIV=div_os_info URL=sdcp.cgi?call=openstack_result&os_service=contrail&os_call={0}/{1}>{0}</A></DIV></DIV>".format(res['data']['type'],aWeb['os_uuid'])
    print "</DIV></DIV><BR>"
   else:
    print "<DIV CLASS=table STYLE='width:100%'><DIV CLASS=tbody>"
    for key,value in res.iteritems():
     print "<DIV CLASS=tr><DIV CLASS=td STYLE='width:100px'>{}</DIV><DIV CLASS=td>{}</DIV></DIV>".format(key.upper(),value)
    print "</DIV></DIV>"
 print "</ARTICLE>"
 print "<DIV ID=div_os_info></DIV>"

#
#
def result(aWeb):
 cookie = aWeb.cookie_unjar('openstack')
 if (not aWeb['os_call'] and not aWeb['os_href']) or not cookie.get('token'):
  return
 from json import dumps,loads
 try:    arguments = loads(aWeb['os_args'])
 except: arguments = None
 args = {"token":cookie['db_token'],'arguments':arguments,'method':aWeb['os_method']}
 if aWeb['os_href']:
  args['href'] = aWeb['os_href']
 else:
  args['service'] = aWeb['os_service']
  args['call'] = aWeb['os_call']
 res = aWeb.rest_call("openstack_rest",args)
 print "<ARTICLE CLASS=info STYLE='width:auto; overflow:auto'><DIV CLASS='border'>"
 if res['result'] == 'OK':
  print "<PRE CLASS='white'>%s</PRE>"%dumps(res['data'],indent=4, sort_keys=True)
 else:
  print "<DIV CLASS=table STYLE='width:auto'><DIV CLASS=tbody>"
  for key,value in res.iteritems():
   print "<DIV CLASS=tr><DIV CLASS=td STYLE='width:100px'>{}</DIV><DIV CLASS=td>{}</DIV></DIV>".format(key.upper(),value)
  print "</DIV></DIV>" 
 print "</DIV></ARTICLE>"
