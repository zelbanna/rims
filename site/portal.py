"""HTML5 Ajax Portal function module"""
__author__= "Zacharias El Banna"

#
#
def main(aWeb):
 cookie = aWeb.cookie('rims')
 auth,data,args = {},{},aWeb.args()
 if not cookie.get('token') and (args.get('username') and args.get('password')):
  try:  auth = aWeb.rest_full("%s/auth"%aWeb.url(), aArgs = args, aDataOnly = True)
  except Exception as e:
   auth = e.args[0].get('data',{})
  else:
   cookie = {'node':auth['node'],'id':auth['id'],'token':auth['token'],'theme':auth['theme']}
 if cookie.get('token'):
  id = cookie['id']
  menu = aWeb.rest_call("portal/menu",{"id":id})
  aWeb.put_html(aTitle = menu.get('title','Portal'), aTheme = cookie['theme'])
  """ If just auth:ed """
  if auth.get('token'):
   aWeb.wr("<SCRIPT>set_cookie('rims','%s','%s');</SCRIPT>"%(aWeb.cookie_encode(cookie),auth['expires']))
  aWeb.wr("<HEADER>")
  for item in menu['menu']:
   if   item['view'] == 'inline':
    aWeb.wr("<BUTTON CLASS='z-op menu' TITLE='%s' DIV=main URL='%s'><IMG ALT='%s' SRC='%s' /></BUTTON>"%(item['title'],item['href'],item['title'],item['icon']))
   elif item['view'] == 'framed':
    aWeb.wr("<BUTTON CLASS='z-op menu' TITLE='%s' DIV=main URL='resources_framed?type=%s&title=%s'><IMG ALT='%s' SRC='%s' /></BUTTON>"%(item['title'],item['type'],item['title'],item['title'],item['icon']))
   else:
    aWeb.wr("<A CLASS='btn menu' TITLE='%s' TARGET=_blank HREF='%s'><IMG ALT='%s' SRC='%s' /></A>"%(item['title'],item['href'],item['title'],item['icon']))
  aWeb.wr("<BUTTON CLASS='z-op menu right warning' OP=logout COOKIE=rims URL=portal_main>Log out</BUTTON>")
  aWeb.wr("<BUTTON CLASS='z-op menu right' TITLE='System' DIV=main URL='system_main?node=%s'><IMG SRC='../images/icon-config.png' /></BUTTON>"%aWeb.node())
  aWeb.wr("<BUTTON CLASS='z-op menu right' TITLE='User'   DIV=main URL='users_%s'><IMG SRC='../images/icon-users.png' /></BUTTON>"%("main" if id == '1' else "user?id=%s"%id))
  aWeb.wr("</HEADER>")
  aWeb.wr("<MAIN ID=main></MAIN>")
  if menu['start']:
   aWeb.wr("<SCRIPT>include_html('main','%s')</SCRIPT>"%(menu['menu'][0]['href'] if menu['menu'][0]['view'] == 'inline' else "portal_framed?type=%s&title="%(menu['menu'][0]['type'],menu['menu'][0]['title'])))
 else:
  data = aWeb.rest_call("portal/application")
  aWeb.put_html(aTitle = data['title'])
  aWeb.wr("<DIV CLASS='background overlay'><ARTICLE CLASS='login'><H1 CLASS='centered'>%s</H1>"%data['message'])
  if data.get('exception'):
   aWeb.wr("Error retrieving application info - exception info: %s"%(data['exception']))
  else:
   error = auth.get('error',{})
   aWeb.wr("<FORM ACTION='portal_main' METHOD=POST ID='login_form'>")
   aWeb.wr("<DIV CLASS=table STYLE='display:inline; float:left; margin:0px 0px 0px 30px; width:auto;'><DIV CLASS=tbody>")
   aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Username:</DIV><DIV CLASS=td><INPUT TYPE=username ID=username NAME=username PLACEHOLDER='username'></DIV></DIV>")
   aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Password:</DIV><DIV CLASS=td><INPUT TYPE=password ID=password NAME=password PLACEHOLDER='********'></DIV></DIV>")
   aWeb.wr("</DIV></DIV>")
   aWeb.wr("</FORM><BUTTON CLASS='z-op menu' OP=submit STYLE='font-size:18px; margin:20px 20px 30px 40px;' FRM='login_form'><IMG SRC='../images/icon-start.png' /></BUTTON>")
  aWeb.wr("<!-- %s -->"%auth.get('error'))
  aWeb.wr("</ARTICLE></DIV>")

############################################ Resources ##############################################
#
#
def resources(aWeb):
 aWeb.wr("<NAV><UL>")
 aWeb.wr("<LI CLASS='right dropdown'><A>Resources</A><DIV CLASS='dropdown-content'>")
 aWeb.wr("<A CLASS=z-op DIV=div_content URL='resources_view?type=menuitem'>Menuitems</A>")
 aWeb.wr("<A CLASS=z-op DIV=div_content URL='resources_view?type=tool'>Tools</A>")
 aWeb.wr("</DIV></LI>")
 aWeb.wr("</UL></NAV><SECTION CLASS=content ID=div_content>")
 view(aWeb)
 aWeb.wr("</SECTION>")

#
#
def view(aWeb):
 cookie = aWeb.cookie('rims')
 res = aWeb.rest_call("portal/resources",{'type':aWeb.get('type','tool')})
 inline = "<BUTTON CLASS='z-op menu' DIV=main URL='%(href)s' STYLE='font-size:10px;' TITLE='%(title)s'><IMG ALT='%(icon)s' SRC='%(icon)s' /></BUTTON>"
 framed = "<BUTTON CLASS='z-op menu' DIV=main URL='resources_framed?type=%(type)s&title=%(title)s' STYLE='font-size:10px;' TITLE='%(title)s'><IMG ALT='%(icon)s' SRC='%(icon)s' /></BUTTON>"
 tabbed = "<A CLASS='btn menu' TARGET=_blank HREF='%(href)s' STYLE='font-size:10px;' TITLE='%(title)s'><IMG ALT='%(icon)s' SRC='%(icon)s' /></A>"
 aWeb.wr("<DIV CLASS=centered STYLE='align-items:initial'>")
 view_map = {'inline':inline,'framed':framed,'tabbed':tabbed}
 for row in res['data']:
  aWeb.wr("<DIV STYLE='float:left; min-width:100px; margin:6px;'>")
  aWeb.wr(view_map[row['view']]%row)
  aWeb.wr("<BR><SPAN STYLE='width:100px; display:block;'>%(title)s</SPAN>"%row)
  aWeb.wr("</DIV>")
 aWeb.wr("</DIV>")

#
#
def framed(aWeb):
 res = aWeb.rest_call("portal/resource",{'type':aWeb['type'],'title':aWeb['title']})
 aWeb.wr("<IFRAME ID=system_resource_frame NAME=system_resource_frame SRC='%s'></IFRAME>"%res['href'])
