"""HTML5 Ajax module"""
__author__= "Zacharias El Banna"

def manage(aWeb):
 id = aWeb['id']
 data = aWeb.rest_call("device/management",{'id':id})

 aWeb.wr("<NAV><UL>")
 aWeb.wr("<LI CLASS='navinfo'><A>%s</A></LI>"%(data['data']['hostname']))
 aWeb.wr("<LI><A CLASS=z-op DIV=div_content_right URL='avocent_info?id=%s'>Info</A></LI>"%id)
 aWeb.wr("<LI><A CLASS=z-op DIV=div_content_left URL='avocent_inventory?id=%s&ip=%s' SPIN=true>Inventory</A></LI>"%(id,data['data']['ip']))
 aWeb.wr("<LI><A CLASS='z-op reload' DIV=main URL='avocent_manage?id=%s'></A></LI>"%id)
 aWeb.wr("</UL></NAV>")
 aWeb.wr("<SECTION CLASS=content ID=div_content>")
 aWeb.wr("<SECTION CLASS=content-left ID=div_content_left></SECTION>")
 aWeb.wr("<SECTION CLASS=content-right ID=div_content_right></SECTION>")
 aWeb.wr("</SECTION>")

#
#
def inventory(aWeb):
 data = aWeb.rest_call("avocent/inventory",{'id':aWeb['id']})
 aWeb.wr("<ARTICLE>")
 aWeb.wr(aWeb.button('reload',DIV='div_content_left', SPIN='true', URL='avocent_inventory?id=%s&ip=%s'%(aWeb['id'],aWeb['ip'])))
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV>PDU</DIV><DIV>Position</DIV><DIV>Device</DIV><DIV CLASS=th STYLE='width:63px;'>State</DIV></DIV>")
 aWeb.wr("<DIV CLASS=tbody>")
 for counter,value in enumerate(data['inventory'],1):
  aWeb.wr("<DIV><DIV TITLE='Open up a browser tab for {0}'><A TARGET='_blank' HREF='https://{0}:3502'>{0}</A></DIV><DIV>{1}</DIV>".format(aWeb['ip'],'%s.%s'%(value['slotname'],value['unit'])))
  aWeb.wr("<DIV><A CLASS=z-op DIV=div_content_right URL='avocent_unit_info?id={0}&slot={1}&unit={2}&text={3}&slotname={4}' TITLE='Edit port info' >{3}</A></DIV><DIV ID=div_pdu_{5}>&nbsp;".format(aWeb['id'],value['slot'],value['unit'],value['name'], value['slotname'],counter))
  url = 'avocent_op?id=%s&slot=%s&unit=%s&div_pdu_id=%i&nstate={}'%(aWeb['id'],value['slot'],value['unit'],counter)
  div = 'div_pdu_%i'%counter
  if value['state'] == "off":
   aWeb.wr(aWeb.button('start',   DIV=div, SPIN='div_content_left', URL=url.format('on')))
  else:
   aWeb.wr(aWeb.button('stop',    DIV=div, SPIN='div_content_left', URL=url.format('off')))
   aWeb.wr(aWeb.button('reload',  DIV=div, SPIN='div_content_left', URL=url.format('reboot')))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</DIV></DIV></ARTICLE>")

#
#
def op(aWeb):
 res = aWeb.rest_call("avocent/op",{'state':aWeb['nstate'],'id':aWeb['id'],'slot':aWeb['slot'],'unit':aWeb['unit']})
 url = 'avocent_op?id=%s&slot=%s&unit=%s&div_pdu_id=%s&nstate={}'%(aWeb['id'],aWeb['slot'],aWeb['unit'],aWeb['div_pdu_id'])
 div = 'div_pdu_%s'%aWeb['div_pdu_id']
 aWeb.wr("&nbsp;")
 if res['state'] == "off":
  aWeb.wr(aWeb.button('start',   DIV=div, SPIN='div_content_left', URL=url.format('on')))
 else:
  aWeb.wr(aWeb.button('stop',    DIV=div, SPIN='div_content_left', URL=url.format('off')))
  aWeb.wr(aWeb.button('reload',  DIV=div, SPIN='div_content_left', URL=url.format('reboot')))

#
#
def info(aWeb):
 res = aWeb.rest_call("avocent/info",{'op':aWeb['op'],'id':aWeb['id']})
 pdudata = res['data']
 aWeb.wr("<ARTICLE CLASS=info><P>PDU Device Info</P>")
 aWeb.wr("<DIV CLASS='info col2'>")
 aWeb.wr("<label for='slots'>Right/Left slots:</label><span id='slots'>%s</span>"%("True" if pdudata['slots'] == 2 else "False"))
 for slot in range(0,pdudata['slots']):
  aWeb.wr("<label for='%s'>Slot %s Name:</label><span id='%s'>%s</span>"%(slot,slot,slot,pdudata['%s_slot_name'%slot]))
  aWeb.wr("<label for='%s'>Slot %s ID:</label><span id='%s'>%s</span>"%(slot,slot,slot,pdudata['%s_slot_id'%slot]))
 aWeb.wr("</DIV>")
 aWeb.wr(aWeb.button('reload',DIV='div_content_right', URL='avocent_info?id=%s'%aWeb['id']))
 aWeb.wr(aWeb.button('search',DIV='div_content_right', URL='avocent_info?id=%s&op=lookup'%aWeb['id'], TITLE='Fetch information'))
 aWeb.wr("</ARTICLE>")

####################################### Device Operations #########################################
#
#
def unit_info(aWeb):
 if aWeb['op'] == 'update':
  res = aWeb.rest_call("avocent/update",aWeb.args())
  aWeb.wr("Updated info: {}".format(res))
  return
 aWeb.wr("<ARTICLE CLASS=info><P>PDU Unit Info</P>")
 aWeb.wr("<FORM ID=avocent_unit_info_form>")
 aWeb.wr("<INPUT NAME=slot VALUE={} TYPE=HIDDEN>".format(aWeb['slot']))
 aWeb.wr("<INPUT NAME=unit VALUE={} TYPE=HIDDEN>".format(aWeb['unit']))
 aWeb.wr("<INPUT NAME=ip   VALUE={} TYPE=HIDDEN>".format(aWeb['id']))
 aWeb.wr("<DIV CLASS='info col2'>")
 aWeb.wr("<label for='su'>Slot.Unit:</label><span id='su'>{0}.{1}</span>".format(aWeb['slotname'],aWeb['unit']))
 aWeb.wr("<label for='text'>Text:</label><INPUT id='text' NAME=text TYPE=TEXT PLACEHOLDER='{0}'>".format(aWeb['text']))
 aWeb.wr("</DIV>")
 aWeb.wr("<SPAN CLASS='results' ID=update_results></SPAN>")
 aWeb.wr("</FORM>")
 aWeb.wr(aWeb.button('save',DIV='update_results', URL='avocent_unit_info?op=update', FRM='avocent_unit_info_form'))
 aWeb.wr("</ARTICLE>")
