"""Module docstring.

Ajax Bookings calls module

"""
__author__= "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__= "Production"

############################################ Bookings ##############################################
#
#
def list(aWeb):
 from sdcp.core.dbase import DB
 op = aWeb.get_value('op')
 id = aWeb.get_value('id')
 
 with DB() as db:
  if   op == 'unbook' and id:
   res = db.do("DELETE FROM bookings WHERE device_id = '{}'".format(id))
  elif op == 'extend' and id:
   res = db.do("UPDATE bookings SET time_start = NOW() WHERE device_id = '{}'".format(id))
  res  = db.do("SELECT user_id, device_id, time_start, NOW() < ADDTIME(time_start, '30 0:0:0.0') AS valid, ADDTIME(time_start, '30 0:0:0.0') as time_end, devices.hostname, users.alias FROM bookings INNER JOIN devices ON device_id = devices.id INNER JOIN users ON user_id = users.id ORDER by user_id")
  rows = db.get_rows()

 print "<DIV CLASS=z-frame><DIV CLASS=title>Bookings</DIV>"
 print "<A TITLE='Reload List' CLASS='z-btn z-small-btn z-op' DIV=div_content_left URL='sdcp.cgi?call=bookings_list'><IMG SRC='images/btn-reboot.png'></A>"
 print "<DIV CLASS=z-table>"
 print "<DIV CLASS=thead><DIV CLASS=th>User (Id)</DIV><DIV CLASS=th>Device</DIV><DIV CLASS=th>Until</DIV><DIV CLASS=th>Op</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for row in rows:
  print "<DIV CLASS=tr><DIV CLASS=td><A CLASS='z-op' DIV=div_content_right URL='sdcp.cgi?call=users_info&id={3}'>{0}</A> ({3})</DIV><DIV CLASS=td><A CLASS='z-op' DIV=div_content_right URL='sdcp.cgi?call=device_info&id={4}'>{1}</A></DIV><DIV CLASS=td {5}>{2}</DIV><DIV CLASS=td>".format(row['alias'],row['hostname'],row['time_end'],row['user_id'],row['device_id'],'' if row['valid'] == 1 else "style='background-color:orange;'")
  if int(aWeb.cookie.get('sdcp_id')) == row['user_id'] or row['valid'] == 0:
   print "<A CLASS='z-btn z-small-btn z-op' DIV=div_content_left TITLE='Extend booking' URL='sdcp.cgi?call=bookings_list&op=extend&id={0}'><IMG SRC='images/btn-add.png'></A>".format(row['device_id'])
   print "<A CLASS='z-btn z-small-btn z-op' DIV=div_content_left TITLE='Remove booking' URL='sdcp.cgi?call=bookings_list&op=unbook&id={0}'><IMG SRC='images/btn-remove.png'></A>".format(row['device_id'])
  print "&nbsp;</DIV></DIV>"
 print "</DIV></DIV></DIV>"
