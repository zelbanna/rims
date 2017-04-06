"""Moduledocstring.

Ajax calls module

"""
__author__= "Zacharias El Banna"                     
__version__= "3.0GA"
__status__= "Production"

from sdcp.core.GenLib import DB, sys_ip2int
from sdcp.devices.RackUtils import Avocent

############################################## PDUs ###################################################
#
# PDUs
#

def pdu_list_units(aWeb):
 domain  = aWeb.get_value('domain')
 pdulist = aWeb.get_list('pdulist')

 # For Operations:
 slot    = aWeb.get_value('slot')
 unit    = aWeb.get_value('unit')
 nstate  = aWeb.get_value('nstate')
 pduop   = aWeb.get_value('pdu')

 db = DB()

 optemplate = "<A CLASS='z-btn z-small-btn z-btnop' OP=load SPIN=true DIV=div_navleft LNK='ajax.cgi?call=pdu_list_units&pdu={0}&nstate={1}&slot={2}&unit={3}'><IMG SRC='images/btn-{4}'></A>"

 if len(pdulist) == 0:
  pdulist.append(pduop)
 print "<DIV CLASS='z-framed'><DIV CLASS='z-table'><TABLE WIDTH=330>"
 print "<TR><TH>PDU</TH><TH>Entry</TH><TH>Device</TH><TH style='width:63px;'>State</TH></TR>"
 for pdu in pdulist:
  avocent = Avocent(pdu)
  avocent.load_snmp()

  # Ops
  if pdu == pduop and slot and unit and nstate:
   avocent.set_state(slot,unit,nstate)
   # Avocent is not fast enough to execute something immediately after reboot op, halt output then :-)
   if nstate == 'reboot':
    from time import sleep
    sleep(10)

  for key in avocent.get_keys(aSortKey = lambda x: int(x.split('.')[0])*100+int(x.split('.')[1])):
   value = avocent.get_entry(key)
   print "<TR><TD TITLE='Open up a browser tab for {1}'><A TARGET='_blank' HREF='https://{0}:3502'>{1}</A></TD><TD>{2}</TD>".format(avocent._ip,pdu,value['slotname']+'.'+value['unit'])
   print "<TD><A CLASS='z-btnop' OP=load DIV=div_navcont LNK='ajax.cgi?call=pdu_unit_info&pdu={0}&slot={1}&unit={2}&name={3}&slotname={4}' TITLE='Edit port info' >{3}</A></TD><TD>".format(pdu,value['slot'],value['unit'],value['name'], value['slotname'])
   if value['state'] == "off":
    print optemplate.format(pdu, "on", value['slot'],value['unit'], "start")
   else:
    print optemplate.format(pdu, "off", value['slot'],value['unit'], "shutdown")
    print optemplate.format(pdu, "reboot", value['slot'],value['unit'], "reboot")
   print "</TD></TR>"
 print "</TABLE></DIV></DIV>"

def pdu_unit_info(aWeb):
 pdu  = aWeb.get_value('pdu')
 slot = aWeb.get_value('slot')
 unit = aWeb.get_value('unit')
 slotname = aWeb.get_value('slotname')
 name = aWeb.get_value('name')
 print "<DIV CLASS='z-framed z-table' style='resize: horizontal; margin-left:0px; width:420px; z-index:101; height:150px;'>"
 print "<FORM ID=pdu_form>"
 print "<INPUT NAME=slot   VALUE={} TYPE=HIDDEN>".format(slot)
 print "<INPUT NAME=unit   VALUE={} TYPE=HIDDEN>".format(unit)
 print "<INPUT NAME=pdu    VALUE={} TYPE=HIDDEN>".format(pdu)
 print "<TABLE style='width:100%'>"
 print "<TR><TH COLSPAN=2>PDU Slot Info</TH></TR>"
 print "<TR><TD>PDU:</TD><TD>{0}</TD></TR>".format(pdu)
 print "<TR><TD>Slot.Unit:</TD><TD>{0}.{1}</TD></TR>".format(slotname,unit)
 print "<TR><TD>Name:</TD><TD><INPUT NAME=name TYPE=TEXT CLASS='z-input' PLACEHOLDER='{0}'></TD></TR>".format(name)
 print "<TR><TD COLSPAN=2>&nbsp;</TD></TR>"
 print "</TABLE>"
 print "<A CLASS='z-btn z-btnop z-small-btn' DIV=update_results LNK=ajax.cgi?call=pdu_unit_update FRM=pdu_form OP=post><IMG SRC='images/btn-save.png'></A>"
 print "<SPAN style='float:right; font-size:9px;' ID=update_results></SPAN>"
 print "</FORM>"
 print "</DIV>"

