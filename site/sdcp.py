"""Module docstring.

HTML5 Ajax SDCP generic module

"""
__author__= "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__= "Production"

#
# Generic Login
#
def login(aWeb):
 """
 Input header/form:
  - application (default to sdcp)
  - 'application' cookie jar with 'portal'

 REST backend requires 'app' (same as application) and response:
  - title
  - message, welcome message
  - portal (xyz_abc in sdcp.site.xyz_abc)
  - choices (list of display, id, data list  with id, data entries)
  - parameters (list of display id data where data is input type)
 """
 application = aWeb.get('application','sdcp')
 cookie = aWeb.cookie_unjar(application)
 if len(cookie) > 0 and cookie.get('portal',False):
  aWeb.put_redirect("sdcp.cgi?call=%s&headers=no"%cookie['portal'])
  return

 from .. import PackageContainer as PC
 data = aWeb.rest_call(PC.generic['url'],"sdcp.rest.%s_application"%(application),aWeb.get_args2dict_except(['call','header']))['data']
 aWeb.cookie_add(application,data['cookie'])
 aWeb.put_html(data['title'])
 print "<DIV CLASS='grey overlay'>"
 print "<ARTICLE CLASS='login'>"
 print "<H1 CLASS='centered'>%s</H1>"%data['message']
 print "<FORM ACTION=sdcp.cgi METHOD=POST ID=login_form>"
 print "<INPUT TYPE=HIDDEN NAME=call VALUE='%s'>"%data['portal']
 print "<INPUT TYPE=HIDDEN NAME=headers VALUE=no>"
 print "<DIV CLASS=table STYLE='display:inline; float:left; margin:0px 0px 0px 30px; width:auto;'><DIV CLASS=tbody>"
 for choice in data.get('choices'):
  print "<DIV CLASS=tr><DIV CLASS=td>%s:</DIV><DIV CLASS=td><SELECT NAME='%s'>"%(choice['display'],choice['id'])
  for row in choice['data']:
   print "<OPTION VALUE='%s'>%s</OPTION>"%(row['id'],row['name'])
  print "</SELECT></DIV></DIV>"
 for param in data.get('parameters'):
  print "<DIV CLASS=tr><DIV CLASS=td>%s:</DIV><DIV CLASS=td><INPUT TYPE=%s NAME='%s'></DIV></DIV>"%(param['display'],param['data'],param['id'])
 print "</DIV></DIV>"
 print "<A CLASS='btn z-op' OP=submit STYLE='margin:20px 20px 30px 40px;' FRM=login_form>Enter</A>"
 print "</FORM>"
 print "</ARTICLE></DIV>"

############################################## SDCP ###############################################
#
#
# Base SDCP Portal, creates DIVs for layout
#
def portal(aWeb):
 from .. import PackageContainer as PC
 cookie = aWeb.cookie_unjar('sdcp')

 if cookie.get('id',None) is None:
  id,user,view = aWeb.get('sdcp_login',"None_None_1").split('_')
  if id == "None":
   aWeb.put_html("SDCP Portal")
   print "Error logging in - please try login again"
   return   
  cookie.update({'id':id,'user':user,'view':view,'portal':'sdcp_portal'})
  aWeb.cookie_jar('sdcp',cookie, 86400)
  aWeb.log("Entering as {}-'{}' ({})".format(id,user,view))
 else:
  id   = cookie.get('id')
  user = cookie.get('user')
  view = cookie.get('view')

 from ..core.dbase import DB
 with DB() as db:
  db.do("SELECT menulist FROM users WHERE id = '{}'".format(id))
  menulist = db.get_val('menulist')

 from ..rest.resources import list as resource_list
 resources = resource_list({'id':id,'dict':'id'})['data']
 aWeb.put_html(PC.sdcp['name'])
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
