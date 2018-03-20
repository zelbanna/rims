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
 ip = aWeb.rest_call("dns_external_ip")['ip']
 print "<NAV><UL>"
 print "<LI><A CLASS=z-op DIV=div_content URL='sdcp.cgi?call=multimedia_list'>Files</A></LI>"
 print "<LI><A CLASS='z-op reload' DIV=main URL='sdcp.cgi?call=multimedia_main'></A></LI>"
 print "<LI CLASS='right navinfo'><A>%s</A></LI>"%(ip)
 print "</UL></NAV>"
 print "<SECTION CLASS=content ID=div_content></SECTION>"

#
#
def list(aWeb):
 data = aWeb.rest_call("multimedia_list")
 print "<SECTION CLASS=content-left  ID=div_content_left>"
 print "<ARTICLE><P>Files</P><DIV CLASS=controls>"
 print aWeb.button('reload',DIV='div_content', URL='sdcp.cgi?call=multimedia_list')
 print "</DIV><DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>File</DIV><DIV CLASS=th>&nbsp;</DIV></DIV><DIV CLASS=tbody>"
 for row in data['files']:
  print "<DIV CLASS=tr><DIV CLASS=td STYLE='max-width:320px'>%s</DIV><DIV CLASS=td><DIV CLASS=controls>"%(row['file'])
  print aWeb.button('info',     DIV='div_content_right', URL='sdcp.cgi?call=multimedia_info&path=%s&file=%s'%(row['path'],row['file']))
  print aWeb.button('document', DIV='div_content_right', URL='sdcp.cgi?call=multimedia_subtitles&path=%s&file=%s'%(row['path'],row['file']))
  print "</DIV></DIV></DIV>"
 print "</DIV></DIV></ARTICLE></SECTION>"
 print "<SECTION CLASS=content-right ID=div_content_right></SECTION>"

#
#
def info(aWeb):
 if aWeb['op']== 'process':
  print 'TBD'
 data = aWeb.rest_call("multimedia_check_title",{'path':aWeb['path'],'file':aWeb['file']})
 print "<ARTICLE CLASS=info><P>%s</P>"%aWeb['file']
 print "<DIV CLASS=table><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Type:</DIV><DIV CLASS=td>%s</DIV></DIV>"%data['type']
 print "<DIV CLASS=tr><DIV CLASS=td>Title:</DIV><DIV CLASS=td>%s</DIV></DIV>"%data['title']
 if data.get('episode'):
  print "<DIV CLASS=tr><DIV CLASS=td>Episode:</DIV><DIV CLASS=td>%s</DIV></DIV>"%data['episode']
 print "<DIV CLASS=tr><DIV CLASS=td>File Info:</DIV><DIV CLASS=td>%s</DIV></DIV>"%data['info']
 print "<DIV CLASS=tr><DIV CLASS=td>File Name:</DIV><DIV CLASS=td>%s</DIV></DIV>"%data['name']
 print "<DIV CLASS=tr><DIV CLASS=td>File Path:</DIV><DIV CLASS=td>%s</DIV></DIV>"%data['path']
 print "<DIV CLASS=tr><DIV CLASS=td>Destination:</DIV><DIV CLASS=td>%s</DIV></DIV>"%data['destination']
 print "</DIV></DIV><DIV CLASS=controls>"
 print aWeb.button('start',DIV='div_content_right', URL='sdcp.cgi?call=multimedia_process&dir=%s&file=%s'%(aWeb['path'],aWeb['file']))
 print "</DIV></ARTICLE>"

#
#
def subtitles(aWeb):
 data = aWeb.rest_call("multimedia_check_srt",{'path':aWeb['path'],'file':aWeb['file']})
 print "<ARTICLE CLASS=info><P>%s</P>"%aWeb['file']
 print "<DIV CLASS=table><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Name:</DIV><DIV CLASS=td>%s</DIV></DIV>"%data['name']
 print "<DIV CLASS=tr><DIV CLASS=td>Code:</DIV><DIV CLASS=td>%s</DIV></DIV>"%data['code']
 print "<DIV CLASS=tr><DIV CLASS=td>File:</DIV><DIV CLASS=td>%s</DIV></DIV>"%data['file']
 print "</DIV></DIV></ARTICLE>"
