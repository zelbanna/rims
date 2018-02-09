"""Module docstring.

HTML5 Ajax SDCP generic module

"""
__author__= "Zacharias El Banna"
__version__ = "18.02.09GA"
__status__= "Production"

#
# Generic Login
#
def login(aWeb):
 application = aWeb.get('application','sdcp')
 cookie = aWeb.cookie_unjar(application)
 if len(cookie) > 0:
  aWeb.put_redirect("sdcp.cgi?call=%s_portal"%application)
  return
 
 data = aWeb.rest_call("%s_application"%(application),aWeb.get_args2dict(['call','header']))
 aWeb.cookie_add(application,data['cookie'])
 aWeb.put_html(data['title'])
 taborder = 2
 print "<DIV CLASS='grey overlay'><ARTICLE CLASS='login'><H1 CLASS='centered'>%s</H1>"%data['message']
 if data.get('exception'):
  print "Error retrieving applicaiton info - exception info: %s"%(data['exception'])
 else:
  print "<FORM ACTION=sdcp.cgi METHOD=POST ID=login_form>"
  print "<INPUT TYPE=HIDDEN NAME=call VALUE='%s'>"%data['portal']
  print "<INPUT TYPE=HIDDEN NAME=headers VALUE=no>"
  print "<INPUT TYPE=HIDDEN NAME=title VALUE='%s'>"%data['title']
  print "<DIV CLASS=table STYLE='display:inline; float:left; margin:0px 0px 0px 30px; width:auto;'><DIV CLASS=tbody>"
  for choice in data.get('choices'):
   print "<DIV CLASS=tr><DIV CLASS=td>%s:</DIV><DIV CLASS=td><SELECT NAME='%s' TABORDER=%s>"%(choice['display'],choice['id'],taborder)
   taborder +=1
   for row in choice['data']:
    print "<OPTION VALUE='%s'>%s</OPTION>"%(row['id'],row['name'])
   print "</SELECT></DIV></DIV>"
  for param in data.get('parameters'):
   print "<DIV CLASS=tr><DIV CLASS=td>%s:</DIV><DIV CLASS=td><INPUT TYPE=%s NAME='%s' TABORDER=%s></DIV></DIV>"%(param['display'],param['data'],param['id'],taborder)
   taborder +=1
  print "</DIV></DIV>"
  print "</FORM><DIV CLASS=controls>"
  print "<BUTTON CLASS=z-op OP=submit STYLE='margin:20px 20px 30px 40px;' FRM=login_form TABORDER=1 TYPE=submit>Enter</BUTTON>"
 print "</DIV></ARTICLE></DIV>"

############################################## SDCP ###############################################
#
#
# Base SDCP Portal, creates DIVs for layout
#
def portal(aWeb):
 cookie = aWeb.cookie_unjar('sdcp')
 if cookie.get('id',None) is None:
  id,user = aWeb.get('sdcp_login',"None_None").split('_')
  if id == "None":
   aWeb.put_redirect("index.cgi")
   return   
  cookie.update({'id':id})
  aWeb.cookie_jar('sdcp',cookie, 86400)
  aWeb.log("Entering as {}-'{}'".format(id,user))
 else:
  id = cookie.get('id')

 menu = aWeb.rest_call("users_menu",{"id":id})
 aWeb.put_html(aWeb.get('title','Portal'))
 print "<HEADER CLASS='background'>"
 for item in menu:
  if item['inline'] == 0:
   print "<FORM><BUTTON CLASS='menu' TITLE='%s' TYPE='submit' FORMTARGET=_blank FORMMETHOD=post FORMACTION='%s'><IMG SRC='%s'/></BUTTON></FORM>"%(item['title'],item['href'],item['icon'])
  else:
   print "<BUTTON CLASS='z-op menu' TITLE='%s' DIV=main URL='%s'><IMG SRC='%s'/></BUTTON>"%(item['title'],item['href'],item['icon'])
 print "<BUTTON CLASS='z-op menu right warning' OP=logout URL=sdcp.cgi>Log out</BUTTON>"
 print "<BUTTON CLASS='z-op menu right' DIV=main TITLE='User info' URL=sdcp.cgi?call=users_user&id=%s><IMG SRC='images/icon-users.png'></BUTTON>"%id
 print "</HEADER>"
 print "<MAIN CLASS='background' ID=main></MAIN>"

##################################################################################################
#
# Weathermap
#
def weathermap(aWeb):
 if aWeb.get('headers','no') == 'no':
  aWeb.put_html("Weathermap")
 else:
  print "Content-Type: text/html\r\n"
 if not aWeb['page']:
  wms = aWeb.rest_call("settings_list",{'section':'weathermap'})['data']
  print "<NAV><UL>" 
  for map in wms:
   print "<LI><A CLASS=z-op OP=iload IFRAME=iframe_wm_cont URL=sdcp.cgi?call=sdcp_weathermap&page={0}>{1}</A></LI>".format(map['parameter'],map['value'])
  print "</UL></NAV>"
  print "<SECTION CLASS='content background' ID='div_wm_content' NAME='Weathermap Content' STYLE='overflow:hidden;'>"
  print "<IFRAME ID=iframe_wm_cont src=''></IFRAME>"
  print "</SECTION>" 
 else:
  from ..core.extras import get_include
  print "<SECTION CLASS='content background' STYLE='top:0px;'>"
  print "<ARTICLE>"
  print get_include('%s.html'%aWeb['page'])
  print "</ARTICLE>"
  print "</SECTION>"
