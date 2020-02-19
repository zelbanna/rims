"""HTML5 Ajax Resources module"""
__author__= "Zacharias El Banna"

############################################ Resources ##############################################
#
# Necessary
def main(aWeb):
 aWeb.wr("<NAV><UL>")
 aWeb.wr("<LI CLASS='right dropdown'><A>Resources</A><DIV CLASS='dropdown-content'>")
 aWeb.wr("<A CLASS=z-op DIV=div_content URL='resource_view?type=menuitem'>Menuitems</A>")
 aWeb.wr("<A CLASS=z-op DIV=div_content URL='resource_view?type=tool'>Tools</A>")
 aWeb.wr("</DIV></LI>")
 aWeb.wr("</UL></NAV><SECTION CLASS=content ID=div_content>")
 view(aWeb)
 aWeb.wr("</SECTION>")

#
#
def view(aWeb):
 cookie = aWeb.cookie('rims')
 res = aWeb.rest_call("portal/resources",{'type':aWeb.get('type','tool')})
 module = "<BUTTON CLASS='z-op menu' DIV=main URL='%(module)s' STYLE='font-size:10px;' TITLE='%(title)s'><IMG ALT='%(icon)s' SRC='%(icon)s' /></BUTTON>"
 frame  = "<BUTTON CLASS='z-op menu' DIV=main URL='resource_framed?type=%(type)s&title=%(title)s' STYLE='font-size:10px;' TITLE='%(title)s'><IMG ALT='%(icon)s' SRC='%(icon)s' /></BUTTON>"
 tab    = "<A CLASS='btn menu' TARGET=_blank HREF='%(tab)s' STYLE='font-size:10px;' TITLE='%(title)s'><IMG ALT='%(icon)s' SRC='%(icon)s' /></A>"
 aWeb.wr("<DIV CLASS=centered STYLE='align-items:initial'>")
 view_map = {'module':module,'frame':frame,'tab':tab}
 for row in res['data']:
  aWeb.wr("<DIV STYLE='float:left; min-width:100px; margin:6px;'>")
  if 'module' in row:
   aWeb.wr(module%row)
  elif 'frame' in row:
   aWeb.wr(frame%row)
  elif 'tab' in row:
   aWeb.wr(tab%row)
  aWeb.wr("<BR><SPAN STYLE='width:100px; display:block;'>%(title)s</SPAN>"%row)
  aWeb.wr("</DIV>")
 aWeb.wr("</DIV>")

#
#
def framed(aWeb):
 res = aWeb.rest_call("portal/resource",{'type':aWeb['type'],'title':aWeb['title']})
 aWeb.wr("<IFRAME ID=system_resource_frame NAME=system_resource_frame SRC='%s'></IFRAME>"%(res['frame'] if 'frame' in res else res['tab']))