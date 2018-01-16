"""Module docstring.

HTML5 Front-End(s)

"""
__author__= "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__= "Production"



#################################################################################################################
#
# SDCP "login"
#
# - writes cookies for sdcp: user(name) ,id and view into a jar (dict)
# - if passwords, then do proper checks
#
#
def login(aWeb):
 cookie = aWeb.cookie_unjar('sdcp')
 if len(cookie) > 0:
  site = "sdcp_portal"
  aWeb.put_redirect("sdcp.cgi?call=%s&headers=no"%site)
  return

 # request from REST
 from ..core.dbase import DB
 with DB() as db:
  db.do("SELECT id,name,view_public FROM users ORDER BY name")
  rows = db.get_rows()
 aWeb.put_html("Login")
 print "<DIV CLASS='grey overlay'>"
 print "<ARTICLE CLASS='login'>"
 print "<H1 CLASS='centered'>Welcome to the management portal</H1>"
 print "<FORM ACTION=sdcp.cgi METHOD=POST ID=sdcp_login_form>"
 print "<INPUT TYPE=HIDDEN NAME=call VALUE=sdcp_portal>"
 print "<INPUT TYPE=HIDDEN NAME=headers VALUE=no>"
 print "<DIV CLASS=table STYLE='display:inline; float:left; margin:0px 0px 0px 30px; width:auto;'><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Username:</DIV><DIV CLASS=td><SELECT NAME=sdcp_login>"
 for row in rows:
  print "<OPTION VALUE='{0}_{1}_{2}'>{1}</OPTION>".format(row['id'],row['name'],row['view_public'])
 print "</SELECT></DIV></DIV>"
 print "</DIV></DIV>"
 print "<A CLASS='btn z-op' OP=submit STYLE='margin:20px 20px 30px 40px;' FRM=sdcp_login_form>Enter</A>"
 print "</FORM>"
 print "</ARTICLE></DIV>"

##################################################################################################
#
# Weathermap
#
def weathermap(aWeb):
 from .. import PackageContainer as PC
 if aWeb.get('headers','no') == 'no':
  aWeb.put_html("Weathermap")
 else:
  print "Content-Type: text/html\r\n"

 page = aWeb['page']
 if not page:
  print "<NAV><UL>" 
  for map,entry in PC.weathermap.iteritems():
   print "<LI><A CLASS=z-op OP=iload IFRAME=iframe_wm_cont URL=sdcp.cgi?call=front_weathermap&page={0}>{1}</A></LI>".format(map,entry['name'])
  print "</UL></NAV>"
  print "<SECTION CLASS='content' ID='div_wm_content' NAME='Weathermap Content' STYLE='overflow:hidden;'>"
  print "<IFRAME ID=iframe_wm_cont src=''></IFRAME>"
  print "</SECTION>" 
 else:
  from ..core.extras import get_include
  entry  = PC.weathermap[page]
  graphs = entry.get('graphs')
  print "<SECTION CLASS=content STYLE='top:0px;'>"
  if graphs:
   from ..tools.munin import widget_rows
   print "<SECTION CLASS=content-left STYLE='width:420px'><ARTICLE>"
   widget_rows(graphs)
   print "</ARTICLE></SECTION><SECTION CLASS=content-right STYLE='left:420px'>"
   print "<ARTICLE>"
   print get_include('%s.html'%page)
   print "</ARTICLE>"
   print "</SECTION>"
  else:
   print "<SECTION CLASS=content STYLE='top:0px;'>"
   print "<ARTICLE>"
   print get_include('%s.html'%page)
   print "</ARTICLE>"
  print "</SECTION>"

###################################################################################################################################
#
# Openstack
#
# Cookies:
# - openstack:
# appformix   = appformix controller ip
# controller   = openstack controller ip
# demo_name    = Name of Customer demoing for
# main_token   = auth token for project recovery
# project_id   = id for selected project
# project_name = name for selected project
# user_name    = username last used
# user_token   = token for user
# services     = x,y,z
#
# - service:
# port         = port for service xyz
# url          = url  for service xyz
# id           = id   for service xyz
#

def openstack(aWeb):
 from .. import PackageContainer as PC
 from ..devices.openstack import OpenstackRPC
 cookie = aWeb.cookie_unjar('openstack')
 utok = cookie.get("user_token")
 if utok:
  aWeb.put_redirect("sdcp.cgi?call=openstack_portal&headers=no")
  return

 # Package all variables found except call and header into cookie, add portal :-), rename demo below
 # request portal info from rest.sdcp_portal

 name = aWeb.get('name',"iaas")
 ctrl = aWeb.get('controller',"127.0.0.1")
 appf = aWeb.get('appformix',"127.0.0.1")

 user = cookie.get("user_name")
 mtok = cookie.get("main_token")
 prev = cookie.get("project_id")

 cookie['demo'] = name
 cookie['controller'] = ctrl
 cookie['appformix'] = appf

 if not mtok:
  controller = OpenstackRPC(ctrl,None)
  res = controller.auth({'project':PC.openstack['project'], 'username':PC.openstack['username'],'password':PC.openstack['password']})
  cookie['main_token'] = controller.get_token()
  aWeb.log("openstack_controller - login result: {}".format(str(res['result'])))
 else:
  aWeb.log("openstack_controller - reusing token: {}".format(mtok))
  controller = OpenstackRPC(ctrl,mtok)

 ret = controller.call("5000","v3/projects")
 projects = [] if not ret['code'] == 200 else ret['data']['projects']

 # Put cookie
 aWeb.cookie_jar('openstack',cookie,3000)
 aWeb.put_html("{} 2 Cloud".format(name.capitalize()))
 print "<DIV CLASS='grey overlay'>"
 print "<ARTICLE CLASS='login'>"
 # REST header
 print "<H1 CLASS='centered'>Welcome to '{}' Cloud portal</H1>".format(name.capitalize())
 print "<FORM ACTION=sdcp.cgi METHOD=POST ID=openstack_login>"
 # REST portal
 print "<INPUT TYPE=HIDDEN NAME=call VALUE=openstack_portal>"
 print "<INPUT TYPE=HIDDEN NAME=headers VALUE=no>"
 print "<DIV CLASS=table STYLE='display:inline; float:left; width:auto; margin:0px 0px 0px 30px;'><DIV CLASS=tbody>"
 # loop through REST choises
 print "<DIV CLASS=tr><DIV CLASS=td>Customer:</DIV><DIV CLASS=td><SELECT NAME=project>"
 for p in projects:
  print "<OPTION VALUE={0}_{1}>{1}</OPTION>".format(p['id'],p['name'])
 print "</SELECT></DIV></DIV>"
 # loop through rest parameters
 print "<DIV CLASS=tr><DIV CLASS=td>Username:</DIV><DIV CLASS=td><INPUT TYPE=text NAME=username></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td>Password:</DIV><DIV CLASS=td><INPUT TYPE=password NAME=password></DIV></DIV>"
 print "</DIV></DIV>"
 print "<A CLASS='btn z-op' STYLE='margin:20px 20px 30px 40px;' OP=submit FRM=openstack_login>Login</A>"
 print "</FORM>"
 print "</ARTICLE></DIV>"
