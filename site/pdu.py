"""Moduledocstring.

Ajax calls module

"""
__author__= "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__= "Production"

############################################## PDUs ###################################################
#
# PDUs
#
def list(aWeb):
 from sdcp.core.dbase import DB
 print "<DIV CLASS=z-frame>"
 print "<DIV CLASS=title>PDUs</DIV>"
 print "<A TITLE='Reload List' CLASS='z-btn z-small-btn z-op' DIV=div_content_left  URL='sdcp.cgi?call=pdu_list'><IMG SRC='images/btn-reload.png'></A>"
 print "<A TITLE='Add PDU' CLASS='z-btn z-small-btn z-op'     DIV=div_content_right URL='sdcp.cgi?call=pdu_info&id=new'><IMG SRC='images/btn-add.png'></A>"
 print "<DIV CLASS=z-table><DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>IP</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 with DB() as db:
  res  = db.do("SELECT id, name, INET_NTOA(ip) as ip from pdus ORDER by name")
  data = db.get_rows()
  for unit in data:
   print "<DIV CLASS=tr><DIV CLASS=td>{0}</DIV><DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL='sdcp.cgi?call=pdu_info&id={0}'>{1}</A></DIV><DIV CLASS=td>{2}</DIV></DIV>".format(unit['id'],unit['name'],unit['ip'])
 print "</DIV></DIV></DIV>"

#
#
#
def info(aWeb):
 from sdcp.devices.avocent import Device
 from sdcp.core.dbase import DB
 id = aWeb['id']
 ip = aWeb['ip']
 with DB() as db:
  if aWeb['op'] == 'lookup':
   pdu   = Device(ip)
   slotl = pdu.get_slot_names()
   slotn = len(slotl)
   if slotn == 1:
    db.do("UPDATE pdus SET slots = 0, 0_slot_id = '{}', 0_slot_name = '{}' WHERE ip = INET_ATON('{}')".format(slotl[0][0],slotl[0][1],ip))
   elif slotn == 2:
    db.do("UPDATE pdus SET slots = 1, 0_slot_id = '{}', 0_slot_name = '{}', 1_slot_id = '{}', 1_slot_name = '{}' WHERE ip = INET_ATON('{}')".format(slotl[0][0],slotl[0][1],slotl[1][0],slotl[1][1],ip))
  elif aWeb['op'] == 'update':
   slots = aWeb.get('slots','0')
   if id == 'new':
    sql = "INSERT into pdus (name, ip, slots) VALUES ('{}',INET_ATON('{}'),'{}')".format(name,aWeb['ip'],slots)
    res = db.do(sql)
    id = db.get_last_id()
   else:
    sql = "UPDATE pdus SET name = '{}', ip = INET_ATON('{}'), slots = '{}' WHERE id = '{}'".format(name,aWeb['ip'],slots,id)
    res = db.do(sql)

  if id == 'new':
   pdudata = { 'id':'new', 'slots':0, '0_slot_name':'unknown', '0_slot_id':0, '1_slot_name':'unknown', '1_slot_id':1, 'ipasc':'127.0.0.1' if not ip else ip,'name':'new-name' if not aWeb['name'] else aWeb['name'] }
  else:
   if id:
    db.do("SELECT pdus.*, INET_NTOA(ip) as ipasc FROM pdus WHERE id = '{}'".format(id))
   else:
    db.do("SELECT pdus.*, INET_NTOA(ip) as ipasc FROM pdus WHERE ip = INET_ATON('{}')".format(ip))
   pdudata = db.get_row()

 print "<DIV CLASS=z-frame style='resize: horizontal; margin-left:0px; width:420px; z-index:101; height:200px;'>"
 print "<DIV CLASS=title>PDU Device Info {}</DIV>".format("(new)" if id == 'new' else "")
 print "<FORM ID=pdu_info_form>"
 print "<DIV CLASS=z-table><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>IP:</DIV><DIV CLASS=td><INPUT NAME=ip TYPE=TEXT VALUE='{0}'></DIV></DIV>".format(pdudata['ipasc'])
 print "<DIV CLASS=tr><DIV CLASS=td>Name:</DIV><DIV CLASS=td><INPUT NAME=name TYPE=TEXT VALUE='{0}'></DIV></DIV>".format(pdudata['name'])
 if pdudata['slots'] == 1:
  print "<DIV CLASS=tr><DIV CLASS=td>Right/Left slots:</DIV><DIV CLASS=td><INPUT TYPE=checkbox NAME=slots VALUE=1 checked=checked></DIV></DIV>"
  print "<DIV CLASS=tr><DIV CLASS=td>Slot 1 Name:</DIV><DIV CLASS=td>{}</DIV></DIV>".format(pdudata['0_slot_name'])
  print "<DIV CLASS=tr><DIV CLASS=td>Slot 1 ID:</DIV><DIV CLASS=td>{}</DIV></DIV>".format(pdudata['0_slot_id'])
  print "<DIV CLASS=tr><DIV CLASS=td>Slot 2 Name:</DIV><DIV CLASS=td>{}</DIV></DIV>".format(pdudata['1_slot_name'])
  print "<DIV CLASS=tr><DIV CLASS=td>Slot 2 ID:</DIV><DIV CLASS=td>{}</DIV></DIV>".format(pdudata['1_slot_id'])
 else:
  print "<DIV CLASS=tr><DIV CLASS=td>Right/Left slots:</DIV><DIV CLASS=td><INPUT TYPE=checkbox NAME=slots VALUE=1></DIV></DIV>"
  print "<DIV CLASS=tr><DIV CLASS=td>Slot 1 Name:</DIV><DIV CLASS=td>{}</DIV></DIV>".format(pdudata['0_slot_name'])
  print "<DIV CLASS=tr><DIV CLASS=td>Slot 1 ID:</DIV><DIV CLASS=td>{}</DIV></DIV>".format(pdudata['0_slot_id'])

 print "</DIV></DIV>"
 if not id == 'new':
  print "<A TITLE='Reload info' CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=sdcp.cgi?call=pdu_info&id={}><IMG SRC='images/btn-reload.png'></A>".format(id)
  print "<A TITLE='Remove unit' CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=sdcp.cgi?call=pdu_remove&id={}><IMG SRC='images/btn-remove.png'></A>".format(id)
  print "<A TITLE='Fetch  info' CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=sdcp.cgi?call=pdu_info&id={}&op=lookup&ip={}><IMG SRC='images/btn-search.png'></A>".format(id,pdudata['ipasc'])
 print "<A  TITLE='Update unit' CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=sdcp.cgi?call=pdu_info&id={}&op=update FRM=pdu_info_form><IMG SRC='images/btn-save.png'></A>".format(id)
 print "</FORM>"
 print "</DIV>"

