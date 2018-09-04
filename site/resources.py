"""Module docstring.

HTML5 Ajax resources module

"""
__author__= "Zacharias El Banna"
__version__ = "1.0GA"
__status__ = "Production"
__icon__ = 'images/icon-tools.png'
__type__ = 'menuitem'

############################################ Resources ##############################################
#
# Necessary
def main(aWeb):
 if not aWeb.cookies.get('system'):
  print "<SCRIPT>location.replace('index.cgi')</SCRIPT>"
  return
 print "<NAV><UL>"
 print "<LI CLASS='right dropdown'><A>Resources</A><DIV CLASS='dropdown-content'>"
 print "<A CLASS=z-op DIV=div_content URL='zdcp.cgi?resources_view&type=bookmark'>Bookmarks</A>"
 print "<A CLASS=z-op DIV=div_content URL='zdcp.cgi?resources_view&type=menuitem'>Menuitems</A>"
 print "<A CLASS=z-op DIV=div_content URL='zdcp.cgi?resources_view&type=tool'>Tools</A>"
 print "</DIV></LI>"
 print "</UL></NAV><SECTION CLASS=content ID=div_content>"
 view(aWeb)
 print "</SECTION>"

#
#
def view(aWeb):
 cookie = aWeb.cookie_unjar('system')
 res = aWeb.rest_call("system_resources_list",{'type':aWeb.get('type','tool'),'user_id':cookie['id'],'node':aWeb.get('node',aWeb.id)})
 inline = "<BUTTON CLASS='z-op menu' DIV=main URL='{0}' STYLE='font-size:10px;' TITLE='{1}'><IMG ALT='{2}' SRC='{2}' /></BUTTON>"
 framed = "<BUTTON CLASS='z-op menu' DIV=main URL='zdcp.cgi?resources_framed&id={0}' STYLE='font-size:10px;' TITLE='{1}'><IMG ALT='{2}' SRC='{2}' /></BUTTON>"
 tabbed = "<A CLASS='btn menu' TARGET=_blank HREF='{0}' STYLE='font-size:10px;' TITLE='{1}'><IMG ALT='{2}' SRC='{2}' /></A>"
 print "<DIV CLASS=centered STYLE='align-items:initial'>"
 for row in res['data']:
  print "<DIV STYLE='float:left; min-width:100px; margin:6px;'>"
  if row['view'] == 0:
   print inline.format(row['href'],row['title'],row['icon'])
  elif row['view'] == 1:
   print framed.format(row['id'],row['title'],row['icon'])
  else:
   print tabbed.format(row['href'],row['title'],row['icon'])
  print "<BR><SPAN STYLE='width:100px; display:block;'>{}</SPAN>".format(row['title'])
  print "</DIV>"
 print "</DIV>"

#
#
def framed(aWeb):
 res = aWeb.rest_call("system_resources_info",{'id':aWeb['id']})
 print "<IFRAME ID=system_resource_frame NAME=system_resource_frame SRC='%s'></IFRAME>"%res['data']['href']

#
#
def list(aWeb):
 if not aWeb.cookies.get('system'):
  print "<SCRIPT>location.replace('index.cgi')</SCRIPT>"
  return
 cookie = aWeb.cookie_unjar('system')
 node = aWeb.get('node',aWeb.id)
 res = aWeb.rest_call("system_resources_list",{'node':node,'user_id':cookie['id']})
 print "<SECTION CLASS=content-left ID=div_content_left>"
 print "<ARTICLE><P>Resources</P><DIV CLASS=controls>"
 print aWeb.button('reload',DIV='div_content', URL='zdcp.cgi?resources_list&node=%s'%node)
 print aWeb.button('back',DIV='div_content', URL='zdcp.cgi?system_node_list')
 print aWeb.button('add', DIV='div_content_right', URL='zdcp.cgi?resources_info&node=%s&id=new&user_id=%s'%(node,cookie['id']))
 print aWeb.button('help',DIV='div_content_right', URL='zdcp.cgi?resources_help', TITLE='Help information')
 print "</DIV><DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Type</DIV><DIV CLASS=th>Title</DIV><DIV CLASS=th>&nbsp;</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for row in res['data']:
  print "<DIV CLASS=tr><DIV CLASS=td><A CLASS=z-op DIV=div_content URL=zdcp.cgi?resources_view&type=%s&node=%s>%s</A></DIV><DIV CLASS=td><A TITLE='%s' "%(row['type'],node,row['type'],row['title'])
  if   row['view'] == 0:
   print "CLASS=z-op DIV=main URL='{}'>".format(row['href'])
  elif row['view'] == 1:
   print "CLASS=z-op DIV=main URL='zdcp.cgi?resources_framed&id=%s'>"%row['id']
  else:
   print "TARGET=_blank HREF='{}'>".format(row['href'])
  print "{}</A></DIV><DIV CLASS=td><DIV CLASS=controls>".format(row['title'])
  print aWeb.button('info', DIV='div_content_right', URL='zdcp.cgi?resources_info&id=%i'%(row['id']), TITLE=row['id'])
  if cookie['id'] == str(row['user_id']):
   print aWeb.button('delete', DIV='div_content_right', URL='zdcp.cgi?resources_delete&id=%i'%row['id'], MSG='Delete resource?')
  print "</DIV></DIV></DIV>"
 print "</DIV></DIV></ARTICLE></SECTION>"
 print "<SECTION CLASS=content-right ID=div_content_right></SECTION>"

