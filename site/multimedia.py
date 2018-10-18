"""HTML5 Ajax Multimedia Controls module"""
__author__= "Zacharias El Banna"
__icon__ = '../images/icon-multimedia.png'

#
#
def main(aWeb):
 cookie = aWeb.cookie('system') 
 ip   = aWeb.rest_call("dns/external_ip")['ip']
 svcs = aWeb.rest_call("multimedia/services")
 aWeb.wr("<NAV><UL>")
 aWeb.wr("<LI><A CLASS=z-op DIV=div_content URL='multimedia_list'>Media files</A></LI>")
 aWeb.wr("<LI CLASS='dropdown'><A>Services</A><DIV CLASS='dropdown-content'>")
 for svc in svcs.get('services',[]):
  aWeb.wr("<A CLASS=z-op DIV=div_content URL='tools_services_info?node=%s&service=%s'>%s</A>"%(aWeb.node(),svc['service'],svc['name']))
 aWeb.wr("</DIV></LI>")
 aWeb.wr("<LI><A CLASS='z-op reload' DIV=main URL='multimedia_main'></A></LI>")
 aWeb.wr("<LI CLASS='right navinfo'><A>%s</A></LI>"%(ip))
 aWeb.wr("</UL></NAV>")
 aWeb.wr("<SECTION CLASS=content ID=div_content></SECTION>")

#
#
def list(aWeb):
 data = aWeb.rest_call("multimedia/list")
 aWeb.wr("<SECTION CLASS=content-left  ID=div_content_left>")
 aWeb.wr("<ARTICLE><P>Files</P>")
 aWeb.wr(aWeb.button('reload',DIV='div_content', URL='multimedia_list'))
 aWeb.wr(aWeb.button('trash', DIV='div_content_right', URL='multimedia_cleanup', MSG='Are you sure?'))
 aWeb.wr("<DIV CLASS=table><DIV CLASS=tbody>")
 for row in data['files']:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td STYLE='max-width:290px'>%s</DIV><DIV CLASS=td>"%(row['file']))
  aWeb.wr(aWeb.button('info',     DIV='div_content_right', TITLE='Title info', URL='multimedia_title?path=%s&file=%s'%(row['path'],row['file'])))
  aWeb.wr(aWeb.button('search',   DIV='div_content_right', TITLE='Lookup info',URL='multimedia_lookup?path=%s&file=%s'%(row['path'],row['file'])))
  aWeb.wr(aWeb.button('document', DIV='div_content_right', TITLE='Subtitles',  URL='multimedia_subtitles?path=%s&file=%s'%(row['path'],row['file'])))
  aWeb.wr(aWeb.button('trash',   DIV='div_content_right', TITLE='Delete file',URL='multimedia_delete?path=%s&file=%s'%(row['path'],row['file'])))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</DIV></DIV></ARTICLE></SECTION>")
 aWeb.wr("<SECTION CLASS=content-right ID=div_content_right></SECTION>")

#
#
def cleanup(aWeb):
 data = aWeb.rest_call("multimedia/cleanup")
 aWeb.wr("<ARTICLE CLASS=info><P>Delete</P>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=tbody>")
 for item in data['items']:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%s:</DIV><DIV CLASS=td>%s</DIV></DIV>"%(item['item'],item['info']))
 aWeb.wr("</DIV></DIV></ARTICLE>")