#
#
def remove(aWeb):
 from sdcp.core.dbase import DB
 with DB() as db:
  db.do("UPDATE rackinfo SET pem0_pdu_unit = 0, pem0_pdu_slot = 0 WHERE pem0_pdu_id = '{0}'".format(aWeb['id']))
  db.do("UPDATE rackinfo SET pem1_pdu_unit = 0, pem1_pdu_slot = 0 WHERE pem1_pdu_id = '{0}'".format(aWeb['id']))
  db.do("DELETE FROM pdus WHERE id = '{0}'".format(aWeb['id']))
  print "<B>PDU {0} deleted<B>".format(aWeb['id'])

####################################### Device Operations #########################################
#
#
def unit_info(aWeb):
 from sdcp.devices.avocent import Device
 if aWeb['op'] == 'update':
  avocent = Device(aWeb['pdu'])
  avocent.set_name(aWeb['slot'],aWeb['unit'],aWeb['name'])
  print "Updated name: {} for {} slot {}".format(aWeb['name'],aWeb['pdu'],aWeb['slot'])
  return
 print "<DIV CLASS=z-frame style='resize: horizontal; margin-left:0px; width:420px; z-index:101; height:150px;'>"
 print "<FORM ID=pdu_form>"
 print "<INPUT NAME=slot   VALUE={} TYPE=HIDDEN>".format(aWeb['slot'])
 print "<INPUT NAME=unit   VALUE={} TYPE=HIDDEN>".format(aWeb['unit'])
 print "<INPUT NAME=pdu    VALUE={} TYPE=HIDDEN>".format(aWeb['pdu'])
 print "<DIV CLASS=title>PDU Unit Info</DIV>"
 print "<DIV CLASS=z-table><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>PDU:</DIV><DIV CLASS=td>{0}</DIV></DIV>".format(aWeb['pdu'])
 print "<DIV CLASS=tr><DIV CLASS=td>Slot.Unit:</DIV><DIV CLASS=td>{0}.{1}</DIV></DIV>".format(aWeb['slotname'],aWeb['unit'])
 print "<DIV CLASS=tr><DIV CLASS=td>Name:</DIV><DIV CLASS=td><INPUT NAME=name TYPE=TEXT PLACEHOLDER='{0}'></DIV></DIV>".format(aWeb['name'])
 print "</DIV></DIV>"
 print "<A CLASS='z-btn z-op z-small-btn' DIV=update_results URL=sdcp.cgi?call=pdu_unit_info&op=update FRM=pdu_form><IMG SRC='images/btn-save.png'></A>"
 print "<SPAN style='float:right; font-size:9px;' ID=update_results></SPAN>"
 print "</FORM>"
 print "</DIV>"

