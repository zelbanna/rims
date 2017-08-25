"""Moduledocstring.

Ajax calls module

"""
__author__= "Zacharias El Banna"                     
__version__ = "17.6.1GA"
__status__= "Production"

import sdcp.core.GenLib as GL
from sdcp.devices.RackUtils import Avocent

############################################## PDUs ###################################################
#
# PDUs
#

def list_units(aWeb):
 domain  = aWeb.get_value('domain')
 pdulist = aWeb.get_list('pdulist')

 # For Operations:
 slot    = aWeb.get_value('slot')
 unit    = aWeb.get_value('unit')
 nstate  = aWeb.get_value('nstate')
 pduop   = aWeb.get_value('pdu')

 optemplate = "<A CLASS='z-btn z-small-btn z-op' OP=load SPIN=true DIV=div_navleft URL='ajax.cgi?call=pdu_list_units&pdu={0}&nstate={1}&slot={2}&unit={3}'><IMG SRC='images/btn-{4}'></A>"

 if len(pdulist) == 0:
  pdulist.append(pduop)
 print "<DIV CLASS=z-fframe><DIV CLASS=z-table2 style='width:330px;'>"
 print "<DIV CLASS=thead><DIV CLASS=th>PDU</DIV><DIV CLASS=th>Entry</DIV><DIV CLASS=th>Device</DIV><DIV CLASS=th style='width:63px;'>State</DIV></DIV>"
 print "<DIV CLASS=tbody>"
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
   print "<DIV CLASS=tr><DIV CLASS=td TITLE='Open up a browser tab for {1}'><A TARGET='_blank' HREF='https://{0}:3502'>{1}</A></DIV><DIV CLASS=td>{2}</DIV>".format(avocent._ip,pdu,value['slotname']+'.'+value['unit'])
   print "<DIV CLASS=td><A CLASS='z-op' OP=load DIV=div_navcont URL='ajax.cgi?call=pdu_unit_info&pdu={0}&slot={1}&unit={2}&name={3}&slotname={4}' TITLE='Edit port info' >{3}</A></DIV><DIV CLASS=td>".format(pdu,value['slot'],value['unit'],value['name'], value['slotname'])
   if value['state'] == "off":
    print optemplate.format(pdu, "on", value['slot'],value['unit'], "start")
   else:
    print optemplate.format(pdu, "off", value['slot'],value['unit'], "shutdown")
    print optemplate.format(pdu, "reboot", value['slot'],value['unit'], "reboot")
   print "&nbsp;</DIV></DIV>"
 print "</DIV></DIV></DIV>"

def unit_info(aWeb):
 op = aWeb.get_value('op')
 pdu  = aWeb.get_value('pdu')
 slot = aWeb.get_value('slot')
 unit = aWeb.get_value('unit')
 if op == 'update':
  name = aWeb.get_value('name')
  avocent = Avocent(pdu)
  avocent.set_name(slot,unit,name)
  print "Updated name: {} for {} slot {}".format(name,pdu,slot)
  return
 slotname = aWeb.get_value('slotname')
 name = aWeb.get_value('name')
 print "<DIV CLASS=z-fframe style='resize: horizontal; margin-left:0px; width:420px; z-index:101; height:150px;'>"
 print "<FORM ID=pdu_form>"
 print "<INPUT NAME=slot   VALUE={} TYPE=HIDDEN>".format(slot)
 print "<INPUT NAME=unit   VALUE={} TYPE=HIDDEN>".format(unit)
 print "<INPUT NAME=pdu    VALUE={} TYPE=HIDDEN>".format(pdu)
 print "<DIV CLASS=title>PDU Slot Info</DIV>"
 print "<DIV CLASS=z-table2 style='width:100%'><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>PDU:</DIV><DIV CLASS=td>{0}</DIV></DIV>".format(pdu)
 print "<DIV CLASS=tr><DIV CLASS=td>Slot.Unit:</DIV><DIV CLASS=td>{0}.{1}</DIV></DIV>".format(slotname,unit)
 print "<DIV CLASS=tr><DIV CLASS=td>Name:</DIV><DIV CLASS=td><INPUT NAME=name TYPE=TEXT PLACEHOLDER='{0}'></DIV></DIV>".format(name)
 print "</DIV></DIV>"
 print "<A CLASS='z-btn z-op z-small-btn' DIV=update_results URL=ajax.cgi?call=pdu_unit_info&op=update FRM=pdu_form OP=load><IMG SRC='images/btn-save.png'></A>"
 print "<SPAN style='float:right; font-size:9px;' ID=update_results></SPAN>"
 print "</FORM>"
 print "</DIV>"

