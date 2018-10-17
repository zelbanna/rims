"""Module docstring.

HTML5 Ajax Reservations module

"""
__author__= "Zacharias El Banna"
__version__ = "5.4"
__status__= "Production"

############################################ Reservations ##############################################
#
#
def list(aWeb):
 args = aWeb.args()
 cookie = aWeb.cookie('system')
 if aWeb['op']:
  aWeb.rest_call("reservation/update",args)
 rows = aWeb.rest_call("reservation/list")['data']
 aWeb.wr("<SECTION CLASS=content-left ID=div_content_left>")
 aWeb.wr("<ARTICLE><P>Reservations</P>")
 aWeb.wr(aWeb.button('reload', DIV='div_content', URL='reservations_list'))
 aWeb.wr("<DIV CLASS=table>")
 aWeb.wr("<DIV CLASS=thead><DIV CLASS=th>User (Id)</DIV><DIV CLASS=th STYLE='max-width:120px; overflow:hidden'>Device</DIV><DIV CLASS=th>Until</DIV><DIV CLASS=th STYLE='width:75px;'>Op</DIV></DIV>")
 aWeb.wr("<DIV CLASS=tbody>")
 for row in rows:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td><A CLASS='z-op' DIV=div_content_right URL='users_info?id={3}'>{0}</A></DIV><DIV CLASS=td><A CLASS='z-op' DIV=div_content_right URL='device_info?id={4}'>{1}</A></DIV><DIV CLASS='td {5}'>{2}</DIV><DIV CLASS=td>".format(row['alias'],row['hostname'],row['end'],row['user_id'],row['device_id'],'' if row['valid'] else "orange'"))
  if int(cookie['id']) == row['user_id'] or not row['valid']:
   aWeb.wr(aWeb.button('info',   DIV='div_content_right', TITLE='Info', URL='reservations_info?device_id=%i&user_id=%i'%(row['device_id'],row['user_id'])))
   aWeb.wr(aWeb.button('add',    DIV='div_content', TITLE='Extend reservation', URL='reservations_list?op=extend&device_id=%i&user_id=%i&days=14'%(row['device_id'],row['user_id'])))
   aWeb.wr(aWeb.button('delete', DIV='div_content', TITLE='Remove reservation', URL='reservations_list?op=drop&device_id=%i&user_id=%i'%(row['device_id'],row['user_id'])))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</DIV></DIV></ARTICLE></SECTION>")
 aWeb.wr("<SECTION CLASS=content-right ID=div_content_right></SECTION>")
#
#
def update(aWeb):
 cookie = aWeb.cookie('system')
 res = aWeb.rest_call("reservation/update",{'device_id':aWeb['id'],'user_id':cookie['id'],'op':aWeb['op'],'days':14})
 aWeb.wr("<DIV CLASS=td>Reserve:</DIV>")
 if res['update'] == 1:
  if aWeb['op'] == 'drop':
   aWeb.wr("<DIV CLASS='td green'><A CLASS=z-op DIV=div_reservation_info URL='reservations_update?op=reserve&id=%s'>Available</A></DIV>"%aWeb['id'])
  else:
   aWeb.wr("<DIV CLASS='td red'><A CLASS=z-op DIV=div_reservation_info URL='reservations_update?op=drop&id=%s'>%s</A></DIV>"%(aWeb['id'],res['alias']))
 else:
  aWeb.wr("<DIV CLASS='td blue'>Error Updating</DIV>")

#
#
def info(aWeb):
 aWeb.wr("<ARTICLE CLASS=info><P>Device</P>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=tbody>")
 aWeb.wr("</DIV></DIV></ARTICLE>")

#
#
def report(aWeb):
 reservations = aWeb.rest_call("reservation/list",{'extended':True})['data']
 aWeb.wr("<ARTICLE><P>Reservations</P>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>User</DIV><DIV CLASS=th>Device</DIV><DIV CLASS=th>Start</DIV><DIV CLASS=th>End</DIV><DIV CLASS=th>On Loan</DIV><DIV CLASS=th>Location</DIV></DIV><DIV CLASS=tbody>")
 for res in reservations:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%(alias)s</DIV><DIV CLASS=td>%(hostname)s</DIV><DIV CLASS=td>%(start)s</DIV><DIV CLASS=td>%(end)s</DIV><DIV CLASS=td>%(loan)s</DIV><DIV CLASS=td>%(address)s</DIV></DIV>"%res)
 aWeb.wr("</DIV></DIV></ARTICLE>")
