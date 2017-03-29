"""Moduledocstring.

Ajax Racks calls module

"""
__author__= "Zacharias El Banna"                     
__version__= "1.0GA"
__status__= "Production"

################################################## Basic Rack Info ######################################################
#
# Basic rack info - right now only a display of a typical rack.. Change to table?
#

def rack_info(aWeb):
 rack = aWeb.get_value('rack', 0)
 print "<DIV style='padding:20px;'>"
 print "<H1>Rack {}</H1>".format(rack)
 print "Data: [{}]".format(" ".join(aWeb.get_keys()))
 print "<DIV style=' background-image: url(images/rack48u.png); background-position: center; background-repeat: no-repeat; height:1680px; width:770px;'></DIV>"
 print "</DIV>"

def rack_infra(aWeb):
 from sdcp.core.GenLib import DB, sys_int2ip 
 db   = DB()
 db.connect()
 type = aWeb.get_value('type','racks')
 print "<DIV CLASS='z-framed'>"
 print "<DIV CLASS='z-table'><TABLE WIDTH=330>"
 print "<TR style='height:20px'><TH COLSPAN=3><CENTER>{0}</CENTER></TH></TR>".format(type.capitalize())
 print "<TR style='height:20px'><TD COLSPAN=3>"
 print "<A CLASS='z-btn z-small-btn z-btnop' OP=load DIV=div_navcont LNK='ajax.cgi?call=rack_data&type={0}&id=new'><IMG SRC='images/btn-add.png'></A>".format(type)
 print "<A CLASS='z-btn z-small-btn z-btnop' OP=load DIV=div_navleft LNK='ajax.cgi?call=rack_infra&type={0}'><IMG SRC='images/btn-reboot.png'></A>".format(type)
 print "</TD></TR>"
 res  = db.do("SELECT * from {} ORDER by name".format(type))
 data = db.get_all_rows()
 if type == 'pdus' or type == 'consoles':
  print "<TR><TH>ID</TH><TH>Name</TH><TH>IP</TH></TR>"
  for unit in data:
   print "<TR><TD>{0}</TD><TD><A CLASS='z-btnop' OP=load DIV=div_navcont LNK='ajax.cgi?call=rack_data&type={3}&id={0}&name={1}&ip={2}'>{1}</A></TD><TD>{2}</TD>".format(unit['id'],unit['name'],sys_int2ip(unit['ip']),type)
 elif type == 'racks':
  print "<TR><TH>ID</TH><TH>Name</TH><TH>Size</TH></TR>"
  for unit in data:
   print "<TR><TD>{0}</TD><TD><A CLASS='z-btnop' OP=load DIV=div_navcont LNK='ajax.cgi?call=rack_data&type={3}&id={0}&name={1}'>{1}</A></TD><TD>{2}</TD>".format(unit['id'],unit['name'],unit['size'],type)  
 print "</TABLE></DIV>"
 db.close()

#
#
#
def rack_data(aWeb):
 type = aWeb.get_value('type')
 id   = aWeb.get_value('id','new')
 name = aWeb.get_value('name','new-name')
 ip   = aWeb.get_value('ip','127.0.0.1') 

 print "<DIV CLASS='z-framed z-table' style='resize: horizontal; margin-left:0px; width:420px; z-index:101; height:170px;'>"
 print "<FORM ID=rack_data_form>"
 print "<INPUT TYPE=HIDDEN NAME=type VALUE={}>".format(type)
 print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(id)
 print "<TABLE style='width:100%'>"
 print "<TR><TH COLSPAN=2>{} Info {}</TH></TR>".format(type[:-1].capitalize(), "(new)" if id == 'new' else "")

 if type == "pdus":
  print "<TR><TD>IP:</TD><TD><INPUT NAME=ip TYPE=TEXT CLASS='z-input' VALUE='{0}'></TD></TR>".format(ip)
  print "<TR><TD>Name:</TD><TD><INPUT NAME=name TYPE=TEXT CLASS='z-input' VALUE='{0}'></TD></TR>".format(name)
 if type == 'consoles':
  print "<TR><TD>IP:</TD><TD><INPUT NAME=ip TYPE=TEXT CLASS='z-input' VALUE='{0}'></TD></TR>".format(ip)
  print "<TR><TD>Name:</TD><TD><INPUT NAME=name TYPE=TEXT CLASS='z-input' VALUE='{0}'></TD></TR>".format(name)
 if type == 'racks':
  from sdcp.core.GenLib import DB
  db = DB()
  db.connect()
  rack = {}
  if id == 'new':
   rack = { 'id':'new', 'name':'new-name', 'size':'48', 'fk_pdu_1':0, 'fk_pdu_2':0, 'fk_console':0 }
  else:
   db.do("SELECT * from racks WHERE id = {}".format(id))
   rack = db.get_row()
  db.do("SELECT id,name from pdus")
  pdus = db.get_all_rows()
  pdus.append({'id':0, 'name':'Not Used'})
  db.do("SELECT id,name from consoles")
  consoles = db.get_all_rows()
  consoles.append({'id':0, 'name':'Not Used'})
  db.close()
  print "<TR><TD>Name:</TD><TD><INPUT NAME=name TYPE=TEXT CLASS='z-input' VALUE='{0}'></TD></TR>".format(name)
  print "<TR><TD>Size:</TD><TD><INPUT NAME=size TYPE=TEXT CLASS='z-input' VALUE='{0}'></TD></TR>".format(rack['size'])
  print "<TR><TD>PDU_1:</TD><TD><SELECT NAME=fk_pdu_1 CLASS='z-select'>"
  for unit in pdus:
   extra = " selected" if rack['fk_pdu_1'] == unit['id'] else ""
   print "<OPTION VALUE={0} {1}>{2}</OPTION>".format(unit['id'],extra,unit['name'])
  print "</SELECT></TD></TR>"

  print "<TR><TD>PDU_2:</TD><TD><SELECT NAME=fk_pdu_2 CLASS='z-select'>"
  for unit in pdus:
   extra = " selected" if rack['fk_pdu_2'] == unit['id'] else ""
   print "<OPTION VALUE={0} {1}>{2}</OPTION>".format(unit['id'],extra,unit['name'])
  print "</SELECT></TD></TR>"

  print "<TR><TD>Console:</TD><TD><SELECT NAME=fk_console CLASS='z-select'>"
  for unit in consoles:
   extra = " selected" if rack['fk_console'] == unit['id'] else ""
   print "<OPTION VALUE={0} {1}>{2}</OPTION>".format(unit['id'],extra,unit['name'])
  print "</SELECT></TD></TR>"
 print "</TABLE>"
 print "<A TITLE='Update unit' CLASS='z-btn z-btnop z-small-btn' DIV=update_results LNK=ajax.cgi?call=rack_update FRM=rack_data_form OP=post><IMG SRC='images/btn-save.png'></A>"
 if not id == 'new':
  print "<A TITLE='Remove unit' CLASS='z-btn z-btnop z-small-btn' DIV=div_navcont LNK=ajax.cgi?call=rack_remove&type={0}&id={1} OP=load><IMG SRC='images/btn-remove.png'></A>".format(type,id)
 print "&nbsp;<SPAN ID=update_results></SPAN>"
 print "</FORM>"
 print "</DIV>"