#
#
#
def pdu_list_pdus(aWeb):
 db   = DB()
 db.connect()
 print "<DIV CLASS='z-framed'><DIV CLASS='z-table'><TABLE WIDTH=330>"
 print "<TR style='height:20px'><TH COLSPAN=3><CENTER>PDUs</CENTER></TH></TR>"
 print "<TR style='height:20px'><TD COLSPAN=3>"
 print "<A TITLE='Reload List' CLASS='z-btn z-small-btn z-btnop' OP=load DIV=div_navleft LNK='ajax.cgi?call=pdu_list_pdus'><IMG SRC='images/btn-reboot.png'></A>"
 print "<A TITLE='Add PDU' CLASS='z-btn z-small-btn z-btnop' OP=load DIV=div_navcont LNK='ajax.cgi?call=pdu_device_info&id=new'><IMG SRC='images/btn-add.png'></A>"
 print "</TD></TR>"
 res  = db.do("SELECT id, name, INET_NTOA(ip) as ip from pdus ORDER by name")
 data = db.get_all_rows()
 print "<TR><TH>ID</TH><TH>Name</TH><TH>IP</TH></TR>"
 for unit in data:
  print "<TR><TD>{0}</TD><TD><A CLASS='z-btnop' OP=load DIV=div_navcont LNK='ajax.cgi?call=pdu_device_info&id={0}'>{1}</A></TD><TD>{2}</TD></TR>".format(unit['id'],unit['name'],unit['ip'])
 print "</TABLE></DIV></DIV>"
 db.close()

#
#
#
def pdu_device_info(aWeb):
 id = aWeb.get_value('id')
 ip = aWeb.get_value('ip')
 ipint = sys_ip2int(ip)
 op = aWeb.get_value('op')
 name = aWeb.get_value('name')
 db = DB()
 db.connect()

 if op == 'lookup':
  # Assume lookup for now
  pdu   = Avocent(ip)
  slotl = pdu.get_slot_names()
  slotn = len(slotl)
  if slotn == 1:
   db.do("UPDATE pdus SET slots = 0, 0_slot_id = '{1}', 0_slot_name = '{2}' WHERE ip = '{0}'".format(ipint,slotl[0][0],slotl[0][1]))
  elif slotn == 2:
   db.do("UPDATE pdus SET slots = 1, 0_slot_id = '{1}', 0_slot_name = '{2}', 1_slot_id = '{3}', 1_slot_name = '{4}' WHERE ip = '{0}'".format(ipint,slotl[0][0],slotl[0][1],slotl[1][0],slotl[1][1]))
  db.commit()
 elif op == 'update':
  slots = aWeb.get_value('slots','0')
  if id == 'new':
   sql = "INSERT into pdus (name, ip, slots) VALUES ('{0}','{1}','{2}')".format(name,ipint,slots)
   res = db.do(sql)
   db.commit()
   db.do("SELECT id FROM pdus WHERE ip = '{0}'".format(ipint)) 
   res = db.get_row()
   id  = res['id']
  else:
   sql = "UPDATE pdus SET name = '{0}', ip = '{1}', slots = '{2}' WHERE id = '{3}'".format(name,ipint,slots,id)
   res = db.do(sql)
   db.commit()

 print "<DIV CLASS='z-framed z-table' style='resize: horizontal; margin-left:0px; width:420px; z-index:101; height:200px;'>"
 print "<FORM ID=pdu_device_info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(id)
 print "<TABLE style='width:100%'>"
 print "<TR><TH COLSPAN=2>PDU Device Info {}</TH></TR>".format("(new)" if id == 'new' else "")

 if id == 'new':
  pdudata = { 'id':'new', 'slots':0, '0_slot_name':'unknown', '0_slot_id':0, '1_slot_name':'unknown', '1_slot_id':1 }
  if not ip:
   ip ='127.0.0.1'
  if not name:
   name = 'new-name'
 else:
  if id:
   db.do("SELECT *, INET_NTOA(ip) as ipasc FROM pdus WHERE id = '{0}'".format(id))
  else:
   db.do("SELECT *, INET_NTOA(ip) as ipasc FROM pdus WHERE ip = '{0}'".format(ipint))
  pdudata = db.get_row()
  ip   = pdudata['ipasc']
  name = pdudata['name']

 print "<TR><TD>IP:</TD><TD><INPUT NAME=ip TYPE=TEXT CLASS='z-input' VALUE='{0}'></TD></TR>".format(ip)
 print "<TR><TD>Name:</TD><TD><INPUT NAME=name TYPE=TEXT CLASS='z-input' VALUE='{0}'></TD></TR>".format(name)
 if pdudata['slots'] == 1:
  print "<TR><TD>Right/Left slots:</TD><TD><INPUT TYPE=checkbox style='border:none;' NAME=slots VALUE=1 checked=checked></TD></TR>"
  print "<TR><TD>Slot 1 Name:</TD><TD>{}</TD></TR>".format(pdudata['0_slot_name'])
  print "<TR><TD>Slot 1 ID:</TD><TD>{}</TD></TR>".format(pdudata['0_slot_id'])
  print "<TR><TD>Slot 2 Name:</TD><TD>{}</TD></TR>".format(pdudata['1_slot_name'])
  print "<TR><TD>Slot 2 ID:</TD><TD>{}</TD></TR>".format(pdudata['1_slot_id'])
 else:
  print "<TR><TD>Right/Left slots:</TD><TD><INPUT TYPE=checkbox style='border:none;' NAME=slots VALUE=1></TD></TR>"
  print "<TR><TD>Slot 1 Name:</TD><TD>{}</TD></TR>".format(pdudata['0_slot_name'])
  print "<TR><TD>Slot 1 ID:</TD><TD>{}</TD></TR>".format(pdudata['0_slot_id'])

 db.close()
 print "</TABLE>"
 if not id == 'new':
  print "<A TITLE='Reload info' CLASS='z-btn z-btnop z-small-btn' DIV=div_navcont LNK=ajax.cgi?call=pdu_device_info&id={0} OP=load><IMG SRC='images/btn-reboot.png'></A>".format(id)
  print "<A TITLE='Remove unit' CLASS='z-btn z-btnop z-small-btn' DIV=div_navcont LNK=ajax.cgi?call=pdu_remove&id={0} OP=load><IMG SRC='images/btn-remove.png'></A>".format(id)
  print "<A TITLE='Fecth  info' CLASS='z-btn z-btnop z-small-btn' DIV=div_navcont LNK=ajax.cgi?call=pdu_device_info&id={0}&op=lookup&ip={1} OP=load><IMG SRC='images/btn-search.png'></A>".format(id,ip)
 print "<A TITLE='Update unit' CLASS='z-btn z-btnop z-small-btn' DIV=div_navcont LNK=ajax.cgi?call=pdu_device_info&op=update FRM=pdu_device_info_form OP=post><IMG SRC='images/btn-save.png'></A>"
 print "</FORM>"
 print "</DIV>"

