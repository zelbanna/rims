"""HTML5 Activities module"""
__author__= "Zacharias El Banna"

########################################### Activities #############################################
def main(aWeb):
 cookie = aWeb.cookie('rims')
 aWeb.wr("<NAV><UL>")
 aWeb.wr("<LI><A CLASS=z-op DIV=div_content URL='activities_list'>Activities</A></LI>")
 aWeb.wr("<LI><A CLASS=z-op DIV=div_content URL='activities_report'>Report</A></LI>")
 aWeb.wr("</UL></NAV>")
 aWeb.wr("<SECTION CLASS=content       ID=div_content></SECTION>")

#
#
def report(aWeb):
 activities = aWeb.rest_call("master/activity_list",{'group':'month','mode':'full'})['data']
 aWeb.wr("<ARTICLE><P>Activities Report</P><DIV CLASS=table><DIV CLASS=thead><DIV>Time</DIV><DIV>User</DIV><DIV>Type</DIV><DIV>Event</DIV></DIV><DIV CLASS=tbody>")
 for act in activities:
  aWeb.wr("<DIV><DIV>{} - {}</DIV><DIV>{}</DIV><DIV>{}</DIV><DIV>{}</DIV></DIV>".format(act['date'],act['time'],act['user'],act['type'],act['event']))
 aWeb.wr("</DIV></DIV></ARTICLE>")

#
#
def list(aWeb):
 rows = aWeb.rest_call("master/activity_list")['data']
 aWeb.wr("<SECTION CLASS=content-left  ID=div_content_left>")
 aWeb.wr("<ARTICLE><P>Activities</P>")
 aWeb.wr(aWeb.button('reload', DIV='div_content', URL='activities_list'))
 aWeb.wr(aWeb.button('add',    DIV='div_content_right',URL='activities_info?id=new'))
 aWeb.wr(aWeb.button('info',   DIV='div_content',URL='activities_type_list'))
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV>Date</DIV><DIV>Type</DIV><DIV>&nbsp;</DIV></DIV><DIV CLASS=tbody>")
 for row in rows:
  aWeb.wr("<DIV><DIV>{} - {}</DIV><DIV>{}</DIV><DIV>".format(row['date'],row['time'],row['type']))
  aWeb.wr(aWeb.button('info',   DIV='div_content_right', URL='activities_info?id=%s'%row['id']))
  aWeb.wr(aWeb.button('delete', DIV='div_content_right', URL='activities_delete?id=%s'%row['id']))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</DIV></DIV></ARTICLE></SECTION>")
 aWeb.wr("<SECTION CLASS=content-right ID=div_content_right></SECTION>")

#
#
def info(aWeb):
 cookie = aWeb.cookie('rims')
 args = aWeb.args()
 res  = aWeb.rest_call("master/activity_info",args)
 data = res['data']
 aWeb.wr("<ARTICLE CLASS='info'><P>Activity (%s)</P>"%(data['id']))
 aWeb.wr("<FORM ID=activities_info_form>")
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(data['id']))
 aWeb.wr("<DIV CLASS='info col2'>")
 aWeb.wr("<LABEL for='user_id'>User:</LABEL><SELECT id='user_id' NAME=user_id>")
 for user in res['users']:
  selected = 'selected' if data['user_id'] == user['id'] or (data['id'] == 'new' and cookie['id'] == user['id']) else ''
  aWeb.wr("<OPTION %s VALUE='%s'>%s</OPTION>"%(selected,user['id'],user['alias']))
 aWeb.wr("</SELECT>")
 aWeb.wr("<LABEL for='type_id'>Type:</LABEL><SELECT id='type_id' NAME=type_id>")
 for type in res['types']:
  selected = 'selected' if data['type_id'] == type['id'] else ''
  aWeb.wr("<OPTION %s VALUE='%s'>%s</OPTION>"%(selected,type['id'],type['type']))
 aWeb.wr("</SELECT>")
 aWeb.wr("<LABEL for='date'>Date:</LABEL><DIV><INPUT TYPE=date NAME=date VALUE='%s'> <INPUT TYPE=time NAME=time VALUE='%s'></DIV>"%(data['date'],data['time']))
 aWeb.wr("</DIV>")
 aWeb.wr("<TEXTAREA STYLE='width:100%; height:70px;' NAME=event>{}</TEXTAREA>".format(data['event']))
 aWeb.wr("</FORM>")
 if data['id'] != 'new':
  aWeb.wr(aWeb.button('delete',DIV='div_content_right',URL='activities_delete?id={0}'.format(data['id']), MSG='Really remove activity?'))
 aWeb.wr(aWeb.button('save',DIV='div_content_right', URL='activities_info?op=update', FRM='activities_info_form'))
 aWeb.wr("</ARTICLE>")

#
#
def delete(aWeb):
 res = aWeb.rest_call("master/activity_delete",{'id':aWeb['id']})
 aWeb.wr("<ARTICLE>Activity with id %s removed(%s)</ARTICLE>"%(aWeb['id'],res))

#
#
def type_list(aWeb):
 rows = aWeb.rest_call("master/activity_type_list")['data']
 aWeb.wr("<SECTION CLASS=content-left  ID=div_content_left>")
 aWeb.wr("<ARTICLE><P>Activity Types</P>")
 aWeb.wr(aWeb.button('reload', DIV='div_content', URL='activities_type_list'))
 aWeb.wr(aWeb.button('add',    DIV='div_content_right',URL='activities_type_info?id=new'))
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV>ID</DIV><DIV>Type</DIV><DIV>&nbsp;</DIV></DIV><DIV CLASS=tbody>")
 for row in rows:
  aWeb.wr("<DIV><DIV>%s</DIV><DIV>%s</DIV><DIV>"%(row['id'],row['type']))
  aWeb.wr(aWeb.button('info',   DIV='div_content_right', URL='activities_type_info?id=%s'%row['id']))
  aWeb.wr(aWeb.button('delete', DIV='div_content_right', URL='activities_type_delete?id=%s'%row['id']))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</DIV></DIV></ARTICLE></SECTION>")
 aWeb.wr("<SECTION CLASS=content-right ID=div_content_right></SECTION>")

#
#
def type_info(aWeb):
 args = aWeb.args()
 res  = aWeb.rest_call("master/activity_type_info",args)
 data = res['data']
 aWeb.wr("<ARTICLE CLASS='info'><P>Activity Type (%s)</P>"%(data['id']))
 aWeb.wr("<FORM ID=activities_type_info_form>")
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(data['id']))
 aWeb.wr("<DIV CLASS='info col2'>")
 aWeb.wr("<LABEL for='type'>Type:</LABEL><INPUT id='type' TYPE=TEXT NAME=type VALUE='%s'>"%data['type'])
 aWeb.wr("</DIV>")
 aWeb.wr("</FORM>")
 if data['id'] != 'new':
  aWeb.wr(aWeb.button('delete',DIV='div_content_right',URL='activities_type_delete?id={0}'.format(data['id']), MSG='Really remove activity?'))
 aWeb.wr(aWeb.button('save',DIV='div_content_right', URL='activities_type_info?op=update', FRM='activities_type_info_form'))
 aWeb.wr("</ARTICLE>")

#
#
def type_delete(aWeb):
 res = aWeb.rest_call("master/activity_type_delete",{'id':aWeb['id']})
 aWeb.wr("<ARTICLE>Activity type with id %s removed(%s)</ARTICLE>"%(aWeb['id'],res))