#
#
#
def rack_update(aWeb):
 from sdcp.core.GenLib import DB, sys_int2ip, sys_ip2int 
 values = aWeb.get_keys()
 values.remove('call')
 db   = DB()
 db.connect()
 type = aWeb.get_value('type')
 id   = aWeb.get_value('id')
 name = aWeb.get_value('name')
 if type == 'pdus':
  ip   = aWeb.get_value('ip')
  ipint = sys_ip2int(ip)
  sql = ""
  if id == 'new':
   print "New {} created".format(type[:-1])
   sql = "INSERT into {0} (name, ip) VALUES ('{1}','{2}')".format(type,name,ipint)
  else:
   print "Updated {} {}".format(type[:-1],id)
   sql = "UPDATE {0} SET name = '{1}', ip = '{2}' WHERE id = '{3}'".format(type,name,ipint,id)
  res = db.do(sql)
  db.commit()
 elif type == 'consoles':
  ip   = aWeb.get_value('ip')
  ipint = sys_ip2int(ip)
  sql = ""
  if id == 'new':
   print "New {} created".format(type[:-1])
   sql = "INSERT into {0} (name, ip) VALUES ('{1}','{2}')".format(type,name,ipint)
  else:
   print "Updated {} {}".format(type[:-1],id)
   sql = "UPDATE {0} SET name = '{1}', ip = '{2}' WHERE id = '{3}'".format(type,name,ipint,id)
  res = db.do(sql)
  db.commit()  
 elif type == 'racks':
  size       = aWeb.get_value('size')
  fk_pdu_1   = aWeb.get_value('fk_pdu_1')
  fk_pdu_2   = aWeb.get_value('fk_pdu_2')
  fk_console = aWeb.get_value('fk_console')
  if id == 'new':
   print "New rack created"
   sql = "INSERT into racks (name, size, fk_pdu_1, fk_pdu_2, fk_console) VALUES ('{}','{}','{}','{}','{}')".format(name,size,fk_pdu_1,fk_pdu_2,fk_console)
  else:
   print "Updated rack {}".format(id)
   sql = "UPDATE racks SET name = '{}', size = '{}', fk_pdu_1 = '{}', fk_pdu_2 = '{}', fk_console = '{}' WHERE id = '{}'".format(name,size,fk_pdu_1,fk_pdu_2,fk_console,id)
  res = db.do(sql)
  db.commit()
 else:
  print "unknown type"
 db.close()

#
#
#
def rack_remove(aWeb):
 from sdcp.core.GenLib import DB
 type = aWeb.get_value('type')
 id   = aWeb.get_value('id')
 db   = DB()
 db.connect()
 db.do("DELETE FROM {0} WHERE id = '{1}'".format(type,id))
 db.do("UPDATE devices SET {}_id = '0' WHERE {}_id = '{1}'".format(type[:-1],id))
 db.commit()
 print "Unit {} of type {} deleted".format(id,type)
 db.close()