#
#
def inventory(aWeb):
 pdulist = aWeb.form.getlist('pdulist')
 if len(pdulist) == 0:
  pdulist.append(aWeb['pduop'])

 print "<DIV CLASS=z-frame>"
 print "<A CLASS='z-op z-btn z-small-btn' DIV=div_content_left SPIN=true  URL='sdcp.cgi?{}'><IMG SRC=images/btn-reload.png></A>".format(aWeb.get_args())
 print "<DIV CLASS=z-table><DIV CLASS=thead><DIV CLASS=th>PDU</DIV><DIV CLASS=th>Position</DIV><DIV CLASS=th>Device</DIV><DIV CLASS=th style='width:63px;'>State</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 from sdcp.devices.avocent import Device
 counter = 0
 for pdu in pdulist:
  avocent = Device(pdu)
  avocent.load_snmp()
  for key in avocent.get_keys(aSortKey = lambda x: int(x.split('.')[0])*100+int(x.split('.')[1])):
   counter += 1
   value = avocent.get_entry(key)
   print "<DIV CLASS=tr><DIV CLASS=td TITLE='Open up a browser tab for {1}'><A TARGET='_blank' HREF='https://{0}:3502'>{1}</A></DIV><DIV CLASS=td>{2}</DIV>".format(avocent._ip,pdu,value['slotname']+'.'+value['unit'])
   print "<DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL='sdcp.cgi?call=pdu_unit_info&pdu={0}&slot={1}&unit={2}&name={3}&slotname={4}' TITLE='Edit port info' >{3}</A></DIV><DIV CLASS=td ID=div_pdu_{5}>".format(pdu,value['slot'],value['unit'],value['name'], value['slotname'],counter)
   _pdu_options(pdu,value['slot'],value['unit'],value['state'],counter)
   print "</DIV></DIV>"
 print "</DIV></DIV></DIV>"

#
#
def op(aWeb):
 from sdcp.devices.avocent import Device
 avocent = Device(aWeb['ip'])
 avocent.set_state(aWeb['slot'],aWeb['unit'],aWeb['nstate'])
 # Avocent is not fast enough to execute something immediately after op, halt output then :-)
 from time import sleep
 sleep(10 if aWeb['nstate'] == 'reboot' else 4)
 _pdu_options(aWeb['ip'],aWeb['slot'],aWeb['unit'],avocent.get_state(aWeb['slot'],aWeb['unit'])['state'],aWeb['id'])

#
#
def _pdu_options(aIP,aSlot,aUnit,aState,aID):
 optemplate = "<A CLASS='z-btn z-small-btn z-op' SPIN=div_content_left DIV=div_pdu_"+str(aID)+" URL='sdcp.cgi?call=pdu_op&ip="+aIP+"&slot="+aSlot+"&unit="+aUnit+"&id="+str(aID)+"&nstate={0}'><IMG SRC='images/btn-{1}'></A>"
 print "&nbsp;"
 if aState == "off":
  print optemplate.format("on", "start")
 else:
  print optemplate.format("off", "shutdown")
  print optemplate.format("reboot", "reboot")
