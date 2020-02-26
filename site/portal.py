"""HTML5 Ajax Portal function module"""
__author__= "Zacharias El Banna"

#
#
def login(aWeb):
 data = aWeb.rest_call("portal/application")
 aWeb.put_html(aTitle = data['title'])
 aWeb.wr("<DIV CLASS='background overlay'><ARTICLE CLASS='login'><H1 CLASS='centered'>%s</H1>"%data['message'])
 if data.get('exception'):
  aWeb.wr("Error retrieving application info - exception info: %s"%(data['exception']))
 else:
  aWeb.wr("<FORM ACTION='portal_main' METHOD=POST ID='login_form'>")
  aWeb.wr("<DIV CLASS='info col2' STYLE='float:left;'>")
  aWeb.wr("<label for='username'>Username:</label><INPUT TYPE=text ID=username NAME=username PLACEHOLDER='username'>")
  aWeb.wr("<label for='password'>Password:</label><INPUT TYPE=password ID=password NAME=password PLACEHOLDER='********'>")
  aWeb.wr("</DIV>")
  aWeb.wr("</FORM><BUTTON CLASS='z-op menu' OP=submit STYLE='font-size:18px; margin:10px 10px 10px 10px;' FRM='login_form'><IMG SRC='images/icon-start.png' /></BUTTON>")
  aWeb.wr("</ARTICLE></DIV>")

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
  aWeb.wr("<BUTTON CLASS='z-op menu right warning' OP=logout COOKIE=rims URL=portal_main>Log out</BUTTON>")
  aWeb.wr("<BUTTON CLASS='z-op menu right' TITLE='System' DIV=main URL='system_main?node=%s'><IMG SRC='images/icon-config.png' /></BUTTON>"%aWeb.node())
  aWeb.wr("<BUTTON CLASS='z-op menu right' TITLE='User'   DIV=main URL='user_%s'><IMG SRC='images/icon-users.png' /></BUTTON>"%("main" if id == '1' else "user?id=%s"%id))
  for title,item in menu['menu'].items():
   if 'mod_fun' in item:
    aWeb.wr("<BUTTON CLASS='z-op menu' TITLE='%s' DIV=main URL='%s'><IMG ALT='%s' SRC='%s' /></BUTTON>"%(title,item['mod_fun'],title,item['icon']))
   elif 'frame' in item:
    aWeb.wr("<BUTTON CLASS='z-op menu' TITLE='%s' DIV=main URL='resource_framed?type=%s&title=%s'><IMG ALT='%s' SRC='%s' /></BUTTON>"%(title,item['type'],title,title,item['icon']))
   elif 'tab' in item:
    aWeb.wr("<A CLASS='btn menu' TARGET=_blank HREF='%s'><IMG ALT='%s' SRC='%s' /></A>"%(title,item['tab'],title,item['icon']))
  aWeb.wr("</HEADER>")
  aWeb.wr("<MAIN ID=main></MAIN>")
  if menu['start']:
   aWeb.wr("<SCRIPT>include_html('main','%s')</SCRIPT>"%(menu['menu'][menu['start']]['mod_fun'] if 'mod_fun' in menu['menu'][menu['start']] else "portal_framed?type=%s&title=%s"%(menu['menu'][menu['start']]['type'],menu['menu'][0]['title'])))
 else:
  aWeb.wr("<SCRIPT>window.location.replace('/portal_login');</SCRIPT>")
