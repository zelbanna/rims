"""Moduledocstring.

HTML5 Ajax calls module

"""
__author__= "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__= "Production"

def manage(aWeb):
 id = aWeb['id'] 
 if aWeb['ip']:
  ip = aWeb['ip']
  hostname = aWeb['hostname']
 else:
  data = aWeb.rest("device_info",{'id':id})
  ip = data['ip']
  hostname = data['info']['hostname']

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
 from ..devices.avocent import Device
 counter = 0
 ip = aWeb['ip'] if not aIP else aIP
 avocent = Device(ip)
 avocent.load_snmp()
 print "<ARTICLE>"
 print aWeb.button('reload',DIV='div_content_left', SPIN='true', URL='sdcp.cgi?%s'%aWeb.get_args())
 print "<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>PDU</DIV><DIV CLASS=th>Position</DIV><DIV CLASS=th>Device</DIV><DIV CLASS=th STYLE='width:63px;'>State</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for key in avocent.get_keys(aSortKey = lambda x: int(x.split('.')[0])*100+int(x.split('.')[1])):
  counter += 1
  value = avocent.get_entry(key)
  print "<DIV CLASS=tr><DIV CLASS=td TITLE='Open up a browser tab for {0}'><A TARGET='_blank' HREF='https://{0}:3502'>{0}</A></DIV><DIV CLASS=td>{1}</DIV>".format(ip,value['slotname']+'.'+value['unit'])
  print "<DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL='sdcp.cgi?call=avocent_unit_info&ip={0}&slot={1}&unit={2}&text={3}&slotname={4}' TITLE='Edit port info' >{3}</A></DIV><DIV CLASS=td ID=div_pdu_{5}>&nbsp;".format(ip,value['slot'],value['unit'],value['name'], value['slotname'],counter)
  url = 'sdcp.cgi?call=pdu_op&ip=%s&slot=%s&unit=%s&id=%i&nstate={}'%(ip,value['slot'],value['unit'],counter)
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
 from ..devices.avocent import Device
 avocent = Device(aWeb['ip'])
 avocent.set_state(aWeb['slot'],aWeb['unit'],aWeb['nstate'])
 # Avocent is not fast enough to execute something immediately after op, halt output then :-)
 from time import sleep
 sleep(10 if aWeb['nstate'] == 'reboot' else 4)
 url = 'sdcp.cgi?call=pdu_op&ip=%s&slot=%s&unit=%s&id=%s&nstate={}'%(aWeb['ip'],aWeb['slot'],aWeb['unit'],aWeb['id'])
 div = 'div_pdu_%s'%aWeb['id']
 print "&nbsp;"
 if avocent.get_state(aWeb['slot'],aWeb['unit'])['state'] == "off":
  print aWeb.button('start',   DIV=div, SPIN='div_content_left', URL=url.format('on'))
 else:
  print aWeb.button('shutdown',DIV=div, SPIN='div_content_left', URL=url.format('off'))
  print aWeb.button('reboot',  DIV=div, SPIN='div_content_left', URL=url.format('reboot'))

#
#
def info(aWeb):
 res = aWeb.rest("avocent_info",{'op':aWeb['op'],'id':aWeb['id'],'ip':aWeb['ip']})
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
 print aWeb.button('reload',DIV='div_content_right', URL='sdcp.cgi?call=avocent_info&id=%s&ip=%s&hostname=%s'%(aWeb['id'],aWeb['ip'],aWeb['hostname']))
 print aWeb.button('search',DIV='div_content_right', URL='sdcp.cgi?call=avocent_info&id=%s&ip=%s&hostname=%s&op=lookup'%(aWeb['id'],aWeb['ip'],aWeb['hostname']), TITLE='Fetch information')
 print "</FORM>"
 print "</ARTICLE>"

####################################### Device Operations #########################################
#
#
def unit_info(aWeb):
 from ..devices.avocent import Device
 if aWeb['op'] == 'update':
  res = aWeb.rest("avocent_update",aWeb.get_args2dict())
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
 print aWeb.button('save',DIV='update_results', URL='sdcp.cgi?call=pdu_unit_info&op=update', FRM='pdu_form')
 print "<SPAN CLASS='results' ID=update_results></SPAN>"
 print "</FORM>"
 print "</ARTICLE>"
