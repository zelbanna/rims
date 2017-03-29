"""Moduledocstring.

Ajax calls module

"""
__author__= "Zacharias El Banna"                     
__version__= "3.0GA"
__status__= "Production"

############################################## PDUs ###################################################
#
# PDUs
#

def pdu_list(aWeb):
 from sdcp.core.GenLib import DB
 from sdcp.devices.RackUtils import Avocent
 domain  = aWeb.get_value('domain')
 slot    = aWeb.get_value('slot')
 nstate  = aWeb.get_value('nstate')
 pdulist = aWeb.get_list('pdulist')
 pduop   = aWeb.get_value('pdu')
 db = DB()

 optemplate = "<A CLASS='z-btn z-small-btn z-btnop' OP=load SPIN=true DIV=div_navleft LNK='ajax.cgi?call=pdu_list&pdu={0}&nstate={1}&slot={2}'><IMG SRC='images/btn-{3}'></A>"

 if len(pdulist) == 0:
  pdulist.append(pduop)
 print "<DIV CLASS='z-framed'><DIV CLASS='z-table'><TABLE WIDTH=330>"
 print "<TR><TH>PDU</TH><TH>Entry</TH><TH>Device</TH><TH style='width:63px;'>State</TH></TR>"
 for pdu in pdulist:
  avocent = Avocent(pdu,domain)
  avocent.load_snmp()
  if pdu == pduop and slot and nstate:
   avocent.set_state(slot,nstate)
   # Avocent is not fast enough to execute something immediately after reboot op, halt output then :-)
   if nstate == 'reboot':
    from time import sleep
    sleep(10)
  for key in avocent.get_keys(aSortKey = lambda x: int(x.split('.')[0])*100+int(x.split('.')[1])):
   value = avocent.get_entry(key)
   print "<TR><TD TITLE='Open up a browser tab for {1}'><A TARGET='_blank' HREF='https://{0}:3502'>{1}</A></TD><TD>{2}</TD>".format(avocent._ip,pdu,value['pduslot'])
   print "<TD><A CLASS='z-btnop' OP=load DIV=div_navcont LNK='ajax.cgi?call=pdu_info&domain={0}&pdu={1}&slot={2}&name={3}&slotname={4}' TITLE='Edit port info' >{3}</A></TD><TD>".format(domain,pdu,key,value['name'], value['pduslot'])
   if value['state'] == "off":
    print optemplate.format(pdu, "on", key, "start")
   else:
    print optemplate.format(pdu, "off", key, "shutdown")
    print optemplate.format(pdu, "reboot", key, "reboot")
   print "</TD></TR>"
 print "</TABLE></DIV></DIV>"

def pdu_info(aWeb):
 pdu  = aWeb.get_value('pdu')
 slot = aWeb.get_value('slot')
 slotname = aWeb.get_value('slotname')
 name = aWeb.get_value('name')
 domain = aWeb.get_value('domain')
 print "<DIV CLASS='z-framed z-table' style='resize: horizontal; margin-left:0px; width:420px; z-index:101; height:150px;'>"
 print "<FORM ID=pdu_form>"
 print "<INPUT NAME=call VALUE=pdu_update TYPE=HIDDEN>"
 print "<INPUT NAME=domain VALUE={} TYPE=HIDDEN>".format(domain)
 print "<INPUT NAME=slot   VALUE={} TYPE=HIDDEN>".format(slot)
 print "<INPUT NAME=pdu    VALUE={} TYPE=HIDDEN>".format(pdu)
 print "<TABLE style='width:100%'>"
 print "<TR><TH COLSPAN=2>PDU Info</TH></TR>"
 print "<TR><TD>PDU:</TD><TD>{0}</TD></TR>".format(pdu)
 print "<TR><TD>Slot:</TD><TD>{0}</TD></TR>".format(slotname)
 print "<TR><TD>Name:</TD><TD><INPUT NAME=name TYPE=TEXT CLASS='z-input' PLACEHOLDER='{0}'></TD></TR>".format(name)
 print "<TR><TD COLSPAN=2>&nbsp;</TD></TR>"
 print "</TABLE>"
 print "<A CLASS='z-btn z-btnop z-small-btn' DIV=update_results LNK=ajax.cgi FRM=pdu_form OP=post><IMG SRC='images/btn-save.png'></A><SPAN ID=update_results></SPAN>"
 print "</FORM>"
 print "</DIV>"

#
# Update PDU slot info (name basically)
#
def pdu_update(aWeb):
 values = aWeb.get_keys()
 values.remove('call')
 if 'name' in values:
  from sdcp.devices.RackUtils import Avocent
  name = aWeb.get_value('name')
  pdu  = aWeb.get_value('pdu')
  slot = aWeb.get_value('slot')
  domain = aWeb.get_value('domain')
  avocent = Avocent(pdu,domain)
  avocent.set_name(slot,name)
  print "Updated name: {} for {}.{}:{}".format(name,pdu,domain,slot)
 else:
  print "Name not updated"
