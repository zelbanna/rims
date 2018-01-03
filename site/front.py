"""Module docstring.

HTML5 Front-End(s)

"""
__author__= "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__= "Production"


from sdcp import PackageContainer as PC

#################################################################################################################
#
# SDCP "login"
#
# - writes cookies for sdcp: user(name) ,id and view into a jar (dict)
# - if passwords, then do proper checks
#
# Now do referrer?
#
def login(aWeb):
 from sdcp.core.dbase import DB
 if PC.generic['db'] == '':
  aWeb.log("No Database available so login not possible")
  aWeb.put_html("Error")
  return

 if aWeb.cookies.get('sdcp'):
  cookie = aWeb.cookie_unjar('sdcp')
  id   = cookie['id']
  user = cookie['user']
  view = cookie['view']
 else:
  id,user,view = aWeb.get('sdcp_login',"None_None_1").split('_')
  if id != "None":
   # "Login successful"
   aWeb.cookie_jar('sdcp',{'id':id,'user':user,'view':view}, 86400)

 if id != "None":
  aWeb.put_html(PC.sdcp['name'])
  aWeb.log("Entering as {}-'{}' ({})".format(id,user,view))
  with DB() as db:
   db.do("SELECT menulist FROM users WHERE id = '{}'".format(id))
   menulist = db.get_val('menulist')

  from sdcp.rest.resources import list as resource_list
  resources = resource_list({'id':id,'dict':'id'})['data']
  print "<HEADER>"
  inline = "<A CLASS='btn menu-btn z-op' DIV=main      TITLE='%s' URL='%s' ><IMG SRC='%s'/></A>"
  extern = "<A CLASS='btn menu-btn z-op' TARGET=_blank TITLE='%s' HREF='%s'><IMG SRC='%s'/></A>"
  if menulist == 'default':
   for key,item in resources.iteritems():
    item = resources.get(int(key))
    if item['type'] == 'menuitem':
     print inline%(item['title'],item['href'],item['icon'])
  else:
   for key in menulist.split(','):
    item = resources.get(int(key))
    if item['inline'] == 1:
     print inline%(item['title'],item['href'],item['icon'])
    else:
     print extern%(item['title'],item['href'],item['icon'])
  print "<A CLASS='btn menu-btn z-op right warning' OP=logout URL=sdcp.cgi>Log out</A>"
  print "<A CLASS='btn menu-btn z-op right' DIV=main TITLE='%s' URL=sdcp.cgi?call=users_user&id=%s><IMG SRC='images/icon-users.png'></A>"%(user,id)
  print "</HEADER>"
  print "<main ID=main></main>"
 else:
  with DB() as db:
   db.do("SELECT id,name,view_public FROM users ORDER BY name")
   rows = db.get_rows()
  aWeb.put_html("Login")
  print "<DIV CLASS='grey overlay'>"
  print "<ARTICLE CLASS='login'>"
  print "<H1 CLASS='centered'>Welcome to the management portal</H1>"
  print "<FORM ACTION=sdcp.cgi METHOD=POST ID=sdcp_login_form>"
  print "<INPUT TYPE=HIDDEN NAME=call VALUE=front_login>"
  print "<DIV CLASS=table STYLE='display:inline; float:left; margin:0px 0px 0px 30px; width:auto;'><DIV CLASS=tbody>"
  print "<DIV CLASS=tr><DIV CLASS=td>Username:</DIV><DIV CLASS=td><SELECT NAME=sdcp_login>"
  for row in rows:
   print "<OPTION VALUE='{0}_{1}_{2}' {3}>{1}</OPTION>".format(row['id'],row['name'],row['view_public'],'' if str(row['id']) != id else "selected=True")
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
  from sdcp.core.extras import get_include
  entry  = PC.weathermap[page]
  graphs = entry.get('graphs')
  print "<SECTION CLASS=content STYLE='top:0px;'>"
  if graphs:
   from sdcp.tools.munin import widget_rows
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
# af_controller   = appformix controller ip
# os_controller   = openstack controller ip
# os_demo_name    = Name of Customer demoing for
# os_main_token   = auth token for project recovery
# os_project_id   = id for selected project
# os_project_name = name for selected project
# os_user_name    = username last used
# os_user_token   = token for user
# os_xyz_port     = port for service xyz
# os_xyz_url      = url  for service xyz
# os_xyz_id       = id   for service xyz
#

def openstack(aWeb):
 from sdcp.devices.openstack import OpenstackRPC
 name = aWeb.get('name',"iaas")
 ctrl = aWeb.get('controller',"127.0.0.1")
 appf = aWeb.get('appformix',"127.0.0.1")

 cookie = aWeb.cookie_unjar('openstack') if aWeb.cookies.get('openstack') else {}

 user = aWeb.cookies.get("os_user_name")
 utok = aWeb.cookies.get("os_user_token")
 mtok = aWeb.cookies.get("os_main_token")
 prev = aWeb.cookies.get("os_project_id")
 if utok:
  aWeb.put_redirect("sdcp.cgi?call=openstack_portal&headers=no")
  return

 aWeb.cookie_add("os_demo_name",name)
 aWeb.cookie_add("os_controller",ctrl)
 aWeb.cookie_add("af_controller",appf)

 if not mtok:
  controller = OpenstackRPC(ctrl,None)
  res = controller.auth({'project':PC.openstack['project'], 'username':PC.openstack['username'],'password':PC.openstack['password']})
  aWeb.cookie_add("os_main_token",controller.get_token())
  aWeb.log("openstack_login - login result: {}".format(str(res['result'])))
 else:
  aWeb.log("openstack_login - reusing token: {}".format(mtok))
  controller = OpenstackRPC(ctrl,mtok)

 ret = controller.call("5000","v3/projects")
 projects = [] if not ret['code'] == 200 else ret['data']['projects']

 aWeb.put_html("{} 2 Cloud".format(name.capitalize()))
 print "<DIV CLASS='grey overlay'>"
 print "<ARTICLE CLASS='login'>"
 print "<H1 CLASS='centered'>Welcome to '{}' Cloud portal</H1>".format(name.capitalize())
 print "<FORM ACTION=sdcp.cgi METHOD=POST ID=openstack_login>"
 print "<INPUT TYPE=HIDDEN NAME=call VALUE=openstack_portal>"
 print "<INPUT TYPE=HIDDEN NAME=headers VALUE=no>"
 print "<DIV CLASS=table STYLE='display:inline; float:left; width:auto; margin:0px 0px 0px 30px;'><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Customer:</DIV><DIV CLASS=td><SELECT NAME=project>"
 for p in projects:
  print "<OPTION VALUE={0}_{1} {2}>{1}</OPTION>".format(p['id'],p['name'],'' if not p['id'] == prev else "selected")
 print "</SELECT></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td>Username:</DIV><DIV CLASS=td><INPUT TYPE=text NAME=username {}></DIV></DIV>".format('' if not user else "VALUE={}".format(user))
 print "<DIV CLASS=tr><DIV CLASS=td>Password:</DIV><DIV CLASS=td><INPUT TYPE=password NAME=password></DIV></DIV>"
 print "</DIV></DIV>"
 print "<A CLASS='btn z-op' STYLE='margin:20px 20px 30px 40px;' OP=submit FRM=openstack_login>Login</A>"
 print "</FORM>"
 print "</ARTICLE></DIV>"
