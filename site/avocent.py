"""Moduledocstring.

HTML5 Ajax calls module

"""
__author__= "Zacharias El Banna"
__version__ = "18.02.09GA"
__status__= "Production"

def manage(aWeb):
 id = aWeb['id'] 
 if aWeb['ip']:
  ip = aWeb['ip']
  hostname = aWeb['hostname']
 else:
  data = aWeb.rest_call("device_basics",{'id':id})
  ip = data['ip']
  hostname = data['hostname']

 print "<NAV><UL>"
 print "<LI CLASS='navinfo'><A>%s</A></LI>"%(hostname)
 print "<LI><A CLASS=z-op DIV=div_content_right URL='sdcp.cgi?call=avocent_info&id=%s&ip=%s&hostname=%s'>Info</A></LI>"%(id,ip,hostname)
 print "<LI><A CLASS=z-op DIV=div_content_left URL='sdcp.cgi?call=avocent_inventory&id=%s&ip=%s'>Inventory</A></LI>"%(id,ip)
 print "<LI><A CLASS='z-op reload' DIV=main URL='sdcp.cgi?%s'></A></LI>"%(aWeb.get_args())
 print "</UL></NAV>"
 print "<SECTION CLASS=content ID=div_content>"
 print "<SECTION CLASS=content-left ID=div_content_left></SECTION>"
 print "<SECTION CLASS=content-right ID=div_content_right></SECTION>"
 print "</SECTION>"

#
#
def inventory(aWeb,aIP = None):
 ip = aWeb['ip'] if not aIP else aIP
 data = aWeb.rest_call("avocent_inventory",{'ip':ip})
 print "<ARTICLE>"
 print aWeb.button('reload',DIV='div_content_left', SPIN='true', URL='sdcp.cgi?%s'%aWeb.get_args())
 print "<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>PDU</DIV><DIV CLASS=th>Position</DIV><DIV CLASS=th>Device</DIV><DIV CLASS=th STYLE='width:63px;'>State</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for counter,value in enumerate(data,1):
  print "<DIV CLASS=tr><DIV CLASS=td TITLE='Open up a browser tab for {0}'><A TARGET='_blank' HREF='https://{0}:3502'>{0}</A></DIV><DIV CLASS=td>{1}</DIV>".format(ip,value['slotname']+'.'+value['unit'])
  print "<DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL='sdcp.cgi?call=avocent_unit_info&ip={0}&slot={1}&unit={2}&text={3}&slotname={4}' TITLE='Edit port info' >{3}</A></DIV><DIV CLASS=td ID=div_pdu_{5}>&nbsp;".format(ip,value['slot'],value['unit'],value['name'], value['slotname'],counter)
  url = 'sdcp.cgi?call=avocent_op&ip=%s&slot=%s&unit=%s&id=%i&nstate={}'%(ip,value['slot'],value['unit'],counter)
  div = 'div_pdu_%i'%counter
  if value['state'] == "off":
   print aWeb.button('start',   DIV=div, SPIN='div_content_left', URL=url.format('on'))
  else:
   print aWeb.button('shutdown',DIV=div, SPIN='div_content_left', URL=url.format('off'))
   print aWeb.button('reboot',  DIV=div, SPIN='div_content_left', URL=url.format('reboot'))
  print "</DIV></DIV>"
 print "</DIV></DIV></ARTICLE>"

#
#
def op(aWeb):
 res = aWeb.rest_call("avocent_op",{'state':aWeb['nstate'],'ip':aWeb['ip'],'slot':aWeb['slot'],'unit':aWeb['unit']})
 url = 'sdcp.cgi?call=avocent_op&ip=%s&slot=%s&unit=%s&id=%s&nstate={}'%(aWeb['ip'],aWeb['slot'],aWeb['unit'],aWeb['id'])
 div = 'div_pdu_%s'%aWeb['id']
 print "&nbsp;"
 if res['state'] == "off":
  print aWeb.button('start',   DIV=div, SPIN='div_content_left', URL=url.format('on'))
 else:
  print aWeb.button('shutdown',DIV=div, SPIN='div_content_left', URL=url.format('off'))
  print aWeb.button('reboot',  DIV=div, SPIN='div_content_left', URL=url.format('reboot'))