#
#
#
def list_pdus(aWeb):
 db   = GL.DB()
 db.connect()
 print "<DIV CLASS=z-fframe>"
 print "<DIV CLASS=title>PDUs</DIV>"
 print "<A TITLE='Reload List' CLASS='z-btn z-small-btn z-op' OP=load DIV=div_navleft URL='ajax.cgi?call=pdu_list_pdus'><IMG SRC='images/btn-reboot.png'></A>"
 print "<A TITLE='Add PDU' CLASS='z-btn z-small-btn z-op' OP=load DIV=div_navcont URL='ajax.cgi?call=pdu_device_info&id=new'><IMG SRC='images/btn-add.png'></A>"
 print "<DIV CLASS=z-table2 style='width:99%'><DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>IP</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 res  = db.do("SELECT id, name, INET_NTOA(ip) as ip from pdus ORDER by name")
 data = db.get_all_rows()

 for unit in data:
  print "<DIV CLASS=tr><DIV CLASS=td>{0}</DIV><DIV CLASS=td><A CLASS='z-op' OP=load DIV=div_navcont URL='ajax.cgi?call=pdu_device_info&id={0}'>{1}</A></DIV><DIV CLASS=td>{2}</DIV></DIV>".format(unit['id'],unit['name'],unit['ip'])
 print "</DIV></DIV></DIV>"
 db.close()

