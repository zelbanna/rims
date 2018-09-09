"""Module docstring.

HTML5 Ajax resources module

"""
__author__= "Zacharias El Banna"
__version__ = "1.0GA"
__status__ = "Production"
__icon__ = '../images/icon-tools.png'
__type__ = 'menuitem'

############################################ Resources ##############################################
#
# Necessary
def main(aWeb):
 if not aWeb.cookie('system'):
  aWeb.wr("<SCRIPT>location.replace('system_login')</SCRIPT>")
  return
 aWeb.wr("<NAV><UL>")
 aWeb.wr("<LI CLASS='right dropdown'><A>Resources</A><DIV CLASS='dropdown-content'>")
 aWeb.wr("<A CLASS=z-op DIV=div_content URL='resources_view?type=bookmark'>Bookmarks</A>")
 aWeb.wr("<A CLASS=z-op DIV=div_content URL='resources_view?type=menuitem'>Menuitems</A>")
 aWeb.wr("<A CLASS=z-op DIV=div_content URL='resources_view?type=tool'>Tools</A>")
 aWeb.wr("</DIV></LI>")
 aWeb.wr("</UL></NAV><SECTION CLASS=content ID=div_content>")
 view(aWeb)
 aWeb.wr("</SECTION>")

#
#
def view(aWeb):
 cookie = aWeb.cookie('system')
 res = aWeb.rest_call("system_resources_list",{'type':aWeb.get('type','tool'),'user_id':cookie['id'],'node':aWeb.get('node',aWeb.node())})
 inline = "<BUTTON CLASS='z-op menu' DIV=main URL='{0}' STYLE='font-size:10px;' TITLE='{1}'><IMG ALT='{2}' SRC='{2}' /></BUTTON>"
 framed = "<BUTTON CLASS='z-op menu' DIV=main URL='resources_framed?id={0}' STYLE='font-size:10px;' TITLE='{1}'><IMG ALT='{2}' SRC='{2}' /></BUTTON>"
 tabbed = "<A CLASS='btn menu' TARGET=_blank HREF='{0}' STYLE='font-size:10px;' TITLE='{1}'><IMG ALT='{2}' SRC='{2}' /></A>"
 aWeb.wr("<DIV CLASS=centered STYLE='align-items:initial'>")
 for row in res['data']:
  aWeb.wr("<DIV STYLE='float:left; min-width:100px; margin:6px;'>")
  if row['view'] == 0:
   aWeb.wr(inline.format(row['href'],row['title'],row['icon']))
  elif row['view'] == 1:
   aWeb.wr(framed.format(row['id'],row['title'],row['icon']))
  else:
   aWeb.wr(tabbed.format(row['href'],row['title'],row['icon']))
  aWeb.wr("<BR><SPAN STYLE='width:100px; display:block;'>{}</SPAN>".format(row['title']))
  aWeb.wr("</DIV>")
 aWeb.wr("</DIV>")

#
#
def framed(aWeb):
 res = aWeb.rest_call("system_resources_info",{'id':aWeb['id']})
 aWeb.wr("<IFRAME ID=system_resource_frame NAME=system_resource_frame SRC='%s'></IFRAME>"%res['data']['href'])

#
#
def list(aWeb):
 if not aWeb.cookie('system'):
  aWeb.wr("<SCRIPT>location.replace('system_login')</SCRIPT>")
  return
 cookie = aWeb.cookie('system')
 node = aWeb.get('node',aWeb.node())
 res = aWeb.rest_call("system_resources_list",{'node':node,'user_id':cookie['id']})
 aWeb.wr("<SECTION CLASS=content-left ID=div_content_left>")
 aWeb.wr("<ARTICLE><P>Resources</P><DIV CLASS=controls>")
 aWeb.wr(aWeb.button('reload',DIV='div_content', URL='resources_list?node=%s'%node))
 aWeb.wr(aWeb.button('back',DIV='div_content', URL='system_node_list'))
 aWeb.wr(aWeb.button('add', DIV='div_content_right', URL='resources_info?node=%s&id=new&user_id=%s'%(node,cookie['id'])))
 aWeb.wr(aWeb.button('help',DIV='div_content_right', URL='resources_help', TITLE='Help information'))
 aWeb.wr("</DIV><DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Type</DIV><DIV CLASS=th>Title</DIV><DIV CLASS=th>&nbsp;</DIV></DIV>")
 aWeb.wr("<DIV CLASS=tbody>")
 for row in res['data']:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content URL='resources_view?type=%s&node=%s'>%s</A></DIV><DIV CLASS=td><A TITLE='%s' "%(row['type'],node,row['type'],row['title']))
  if   row['view'] == 0:
   aWeb.wr("CLASS=z-op DIV=main URL='{}'>".format(row['href']))
  elif row['view'] == 1:
   aWeb.wr("CLASS=z-op DIV=main URL='resources_framed?id=%s'>"%row['id'])
  else:
   aWeb.wr("TARGET=_blank HREF='{}'>".format(row['href']))
  aWeb.wr("{}</A></DIV><DIV CLASS=td><DIV CLASS=controls>".format(row['title']))
  aWeb.wr(aWeb.button('info', DIV='div_content_right', URL='resources_info?id=%i'%(row['id']), TITLE=row['id']))
  if cookie['id'] == str(row['user_id']):
   aWeb.wr(aWeb.button('delete', DIV='div_content_right', URL='resources_delete?id=%i'%row['id'], MSG='Delete resource?'))
  aWeb.wr("</DIV></DIV></DIV>")
 aWeb.wr("</DIV></DIV></ARTICLE></SECTION>")
 aWeb.wr("<SECTION CLASS=content-right ID=div_content_right></SECTION>")

