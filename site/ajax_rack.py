"""Module docstring.

Ajax Racks calls module

"""
__author__= "Zacharias El Banna"                     
__version__ = "17.6.1GA"
__status__= "Production"

import sdcp.core.GenLib as GL

################################################## Basic Rack Info ######################################################
#
#
#
def list_racks(aWeb):
 db   = GL.DB()
 db.connect()
 print "<DIV CLASS=z-frame>"
 print "<DIV CLASS=title>Rack</DIV>"
 print "<A TITLE='Reload List' CLASS='z-btn z-small-btn z-op' OP=load DIV=div_content_left URL='ajax.cgi?call=rack_list_racks'><IMG SRC='images/btn-reboot.png'></A>"
 print "<A TITLE='Add rack' CLASS='z-btn z-small-btn z-op' OP=load DIV=div_content_right URL='ajax.cgi?call=rack_info&id=new'><IMG SRC='images/btn-add.png'></A>"
 print "<DIV CLASS=z-table style='width:99%'>"
 print "<DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>Size</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 res  = db.do("SELECT * from racks ORDER by name")
 data = db.get_all_rows()
 for unit in data:
  print "<DIV CLASS=tr><DIV CLASS=td>{0}</DIV><DIV CLASS=td><A CLASS='z-op' OP=load DIV=div_content_right URL='ajax.cgi?call=rack_info&id={0}'>{1}</A></DIV><DIV CLASS=td>{2}</DIV></DIV>".format(unit['id'],unit['name'],unit['size'])
 print "</DIV></DIV></DIV>"
 db.close()

#
# Basic rack info - right now only a display of a typical rack.. Change to table?
#
def inventory(aWeb):
 rack = aWeb.get_value('rack', 0)
 db = GL.DB()
 db.connect()
 db.do("SELECT name, size from racks where id = {}".format(rack))
 rackinfo = db.get_row() 
 db.do("SELECT devices.id, hostname, rackinfo.rack_unit, rackinfo.rack_size, bookings.user_id FROM devices LEFT JOIN bookings ON devices.id = bookings.device_id LEFT JOIN rackinfo ON devices.id = rackinfo.device_id WHERE rack_id = {}".format(rack))
 rackunits = db.get_all_dict('rack_unit')
 db.close()
 print "<DIV style='margin:10px;'><SPAN style='font-size:20px; font-weight:bold'>{}</SPAN></DIV>".format(rackinfo['name'])

 for side in ['Front','Back']:
  print "<DIV style='margin:10px 20px; float:left;'><SPAN style='font-size: 16px; font-weight:bold'>{} side</SPAN>".format(side)
  count = 1 if side == 'Front' else -1
  print "<TABLE CLASS=z-rack>"
  rowspan = 0
  for index in range(rackinfo['size'],0,-1):
   print "<TR><TD CLASS=indx>{0}</TD>".format(index)
   if index == rackinfo['size'] and count == 1:
    print "<TD CLASS=data style='background:yellow;'><CENTER>Patch Panel</CENTER></TD>"
   else:
    if rowspan > 0:
     rowspan = rowspan - 1
    else:
     s_index = count*index
     if rackunits.get(s_index):
      print "<!-- {} -->".format(rackunits[s_index].get('user_id'))
      rowspan = rackunits[s_index].get('rack_size')
      print "<TD CLASS=data rowspan={2} style='background-color:{3}'><CENTER><A CLASS='z-op' TITLE='Show device info for {0}' OP=load DIV='div_content_right' URL='ajax.cgi?call=device_info&id={1}'>{0}</A></CENTER></TD>".format(rackunits[s_index]['hostname'],rackunits[s_index]['id'],rowspan,"#00cc66" if not rackunits[s_index].get('user_id') else "#df3620")
      rowspan = rowspan - 1
     else:
      print "<TD CLASS=data style='line-height:14px;'>&nbsp;</TD>"
   print "<TD CLASS=indx>{0}</TD></TR>".format(index)
  print "</TABLE></DIV>"

