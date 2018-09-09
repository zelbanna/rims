"""Moduledocstring.

HTML5 Ajax module

"""
__author__= "Zacharias El Banna"
__version__ = "1.0GA"
__status__= "Production"

def manage(aWeb):
 id = aWeb['id']
 if aWeb['ip']:
  ip = aWeb['ip']
  hostname = aWeb['hostname']
 else:
  data = aWeb.rest_call("device_info",{'id':id,'op':'basics'})
  ip = data['ip']
  hostname = data['info']['hostname']

 aWeb.wr("<NAV><UL>")
 aWeb.wr("<LI CLASS='navinfo'><A>%s</A></LI>"%(hostname))
 aWeb.wr("<LI><A CLASS=z-op DIV=div_content_right URL='avocent_info?id=%s&ip=%s&hostname=%s'>Info</A></LI>"%(id,ip,hostname))
 aWeb.wr("<LI><A CLASS=z-op DIV=div_content_left URL='avocent_inventory?id=%s&ip=%s' SPIN=true>Inventory</A></LI>"%(id,ip))
 aWeb.wr("<LI><A CLASS='z-op reload' DIV=main URL='avocent_manage?id=%s&ip=%s&hostname=%s'></A></LI>"%(id,ip,hostname))
 aWeb.wr("</UL></NAV>")
 aWeb.wr("<SECTION CLASS=content ID=div_content>")
 aWeb.wr("<SECTION CLASS=content-left ID=div_content_left></SECTION>")
 aWeb.wr("<SECTION CLASS=content-right ID=div_content_right></SECTION>")
 aWeb.wr("</SECTION>")

#
#
def inventory(aWeb,aIP = None):
 ip = aWeb['ip'] if not aIP else aIP
 data = aWeb.rest_call("avocent_inventory",{'ip':ip})
 aWeb.wr("<ARTICLE>")
 aWeb.wr(aWeb.button('reload',DIV='div_content_left', SPIN='true', URL='avocent_inventory?ip=%s'%ip))
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>PDU</DIV><DIV CLASS=th>Position</DIV><DIV CLASS=th>Device</DIV><DIV CLASS=th STYLE='width:63px;'>State</DIV></DIV>")
 aWeb.wr("<DIV CLASS=tbody>")
 for counter,value in enumerate(data,1):
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td TITLE='Open up a browser tab for {0}'><A TARGET='_blank' HREF='https://{0}:3502'>{0}</A></DIV><DIV CLASS=td>{1}</DIV>".format(ip,value['slotname']+'.'+value['unit']))
  aWeb.wr("<DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL='avocent_unit_info?ip={0}&slot={1}&unit={2}&text={3}&slotname={4}' TITLE='Edit port info' >{3}</A></DIV><DIV CLASS=td ID=div_pdu_{5}>&nbsp;".format(ip,value['slot'],value['unit'],value['name'], value['slotname'],counter))
  url = 'avocent_op?ip=%s&slot=%s&unit=%s&id=%i&nstate={}'%(ip,value['slot'],value['unit'],counter)
  div = 'div_pdu_%i'%counter
  if value['state'] == "off":
   aWeb.wr(aWeb.button('start',   DIV=div, SPIN='div_content_left', URL=url.format('on')))
  else:
   aWeb.wr(aWeb.button('stop',DIV=div, SPIN='div_content_left', URL=url.format('off')))
   aWeb.wr(aWeb.button('reload',  DIV=div, SPIN='div_content_left', URL=url.format('reboot')))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</DIV></DIV></ARTICLE>")

