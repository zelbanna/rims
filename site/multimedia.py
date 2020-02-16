"""HTML5 Ajax Multimedia Controls module"""
__author__= "Zacharias El Banna"
__icon__ = 'icon-multimedia.png'

#
#
def main(aWeb):
 cookie = aWeb.cookie('rims')
 ip   = aWeb.rest_call("dns/external_ip")['ip']
 svcs = aWeb.rest_call("system/service_list")['services']
 aWeb.wr("<NAV><UL>")
 aWeb.wr("<LI><A CLASS=z-op DIV=div_content URL='multimedia_list'>Media files</A></LI>")
 aWeb.wr("<LI CLASS='dropdown'><A>Services</A><DIV CLASS='dropdown-content'>")
 for svc in svcs:
  aWeb.wr("<A CLASS=z-op DIV=div_content URL='system_services_info?node=%s&service=%s'>%s</A>"%(aWeb.node(),svc['service'],svc['name']))
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
  aWeb.wr("<DIV><DIV  STYLE='max-width:290px'>%s</DIV><DIV>"%(row['file']))
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
  aWeb.wr("<DIV><DIV>%s:</DIV><DIV>%s</DIV></DIV>"%(item['item'],item['info']))
 aWeb.wr("</DIV></DIV></ARTICLE>")

#
#
def title(aWeb):
 data = aWeb.rest_call("multimedia/check_title",{'path':aWeb['path'],'file':aWeb['file']})
 aWeb.wr("<ARTICLE CLASS=info><P>%s</P>"%aWeb['file'])
 aWeb.wr("<FORM ID=multimedia_info_form>")
 aWeb.wr("<INPUT TYPE=hidden VALUE='%s' NAME=file>"%(aWeb['file']))
 aWeb.wr("<DIV CLASS='info col2'>")
 aWeb.wr("<label for='type'>Type:</label><INPUT id='type' TYPE=TEXT REQUIRED VALUE='%s' NAME=type>"%data['type'])
 aWeb.wr("<label for='title'>Title:</label><INPUT id='title' TYPE=TEXT REQUIRED VALUE='%s' NAME=title>"%data['title'])
 if data.get('episode'):
  aWeb.wr("<label for='episode'>Episode:</label><INPUT id='episode' TYPE=TEXT REQUIRED VALUE='%s' NAME=episode>"%data['episode'])
 aWeb.wr("<label for='info'>File Info:</label><INPUT id='info' TYPE=TEXT REQUIRED VALUE='%s' NAME=info>"%data['info'])
 aWeb.wr("<label for='name'>File Name:</label><INPUT id='name' TYPE=TEXT REQUIRED VALUE='%s' NAME=name>"%data['name'])
 aWeb.wr("<label for='path'>File Path:</label><INPUT id='path' TYPE=TEXT READONLY VALUE='%s' NAME=path>"%data['path'])
 aWeb.wr("</DIV></FORM>")
 aWeb.wr(aWeb.button('start',DIV='div_content_right', SPIN='true', URL='multimedia_request?request=process',  FRM='multimedia_info_form'))
 aWeb.wr(aWeb.button('sync', DIV='div_content_right', SPIN='true', URL='multimedia_request?request=transfer', FRM='multimedia_info_form'))
 aWeb.wr("</ARTICLE>")

#
#
def subtitles(aWeb):
 data = aWeb.rest_call("multimedia/check_srt",{'path':aWeb['path'],'file':aWeb['file']})
 aWeb.wr("<ARTICLE CLASS=info><P>%s</P>"%aWeb['file'])
 aWeb.wr("<DIV CLASS='info col2'>")
 aWeb.wr("<label for='name'>Name:</label><span id='name'>%s</span>"%data['name'])
 aWeb.wr("<label for='code'>Code:</label><span id='code'>%s</span>"%data['code'])
 aWeb.wr("<label for='file'>File:</label><span id='file'>%s</span>"%data['file'])
 aWeb.wr("</DIV></ARTICLE>")

#
#
def lookup(aWeb):
 data = aWeb.rest_call("multimedia/check_content",{'path':aWeb['path'],'file':aWeb['file'],'subtitle':None})
 aWeb.wr("<ARTICLE CLASS=info><P>%s</P>"%aWeb['file'])
 aWeb.wr("<DIV CLASS='info col3'>")
 aWeb.wr("<label for='status'>Result:</label><span id='status'>%s</span><span>&nbsp;</span>"%data['status'])
 aWeb.wr("<label for='video'>Video:</label><span id='video'>Set default: %s</span><span>Language: %s</span>"%(data['video']['set_default'],data['video']['language']))
 aWeb.wr("<label for='audio'>Audio:</label><span id='audio'>Add/Remove: [%s/%s]</span><span>Add AAC: %s</span>"%(",".join(data['audio']['add']),",".join(data['audio']['remove']),data['audio']['add_aac']))
 aWeb.wr("<label for='subtitle'>Subtitles:</label><span id='subtitle'>Add/Remove: [%s/%s]</span><span>Languages: %s</span>"%(",".join(data['subtitle']['add']),",".join(data['subtitle']['remove']),data['subtitle']['languages']))
 if data.get('error'):
  aWeb.wr("<label for='error'>Audio:</label><span id='error'>%s</span><span>&nbsp;</span>"%data['error'])
 aWeb.wr("</DIV></ARTICLE>")

#
#
def request(aWeb):
 args = aWeb.args()
 request = args.pop('request',None)
 data = aWeb.rest_call("system/worker",{'module':'multimedia','function':request,'output':True,'args':args})
 aWeb.wr("<ARTICLE CLASS=info><P>%s</P>"%aWeb['file'])
 aWeb.wr("<DIV CLASS='info col2'>")
 aWeb.wr("<label for='res'>Res:</label><span id='res'>%s</span>"%data)
 aWeb.wr("</DIV></ARTICLE>")

#
#
def delete(aWeb):
 data = aWeb.rest_call("multimedia/delete",{'path':aWeb['path'],'file':aWeb['file']})
 aWeb.wr("<ARTICLE>Delete: %s/%s => %s</ARTICLE>"%(aWeb['path'],aWeb['file'],data))
