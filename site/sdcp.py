"""Module docstring.

HTML5 Ajax SDCP generic module

"""
__author__= "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__= "Production"

############################################## SDCP ###############################################
#
#
# SDCP Portal - New "Window"/Pane
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
  cookie.update({'id':id,'user':user,'view':view})
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
