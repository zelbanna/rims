"""Moduledocstring.

Ajax calls module

"""
__author__= "Zacharias El Banna"                     
__version__= "3.0GA"
__status__= "Production"

from sdcp.core.GenLib import DB, sys_int2ip, sys_ip2int

############################################## PDUs ###################################################
#
# PDUs
#

def pdu_list(aWeb):
 from sdcp.devices.RackUtils import Avocent
 domain  = aWeb.get_value('domain')
 pdulist = aWeb.get_list('pdulist')

 # For Operations:
 slot    = aWeb.get_value('slot')
 nstate  = aWeb.get_value('nstate')
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

  # Ops
  if pdu == pduop and slot and nstate:
   avocent.set_state(slot,nstate)
   # Avocent is not fast enough to execute something immediately after reboot op, halt output then :-)
   if nstate == 'reboot':
    from time import sleep
    sleep(10)

  for key in avocent.get_keys(aSortKey = lambda x: int(x.split('.')[0])*100+int(x.split('.')[1])):
   value = avocent.get_entry(key)
   print "<TR><TD TITLE='Open up a browser tab for {1}'><A TARGET='_blank' HREF='https://{0}:3502'>{1}</A></TD><TD>{2}</TD>".format(avocent._ip,pdu,value['pduslot'])
   print "<TD><A CLASS='z-btnop' OP=load DIV=div_navcont LNK='ajax.cgi?call=pdu_slot_info&domain={0}&pdu={1}&slot={2}&name={3}&slotname={4}' TITLE='Edit port info' >{3}</A></TD><TD>".format(domain,pdu,key,value['name'], value['pduslot'])
   if value['state'] == "off":
    print optemplate.format(pdu, "on", key, "start")
   else:
    print optemplate.format(pdu, "off", key, "shutdown")
    print optemplate.format(pdu, "reboot", key, "reboot")
   print "</TD></TR>"
 print "</TABLE></DIV></DIV>"

def pdu_slot_info(aWeb):
 pdu  = aWeb.get_value('pdu')
 slot = aWeb.get_value('slot')
 slotname = aWeb.get_value('slotname')
 name = aWeb.get_value('name')
 domain = aWeb.get_value('domain')
 print "<DIV CLASS='z-framed z-table' style='resize: horizontal; margin-left:0px; width:420px; z-index:101; height:150px;'>"
 print "<FORM ID=pdu_form>"
 print "<INPUT NAME=domain VALUE={} TYPE=HIDDEN>".format(domain)
 print "<INPUT NAME=slot   VALUE={} TYPE=HIDDEN>".format(slot)
 print "<INPUT NAME=pdu    VALUE={} TYPE=HIDDEN>".format(pdu)
 print "<TABLE style='width:100%'>"
 print "<TR><TH COLSPAN=2>PDU Slot Info</TH></TR>"
 print "<TR><TD>PDU:</TD><TD>{0}</TD></TR>".format(pdu)
 print "<TR><TD>Slot.Unit:</TD><TD>{0}</TD></TR>".format(slotname)
 print "<TR><TD>Name:</TD><TD><INPUT NAME=name TYPE=TEXT CLASS='z-input' PLACEHOLDER='{0}'></TD></TR>".format(name)
 print "<TR><TD COLSPAN=2>&nbsp;</TD></TR>"
 print "</TABLE>"
 print "<A CLASS='z-btn z-btnop z-small-btn' DIV=update_results LNK=ajax.cgi?pdu_slot_update FRM=pdu_form OP=post><IMG SRC='images/btn-save.png'></A><SPAN ID=update_results></SPAN>"
 print "</FORM>"
 print "</DIV>"

#
#
#
def pdu_list_pdus(aWeb):
 db   = DB()
 db.connect()
 print "<DIV CLASS='z-framed'>"
 print "<DIV CLASS='z-table'><TABLE WIDTH=330>"
 print "<TR style='height:20px'><TH COLSPAN=3><CENTER>PDUs</CENTER></TH></TR>"
 print "<TR style='height:20px'><TD COLSPAN=3>"
 print "<A TITLE='Add PDU' CLASS='z-btn z-small-btn z-btnop' OP=load DIV=div_navcont LNK='ajax.cgi?call=pdu_device_info&id=new'><IMG SRC='images/btn-add.png'></A>"
 print "<A TITLE='Reload List' CLASS='z-btn z-small-btn z-btnop' OP=load DIV=div_navleft LNK='ajax.cgi?call=pdu_list_pdus'><IMG SRC='images/btn-reboot.png'></A>"
 print "</TD></TR>"
 res  = db.do("SELECT * from pdus ORDER by name")
 data = db.get_all_rows()
 print "<TR><TH>ID</TH><TH>Name</TH><TH>IP</TH></TR>"
 for unit in data:
  print "<TR><TD>{0}</TD><TD><A CLASS='z-btnop' OP=load DIV=div_navcont LNK='ajax.cgi?call=pdu_device_info&id={0}'>{1}</A></TD><TD>{2}</TD>".format(unit['id'],unit['name'],sys_int2ip(unit['ip']))
 print "</TABLE></DIV>"
 db.close()

