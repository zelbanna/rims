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
 print "<LI><A CLASS=z-op DIV=div_content URL='sdcp.cgi?call=multimedia_list'>Media files</A></LI>"
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
  print "<DIV CLASS=tr><DIV CLASS=td STYLE='max-width:310px'>%s</DIV><DIV CLASS=td><DIV CLASS=controls>"%(row['file'])
  print aWeb.button('info',     DIV='div_content_right', URL='sdcp.cgi?call=multimedia_title&path=%s&file=%s'%(row['path'],row['file']))
  print aWeb.button('search',   DIV='div_content_right', URL='sdcp.cgi?call=multimedia_lookup&path=%s&file=%s'%(row['path'],row['file']))
  print aWeb.button('document', DIV='div_content_right', URL='sdcp.cgi?call=multimedia_subtitles&path=%s&file=%s'%(row['path'],row['file']))
  print "</DIV></DIV></DIV>"
 print "</DIV></DIV></ARTICLE></SECTION>"
 print "<SECTION CLASS=content-right ID=div_content_right></SECTION>"

#
#
def title(aWeb):
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
 print aWeb.button('start',DIV='div_content_right', SPIN='true', URL='sdcp.cgi?call=multimedia_process&path=%s&file=%s'%(aWeb['path'],aWeb['file']))
 print aWeb.button('sync', DIV='div_content_right', SPIN='true', URL='sdcp.cgi?call=multimedia_transfer&path=%s&file=%s'%(aWeb['path'],aWeb['file']))
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

#
#
def lookup(aWeb):
 data = aWeb.rest_call("multimedia_check_content",{'path':aWeb['path'],'file':aWeb['file'],'subtitle':None})
 print "<ARTICLE CLASS=info><P>%s</P>"%aWeb['file']
 print "<DIV CLASS=table><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Result:</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>&nbsp;</DIV></DIV>"%data['res']
 print "<DIV CLASS=tr><DIV CLASS=td>Video:</DIV><DIV CLASS=td>Set default: %s</DIV><DIV CLASS=td>Language: %s</DIV></DIV>"%(data['video']['set_default'],data['video']['language'])
 print "<DIV CLASS=tr><DIV CLASS=td>Audio:</DIV><DIV CLASS=td>Add/Remove: %s/%s</DIV><DIV CLASS=td>Add AAC: %s</DIV></DIV>"%(",".join(data['audio']['add']),",".join(data['audio']['remove']),data['audio']['add_aac'])
 print "<DIV CLASS=tr><DIV CLASS=td>Subtitles:</DIV><DIV CLASS=td>Add/Remove: %s/%s</DIV><DIV CLASS=td>Languages: %s</DIV></DIV>"%(",".join(data['subtitle']['add']),",".join(data['subtitle']['remove']),data['subtitle']['languages'])
 if data.get('error'):
  print "<DIV CLASS=tr><DIV CLASS=td>Audio:</DIV><DIV CLASS=td>%s</DIV></DIV>"%data['error']
 print "</DIV></DIV></ARTICLE>"

#
#
def process(aWeb):
 data = aWeb.rest_full(aWeb._rest_url,"multimedia_process",{'path':aWeb['path'],'file':aWeb['file']},aTimeout = 360)['data']
 print "<ARTICLE CLASS=info><P>%s</P>"%aWeb['file']
 print "<DIV CLASS=table><DIV CLASS=tbody>"
 for key in data.keys():
  print "<DIV CLASS=tr><DIV CLASS=td>%s:</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>&nbsp;</DIV></DIV>"%(key.title(),data[key])
 print "</DIV></DIV></ARTICLE>"

#
#
def transfer(aWeb):
 data = aWeb.rest_call("multimedia_transfer",{'path':aWeb['path'],'file':aWeb['file']})
 print "<ARTICLE CLASS=info><P>%s</P>"%aWeb['file']
 print "<DIV CLASS=table><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Res:</DIV><DIV CLASS=td>%s</DIV></DIV>"%data['res']
 if data.get('error'):
  print "<DIV CLASS=tr><DIV CLASS=td>Error:</DIV><DIV CLASS=td>%s</DIV></DIV>"%data['error']
 print "<DIV CLASS=tr><DIV CLASS=td>Source:</DIV><DIV CLASS=td>%s</DIV></DIV>"%data['source']
 print "<DIV CLASS=tr><DIV CLASS=td>Destination:</DIV><DIV CLASS=td>%s</DIV></DIV>"%data['destination']
 print "</DIV></DIV></ARTICLE>"

