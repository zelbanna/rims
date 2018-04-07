"""Module docstring.

HTML5 Ajax Activities calls module


"""
__author__= "Zacharias El Banna"
__version__ = "18.04.07GA"
__status__ = "Production"
__icon__ = 'images/icon-calendar.png'
__type__ = 'menuitem'

########################################### Activities #############################################
def main(aWeb):
 if not aWeb.cookies.get('system'):
  print "<SCRIPT>location.replace('index.cgi')</SCRIPT>"
  return
 cookie = aWeb.cookie_unjar('system')
 print "<NAV><UL>"
 print "<LI><A CLASS=z-op DIV=div_content URL='sdcp.cgi?call=activities_list'>Activities</A></LI>"
 print "<LI><A CLASS=z-op DIV=div_content URL='sdcp.cgi?call=activities_report'>Report</A></LI>"
 print "</UL></NAV>"
 print "<SECTION CLASS=content       ID=div_content></SECTION>"

#
#
def list(aWeb):
 rows = aWeb.rest_call("system_activities_list")['data']
 print "<SECTION CLASS=content-left  ID=div_content_left>"
 print "<ARTICLE><P>Activities</P><DIV CLASS=controls>"
 print aWeb.button('reload', DIV='div_content', URL='sdcp.cgi?call=activities_list')
 print aWeb.button('add',    DIV='div_content_right',URL='sdcp.cgi?call=activities_info&id=new')
 print "</DIV><DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Date</DIV><DIV CLASS=th>Type</DIV><DIV CLASS=th>&nbsp;</DIV></DIV><DIV CLASS=tbody>"
 for row in rows:
  print "<DIV CLASS=tr><DIV CLASS=td>%s - %s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>&nbsp;</DIV>"%(row['date'],row['time'],row['type'])
  print aWeb.button('info',   DIV='div_content_right', URL='sdcp.cgi?call=activities_info&id=%s'%row['id'])
  print aWeb.button('delete', DIV='div_content_right', URL='sdcp.cgi?call=activities_delete&id=%s'%row['id'])
  print "</DIV>"
 print "</DIV></DIV></ARTICLE></SECTION>"
 print "<SECTION CLASS=content-right ID=div_content_right></SECTION>"

#
#
def info(aWeb):
 cookie = aWeb.cookie_unjar('system')
 args = aWeb.get_args2dict(['call'])
 data = aWeb.rest_call("system_activities_info",args)['data']
 print "<ARTICLE CLASS='info'><P>Activity (%s)</P>"%(data['id'])
 print "<FORM ID=activity_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(data['id'])
 print "<DIV CLASS=table><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>User:</DIV><DIV CLASS=td><SELECT NAME=user_id>"
 for user in data['users']:
  selected = 'selected' if data['user_id'] == user['id'] or (data['id'] == 'new' and cookie['id'] == str(user['id'])) else ''
  print "<OPTION %s VALUE='%s'>%s</OPTION>"%(selected,user['id'],user['alias'])
 print "</SELECT></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td>Date:</DIV><DIV CLASS=td><INPUT TYPE=date NAME=date VALUE='%s'> <INPUT TYPE=time NAME=time VALUE='%s'></DIV></DIV>"%(data['date'],data['time'])
 print "<DIV CLASS=tr><DIV CLASS=td>Type:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=type VALUE='%s'></DIV></DIV>"%(data['type'])
 print "</DIV></DIV>"
 print "<TEXTAREA STYLE='width:100%; height:70px;' NAME=event>{}</TEXTAREA>".format(data['event'])
 print "</FORM><DIV CLASS=controls>"
 if data['id'] != 'new':
  print aWeb.button('delete',DIV='div_content_right',URL='sdcp.cgi?call=activities_delete&id={0}'.format(data['id']), MSG='Really remove activity?')
 print aWeb.button('save',DIV='div_content_right', URL='sdcp.cgi?call=activities_info&op=update', FRM='activity_form')
 print "</DIV></ARTICLE>"

#
#
def delete(aWeb):
 res = aWeb.rest_call("system_activities_delete",{'id':aWeb['id']})
 print "<ARTICLE>Activity with id %s removed(%s)</ARTICLE>"%(aWeb['id'],res)