#
#
#
def info(aWeb):
 import sdcp.PackageContainer as PC
 from os import listdir, path
 id = aWeb.get_value('id')
 db = GL.DB()
 db.connect()
 if id == 'new':
  rack = { 'id':'new', 'name':'new-name', 'size':'48', 'fk_pdu_1':None, 'fk_pdu_2':None, 'fk_console':None }
 else:
  db.do("SELECT * from racks WHERE id = {}".format(id))
  rack = db.get_row()
 print "<DIV CLASS=z-frame style='resize: horizontal; margin-left:0px; width:420px; z-index:101; height:200px;'>"
 print "<FORM ID=rack_info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(id)
 print "<DIV CLASS=title>Rack Info {}</DIV>".format("(new)" if id == 'new' else "")
 print "<DIV CLASS=z-table style='width:100%'><DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>Name:</DIV><DIV CLASS=td><INPUT NAME=name TYPE=TEXT VALUE='{0}'></DIV></DIV>".format(rack['name'])
 print "<DIV CLASS=tr><DIV CLASS=td>Size:</DIV><DIV CLASS=td><INPUT NAME=size TYPE=TEXT VALUE='{0}'></DIV></DIV>".format(rack['size'])
 for key in ['pdu_1','pdu_2','console']:
  dbname = key.partition('_')[0]
  db.do("SELECT id,name from {0}s".format(dbname))
  rows = db.get_all_rows()
  rows.append({'id':'NULL', 'name':"No {}".format(dbname.capitalize())})
  print "<DIV CLASS=tr><DIV CLASS=td>{0}:</DIV><DIV CLASS=td><SELECT NAME=fk_{1}>".format(key.capitalize(),key)
  for unit in rows:
   extra = " selected" if (rack.get("fk_"+key) == unit['id']) or (not rack.get("fk_"+key) and unit['id'] == 'NULL') else ""
   print "<OPTION VALUE={0} {1}>{2}</OPTION>".format(unit['id'],extra,unit['name'])   
  print "</SELECT></DIV></DIV>"
 print "<DIV CLASS=tr><DIV CLASS=td>Image</DIV><DIV CLASS=td><SELECT NAME=image_url>"
 print "<OPTION VALUE=NULL>No picture</OPTION>"
 for image in listdir(path.join(PC.generic_docroot,"images")):
  extra = " selected" if (rack.get("image_url") == image) or (not rack.get('image_url') and image == 'NULL') else ""
  if image[-3:] == "png" or image[-3:] == "jpg":
   print "<OPTION VALUE={0} {1}>{2}</OPTION>".format(image,extra,image[:-4])
 print "</SELECT></DIV></DIV>"
 db.close()
 print "</DIV></DIV>"
 print "</FORM>"
 print "<A TITLE='Reload info' CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=ajax.cgi?call=rack_info&id={0} OP=load><IMG SRC='images/btn-reboot.png'></A>".format(id)
 print "<A TITLE='Update unit' CLASS='z-btn z-op z-small-btn' DIV=update_results URL=ajax.cgi?call=rack_update FRM=rack_info_form OP=load><IMG SRC='images/btn-save.png'></A>"
 if not id == 'new':
  print "<A TITLE='Remove unit' CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=ajax.cgi?call=rack_remove&id={0} OP=load><IMG SRC='images/btn-remove.png'></A>".format(id)
 print "<SPAN style='float:right; font-size:9px;'ID=update_results></SPAN>"
 print "</DIV>"

#
#
#
def update(aWeb):
 id = aWeb.get_value('id')
 db   = GL.DB()
 db.connect()
 name       = aWeb.get_value('name')
 size       = aWeb.get_value('size')
 fk_pdu_1   = aWeb.get_value('fk_pdu_1')
 fk_pdu_2   = aWeb.get_value('fk_pdu_2')
 fk_console = aWeb.get_value('fk_console')
 image_url  = aWeb.get_value('image_url')
 if id == 'new':
  print "Creating new rack [new:{}]".format(name)
  sql = "INSERT into racks (name, size, fk_pdu_1, fk_pdu_2, fk_console, image_url) VALUES ('{}','{}',{},{},{},'{}')".format(name,size,fk_pdu_1,fk_pdu_2,fk_console,image_url)
 else:
  print "Updated rack [{}:{}]".format(id,name)
  sql = "UPDATE racks SET name = '{}', size = '{}', fk_pdu_1 = {}, fk_pdu_2 = {}, fk_console = {}, image_url='{}' WHERE id = '{}'".format(name,size,fk_pdu_1,fk_pdu_2,fk_console,image_url,id)
 res = db.do(sql)
 db.commit()
 db.close()

#
#
#
def remove(aWeb):
 id   = aWeb.get_value('id')
 db   = GL.DB()
 db.connect()
 res  = db.do("SELECT id FROM devices WHERE rack_id = {0}".format(id))
 devs = db.get_all_rows()
 for dev in devs:
  db.do("DELETE FROM rackinfo WHERE device_id = {0}".format(dev['id']))
 db.do("DELETE FROM racks WHERE id = {0}".format(id))
 db.commit()
 print "Rack {0} deleted".format(id)
 db.close()