#
#
def info(aWeb):
 res = aWeb.rest_call("avocent_info",{'op':aWeb['op'],'id':aWeb['id'],'ip':aWeb['ip']})
 pdudata = res['data']
 print "<ARTICLE CLASS=info><P>PDU Device Info</P>"
 print "<FORM ID=pdu_info_form>"
 print "<DIV CLASS=table><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Name:</DIV><DIV CLASS=td>%s</DIV></DIV>"%(aWeb['hostname'])
 print "<DIV CLASS=tr><DIV CLASS=td>Right/Left slots:</DIV><DIV CLASS=td><INPUT TYPE=checkbox NAME=slots VALUE=1 %s></DIV></DIV>"%("checked=checked" if pdudata['slots'] == 2 else "")
 for slot in range(0,pdudata['slots']):
  print "<DIV CLASS=tr><DIV CLASS=td>Slot %s Name:</DIV><DIV CLASS=td>%s</DIV></DIV>"%(slot,pdudata['%s_slot_name'%slot])
  print "<DIV CLASS=tr><DIV CLASS=td>Slot %s ID:</DIV><DIV CLASS=td>%s</DIV></DIV>"%(slot,pdudata['%s_slot_id'%slot])

 print "</DIV></DIV>"
 print "</FORM><DIV CLASS=controls>"
 print aWeb.button('reload',DIV='div_content_right', URL='sdcp.cgi?call=avocent_info&id=%s&ip=%s&hostname=%s'%(aWeb['id'],aWeb['ip'],aWeb['hostname']))
 print aWeb.button('search',DIV='div_content_right', URL='sdcp.cgi?call=avocent_info&id=%s&ip=%s&hostname=%s&op=lookup'%(aWeb['id'],aWeb['ip'],aWeb['hostname']), TITLE='Fetch information')
 print "</DIV></ARTICLE>"

####################################### Device Operations #########################################
#
#
def unit_info(aWeb):
 if aWeb['op'] == 'update':
  res = aWeb.rest_call("avocent_update",aWeb.get_args2dict())
  print "Updated info: {} ({})".format(aWeb['name'],res)
  return
 print "<ARTICLE CLASS=info><P>PDU Unit Info</P>"
 print "<FORM ID=pdu_form>"
 print "<INPUT NAME=slot VALUE={} TYPE=HIDDEN>".format(aWeb['slot'])
 print "<INPUT NAME=unit VALUE={} TYPE=HIDDEN>".format(aWeb['unit'])
 print "<INPUT NAME=ip   VALUE={} TYPE=HIDDEN>".format(aWeb['ip'])
 print "<DIV CLASS=table><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>PDU:</DIV><DIV CLASS=td>{0}</DIV></DIV>".format(aWeb['ip'])
 print "<DIV CLASS=tr><DIV CLASS=td>Slot.Unit:</DIV><DIV CLASS=td>{0}.{1}</DIV></DIV>".format(aWeb['slotname'],aWeb['unit'])
 print "<DIV CLASS=tr><DIV CLASS=td>Text:</DIV><DIV CLASS=td><INPUT NAME=text TYPE=TEXT PLACEHOLDER='{0}'></DIV></DIV>".format(aWeb['text'])
 print "</DIV></DIV>"
 print "<SPAN CLASS='results' ID=update_results></SPAN>"
 print "</FORM><DIV CLASS=controls>"
 print aWeb.button('save',DIV='update_results', URL='sdcp.cgi?call=pdu_unit_info&op=update', FRM='pdu_form')
 print "</DIV></ARTICLE>"
