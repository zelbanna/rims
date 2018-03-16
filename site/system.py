"""Module docstring.

HTML5 Ajax SDCP generic module

"""
__author__= "Zacharias El Banna"
__version__ = "18.03.16GA"
__status__= "Production"

#
# Generic Login - REST based apps required
#
def login(aWeb):
 application = aWeb.get('application','system')
 cookie = aWeb.cookie_unjar(application)
 inline = aWeb.get('inline','no')
 if cookie.get('authenticated') == 'OK' and inline == 'no':
  aWeb.put_redirect("sdcp.cgi?call=%s_portal"%application)
  return

 args = aWeb.get_args2dict(['call'])
 args['node'] = aWeb.id
 data = aWeb.rest_call("%s_application"%(application),args)
 if inline == 'no':
  aWeb.put_html(data['title'])
 aWeb.put_cookie(application,data['cookie'],data['expires'])
 print "<DIV CLASS='grey overlay'><ARTICLE CLASS='login'><H1 CLASS='centered'>%s</H1>"%data['message']
 if data.get('exception'):
  print "Error retrieving application info - exception info: %s"%(data['exception'])
 else:
  print "<FORM ACTION=sdcp.cgi METHOD=POST ID=login_form>"
  print "<INPUT TYPE=HIDDEN NAME=call VALUE='%s_%s'>"%(application,"portal" if inline=='no' else 'inline')
  print "<INPUT TYPE=HIDDEN NAME=title VALUE='%s'>"%data['title']
  print "<DIV CLASS=table STYLE='display:inline; float:left; margin:0px 0px 0px 30px; width:auto;'><DIV CLASS=tbody>"
  for choice in data.get('choices'):
   print "<DIV CLASS=tr><DIV CLASS=td>%s:</DIV><DIV CLASS=td><SELECT NAME='%s'>"%(choice['display'],choice['id'])
   for row in choice['data']:
    print "<OPTION VALUE='%s'>%s</OPTION>"%(row['id'],row['name'])
   print "</SELECT></DIV></DIV>"
  for param in data.get('parameters'):
   print "<DIV CLASS=tr><DIV CLASS=td>%s:</DIV><DIV CLASS=td><INPUT TYPE=%s NAME='%s'></DIV></DIV>"%(param['display'],param['data'],param['id'])
  print "</DIV></DIV>"
  print "</FORM><DIV CLASS=controls>"
  print "<BUTTON CLASS=z-op %s STYLE='margin:20px 20px 30px 40px;' FRM=login_form>Enter</BUTTON>"%("OP=submit" if not aWeb['inline'] == 'yes' else "DIV=main URL=sdcp.cgi")
 print "</DIV></ARTICLE></DIV>"

############################################## SDCP ###############################################
#
#
# Base SDCP Portal, creates DIVs for layout
#
def portal(aWeb):
 cookie = aWeb.cookie_unjar('system')
 aWeb.put_html(aWeb.get('title','Portal'))
 if cookie.get('id') is None:
  id,username = aWeb.get('system_login',"None_None").split('_')
  res = aWeb.rest_call("system_authenticate",{'id':id,'username':username})
  if not res['authenticated'] == "OK":
   aWeb.put_redirect("index.cgi")
   return
  cookie.update({'id':id,'authenticated':'OK'})
  aWeb.put_cookie('system',cookie,res['expires'])
  aWeb.log("Entering as {}-'{}'".format(id,username))
 else:
  id = cookie.get('id')

 menu = aWeb.rest_call("users_menu",{"id":id,'node':aWeb.id})

 print "<HEADER CLASS='background'>"
 for item in menu['menu']:
  if item['inline'] == 0:
   print "<A CLASS='btn menu' TITLE='%s' TARGET=_blank HREF='%s'><IMG SRC='%s'/></A>"%(item['title'],item['href'],item['icon'])
  else:
   print "<BUTTON CLASS='z-op menu' TITLE='%s' DIV=main URL='%s'><IMG SRC='%s'/></BUTTON>"%(item['title'],item['href'],item['icon'])
 print "<BUTTON CLASS='z-op menu right warning' OP=logout COOKIE=system URL=sdcp.cgi>Log out</BUTTON>"
 print "<BUTTON CLASS='z-op menu right' TITLE='Tools' DIV=main URL='sdcp.cgi?call=tools_main&node=%s'><IMG SRC='images/icon-config'/></BUTTON>"%aWeb.id
 print "<BUTTON CLASS='z-op menu right' TITLE='User'  DIV=main URL='sdcp.cgi?call=users_%s'><IMG SRC='images/icon-users.png'></BUTTON>"%("main" if id == '1' else "user&id=%s"%id)
 print "</HEADER>"
 print "<MAIN CLASS='background' ID=main></MAIN>"
 print "<SCRIPT>include_html('main','%s')</SCRIPT>"%menu['start']

