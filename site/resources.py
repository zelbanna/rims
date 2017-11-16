"""Module docstring.

Ajax resources calls module

"""
__author__= "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__= "Production"

from sdcp.core.dbase import DB

############################################ resources ##############################################
#
def navigate(aWeb):
 if not aWeb.cookie.get('sdcp_id'):
  print "<SCRIPT>location.replace('index.cgi')</SCRIPT>"
  return
 print "<nav>&nbsp;</nav>"
 print "<DIV CLASS=z-content ID=div_content>"
 view(aWeb)
 print "</DIV>"

#
#
#
def list(aWeb):
 with DB() as db:
  res  = db.do("SELECT id, title, href, type, inline, user_id FROM resources WHERE (user_id = '{}' {}) ORDER BY type,title".format(aWeb.cookie['sdcp_id'],'' if aWeb.cookie['sdcp_view'] == '0' else 'OR private = 0'))
  rows = db.get_rows()
 print "<DIV CLASS=z-content-left ID=div_content_left>"
 print "<DIV CLASS=z-frame><DIV CLASS=title>Resources</DIV>"
 print aWeb.button('reload',DIV='div_content', URL='sdcp.cgi?call=resources_list')
 print aWeb.button('add', DIV='div_content_right', URL='sdcp.cgi?call=resources_info&id=new')
 print "<DIV CLASS=z-table><DIV CLASS=thead><DIV CLASS=th>Type</DIV><DIV CLASS=th>Title</DIV><DIV CLASS=th>&nbsp;</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for row in rows:
  print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><DIV CLASS=td><A TITLE='{}' ".format(row['type'],row['title'])
  if row['inline'] == 0:
   print "TARGET=_blank HREF='{}'>".format(row['href'])
  else:
   print "CLASS=z-op DIV=main URL='{}'>".format(row['href'])
  print "{}</A></DIV><DIV CLASS=td>&nbsp;".format(row['title'])
  print aWeb.button('info', DIV='div_content_right', URL='sdcp.cgi?call=resources_info&id=%i'%row['id'])
  if aWeb.cookie['sdcp_id'] == str(row['user_id']):
   print aWeb.button('delete', DIV='div_content_right', URL='sdcp.cgi?call=resources_delete&id=%i'%row['id'], MSG='Delete resource?')
  print "</DIV></DIV>"
 print "</DIV></DIV></DIV></DIV>"
 print "<DIV CLASS=z-content-right ID=div_content_right>"

