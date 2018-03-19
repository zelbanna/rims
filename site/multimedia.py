"""Module docstring.

HTML5 Ajax Multimedia Controls calls module

"""
__author__= "Zacharias El Banna"
__version__ = "18.03.16GA"
__status__= "Production"
__icon__ = 'images/icon-multimedia.png'

#
#
def main(aWeb):
 if not aWeb.cookies.get('system'):
  print "<SCRIPT>location.replace('index.cgi')</SCRIPT>"
  return
 cookie = aWeb.cookie_unjar('system')
 ip = aWeb.rest_call("dns_external_ip")['ip']
 print "<NAV><UL>"
 print "<LI><A CLASS=z-op DIV=div_content URL='sdcp.cgi?call=multimedia_list'>Files</A></LI>"
 print "<LI><A CLASS='z-op reload' DIV=main URL='sdcp.cgi?call=multimedia_main'></A></LI>"
 print "<LI CLASS='right navinfo'><A>%s</A></LI>"%(ip)
 print "</UL></NAV>"
 print "<SECTION CLASS=content ID=div_content></SECTION>"

#
#
def files(aWeb):
 print "<SECTION CLASS=content-left  ID=div_content_left>"
 print "<ARTICLE><P>Files</P>"

