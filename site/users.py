"""HTML5 Ajax Users module"""
__author__= "Zacharias El Banna"

############################################ Users ##############################################
def main(aWeb):
 cookie = aWeb.cookie('rims')
 info = aWeb.rest_call("master/user_info",{'id':cookie['id']})
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
 rows = aWeb.rest_call("master/user_list")['data']
 aWeb.wr("<SECTION CLASS=content-left  ID=div_content_left>")
 aWeb.wr("<ARTICLE><P>Users</P>")
 aWeb.wr(aWeb.button('reload', DIV='div_content', URL='users_list'))
 aWeb.wr(aWeb.button('add',    DIV='div_content_right',URL='users_info?id=new'))
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV>ID</DIV><DIV>Alias</DIV><DIV>Name</DIV><DIV>&nbsp;</DIV></DIV><DIV CLASS=tbody>")
 for row in rows:
  aWeb.wr("<DIV><DIV>%(id)s</DIV><DIV>%(alias)s</DIV><DIV>%(name)s</DIV><DIV>"%row)
  aWeb.wr(aWeb.button('info', DIV='div_content_right', URL='users_info?id=%(id)s'%row))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</DIV></DIV></ARTICLE></SECTION>")
 aWeb.wr("<SECTION CLASS=content-right ID=div_content_right></SECTION>")

#
#
def info(aWeb):
 cookie = aWeb.cookie('rims')
 args = aWeb.args()
 data = aWeb.rest_call("master/user_info?log=false",args)['data']
 themes = aWeb.rest_call("system/theme_list")
 if args.get('op') == 'update':
  from time import strftime, time
  from datetime import datetime,timedelta
  expires = (datetime.utcnow() + timedelta(days=30)).strftime("%a, %d %b %Y %H:%M:%S GMT")
  cookie['theme'] = data['theme']
  aWeb.wr("<SCRIPT>set_cookie('rims','%s','%s');</SCRIPT>"%(aWeb.cookie_encode(cookie),expires))
 aWeb.wr("<ARTICLE CLASS='info'><P>User Info (%s)</P>"%(data['id']))
 aWeb.wr("<FORM ID=user_info_form>")
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(data['id']))
 aWeb.wr("<DIV CLASS='info col2'>")
 aWeb.wr("<label for='alias' TITLE='Login username'>Alias:</label><INPUT id='alias' NAME=alias TYPE=TEXT VALUE='{}'>".format(data['alias']))
 aWeb.wr("<label for='password'>Password:</label><INPUT id='password' NAME=password TYPE=password PLACEHOLDER='*******'>")
 aWeb.wr("<label for='name'>Name:</label><INPUT id='name' NAME=name   TYPE=TEXT  VALUE='{}'>".format(data['name']))
 aWeb.wr("<label for='email'>E-mail:</label><INPUT id='email' NAME=email  TYPE=email VALUE='{}'>".format(data['email']))
 aWeb.wr("<label for='theme' TITLE='UI Theme'>Theme:</label><SELECT id='theme' NAME=theme>")
 for theme in themes:
  aWeb.wr("<OPTION %s VALUE='%s'>%s</OPTION>"%("selected='selected'" if theme == data['theme'] else "",theme,theme))
 aWeb.wr("</SELECT>")
 if cookie['id'] == data['id']:
  aWeb.wr("<label for='cookie'>Cookie:</label><span id='cookie'>%s</span>"%(",".join('%s=%s'%i for i in cookie.items())))
 aWeb.wr("</DIV>")
 aWeb.wr("</FORM>")
 aWeb.wr(aWeb.button('save',DIV='div_content_right', URL='users_info?op=update', FRM='user_info_form'))
 if data['id'] != 'new' and ((cookie['id'] == str(data['id']) or cookie['id'] == "1")):
  aWeb.wr(aWeb.button('trash',DIV='div_content_right',URL='users_delete?id={0}'.format(data['id']), MSG='Really remove user?'))
 aWeb.wr("</ARTICLE>")

#
#
def delete(aWeb):
 res = aWeb.rest_call("master/user_delete",{'id':aWeb['id']})
 aWeb.wr("<ARTICLE>User with id %s removed(%s)</ARTICLE>"%(aWeb['id'],res))