#
#
#
def info(aWeb):
 from os import listdir, path
 data  = {}
 data['id'] = aWeb.get('id','new')
 if aWeb['op'] == 'update' or data['id'] == 'new':
  data['title'] = aWeb.get('title',"unknown")
  data['href']  = aWeb.get('href',"unknown")
  data['type']  = aWeb['type']
  data['icon']  = aWeb['icon']
  data['inline']  = aWeb.get('inline',"0")
  data['private'] = aWeb.get('private',"0")
  data['user_id'] = aWeb.get('user_id',aWeb.cookie['sdcp_id'])
  if aWeb['op'] == 'update':
   with DB() as db:
    if data['id'] == 'new':
     db.do("INSERT INTO resources (title,href,icon,type,inline,private,user_id) VALUES ('{}','{}','{}','{}','{}','{}','{}')".format(data['title'],data['href'],data['icon'],data['type'],data['inline'],data['private'],data['user_id']))
     data['id']  = db.get_last_id()
    else:
     db.do("UPDATE resources SET title='{}',href='{}',icon='{}', type='{}', inline='{}', private='{}' WHERE id = '{}'".format(data['title'],data['href'],data['icon'],data['type'],data['inline'],data['private'],data['id']))
 else:
  with DB() as db:
   db.do("SELECT id,title,href,icon,type,inline,private,user_id FROM resources WHERE id = '{}'".format(data['id']))
   data = db.get_row()

 print "<DIV CLASS=z-frame>"
 print "<DIV CLASS=title>Resource entity ({})</DIV>".format(data['id'])
 print "<FORM ID=sdcp_resource_info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(data['id'])
 print "<INPUT TYPE=HIDDEN NAME=user_id VALUE={}>".format(data['user_id'])
 print "<DIV CLASS=z-table style='float:left; width:auto;'><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Title:</DIV><DIV    CLASS=td><INPUT NAME=title STYLE='min-width:400px' TYPE=TEXT VALUE='{}'></DIV></DIV>".format(data['title'])
 print "<DIV CLASS=tr><DIV CLASS=td>HREF:</DIV><DIV     CLASS=td><INPUT NAME=href  STYLE='min-width:400px' TYPE=TEXT VALUE='{}'></DIV></DIV>".format(data['href'])
 print "<DIV CLASS=tr><DIV CLASS=td>Icon URL:</DIV><DIV CLASS=td><INPUT NAME=icon  STYLE='min-width:400px' TYPE=TEXT VALUE='{}'></DIV></DIV>".format(data['icon'])
 print "<DIV CLASS=tr><DIV CLASS=td>Inline:</DIV><DIV   CLASS=td><INPUT NAME=inline  {}                TYPE=CHECKBOX VALUE=1   ></DIV></DIV>".format("checked=checked" if data['inline'] == 1 or data['inline'] == "1" else '')
 print "<DIV CLASS=tr><DIV CLASS=td>Private:</DIV><DIV  CLASS=td><INPUT NAME=private {} {}             TYPE=CHECKBOX VALUE=1   ></DIV></DIV>".format("checked=checked" if data['private'] == 1 or data['private'] == "1" else "","disabled" if aWeb.cookie['sdcp_id'] <> str(data['user_id']) else "")
 print "<DIV CLASS=tr><DIV CLASS=td>Type:</DIV><DIV     CLASS=td><SELECT NAME=type STYLE='min-width:400px'>"
 for tp in ['bookmark','demo','tool']:
  print "<OPTION VALUE={} {}>{}</OPTION>".format(tp,"" if data['type'] != tp else 'selected',tp.title())
 print "</SELECT></DIV></DIV>"
 print "</DIV></DIV>"
 print "</FORM>"
 if data['icon'] and data['icon'] != 'NULL':
  print "<A CLASS='z-btn z-menu-btn' style='float:left; min-width:52px; font-size:10px; cursor:default;'><IMG ALT={0} SRC='{0}'></A>".format(data['icon'])
 print "<BR style='clear:left'>"
 if data['id'] != 'new':
  print aWeb.button('delete', DIV='div_content_right', URL='sdcp.cgi?call=resources_delete&id=%s'%data['id'], MSG='Delete resource?')
 print aWeb.button('save',    DIV='div_content_right', URL='sdcp.cgi?call=resources_info&op=update', FRM='sdcp_resource_info_form')
 print "</DIV>"

#
#
#
def view(aWeb):
 with DB() as db:
  db.do("SELECT title,href,icon,inline FROM resources WHERE type = '{}' AND ( user_id = {} {} ) ORDER BY title".format(aWeb['type'],aWeb.cookie['sdcp_id'],'' if aWeb.cookie.get('sdcp_view') == '0' else "OR private = 0"))
  rows = db.get_rows()
 index = 0;
 print "<DIV CLASS=z-centered style='align-items:initial'>"
 for row in rows:
  print "<DIV style='float:left; min-width:100px; margin:6px;'><A STYLE='font-size:10px;' TITLE='{}'".format(row['title'])
  if row['inline'] == 0:
   print "CLASS='z-btn z-menu-btn' TARGET=_blank HREF='{}'>".format(row['href'])
  else:
   print "CLASS='z-op z-btn z-menu-btn' DIV=main URL='{}'>".format(row['href'])
  print "<IMG ALT='{0}' SRC='{0}'></A>".format(row['icon'])
  print "</A><BR><SPAN style='width:100px; display:block;'>{}</SPAN>".format(row['title'])
  print "</DIV>"
 print "</DIV>"

#
#
#
def delete(aWeb):
 with DB() as db:
  id = aWeb['id']
  res = db.do("DELETE FROM resources WHERE id = '{}'".format(id))
 print "<DIV CLASS=z-frame>Result: {}</DIV>".format("OK" if res == 1 else "Not OK:{}".format(res))