#
#
def node_list(aWeb):
 nodes = aWeb.rest_call("system_node_list")['data']
 print "<SECTION CLASS=content-left ID=div_content_left>"
 print "<ARTICLE><P>Nodes</P><DIV CLASS=controls>"
 print aWeb.button('reload',DIV='div_content', URL='sdcp.cgi?call=system_node_list')
 print aWeb.button('add', DIV='div_content_right', URL='sdcp.cgi?call=system_node_info&id=new')
 print "</DIV><DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Node</DIV><DIV CLASS=th>URL</DIV><DIV CLASS=th>&nbsp;</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for row in nodes:
  print "<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td STYLE='max-width:190px; overflow-x:hidden'>%s</DIV><DIV CLASS=td>"%(row['node'],row['url'])
  print aWeb.button('info',DIV='div_content_right', URL='sdcp.cgi?call=system_node_info&id=%s'%row['id'])
  if row['system']:
   print aWeb.button('document',DIV='div_content', URL='sdcp.cgi?call=settings_list&node=%s'%row['node']) 
  print "</DIV></DIV>"
 print "</DIV></DIV></ARTICLE></SECTION>"
 print "<SECTION CLASS=content-right ID=div_content_right></SECTION>"

#
#
def node_info(aWeb):
 data = {'id':aWeb.get('id','new')}
 if aWeb['op'] == 'update' or aWeb['id'] == 'new':
  data['op']   = aWeb['op']
  data['node'] = aWeb.get('node','Not set')
  data['url']  = aWeb.get('url','Not set')
  if aWeb['op'] == 'update':
   data = aWeb.rest_call("system_node_info",data)['data']
 else:
  data = aWeb.rest_call("system_node_info",data)['data']
 print "<ARTICLE CLASS='info'><P>Node Info</DIV>"
 print "<FORM ID=system_node_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE='%s'>"%(aWeb['id'])
 print "<DIV CLASS=table STYLE='width:auto'><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Node:</DIV><DIV CLASS=td><INPUT TYPE=TEXT NAME=node STYLE='min-width:200px;' VALUE='%s'></DIV></DIV>"%(data['node'])
 print "<DIV CLASS=tr><DIV CLASS=td>URL:</DIV><DIV CLASS=td><INPUT  TYPE=TEXT NAME=url  STYLE='min-width:200px;' VALUE='%s'></DIV></DIV>"%(data['url'])
 print "</DIV></DIV>"
 print "<SPAN></SPAN>"
 print "</FORM><DIV CLASS=controls>"
 if str(data.get('system','0')) == '0':
  print aWeb.button('save',   DIV='div_content_right', URL='sdcp.cgi?call=system_node_info&op=update', FRM='system_node_form')
  print aWeb.button('delete', DIV='div_content_right', URL='sdcp.cgi?call=system_node_delete', FRM='system_node_form')
 print "</DIV></ARTICLE>"

#
#
def node_delete(aWeb):
 res = aWeb.rest_call("system_node_delete",{'id':aWeb['id']})
 print "<ARTICLE>Result: %s</ARTICLE>"%(res)

##################################################################################################
#
# Weathermap
#
def weathermap(aWeb):
 aWeb.put_html("Weathermap")
 if not aWeb['page']:
  wms = aWeb.rest_call("settings_list",{'section':'weathermap'})['data']
  print "<NAV><UL>"
  for map in wms:
   print "<LI><A CLASS=z-op OP=iload IFRAME=iframe_wm_cont URL=sdcp.cgi?call=system_weathermap&page={0}>{1}</A></LI>".format(map['parameter'],map['value'])
  print "</UL></NAV>"
  print "<SECTION CLASS='content background' ID='div_wm_content' NAME='Weathermap Content' STYLE='overflow:hidden;'>"
  print "<IFRAME ID=iframe_wm_cont src=''></IFRAME>"
  print "</SECTION>"
 else:
  print "<SECTION CLASS='content background' STYLE='top:0px;'>"
  print "<ARTICLE ID='including'>"
  print "<SCRIPT>include_html('including','%s.html');</SCRIPT>"%aWeb['page']
  print "</ARTICLE>"
  print "</SECTION>"