#
#
def info(aWeb):
 cookie = aWeb.cookie_unjar('system')
 args = aWeb.get_args2dict()
 data = aWeb.rest_call("system_resources_info",args)['data']
 print "<ARTICLE><P>Resource entity ({})</P>".format(data['id'])
 print "<FORM ID=resource_info_form>"
 print "<INPUT TYPE=HIDDEN NAME=node VALUE={}>".format(data['node'])
 print "<INPUT TYPE=HIDDEN NAME=id   VALUE={}>".format(data['id'])
 print "<INPUT TYPE=HIDDEN NAME=user_id VALUE={}>".format(data['user_id'])
 print "<DIV CLASS=table STYLE='float:left; width:auto;'><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Title:</DIV><DIV    CLASS=td><INPUT NAME=title TYPE=TEXT VALUE='%s' REQUIRED STYLE='min-width:400px'></DIV></DIV>"%data['title']
 print "<DIV CLASS=tr><DIV CLASS=td>HREF:</DIV><DIV     CLASS=td><INPUT NAME=href  TYPE=URL  VALUE='%s' REQUIRED></DIV></DIV>"%data['href']
 print "<DIV CLASS=tr><DIV CLASS=td>Icon URL:</DIV><DIV CLASS=td><INPUT NAME=icon  TYPE=URL  VALUE='%s'></DIV></DIV>"%data['icon']
 print "<DIV CLASS=tr><DIV CLASS=td>View:</DIV><DIV     CLASS=td>"
 for name,view in [('inline','0'),('framed','1'),('new tab','2')]:
  print "<INPUT NAME=view TYPE=RADIO VALUE=%s %s>%s"%(view,"checked" if str(data['view']) == view else "",name)
 print " </DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td>Private:</DIV><DIV  CLASS=td><INPUT NAME=private {} {}             TYPE=CHECKBOX VALUE=1   ></DIV></DIV>".format("checked=checked" if data['private'] == 1 or data['private'] == "1" else "","disabled" if cookie['id'] <> str(data['user_id']) else "")
 print "<DIV CLASS=tr><DIV CLASS=td>Type:</DIV>"
 if data['type'] == 'menuitem' and cookie['id'] != str(data['user_id']):
  print "<DIV CLASS=td><INPUT  NAME=type TYPE=TEXT VALUE='menuitem' STYLE='font-style:italic' readonly></DIV>"
 else:
  print "<DIV CLASS=td><SELECT NAME=type>"
  for tp in ['bookmark','demo','tool','menuitem']:
   print "<OPTION VALUE={} {}>{}</OPTION>".format(tp,"" if data['type'] != tp else 'selected',tp.title())
  print "</SELECT></DIV>"
 print "</DIV></DIV></DIV>"
 if data['icon'] and data['icon'] != 'NULL':
  print "<BUTTON CLASS='menu' TYPE=button STYLE='float:left; min-width:52px; font-size:10px; cursor:default;'><IMG ALT={0} SRC='{0}' /></BUTTON>".format(data['icon'])
 print "</FORM><BR><DIV CLASS=controls>"
 if cookie['id'] == str(data['user_id']):
  print aWeb.button('save',    DIV='div_content_right', URL='zdcp.cgi?resources_info&op=update', FRM='resource_info_form', TITLE='Save')
  if data['id'] != 'new':
   print aWeb.button('delete', DIV='div_content_right', URL='zdcp.cgi?resources_delete&id=%s'%data['id'], MSG='Delete resource?')
 print "</DIV></ARTICLE>"

#
#
def delete(aWeb):
 res = aWeb.rest_call("system_resources_delete",{'id':aWeb['id']})
 print "<ARTICLE>Result: %s</ARTICLE>"%(res)

#
#
def help(aWeb):
 print """<ARTICLE><PRE>
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
 </PRE></ARTICLE"""