#
#
def op(aWeb):
 res = aWeb.rest_call("avocent_op",{'state':aWeb['nstate'],'ip':aWeb['ip'],'slot':aWeb['slot'],'unit':aWeb['unit']})
 url = 'avocent_op?ip=%s&slot=%s&unit=%s&id=%s&nstate={}'%(aWeb['ip'],aWeb['slot'],aWeb['unit'],aWeb['id'])
 div = 'div_pdu_%s'%aWeb['id']
 aWeb.wr("&nbsp;")
 if res['state'] == "off":
  aWeb.wr(aWeb.button('start',   DIV=div, SPIN='div_content_left', URL=url.format('on')))
 else:
  aWeb.wr(aWeb.button('stop',DIV=div, SPIN='div_content_left', URL=url.format('off')))
  aWeb.wr(aWeb.button('reload',  DIV=div, SPIN='div_content_left', URL=url.format('reboot')))

#
#
def info(aWeb):
 res = aWeb.rest_call("avocent_info",{'op':aWeb['op'],'id':aWeb['id'],'ip':aWeb['ip']})
 pdudata = res['data']
 aWeb.wr("<ARTICLE CLASS=info><P>PDU Device Info</P>")
 aWeb.wr("<FORM ID=pdu_info_form>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=tbody>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Name:</DIV><DIV CLASS=td>%s</DIV></DIV>"%(aWeb['hostname']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Right/Left slots:</DIV><DIV CLASS=td><INPUT TYPE=checkbox NAME=slots VALUE=1 %s></DIV></DIV>"%("checked=checked" if pdudata['slots'] == 2 else ""))
 for slot in range(0,pdudata['slots']):
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Slot %s Name:</DIV><DIV CLASS=td>%s</DIV></DIV>"%(slot,pdudata['%s_slot_name'%slot]))
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Slot %s ID:</DIV><DIV CLASS=td>%s</DIV></DIV>"%(slot,pdudata['%s_slot_id'%slot]))

 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</FORM><DIV CLASS=controls>")
 aWeb.wr(aWeb.button('reload',DIV='div_content_right', URL='avocent_info?id=%s&ip=%s&hostname=%s'%(aWeb['id'],aWeb['ip'],aWeb['hostname'])))
 aWeb.wr(aWeb.button('search',DIV='div_content_right', URL='avocent_info?id=%s&ip=%s&hostname=%s&op=lookup'%(aWeb['id'],aWeb['ip'],aWeb['hostname']), TITLE='Fetch information'))
 aWeb.wr("</DIV></ARTICLE>")

####################################### Device Operations #########################################
#
#
def unit_info(aWeb):
 if aWeb['op'] == 'update':
  res = aWeb.rest_call("avocent_update",aWeb.args())
  aWeb.wr("Updated info: {}".format(res))
  return
 aWeb.wr("<ARTICLE CLASS=info><P>PDU Unit Info</P>")
 aWeb.wr("<FORM ID=pdu_form>")
 aWeb.wr("<INPUT NAME=slot VALUE={} TYPE=HIDDEN>".format(aWeb['slot']))
 aWeb.wr("<INPUT NAME=unit VALUE={} TYPE=HIDDEN>".format(aWeb['unit']))
 aWeb.wr("<INPUT NAME=ip   VALUE={} TYPE=HIDDEN>".format(aWeb['ip']))
 aWeb.wr("<DIV CLASS=table><DIV CLASS=tbody>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>PDU:</DIV><DIV CLASS=td>{0}</DIV></DIV>".format(aWeb['ip']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Slot.Unit:</DIV><DIV CLASS=td>{0}.{1}</DIV></DIV>".format(aWeb['slotname'],aWeb['unit']))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Text:</DIV><DIV CLASS=td><INPUT NAME=text TYPE=TEXT PLACEHOLDER='{0}'></DIV></DIV>".format(aWeb['text']))
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("<SPAN CLASS='results' ID=update_results></SPAN>")
 aWeb.wr("</FORM><DIV CLASS=controls>")
 aWeb.wr(aWeb.button('save',DIV='update_results', URL='avocent_unit_info?op=update', FRM='pdu_form'))
 aWeb.wr("</DIV></ARTICLE>")
