"""Moduledocstring.

Ajax Racks calls module

"""
__author__= "Zacharias El Banna"                     
__version__= "1.1GA"
__status__= "Production"

from sdcp.core.GenLib import DB

################################################## Basic Rack Info ######################################################
#
# Basic rack info - right now only a display of a typical rack.. Change to table?
#

def rack_info(aWeb):
 rack = aWeb.get_value('rack', 0)
 db = DB()
 db.connect()
 db.do("SELECT name, size from racks where id = {}".format(rack))
 rackinfo = db.get_row() 
 db.do("SELECT id, hostname, rack_unit, rack_size from devices where rack_id = {}".format(rack))
 rackunits = db.get_all_dict('rack_unit')
 db.close()
 print "<DIV style='margin:10px;'><SPAN style='font-size:20px; font-weight:bold'>{}</SPAN></DIV>".format(rackinfo['name'])

 for side in ['Front','Back']:
  print "<DIV style='margin:10px 20px; float:left;'><SPAN style='font-size: 16px; font-weight:bold'>{} side</SPAN>".format(side)
  count = 1 if side == 'Front' else -1
  print "<TABLE>"
  rowspan = 0
  for index in range(rackinfo['size'],0,-1):
   print "<TR CLASS='z-rack'><TD CLASS='z-rack-indx'>{0}</TD>".format(index)
   if index == rackinfo['size'] and count == 1:
    print "<TD CLASS='z-rack-data' style='background:yellow;'><CENTER>Patch Panel</CENTER></TD>"
   else:
    if rowspan > 0:
     rowspan = rowspan - 1
    else:
     if rackunits.get(count*index,None):
      rowspan = rackunits[count*index].get('rack_size')
      print "<TD CLASS='z-rack-data' rowspan={2} style='background-color:green'><CENTER><a class='z-btnop' title='Show device info for {0}' op='load' div='div_navcont' lnk='ajax.cgi?call=device_device_info&node={1}'>{0}</a></CENTER></TD>".format(rackunits[count*index]['hostname'],rackunits[count*index]['id'],rowspan)
      rowspan = rowspan - 1
     else:
      print "<TD CLASS='z-rack-data'>&nbsp;</TD>"
   print "<TD CLASS='z-rack-indx'>{0}</TD></TR>".format(index)
  print "</TABLE>"
  print "</DIV>"

#
#
#
def rack_list_racks(aWeb):
 db   = DB()
 db.connect()
 print "<DIV CLASS='z-framed'><DIV CLASS='z-table'><TABLE WIDTH=330>"
 print "<TR style='height:20px'><TH COLSPAN=3><CENTER>Rack</CENTER></TH></TR>"
 print "<TR style='height:20px'><TD COLSPAN=3>"
 print "<A TITLE='Reload List' CLASS='z-btn z-small-btn z-btnop' OP=load DIV=div_navleft LNK='ajax.cgi?call=rack_list_racks'><IMG SRC='images/btn-reboot.png'></A>"
 print "<A TITLE='Add rack' CLASS='z-btn z-small-btn z-btnop' OP=load DIV=div_navcont LNK='ajax.cgi?call=rack_device_info&id=new'><IMG SRC='images/btn-add.png'></A>"
 print "</TD></TR>"
 res  = db.do("SELECT * from racks ORDER by name")
 data = db.get_all_rows()
 print "<TR><TH>ID</TH><TH>Name</TH><TH>Size</TH></TR>"
 for unit in data:
  print "<TR><TD>{0}</TD><TD><A CLASS='z-btnop' OP=load DIV=div_navcont LNK='ajax.cgi?call=rack_device_info&id={0}'>{1}</A></TD><TD>{2}</TD></TR>".format(unit['id'],unit['name'],unit['size'])
 print "</TABLE></DIV></DIV>"
 db.close()

