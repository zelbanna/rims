"""HTML5 Ajax Users module"""
__author__= "Zacharias El Banna"
__icon__ = 'icon-users.png'
__type__ = 'menuitem'

############################################ Users ##############################################
def main(aWeb):
 cookie = aWeb.cookie('rims')
 info = aWeb.rest_call("system/user_info",{'id':cookie['id']})
 aWeb.wr("<NAV><UL>")
 aWeb.wr("<LI><A CLASS=z-op DIV=div_content URL='users_list'>Users</A></LI>")
 aWeb.wr("<LI><A CLASS=z-op DIV=div_content URL='reservations_list'>Reservations</A></LI>")
 aWeb.wr("<LI CLASS='right navinfo'><A>%s</A></LI>"%info['data']['name'])
 aWeb.wr("</UL></NAV>")
 aWeb.wr("<SECTION CLASS=content       ID=div_content></SECTION>")

#
#
def user(aWeb):
 cookie = aWeb.cookie('rims')
 aWeb.wr("<NAV><UL></UL></NAV>")
 aWeb.wr("<SECTION CLASS=content       ID=div_content>")
 aWeb.wr("<SECTION CLASS=content-left  ID=div_content_left></SECTION>")
 aWeb.wr("<SECTION CLASS=content-right ID=div_content_right>")
 info(aWeb)
 aWeb.wr("</SECTION>")
 aWeb.wr("</SECTION>")

#
#
def list(aWeb):
 rows = aWeb.rest_call("system/user_list")['data']
 aWeb.wr("<SECTION CLASS=content-left  ID=div_content_left>")
 aWeb.wr("<ARTICLE><P>Users</P>")
 aWeb.wr(aWeb.button('reload', DIV='div_content', URL='users_list'))
 aWeb.wr(aWeb.button('add',    DIV='div_content_right',URL='users_info?id=new'))
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Alias</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>&nbsp;</DIV></DIV><DIV CLASS=tbody>")
 for row in rows:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%(id)s</DIV><DIV CLASS=td>%(alias)s</DIV><DIV CLASS=td>%(name)s</DIV><DIV CLASS=td>"%row)
  aWeb.wr(aWeb.button('info', DIV='div_content_right', URL='users_info?id=%(id)s'%row))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</DIV></DIV></ARTICLE></SECTION>")
 aWeb.wr("<SECTION CLASS=content-right ID=div_content_right></SECTION>")

#
#
def info(aWeb):
 cookie = aWeb.cookie('rims')
 args = aWeb.args()
 data = aWeb.rest_call("system/user_info?log=false",args)['data']
 resources = aWeb.rest_call("system/resource_list",{'user_id':cookie['id'], 'dict':'id','view_public':True,'node':aWeb.node()})['data']
 themes = aWeb.rest_call("system/theme_list")
 if args.get('op') == 'update':
  from time import strftime, time
  from datetime import datetime,timedelta
  expires = (datetime.utcnow() + timedelta(days=30)).strftime("%a, %d %b %Y %H:%M:%S GMT")
  cookie['theme'] = data['theme']
  aWeb.wr("<SCRIPT>set_cookie('rims','%s','%s');</SCRIPT>"%(aWeb.cookie_encode(cookie),expires))
 aWeb.wr("<SCRIPT>dragndrop();</SCRIPT>")
 aWeb.wr("<ARTICLE CLASS='info'><P>User Info (%s)</P>"%(data['id']))
 aWeb.wr("<FORM ID=user_info_form>")
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(data['id']))
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=menulist ID=menulist VALUE='{}'>".format(data['menulist']))
 aWeb.wr("<DIV CLASS=table><DIV CLASS=tbody>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td TITLE='Login username'>Alias:</DIV>  <DIV CLASS=td><INPUT NAME=alias  TYPE=TEXT  VALUE='{}' STYLE='min-width:400px'></DIV></DIV>".format(data['alias']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Password:</DIV><DIV CLASS=td><INPUT NAME=password TYPE=password PLACEHOLDER='*******' STYLE='min-width:400px'></DIV></DIV>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Name:</DIV>   <DIV CLASS=td><INPUT NAME=name   TYPE=TEXT  VALUE='{}' STYLE='min-width:400px'></DIV></DIV>".format(data['name']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>E-mail:</DIV> <DIV CLASS=td><INPUT NAME=email  TYPE=email VALUE='{}' STYLE='min-width:400px'></DIV></DIV>".format(data['email']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td TITLE='Slack username'>Slack:</DIV>  <DIV CLASS=td><INPUT NAME=slack  TYPE=TEXT  VALUE='{}' STYLE='min-width:400px'></DIV></DIV>".format(data['slack']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td TITLE='UI Theme'>Theme:</DIV><DIV CLASS=td><SELECT NAME=theme>")
 for theme in themes:
  aWeb.wr("<OPTION %s VALUE='%s'>%s</OPTION>"%("selected='selected'" if theme == data['theme'] else "",theme,theme))
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>View All:</DIV><DIV CLASS=td><INPUT NAME=view_public TYPE=CHECKBOX VALUE=1 {}             {}></DIV></DIV>".format("checked=checked" if str(data['view_public']) == "1" else "","disabled" if cookie['id'] != str(data['id']) else ""))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Cookie:</DIV><DIV CLASS='td small-text'>%s</DIV></DIV>"%",".join('%s=%s'%i for i in cookie.items()))
 aWeb.wr("</DIV></DIV><SPAN>Menu list</SPAN>")
 aWeb.wr("<DIV CLASS='border' STYLE='display:flex; flex-wrap:wrap; min-height:100px;'><UL STYLE='width:100%' ID=ul_menu DEST=menulist CLASS='drop'>")
 menulist = data['menulist'].split(',') if not data.get('menulist') == 'default' else [ value['id'] for key,value in resources.items() if value['type'] == 'menuitem']
 for key in menulist:
  try:
   resource = resources.pop(key,None)
   aWeb.wr("<LI CLASS='drag' ID={0}><BUTTON CLASS='menu' STYLE='font-size:10px;' TITLE='{1}'><IMG SRC='{2}' ALT='{1}' /></BUTTON></LI>".format(key,resource['title'],resource['icon']))
  except: pass
 aWeb.wr("</UL></DIV>")
 aWeb.wr("</FORM>")
 aWeb.wr(aWeb.button('save',DIV='div_content_right', URL='users_info?op=update', FRM='user_info_form'))
 if data['id'] != 'new' and ((cookie['id'] == str(data['id']) or cookie['id'] == "1")):
  aWeb.wr(aWeb.button('trash',DIV='div_content_right',URL='users_delete?id={0}'.format(data['id']), MSG='Really remove user?'))
 aWeb.wr("<SPAN STYLE='display:block'>Available menu options</SPAN>")
 aWeb.wr("<DIV STYLE='display:flex; flex-wrap:wrap;'><UL STYLE='width:100%' ID=ul_avail CLASS='drop'>")
 for id,resource in resources.items():
  aWeb.wr("<LI CLASS='drag' ID={0}><BUTTON CLASS='menu' STYLE='font-size:10px;' TITLE='{1}'><IMG SRC='{2}' ALT='{1}' /></BUTTON></LI>".format(id,resource['title'],resource['icon']))
 aWeb.wr("</UL></DIV>")
 aWeb.wr("</ARTICLE>")

#
#
def delete(aWeb):
 res = aWeb.rest_call("system/user_delete",{'id':aWeb['id']})
 aWeb.wr("<ARTICLE>User with id %s removed(%s)</ARTICLE>"%(aWeb['id'],res))