#
#
def info(aWeb):
 cookie = aWeb.cookie('system')
 args = aWeb.args()
 data = aWeb.rest_call("system_resources_info",args)['data']
 aWeb.wr("<ARTICLE><P>Resource entity ({})</P>".format(data['id']))
 aWeb.wr("<FORM ID=resource_info_form>")
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=node VALUE={}>".format(data['node']))
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=id   VALUE={}>".format(data['id']))
 aWeb.wr("<INPUT TYPE=HIDDEN NAME=user_id VALUE={}>".format(data['user_id']))
 aWeb.wr("<DIV CLASS=table STYLE='float:left; width:auto;'><DIV CLASS=tbody>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Title:</DIV><DIV    CLASS=td><INPUT NAME=title TYPE=TEXT VALUE='%s' REQUIRED STYLE='min-width:400px'></DIV></DIV>"%data['title'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>HREF:</DIV><DIV     CLASS=td><INPUT NAME=href  TYPE=URL  VALUE='%s' REQUIRED></DIV></DIV>"%data['href'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Icon URL:</DIV><DIV CLASS=td><INPUT NAME=icon  TYPE=URL  VALUE='%s'></DIV></DIV>"%data['icon'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>View:</DIV><DIV     CLASS=td>")
 for name,view in [('inline','0'),('framed','1'),('new tab','2')]:
  aWeb.wr("<INPUT NAME=view TYPE=RADIO VALUE=%s %s>%s"%(view,"checked" if str(data['view']) == view else "",name))
 aWeb.wr(" </DIV></DIV>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Private:</DIV><DIV  CLASS=td><INPUT NAME=private {} {}             TYPE=CHECKBOX VALUE=1   ></DIV></DIV>".format("checked=checked" if data['private'] == 1 or data['private'] == "1" else "","disabled" if cookie['id'] != str(data['user_id']) else ""))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Type:</DIV>")
 if data['type'] == 'menuitem' and cookie['id'] != str(data['user_id']):
  aWeb.wr("<DIV CLASS=td><INPUT  NAME=type TYPE=TEXT VALUE='menuitem' STYLE='font-style:italic' readonly></DIV>")
 else:
  aWeb.wr("<DIV CLASS=td><SELECT NAME=type>")
  for tp in ['bookmark','demo','tool','menuitem']:
   aWeb.wr("<OPTION VALUE={} {}>{}</OPTION>".format(tp,"" if data['type'] != tp else 'selected',tp.title()))
  aWeb.wr("</SELECT></DIV>")
 aWeb.wr("</DIV></DIV></DIV>")
 if data['icon'] and data['icon'] != 'NULL':
  aWeb.wr("<BUTTON CLASS='menu' TYPE=button STYLE='float:left; min-width:52px; font-size:10px; cursor:default;'><IMG ALT={0} SRC='{0}' /></BUTTON>".format(data['icon']))
 aWeb.wr("</FORM><BR><DIV CLASS=controls>")
 if cookie['id'] == str(data['user_id']):
  aWeb.wr(aWeb.button('save',    DIV='div_content_right', URL='resources_info?op=update', FRM='resource_info_form', TITLE='Save'))
  if data['id'] != 'new':
   aWeb.wr(aWeb.button('delete', DIV='div_content_right', URL='resources_delete?id=%s'%data['id'], MSG='Delete resource?'))
 aWeb.wr("</DIV></ARTICLE>")

#
#
def delete(aWeb):
 res = aWeb.rest_call("system_resources_delete",{'id':aWeb['id']})
 aWeb.wr("<ARTICLE>Result: %s</ARTICLE>"%(res))

#
#
def help(aWeb):
 aWeb.wr("""<ARTICLE><PRE>
 Resources offers advanced bookmarking functions.

 There are four types of resources:
  - menuitem. Typically generated directly by system
  - bookmark. Generic bookmarks created by users
  - tool. Special bookmarks for external tools
  - demo. Special bookmark used for demo purposes

  All resources are viewed as either:
  - inline (integrated with the CSS system and interactive buttons)
  - framed (looks like inline but a separate frame)
  - tabbed (opens up a new tab when clicked)

  All resources have:
  - A URL that is opened when button is clicked
  - An icon that is shown with menu button properties (size, shadow etc)
  - View
  - private (to the user creating the resource)
 </PRE></ARTICLE""")