#
#
def title(aWeb):
 data = aWeb.rest_call("multimedia/check_title",{'path':aWeb['path'],'file':aWeb['file']})
 aWeb.wr("<ARTICLE CLASS=info><P>%s</P>"%aWeb['file'])
 aWeb.wr("<FORM ID=multimedia_info_form>")
 aWeb.wr("<INPUT TYPE=hidden VALUE='%s' NAME=file>"%(aWeb['file']))
 aWeb.wr("<DIV CLASS=table><DIV CLASS=tbody>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Type:</DIV><DIV CLASS=td><INPUT TYPE=TEXT REQUIRED VALUE='%s' NAME=type></DIV></DIV>"%data['type'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Title:</DIV><DIV CLASS=td><INPUT TYPE=TEXT REQUIRED VALUE='%s' NAME=title></DIV></DIV>"%data['title'])
 if data.get('episode'):
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Episode:</DIV><DIV CLASS=td><INPUT TYPE=TEXT REQUIRED VALUE='%s' NAME=episode></DIV></DIV>"%data['episode'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>File Info:</DIV><DIV CLASS=td><INPUT TYPE=TEXT REQUIRED VALUE='%s' NAME=info></DIV></DIV>"%data['info'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>File Name:</DIV><DIV CLASS=td><INPUT TYPE=TEXT REQUIRED VALUE='%s' NAME=name></DIV></DIV>"%data['name'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>File Path:</DIV><DIV CLASS=td><INPUT TYPE=TEXT READONLY VALUE='%s' NAME=path></DIV></DIV>"%data['path'])
 aWeb.wr("</DIV></DIV></FORM>")
 aWeb.wr(aWeb.button('start',DIV='div_content_right', SPIN='true', URL='multimedia_request?request=process',  FRM='multimedia_info_form'))
 aWeb.wr(aWeb.button('sync', DIV='div_content_right', SPIN='true', URL='multimedia_request?request=transfer', FRM='multimedia_info_form'))
 aWeb.wr("</ARTICLE>")

#
#
def subtitles(aWeb):
 data = aWeb.rest_call("multimedia/check_srt",{'path':aWeb['path'],'file':aWeb['file']})
 aWeb.wr("<ARTICLE CLASS=info><P>%s</P>"%aWeb['file'])
 aWeb.wr("<DIV CLASS=table><DIV CLASS=tbody>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Name:</DIV><DIV CLASS=td>%s</DIV></DIV>"%data['name'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Code:</DIV><DIV CLASS=td>%s</DIV></DIV>"%data['code'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>File:</DIV><DIV CLASS=td>%s</DIV></DIV>"%data['file'])
 aWeb.wr("</DIV></DIV></ARTICLE>")

#
#
def lookup(aWeb):
 data = aWeb.rest_call("multimedia/check_content",{'path':aWeb['path'],'file':aWeb['file'],'subtitle':None})
 aWeb.wr("<ARTICLE CLASS=info><P>%s</P>"%aWeb['file'])
 aWeb.wr("<DIV CLASS=table><DIV CLASS=tbody>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Result:</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>&nbsp;</DIV></DIV>"%data['result'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Video:</DIV><DIV CLASS=td>Set default: %s</DIV><DIV CLASS=td>Language: %s</DIV></DIV>"%(data['video']['set_default'],data['video']['language']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Audio:</DIV><DIV CLASS=td>Add/Remove: [%s/%s]</DIV><DIV CLASS=td>Add AAC: %s</DIV></DIV>"%(",".join(data['audio']['add']),",".join(data['audio']['remove']),data['audio']['add_aac']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Subtitles:</DIV><DIV CLASS=td>Add/Remove: [%s/%s]</DIV><DIV CLASS=td>Languages: %s</DIV></DIV>"%(",".join(data['subtitle']['add']),",".join(data['subtitle']['remove']),data['subtitle']['languages']))
 if data.get('error'):
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Audio:</DIV><DIV CLASS=td>%s</DIV></DIV>"%data['error'])
 aWeb.wr("</DIV></DIV></ARTICLE>")

#
#
def request(aWeb):
 args = aWeb.args()
 request = args.pop('request',None)
 data = aWeb.rest_call("system/task_worker?node=%s"%aWeb.node(),{'module':'multimedia','func':request,'output':True,'args':args})
 aWeb.wr("<ARTICLE CLASS=info><P>%s</P>"%aWeb['file'])
 aWeb.wr("<DIV CLASS=table><DIV CLASS=tbody>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Res:</DIV><DIV CLASS=td>%s</DIV></DIV>"%data)
 aWeb.wr("</DIV></DIV></ARTICLE>")

#
#
def delete(aWeb):
 data = aWeb.rest_call("multimedia/delete",{'path':aWeb['path'],'file':aWeb['file']})
 aWeb.wr("<ARTICLE>Delete: %s/%s => %s</ARTICLE>"%(aWeb['path'],aWeb['file'],data))
