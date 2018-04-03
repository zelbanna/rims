"""Module docstring.

HTML5 Ajax Activities calls module


"""
__author__= "Zacharias El Banna"
__version__ = "18.03.16"
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
 print "<ARTICLE><P>Activities</P>"
 print aWeb.button('reload', DIV='div_content_left', URL='sdcp.cgi?call=activities_list')
 print aWeb.button('add',    DIV='div_content_right',URL='sdcp.cgi?call=activities_info&id=new')
 print "<DIV CLASS=table>"
 print "<DIV CLASS=thead><DIV CLASS=th>Date</DIV><DIV CLASS=th>Type</DIV><DIV CLASS=th>&nbsp;</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for row in rows:
  print "<DIV CLASS=tr><DIV CLASS=td><A CLASS='z-op' DIV=div_content_right URL='sdcp.cgi?call=activities_info&id={0}'>{1}</A></DIV><DIV CLASS=td>{2}</DIV></DIV>".format(row['id'],row['data'],row['type'])
 print "</DIV></DIV></ARTICLE></SECTION>"
 print "<SECTION CLASS=content-right ID=div_content_right></SECTION>"

#
#
def info(aWeb):
 cookie = aWeb.cookie_unjar('system')
 args = aWeb.get_args2dict(['call'])
 if aWeb['op']:
  args['op'] = aWeb['op']
 data = aWeb.rest_call("system_activities_info",args)
 activity = data['activity']
 users = data['users']
 print data
 print "<ARTICLE CLASS='info'><P>Activity ({})</P>".format(activity['id'])
 print "<FORM ID=activity_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(activity['id'])
 print "</DIV></DIV>"
 print "</FORM><DIV CLASS=controls>"
 print aWeb.button('delete',DIV='div_content_right',URL='sdcp.cgi?call=activitys_delete&id={0}'.format(activity['id']), MSG='Really remove activity?')
 print aWeb.button('save',DIV='div_content_right', URL='sdcp.cgi?call=activitys_info&op=update', FRM='activity_form')
 print "</DIV></ARTICLE>"

#
#
def delete(aWeb):
 res = aWeb.rest_call("system_activities_delete",{'id':aWeb['id']})
 print "<ARTICLE>Activity with id %s removed(%s)</ARTICLE>"%(aWeb['id'],res)
