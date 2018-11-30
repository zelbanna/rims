"""HTML5 Ajax Reservations module"""
__author__= "Zacharias El Banna"

############################################ Reservations ##############################################
#
#
def list(aWeb):
 args = aWeb.args()
 cookie = aWeb.cookie('rims')
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
 cookie = aWeb.cookie('rims')
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
 args = aWeb.args()
 data = aWeb.rest_call("reservation/info",args)['data']
 aWeb.wr("<ARTICLE CLASS=info><P>Reservation</P>")
 aWeb.wr("<FORM ID=reservations_info_form>")
 aWeb.wr("<DIV CLASS=table STYLE='width:auto'><DIV CLASS=tbody>")
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=device_id ID=device_id VALUE='%s'>"%(data['device_id']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>User:</DIV><DIV CLASS='td readonly'>%s</DIV></DIV>"%(data['alias']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Start:</DIV><DIV CLASS='td readonly'>%s</DIV></DIV>"%(data['start']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>End:</DIV><DIV CLASS='td readonly'>%s</DIV></DIV>"%(data['end']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td TITLE='Indicate shutdown on expiration'>Shutdown:</DIV><DIV CLASS=td>")
 aWeb.wr("<INPUT NAME=shutdown TYPE=RADIO VALUE=0 %s>no"%(   "checked=checked" if data['shutdown'] == 0 else ""))
 aWeb.wr("<INPUT NAME=shutdown TYPE=RADIO VALUE=1 %s>yes"%(  "checked=checked" if data['shutdown'] == 1 else ""))
 aWeb.wr("<INPUT NAME=shutdown TYPE=RADIO VALUE=2 %s>reset"%("checked=checked" if data['shutdown'] == 2 else ""))
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>On Loan:</DIV><DIV CLASS=td><INPUT TYPE=CHECKBOX NAME=loan VALUE=1 %s></DIV></DIV>"%("checked=checked" if data['loan'] else ""))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Address:</DIV><DIV CLASS=td><INPUT TYPE=TEXT     NAME=address  STYLE='min-width:200px;' VALUE='%s'></DIV></DIV>"%(data['address']))
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</FORM>")
 aWeb.wr(aWeb.button('save', DIV='div_content_right', URL='reservations_info?op=update', FRM='reservations_info_form'))
 aWeb.wr("</ARTICLE>")

#
#
def report(aWeb):
 reservations = aWeb.rest_call("reservation/list",{'extended':True})['data']
 aWeb.wr("<ARTICLE><P>Reservations</P>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>User</DIV><DIV CLASS=th>Device</DIV><DIV CLASS=th>Start</DIV><DIV CLASS=th>End</DIV><DIV CLASS=th>On Loan</DIV><DIV CLASS=th>Location</DIV></DIV><DIV CLASS=tbody>")
 for res in reservations:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%(alias)s</DIV><DIV CLASS=td>%(hostname)s</DIV><DIV CLASS=td>%(start)s</DIV><DIV CLASS=td>%(end)s</DIV><DIV CLASS=td>%(loan)s</DIV><DIV CLASS=td>%(address)s</DIV></DIV>"%res)
 aWeb.wr("</DIV></DIV></ARTICLE>")
