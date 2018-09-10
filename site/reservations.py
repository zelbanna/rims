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
 if not aWeb.cookie('system'):
  aWeb.wr("<SCRIPT>location.replace('system_login')</SCRIPT>")
  return
 cookie = aWeb.cookie('system')

 if aWeb['op']:
  aWeb.rest_call("reservation_update",{'device_id':aWeb['device_id'],'user_id':aWeb['user_id'],'op':aWeb['op']})

 rows = aWeb.rest_call("reservation_list")['data']
 aWeb.wr("<SECTION CLASS=content-left ID=div_content_left>")
 aWeb.wr("<ARTICLE><P>Reservations</P>")
 aWeb.wr(aWeb.button('reload', DIV='div_content', URL='reservations_list'))
 aWeb.wr("<DIV CLASS=table>")
 aWeb.wr("<DIV CLASS=thead><DIV CLASS=th>User (Id)</DIV><DIV CLASS=th>Device</DIV><DIV CLASS=th>Until</DIV><DIV CLASS=th>Op</DIV></DIV>")
 aWeb.wr("<DIV CLASS=tbody>")
 for row in rows:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td><A CLASS='z-op' DIV=div_content_right URL='users_info?id={3}'>{0}</A> ({3})</DIV><DIV CLASS=td><A CLASS='z-op' DIV=div_content_right URL='device_info?id={4}'>{1}</A></DIV><DIV CLASS='td {5}'>{2}</DIV><DIV CLASS=td>".format(row['alias'],row['hostname'],row['end'],row['user_id'],row['device_id'],'' if row['valid'] == 1 else "orange'"))
  if int(cookie['id']) == row['user_id'] or row['valid'] == 0:
   aWeb.wr(aWeb.button('add',    DIV='div_content', TITLE='Extend reservation', URL='reservations_list?op=extend&device_id=%i&user_id=%i'%(row['device_id'],row['user_id'])))
   aWeb.wr(aWeb.button('delete', DIV='div_content', TITLE='Remove reservation', URL='reservations_list?op=drop&device_id=%i&user_id=%i'%(row['device_id'],row['user_id'])))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</DIV></DIV></ARTICLE></SECTION>")
 aWeb.wr("<SECTION CLASS=content-right ID=div_content_right></SECTION>")
#
#
def update(aWeb):
 cookie = aWeb.cookie('system')
 res = aWeb.rest_call("reservation_update",{'device_id':aWeb['id'],'user_id':cookie['id'],'op':aWeb['op']})
 aWeb.wr("<DIV CLASS=td>Reserve:</DIV>")
 if res['update'] == 1:
  if aWeb['op'] == 'drop':
   aWeb.wr("<DIV CLASS='td green'><A CLASS=z-op DIV=div_reservation_info URL='reservations_update?op=reserve&id=%s'>Available</A></DIV>"%aWeb['id'])
  else:
   aWeb.wr("<DIV CLASS='td red'><A CLASS=z-op DIV=div_reservation_info URL='reservations_update?op=drop&id=%s'>%s</A></DIV>"%(aWeb['id'],res['alias']))
 else:
  aWeb.wr("<DIV CLASS='td blue'>Error Updating</DIV>")