#
#
#
def rack_device_info(aWeb):
 id = aWeb.get_value('id')
 db = DB()
 db.connect()
 if id == 'new':
  rack = { 'id':'new', 'name':'new-name', 'size':'48', 'fk_pdu_1':0, 'fk_pdu_2':0, 'fk_console':0 }
 else:
  db.do("SELECT * from racks WHERE id = {}".format(id))
  rack = db.get_row()

 print "<DIV CLASS='z-framed z-table' style='resize: horizontal; margin-left:0px; width:420px; z-index:101; height:185px;'>"
 print "<FORM ID=rack_device_info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(id)
 print "<TABLE style='width:100%'>"
 print "<TR><TH COLSPAN=2>Rack Info {}</TH></TR>".format("(new)" if id == 'new' else "")
 print "<TR><TD>Name:</TD><TD><INPUT NAME=name TYPE=TEXT CLASS='z-input' VALUE='{0}'></TD></TR>".format(rack['name'])
 print "<TR><TD>Size:</TD><TD><INPUT NAME=size TYPE=TEXT CLASS='z-input' VALUE='{0}'></TD></TR>".format(rack['size'])
 for key in ['pdu_1','pdu_2','console']:
  dbname = key.partition('_')[0] + "s"
  db.do("SELECT id,name from "+dbname)
  rows = db.get_all_rows()
  rows.append({'id':0, 'name':'Not Used'})
  print "<TR><TD>{0}:</TD><TD><SELECT NAME=fk_{1} CLASS='z-select'>".format(key.capitalize(),key)
  for unit in rows:
   extra = " selected" if rack["fk_"+key] == unit['id'] else ""
   print "<OPTION VALUE={0} {1}>{2}</OPTION>".format(unit['id'],extra,unit['name'])
  print "</SELECT></TD></TR>"
 db.close()
 print "</TABLE>"
 print "<A TITLE='Reload info' CLASS='z-btn z-btnop z-small-btn' DIV=div_navcont LNK=ajax.cgi?call=rack_device_info&id={0} OP=load><IMG SRC='images/btn-reboot.png'></A>".format(id)
 print "<A TITLE='Update unit' CLASS='z-btn z-btnop z-small-btn' DIV=update_results LNK=ajax.cgi?call=rack_update FRM=rack_device_info_form OP=post><IMG SRC='images/btn-save.png'></A>"
 if not id == 'new':
  print "<A TITLE='Remove unit' CLASS='z-btn z-btnop z-small-btn' DIV=div_navcont LNK=ajax.cgi?call=rack_remove&id={0} OP=load><IMG SRC='images/btn-remove.png'></A>".format(id)
 print "<SPAN style='float:right; font-size:9px;'ID=update_results></SPAN>"
 print "</FORM>"
 print "</DIV>"

#
#
#
def rack_update(aWeb):
 id = aWeb.get_value('id')
 db   = DB()
 db.connect()
 name       = aWeb.get_value('name')
 size       = aWeb.get_value('size')
 fk_pdu_1   = aWeb.get_value('fk_pdu_1')
 fk_pdu_2   = aWeb.get_value('fk_pdu_2')
 fk_console = aWeb.get_value('fk_console')
 if id == 'new':
  print "Creating new rack [new:{}]".format(name)
  sql = "INSERT into racks (name, size, fk_pdu_1, fk_pdu_2, fk_console) VALUES ('{}','{}','{}','{}','{}')".format(name,size,fk_pdu_1,fk_pdu_2,fk_console)
 else:
  print "Updated rack [{}:{}]".format(id,name)
  sql = "UPDATE racks SET name = '{}', size = '{}', fk_pdu_1 = '{}', fk_pdu_2 = '{}', fk_console = '{}' WHERE id = '{}'".format(name,size,fk_pdu_1,fk_pdu_2,fk_console,id)
 res = db.do(sql)
 db.commit()
 db.close()

#
#
#
def rack_remove(aWeb):
 id   = aWeb.get_value('id')
 db   = DB()
 db.connect()
 db.do("DELETE FROM racks WHERE id = '{0}'".format(id))
 db.do("UPDATE devices SET rack_id = '0' WHERE rack_id = '{0}'".format(id))
 db.commit()
 print "Rack {0} deleted".format(id)
 db.close()
