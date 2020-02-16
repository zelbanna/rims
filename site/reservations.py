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
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV>User (Id)</DIV><DIV CLASS=th STYLE='max-width:120px; overflow:hidden'>Device</DIV><DIV>Until</DIV><DIV CLASS=th STYLE='width:75px;'>Op</DIV></DIV><DIV CLASS=tbody>")
 for row in rows:
  aWeb.wr("<DIV><DIV><A CLASS='z-op' DIV=div_content_right URL='users_info?id={3}'>{0}</A></DIV><DIV><A CLASS='z-op' DIV=div_content_right URL='device_info?id={4}'>{1}</A></DIV><DIV CLASS='{5}'>{2}</DIV><DIV>".format(row['alias'],row['hostname'],row['end'],row['user_id'],row['device_id'],'' if row['valid'] else "orange'"))
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
 aWeb.wr("<DIV>Reserve:</DIV>")
 if res['update'] == 1:
  if aWeb['op'] == 'drop':
   aWeb.wr("<DIV CLASS='green'><A CLASS=z-op DIV=div_reservation_info URL='reservations_update?op=reserve&id=%s'>Available</A></DIV>"%aWeb['id'])
  else:
   aWeb.wr("<DIV CLASS='red'><A CLASS=z-op DIV=div_reservation_info URL='reservations_update?op=drop&id=%s'>%s</A></DIV>"%(aWeb['id'],res['alias']))
 else:
  aWeb.wr("<DIV CLASS='blue'>Error Updating</DIV>")

#
#
def info(aWeb):
 args = aWeb.args()
 data = aWeb.rest_call("reservation/info",args)['data']
 aWeb.wr("<ARTICLE CLASS=info><P>Reservation</P>")
 aWeb.wr("<FORM ID=reservations_info_form>")
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=device_id ID=device_id VALUE='%s'>"%(data['device_id']))
 aWeb.wr("<DIV CLASS='info col2'>")
 aWeb.wr("<LABEL FOR='alias'>User:</LABEL><SPAN ID='alias'>%s</SPAN>"%(data['alias']))
 aWeb.wr("<LABEL FOR='start'>Start:</LABEL><SPAN ID='start'>%s</SPAN>"%(data['start']))
 aWeb.wr("<LABEL FOR='end'>End:</LABEL><SPAN ID='end'>%s</SPAN>"%(data['end']))
 aWeb.wr("<LABEL FOR='shutdown' TITLE='Indicate shutdown on expiration'>Shutdown:</LABEL><DIV>")
 aWeb.wr("<INPUT NAME=shutdown TYPE=RADIO VALUE=0 %s>no"%(   "checked=checked" if data['shutdown'] == 0 else ""))
 aWeb.wr("<INPUT NAME=shutdown TYPE=RADIO VALUE=1 %s>yes"%(  "checked=checked" if data['shutdown'] == 1 else ""))
 aWeb.wr("<INPUT NAME=shutdown TYPE=RADIO VALUE=2 %s>reset"%("checked=checked" if data['shutdown'] == 2 else ""))
 aWeb.wr("</DIV>")
 aWeb.wr("<LABEL FOR='info'>Info:</LABEL><INPUT TYPE=TEXT ID='info' NAME='info' STYLE='min-width:200px;' VALUE='%s'>"%(data['info']))
 aWeb.wr("</DIV>")
 aWeb.wr("</FORM>")
 aWeb.wr(aWeb.button('save', DIV='div_content_right', URL='reservations_info?op=update', FRM='reservations_info_form'))
 aWeb.wr("</ARTICLE>")

#
#
def report(aWeb):
 reservations = aWeb.rest_call("reservation/list",{'extended':True})['data']
 aWeb.wr("<ARTICLE><P>Reservations</P>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV>User</DIV><DIV>Device</DIV><DIV>Start</DIV><DIV>End</DIV><DIV>Info</DIV></DIV><DIV CLASS=tbody>")
 for res in reservations:
  aWeb.wr("<DIV><DIV>%(alias)s</DIV><DIV>%(hostname)s</DIV><DIV>%(start)s</DIV><DIV>%(end)s</DIV><DIV>%(info)s</DIV></DIV>"%res)
 aWeb.wr("</DIV></DIV></ARTICLE>")
