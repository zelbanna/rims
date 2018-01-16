"""Module docstring.

HTML5 Front-End(s)

"""
__author__= "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__= "Production"

#################################################################################################################
#
# Login
#
# - Log in to "application" (default to:'sdcp') and redirect to application cookies portal
#
def login(aWeb):
 application = aWeb.get('application','sdcp')
 cookie = aWeb.cookie_unjar(application)
 if len(cookie) > 0 and cookie.get('portal',False):
  aWeb.put_redirect("sdcp.cgi?call=%s&headers=no"%cookie['portal'])
  return

 from .. import PackageContainer as PC
 data = aWeb.rest_call(PC.generic['url'],"sdcp.rest.sdcp_application",{'app':application,'args':aWeb.get_args2dict_except(['call','header'])})['data']
 aWeb.cookie_add(application,data['cookie'])
 aWeb.put_html(data['name'])
 print "<DIV CLASS='grey overlay'>"
 print "<!-- %s -->"%(aWeb.get_args2dict_except(['call','header']))
 print "<ARTICLE CLASS='login'>"
 print "<H1 CLASS='centered'>%s</H1>"%data['message']
 print "<FORM ACTION=sdcp.cgi METHOD=POST ID=login_form>"
 print "<INPUT TYPE=HIDDEN NAME=call VALUE='%s'>"%data['portal']
 print "<INPUT TYPE=HIDDEN NAME=headers VALUE=no>"
 print "<DIV CLASS=table STYLE='display:inline; float:left; margin:0px 0px 0px 30px; width:auto;'><DIV CLASS=tbody>"
 for choice in data.get('choices'):
  print "<DIV CLASS=tr><DIV CLASS=td>%s:</DIV><DIV CLASS=td><SELECT NAME='%s'>"%(choice['display'],choice['id'])
  for row in choice['data']:
   print "<OPTION VALUE='%s'>%s</OPTION>"%(row['id'],row['name'])
  print "</SELECT></DIV></DIV>"
 for param in data.get('parameters'):
  print "<DIV CLASS=tr><DIV CLASS=td>%s:</DIV><DIV CLASS=td><INPUT TYPE=%s NAME='%s'></DIV></DIV>"%(param['display'],param['data'],param['id'])
 print "</DIV></DIV>"
 print "<A CLASS='btn z-op' OP=submit STYLE='margin:20px 20px 30px 40px;' FRM=login_form>Enter</A>"
 print "</FORM>"
 print "</ARTICLE></DIV>"

##################################################################################################
#
# Weathermap
#
def weathermap(aWeb):
 from .. import PackageContainer as PC
 if aWeb.get('headers','no') == 'no':
  aWeb.put_html("Weathermap")
 else:
  print "Content-Type: text/html\r\n"

 page = aWeb['page']
 if not page:
  print "<NAV><UL>" 
  for map,entry in PC.weathermap.iteritems():
   print "<LI><A CLASS=z-op OP=iload IFRAME=iframe_wm_cont URL=sdcp.cgi?call=front_weathermap&page={0}>{1}</A></LI>".format(map,entry['name'])
  print "</UL></NAV>"
  print "<SECTION CLASS='content' ID='div_wm_content' NAME='Weathermap Content' STYLE='overflow:hidden;'>"
  print "<IFRAME ID=iframe_wm_cont src=''></IFRAME>"
  print "</SECTION>" 
 else:
  from ..core.extras import get_include
  entry  = PC.weathermap[page]
  graphs = entry.get('graphs')
  print "<SECTION CLASS=content STYLE='top:0px;'>"
  if graphs:
   from ..tools.munin import widget_rows
   print "<SECTION CLASS=content-left STYLE='width:420px'><ARTICLE>"
   widget_rows(graphs)
   print "</ARTICLE></SECTION><SECTION CLASS=content-right STYLE='left:420px'>"
   print "<ARTICLE>"
   print get_include('%s.html'%page)
   print "</ARTICLE>"
   print "</SECTION>"
  else:
   print "<SECTION CLASS=content STYLE='top:0px;'>"
   print "<ARTICLE>"
   print get_include('%s.html'%page)
   print "</ARTICLE>"
  print "</SECTION>"