#
#
#
def pdu_device_info(aWeb):
 id   = aWeb.get_value('id')
 print "<DIV CLASS='z-framed z-table' style='resize: horizontal; margin-left:0px; width:420px; z-index:101; height:185px;'>"
 print "<FORM ID=pdu_device_info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(id)
 print "<TABLE style='width:100%'>"
 print "<TR><TH COLSPAN=2>PDU Device Info {}</TH></TR>".format("(new)" if id == 'new' else "")

 if id == 'new':
  pdudata = { 'id':'new', 'name':'new-name', 'ip':2130706433, 'slots':1, 'first_slot_name':'unknown', 'first_slot_id':0, 'second_slot_name':'unknown', 'second_slot_id':1 }
 else:
  db = DB()
  db.connect()
  db.do("SELECT * FROM pdus WHERE id = '{0}'".format(id))
  pdudata = db.get_row()
  db.close()
 print "<TR><TD>IP:</TD><TD><INPUT NAME=ip TYPE=TEXT CLASS='z-input' VALUE='{0}'></TD></TR>".format(sys_int2ip(pdudata['ip']))
 print "<TR><TD>Name:</TD><TD><INPUT NAME=name TYPE=TEXT CLASS='z-input' VALUE='{0}'></TD></TR>".format(pdudata['name'])
 if pdudata['slots'] == 1:
  print "<TR><TD>Right/Left slots:</TD><TD>{}</TD></TR>".format(True)
  print "<TR><TD>:</TD><TD>{}</TD></TR>".format(True)   
 else:
  print "<TR><TD>Right/Left slots:</TD><TD>{}</TD></TR>".format(False)
  print "<TR><TD>Slot Name:</TD><TD>{}</TD></TR>".format(pdudata['first_slot_name'])
  print "<TR><TD>Slot ID:</TD><TD>{}</TD></TR>".format(pdudata['first_slot_id'])

 print "</TABLE>"
 print "<A TITLE='Update unit' CLASS='z-btn z-btnop z-small-btn' DIV=update_results LNK=ajax.cgi?call=pdu_update FRM=pdu_device_info_form OP=post><IMG SRC='images/btn-save.png'></A>"
 if not id == 'new':
  print "<A TITLE='Remove unit' CLASS='z-btn z-btnop z-small-btn' DIV=div_navcont LNK=ajax.cgi?call=pdu_remove&id={0} OP=load><IMG SRC='images/btn-remove.png'></A>".format(id)
 print "<A TITLE='Update info' CLASS='z-btn z-btnop z-small-btn' DIV=div_navcont LNK=ajax.cgi?call=pdu_lookup&id={0} OP=load><IMG SRC='images/btn-search.png'></A>".format(id)
 print "&nbsp;<SPAN ID=update_results></SPAN>"
 print "</FORM>"
 print "</DIV>"

#
#
#
def pdu_update(aWeb):
 values = aWeb.get_keys()
 values.remove('call')
 db   = DB()
 db.connect()
 id   = aWeb.get_value('id')
 name = aWeb.get_value('name')
 ip   = aWeb.get_value('ip')
 ipint = sys_ip2int(ip)
 sql = ""
 if id == 'new':
  print "New {} created".format(type[:-1])
  sql = "INSERT into pdus (name, ip) VALUES ('{0}','{1}')".format(name,ipint)
 else:
  print "Updated pdus {}".format(id)
  sql = "UPDATE pdus SET name = '{0}', ip = '{1}' WHERE id = '{2}'".format(name,ipint,id)
 res = db.do(sql)
 db.commit()
 db.close()

#
# Update PDU slot info (name basically)
#
def pdu_slot_update(aWeb):
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


#
#
#
def pdu_remove(aWeb):
 id   = aWeb.get_value('id')
 db   = DB()
 db.connect()
 db.do("DELETE FROM pdus WHERE id = '{0}'".format(id))
 db.do("UPDATE devices SET pwr_left_pdu_id  = '0' WHERE pwr_left_pdu_id = '{0}'".format(id))
 db.do("UPDATE devices SET pwr_right_pdu_id  = '0' WHERE pwr_right_pdu_id = '{0}'".format(id))
 db.do("UPDATE racks SET fk_pdu_1 = '0' WHERE fk_pdu_1 = '{0}'".format(id))
 db.do("UPDATE racks SET fk_pdu_2 = '0' WHERE fk_pdu_2 = '{0}'".format(id))
 db.commit()
 print "Unit {0} deleted".format(id)
 db.close()