#
#
#
def device_info(aWeb):
 id = aWeb.get_value('id')
 ip = aWeb.get_value('ip')
 op = aWeb.get_value('op')
 name = aWeb.get_value('name')
 db = GL.DB()
 db.connect()

 if op == 'lookup':
  ipint = GL.ip2int(ip)
  pdu   = Avocent(ip)
  slotl = pdu.get_slot_names()
  slotn = len(slotl)
  if slotn == 1:
   db.do("UPDATE pdus SET slots = 0, 0_slot_id = '{1}', 0_slot_name = '{2}' WHERE ip = '{0}'".format(ipint,slotl[0][0],slotl[0][1]))
  elif slotn == 2:
   db.do("UPDATE pdus SET slots = 1, 0_slot_id = '{1}', 0_slot_name = '{2}', 1_slot_id = '{3}', 1_slot_name = '{4}' WHERE ip = '{0}'".format(ipint,slotl[0][0],slotl[0][1],slotl[1][0],slotl[1][1]))
  db.commit()
 elif op == 'update':
  ipint = GL.ip2int(ip)
  slots = aWeb.get_value('slots','0')
  if id == 'new':
   sql = "INSERT into pdus (name, ip, slots) VALUES ('{0}','{1}','{2}')".format(name,ipint,slots)
   res = db.do(sql)
   db.commit()
   id = db.get_last_id()
  else:
   sql = "UPDATE pdus SET name = '{0}', ip = '{1}', slots = '{2}' WHERE id = '{3}'".format(name,ipint,slots,id)
   res = db.do(sql)
   db.commit()

 print "<DIV CLASS=z-fframe style='resize: horizontal; margin-left:0px; width:420px; z-index:101; height:200px;'>"
 print "<DIV CLASS=title>PDU Device Info {}</DIV>".format("(new)" if id == 'new' else "")
 print "<FORM ID=pdu_device_info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(id)
 print "<DIV CLASS=z-table2 style='width:100%'><DIV CLASS=tbody>"
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

 print "<DIV CLASS=tr><DIV CLASS=td>IP:</DIV><DIV CLASS=td><INPUT NAME=ip TYPE=TEXT CLASS='z-input' VALUE='{0}'></DIV></DIV>".format(ip)
 print "<DIV CLASS=tr><DIV CLASS=td>Name:</DIV><DIV CLASS=td><INPUT NAME=name TYPE=TEXT CLASS='z-input' VALUE='{0}'></DIV></DIV>".format(name)
 if pdudata['slots'] == 1:
  print "<DIV CLASS=tr><DIV CLASS=td>Right/Left slots:</DIV><DIV CLASS=td><INPUT TYPE=checkbox style='border:none;' NAME=slots VALUE=1 checked=checked></DIV></DIV>"
  print "<DIV CLASS=tr><DIV CLASS=td>Slot 1 Name:</DIV><DIV CLASS=td>{}</DIV></DIV>".format(pdudata['0_slot_name'])
  print "<DIV CLASS=tr><DIV CLASS=td>Slot 1 ID:</DIV><DIV CLASS=td>{}</DIV></DIV>".format(pdudata['0_slot_id'])
  print "<DIV CLASS=tr><DIV CLASS=td>Slot 2 Name:</DIV><DIV CLASS=td>{}</DIV></DIV>".format(pdudata['1_slot_name'])
  print "<DIV CLASS=tr><DIV CLASS=td>Slot 2 ID:</DIV><DIV CLASS=td>{}</DIV></DIV>".format(pdudata['1_slot_id'])
 else:
  print "<DIV CLASS=tr><DIV CLASS=td>Right/Left slots:</DIV><DIV CLASS=td><INPUT TYPE=checkbox style='border:none;' NAME=slots VALUE=1></DIV></DIV>"
  print "<DIV CLASS=tr><DIV CLASS=td>Slot 1 Name:</DIV><DIV CLASS=td>{}</DIV></DIV>".format(pdudata['0_slot_name'])
  print "<DIV CLASS=tr><DIV CLASS=td>Slot 1 ID:</DIV><DIV CLASS=td>{}</DIV></DIV>".format(pdudata['0_slot_id'])

 db.close()
 print "</DIV></DIV>"
 if not id == 'new':
  print "<A TITLE='Reload info' CLASS='z-btn z-op z-small-btn' DIV=div_navcont URL=ajax.cgi?call=pdu_device_info&id={0} OP=load><IMG SRC='images/btn-reboot.png'></A>".format(id)
  print "<A TITLE='Remove unit' CLASS='z-btn z-op z-small-btn' DIV=div_navcont URL=ajax.cgi?call=pdu_remove&id={0} OP=load><IMG SRC='images/btn-remove.png'></A>".format(id)
  print "<A TITLE='Fecth  info' CLASS='z-btn z-op z-small-btn' DIV=div_navcont URL=ajax.cgi?call=pdu_device_info&id={0}&op=lookup&ip={1} OP=load><IMG SRC='images/btn-search.png'></A>".format(id,ip)
 print "<A TITLE='Update unit' CLASS='z-btn z-op z-small-btn' DIV=div_navcont URL=ajax.cgi?call=pdu_device_info&op=update FRM=pdu_device_info_form OP=load><IMG SRC='images/btn-save.png'></A>"
 print "</FORM>"
 print "</DIV>"

#
#
#
def remove(aWeb):
 id = aWeb.get_value('id')
 db = GL.DB()
 db.connect()
 db.do("UPDATE rackinfo SET pem0_pdu_unit = 0, pem0_pdu_slot = 0 WHERE pem0_pdu_id = '{0}'".format(id))
 db.do("UPDATE rackinfo SET pem1_pdu_unit = 0, pem1_pdu_slot = 0 WHERE pem1_pdu_id = '{0}'".format(id))
 db.do("DELETE FROM pdus WHERE id = '{0}'".format(id))
 db.commit()
 print "<B>PDU {0} deleted<B>".format(id)
 db.close()