#
# Update PDU slot info (name basically)
#
def pdu_unit_update(aWeb):
 values = aWeb.get_keys()
 values.remove('call')
 if 'name' in values:
  name = aWeb.get_value('name')
  pdu  = aWeb.get_value('pdu','0')
  slot = aWeb.get_value('slot','0')
  unit = aWeb.get_value('unit','0')
  avocent = Avocent(pdu)
  avocent.set_name(slot,unit,name)
  print "Updated name: {} for {} slot {}".format(name,pdu,slot)
 else:
  print "Name not updated"

#
#
#
def pdu_remove(aWeb):
 id = aWeb.get_value('id')
 db = DB()
 db.connect()
 db.do("DELETE FROM pdus WHERE id = '{0}'".format(id))
 db.do("UPDATE devices SET pem0_pdu_id  = '0', pem0_pdu_slot = '0' WHERE pem0_pdu_id = '{0}'".format(id))
 db.do("UPDATE devices SET pem1_pdu_id  = '0', pem1_pdu_slot = '0' WHERE pem1_pdu_id = '{0}'".format(id))
 db.do("UPDATE racks SET fk_pdu_1 = '0' WHERE fk_pdu_1 = '{0}'".format(id))
 db.do("UPDATE racks SET fk_pdu_2 = '0' WHERE fk_pdu_2 = '{0}'".format(id))
 db.commit()
 print "<B>Unit {0} deleted<B>".format(id)
 db.close()

def pdu_update_device_pdus(aWeb):
 (pem0_id,pem0_slot) = aWeb.get_value('pem0_pdu_slot_id',"0.0").split('.')
 (pem1_id,pem1_slot) = aWeb.get_value('pem1_pdu_slot_id',"0.0").split('.')
 pem0_unit = aWeb.get_value('pem0_unit','0')
 pem1_unit = aWeb.get_value('pem1_unit','0')
 hostname  = aWeb.get_value('name')
 retstr    = ""
 db = DB()
 db.connect()
 db.do("SELECT id,INET_NTOA(ip) as ip FROM pdus WHERE id = '{}' OR id = '{}'".format(pem0_id,pem1_id))
 pdus = db.get_all_dict('id')
 aWeb.log_msg("{} {} {}".format(pem0_id,pem0_slot,pem0_unit))
 if not (pem0_slot == '0' or pem0_unit == '0') and hostname:
  string = hostname+"-P0"
  avocent = Avocent(pdus[int(pem0_id)]['ip'])
  retstr = retstr + " " + avocent.set_name(pem0_slot,pem0_unit,string)
 if not (pem1_slot == '0' or pem1_unit == '0') and hostname:
  string = hostname+"-P1"
  avocent = Avocent(pdus[int(pem1_id)]['ip'])
  retstr = retstr + " " + avocent.set_name(pem1_slot,pem1_unit,string)
 db.close()
 print retstr
