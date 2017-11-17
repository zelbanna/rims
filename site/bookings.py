"""Module docstring.

HTML5 Ajax Bookings calls module

"""
__author__= "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__= "Production"

############################################ Bookings ##############################################
#
#
def list(aWeb):
 from sdcp.core.dbase import DB
 if aWeb['op']:
  from sdcp.rest.booking import booking
  res = booking({'device_id':aWeb['device_id'],'user_id':aWeb['user_id'],'op':aWeb['op']})
 
 with DB() as db:
  res  = db.do("SELECT user_id, device_id, time_start, NOW() < ADDTIME(time_start, '30 0:0:0.0') AS valid, ADDTIME(time_start, '30 0:0:0.0') as time_end, devices.hostname, users.alias FROM bookings INNER JOIN devices ON device_id = devices.id INNER JOIN users ON user_id = users.id ORDER by user_id")
  rows = db.get_rows()

 print "<ARTICLE><P>Bookings</P>"
 print aWeb.button('reload', DIV='div_content_left', URL='sdcp.cgi?call=bookings_list')
 print "<DIV CLASS=table>"
 print "<DIV CLASS=thead><DIV CLASS=th>User (Id)</DIV><DIV CLASS=th>Device</DIV><DIV CLASS=th>Until</DIV><DIV CLASS=th>Op</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for row in rows:
  print "<DIV CLASS=tr><DIV CLASS=td><A CLASS='z-op' DIV=div_content_right URL='sdcp.cgi?call=users_info&id={3}'>{0}</A> ({3})</DIV><DIV CLASS=td><A CLASS='z-op' DIV=div_content_right URL='sdcp.cgi?call=device_info&id={4}'>{1}</A></DIV><DIV CLASS=td {5}>{2}</DIV><DIV CLASS=td>".format(row['alias'],row['hostname'],row['time_end'],row['user_id'],row['device_id'],'' if row['valid'] == 1 else "style='background-color:orange;'")
  if int(aWeb.cookie.get('sdcp_id')) == row['user_id'] or row['valid'] == 0:
   print aWeb.button('add',    DIV='div_content_left', TITLE='Extend booking', URL='sdcp.cgi?call=bookings_list&op=extend&device_id=%i&user_id=%i'%(row['device_id'],row['user_id']))
   print aWeb.button('remove', DIV='div_content_left', TITLE='Remove booking', URL='sdcp.cgi?call=bookings_list&op=debook&device_id=%i&user_id=%i'%(row['device_id'],row['user_id']))
  print "&nbsp;</DIV></DIV>"
 print "</DIV></DIV>"
 print "</ARTICLE>"
