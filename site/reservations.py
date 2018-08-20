"""Module docstring.

HTML5 Ajax Reservations module

"""
__author__= "Zacharias El Banna"
__version__ = "1.0GA"
__status__= "Production"

############################################ Reservations ##############################################
#
#
def list(aWeb):
 if not aWeb.cookies.get('system'):
  print "<SCRIPT>location.replace('index.cgi')</SCRIPT>"
  return
 cookie = aWeb.cookie_unjar('system')

 if aWeb['op']:
  aWeb.rest_call("reservation_update",{'device_id':aWeb['device_id'],'user_id':aWeb['user_id'],'op':aWeb['op']})

 rows = aWeb.rest_call("reservation_list")['data']
 print "<SECTION CLASS=content-left ID=div_content_left>"
 print "<ARTICLE><P>Reservations</P>"
 print aWeb.button('reload', DIV='div_content', URL='zdcp.cgi?reservations_list')
 print "<DIV CLASS=table>"
 print "<DIV CLASS=thead><DIV CLASS=th>User (Id)</DIV><DIV CLASS=th>Device</DIV><DIV CLASS=th>Until</DIV><DIV CLASS=th>Op</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for row in rows:
  print "<DIV CLASS=tr><DIV CLASS=td><A CLASS='z-op' DIV=div_content_right URL='zdcp.cgi?users_info&id={3}'>{0}</A> ({3})</DIV><DIV CLASS=td><A CLASS='z-op' DIV=div_content_right URL='zdcp.cgi?device_info&id={4}'>{1}</A></DIV><DIV CLASS='td {5}'>{2}</DIV><DIV CLASS='td controls'>".format(row['alias'],row['hostname'],row['end'],row['user_id'],row['device_id'],'' if row['valid'] == 1 else "orange'")
  if int(cookie['id']) == row['user_id'] or row['valid'] == 0:
   print aWeb.button('add',    DIV='div_content', TITLE='Extend reservation', URL='zdcp.cgi?reservations_list&op=extend&device_id=%i&user_id=%i'%(row['device_id'],row['user_id']))
   print aWeb.button('delete', DIV='div_content', TITLE='Remove reservation', URL='zdcp.cgi?reservations_list&op=debook&device_id=%i&user_id=%i'%(row['device_id'],row['user_id']))
  print "&nbsp;</DIV></DIV>"
 print "</DIV></DIV></ARTICLE></SECTION>"
 print "<SECTION CLASS=content-right ID=div_content_right></SECTION>"
#
#
def update(aWeb):
 cookie = aWeb.cookie_unjar('system')
 res = aWeb.rest_call("reservation_update",{'device_id':aWeb['id'],'user_id':cookie['id'],'op':aWeb['op']})
 print "<DIV CLASS=td>Reserve:</DIV>"
 if res['update'] == 1:
  if aWeb['op'] == 'drop':
   print "<DIV CLASS='td green'><A CLASS=z-op DIV=div_reservation_info URL='zdcp.cgi?reservations_update&op=reserve&id=%s'>Available</A></DIV>"%aWeb['id']
  else:
   print "<DIV CLASS='td red'><A CLASS=z-op DIV=div_reservation_info URL='zdcp.cgi?reservations_update&op=drop&id=%s'>%s</A></DIV>"%(aWeb['id'],res['alias'])
 else:
  print "<DIV CLASS='td blue'>Error Updating</DIV>"
