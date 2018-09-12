"""Module docstring.

HTML5 Ajax Activities module


"""
__author__= "Zacharias El Banna"
__version__ = "4.0GA"
__status__ = "Production"
__icon__ = '../images/icon-calendar.png'
__type__ = 'menuitem'

########################################### Activities #############################################
def main(aWeb):
 cookie = aWeb.cookie('system')
 if not cookie.get('authenticated'):
  aWeb.wr("<SCRIPT>location.replace('system_login')</SCRIPT>")
  return
 aWeb.wr("<NAV><UL>")
 aWeb.wr("<LI><A CLASS=z-op DIV=div_content URL='activities_list'>Activities</A></LI>")
 aWeb.wr("<LI><A CLASS=z-op DIV=div_content URL='activities_report'>Report</A></LI>")
 aWeb.wr("</UL></NAV>")
 aWeb.wr("<SECTION CLASS=content       ID=div_content></SECTION>")

#
#
def report(aWeb):
 activities = aWeb.rest_call("system_activities_list",{'group':'month','mode':'full'})['data']
 aWeb.wr("<ARTICLE><P>Activities Report</P><DIV CLASS=table>")
 aWeb.wr("<DIV CLASS=thead><DIV CLASS=th>Time</DIV><DIV CLASS=th>User</DIV><DIV CLASS=th>Type</DIV><DIV CLASS=th>Event</DIV></DIV><DIV CLASS=tbody>")
 for act in activities:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>{} - {}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV></DIV>".format(act['date'],act['time'],act['user'],act['type'].encode("utf-8"),act['event'].encode("utf-8")))
 aWeb.wr("</DIV></DIV></ARTICLE>")

#
#
def list(aWeb):
 rows = aWeb.rest_call("system_activities_list")['data']
 aWeb.wr("<SECTION CLASS=content-left  ID=div_content_left>")
 aWeb.wr("<ARTICLE><P>Activities</P>")
 aWeb.wr(aWeb.button('reload', DIV='div_content', URL='activities_list'))
 aWeb.wr(aWeb.button('add',    DIV='div_content_right',URL='activities_info?id=new'))
 aWeb.wr(aWeb.button('info',   DIV='div_content',URL='activities_type_list'))
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Date</DIV><DIV CLASS=th>Type</DIV><DIV CLASS=th>&nbsp;</DIV></DIV><DIV CLASS=tbody>")
 for row in rows:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>{} - {}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>".format(row['date'],row['time'],row['type'].encode("utf-8")))
  aWeb.wr(aWeb.button('info',   DIV='div_content_right', URL='activities_info?id=%s'%row['id']))
  aWeb.wr(aWeb.button('delete', DIV='div_content_right', URL='activities_delete?id=%s'%row['id']))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</DIV></DIV></ARTICLE></SECTION>")
 aWeb.wr("<SECTION CLASS=content-right ID=div_content_right></SECTION>")

#
#
def info(aWeb):
 cookie = aWeb.cookie('system')
 args = aWeb.args()
 res  = aWeb.rest_call("system_activities_info",args)
 data = res['data']
 aWeb.wr("<ARTICLE CLASS='info'><P>Activity (%s)</P>"%(data['id']))
 aWeb.wr("<FORM ID=activity_form>")
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(data['id']))
 aWeb.wr("<DIV CLASS=table><DIV CLASS=tbody>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>User:</DIV><DIV CLASS=td><SELECT NAME=user_id>")
 for user in res['users']:
  selected = 'selected' if data['user_id'] == user['id'] or (data['id'] == 'new' and cookie['id'] == str(user['id'])) else ''
  aWeb.wr("<OPTION %s VALUE='%s'>%s</OPTION>"%(selected,user['id'],user['alias']))
 aWeb.wr("</SELECT></DIV></DIV>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Type:</DIV><DIV CLASS=td><SELECT NAME=type_id>")
 for type in res['types']:
  selected = 'selected' if data['type_id'] == type['id'] else ''
  aWeb.wr("<OPTION %s VALUE='%s'>%s</OPTION>"%(selected,type['id'],type['type'].encode("utf-8")))
 aWeb.wr("</SELECT></DIV></DIV>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Date:</DIV><DIV CLASS=td><INPUT TYPE=date NAME=date VALUE='%s'> <INPUT TYPE=time NAME=time VALUE='%s'></DIV></DIV>"%(data['date'],data['time']))
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("<TEXTAREA STYLE='width:100%; height:70px;' NAME=event>{}</TEXTAREA>".format(data['event'].encode("utf-8")))
 aWeb.wr("</FORM>")
 if data['id'] != 'new':
  aWeb.wr(aWeb.button('delete',DIV='div_content_right',URL='activities_delete?id={0}'.format(data['id']), MSG='Really remove activity?'))
 aWeb.wr(aWeb.button('save',DIV='div_content_right', URL='activities_info?op=update', FRM='activity_form'))
 aWeb.wr("</ARTICLE>")

#
#
def delete(aWeb):
 res = aWeb.rest_call("system_activities_delete",{'id':aWeb['id']})
 aWeb.wr("<ARTICLE>Activity with id %s removed(%s)</ARTICLE>"%(aWeb['id'],res))

#
#
def type_list(aWeb):
 rows = aWeb.rest_call("system_activities_type_list")['data']
 aWeb.wr("<SECTION CLASS=content-left  ID=div_content_left>")
 aWeb.wr("<ARTICLE><P>Activity Types</P>")
 aWeb.wr(aWeb.button('reload', DIV='div_content', URL='activities_type_list'))
 aWeb.wr(aWeb.button('add',    DIV='div_content_right',URL='activities_type_info?id=new'))
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Type</DIV><DIV CLASS=th>&nbsp;</DIV></DIV><DIV CLASS=tbody>")
 for row in rows:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>"%(row['id'],row['type'].encode("utf-8")))
  aWeb.wr(aWeb.button('info',   DIV='div_content_right', URL='activities_type_info?id=%s'%row['id']))
  aWeb.wr(aWeb.button('delete', DIV='div_content_right', URL='activities_type_delete?id=%s'%row['id']))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</DIV></DIV></ARTICLE></SECTION>")
 aWeb.wr("<SECTION CLASS=content-right ID=div_content_right></SECTION>")

#
#
def type_info(aWeb):
 args = aWeb.args()
 res  = aWeb.rest_call("system_activities_type_info",args)
 data = res['data']
 aWeb.wr("<ARTICLE CLASS='info'><P>Activity Type (%s)</P>"%(data['id']))
 aWeb.wr("<FORM ID=activity_form>")
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(data['id']))
 aWeb.wr("<DIV CLASS=table><DIV CLASS=tbody>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Type:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=type VALUE='%s'></DIV></DIV>"%(data['type'].encode("utf-8")))
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</FORM>")
 if data['id'] != 'new':
  aWeb.wr(aWeb.button('delete',DIV='div_content_right',URL='activities_type_delete?id={0}'.format(data['id']), MSG='Really remove activity?'))
 aWeb.wr(aWeb.button('save',DIV='div_content_right', URL='activities_type_info?op=update', FRM='activity_form'))
 aWeb.wr("</ARTICLE>")

#
#
def type_delete(aWeb):
 res = aWeb.rest_call("system_activities_type_delete",{'id':aWeb['id']})
 aWeb.wr("<ARTICLE>Activity type with id %s removed(%s)</ARTICLE>"%(aWeb['id'],res))
