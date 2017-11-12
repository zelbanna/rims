"""Module docstring.

Ajax Racks calls module

"""
__author__= "Zacharias El Banna"                     
__version__ = "17.11.01GA"
__status__= "Production"

from sdcp.core.dbase import DB

################################################## Basic Rack Info ######################################################

def main(aWeb):
 with DB() as db:
  db.do("SELECT id,name,image_url from racks")
  racks = db.get_rows()
 print "<CENTER><H1>Rack Overview</H1></CENTER>"
 print "<DIV CLASS=z-centered>"
 rackstr = "<DIV STYLE='float:left; margin:6px;'><A TITLE='{0}' CLASS=z-op DIV=div_main_cont URL=sdcp.cgi?call=device_main&target=rack_id&arg={0}><IMG STYLE='max-height:400px; max-width:200px;' ALT='{1} ({2})' SRC='images/{2}'></A></DIV>"
 print "<DIV STYLE='float:left; margin:6px;'><A CLASS=z-op DIV=div_main_cont URL=sdcp.cgi?call=device_main&target=vm&arg=1><IMG STYLE='max-height:400px; max-width:200px;' ALT='VMs' SRC='images/hypervisor.png'></A></DIV>"
 for rack in racks:
  print rackstr.format(rack['id'], rack['name'], rack['image_url'])
 print "</DIV>"

#
#
def list(aWeb):
 print "<DIV CLASS=z-frame>"
 print "<DIV CLASS=title>Rack</DIV>"
 print "<A TITLE='Reload List' CLASS='z-btn z-small-btn z-op' DIV=div_content_left URL='sdcp.cgi?call=rack_list'><IMG SRC='images/btn-reload.png'></A>"
 print "<A TITLE='Add rack' CLASS='z-btn z-small-btn z-op' DIV=div_content_right URL='sdcp.cgi?call=rack_info&id=new'><IMG SRC='images/btn-add.png'></A>"
 print "<DIV CLASS=z-table>"
 print "<DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>Size</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 with DB() as db:
  res  = db.do("SELECT racks.* from racks ORDER by name")
  data = db.get_rows()
  for unit in data:
   print "<DIV CLASS=tr><DIV CLASS=td>{0}</DIV><DIV CLASS=td><A CLASS='z-op' DIV=div_content_right URL='sdcp.cgi?call=rack_info&id={0}'>{1}</A></DIV><DIV CLASS=td>{2}</DIV></DIV>".format(unit['id'],unit['name'],unit['size'])
 print "</DIV></DIV></DIV>"

#
#
def inventory(aWeb):
 rack = aWeb.get('rack', 0)
 with DB() as db:
  db.do("SELECT name, size from racks where id = {}".format(rack))
  ri = db.get_row() 
  db.do("SELECT devices.id, hostname, rackinfo.rack_unit, rackinfo.rack_size, bookings.user_id FROM devices LEFT JOIN bookings ON devices.id = bookings.device_id LEFT JOIN rackinfo ON devices.id = rackinfo.device_id WHERE rackinfo.rack_id = {}".format(rack))
  devs = db.get_rows()
 size = ri['size']
 print "<DIV style='display:grid; justify-items:stretch; align-items:stretch; margin:10px; grid: repeat({}, 20px)/20px 220px 20px 20px 20px 220px 20px;'>".format(size)
 # Create rack and some text, then place devs
 print "<DIV STYLE='grid-column:1/4; grid-row:1; justify-self:center; font-weight:bold; font-size:14px;'>Front</DIV>"
 print "<DIV STYLE='grid-column:5/8; grid-row:1; justify-self:center; font-weight:bold; font-size:14px;'>Back</DIV>"
 print "<DIV STYLE='grid-column:2;   grid-row:2; text-align:center; background:yellow; border: solid 2px grey; font-size:12px;'>Panel</DIV>"
 for idx in range(2,size+2):
  ru = size-idx+2
  print "<DIV CLASS=z-rack-indx STYLE='grid-column:1; grid-row:{0}; border-right:1px solid grey'>{1}</DIV>".format(idx,ru)
  print "<DIV CLASS=z-rack-indx STYLE='grid-column:3; grid-row:{0};  border-left:1px solid grey'>{1}</DIV>".format(idx,ru)
  print "<DIV CLASS=z-rack-indx STYLE='grid-column:5; grid-row:{0}; border-right:1px solid grey'>{1}</DIV>".format(idx,ru)
  print "<DIV CLASS=z-rack-indx STYLE='grid-column:7; grid-row:{0};  border-left:1px solid grey'>{1}</DIV>".format(idx,ru)

 for dev in devs:
  if dev['rack_unit'] == 0:
   continue
  rowstart = size-abs(dev['rack_unit'])+2
  rowend   = rowstart + dev['rack_size']
  col = "2" if dev['rack_unit'] > 0 else "6"
  print "<DIV CLASS='z-rack-data z-centered' STYLE='grid-column:{0}; grid-row:{1}/{2}; background:{3};'>".format(col,rowstart,rowend,"#00cc66" if not dev.get('user_id') else "#df3620")
  print "<A CLASS='z-op' TITLE='Show device info for {0}' DIV='div_content_right' URL='sdcp.cgi?call=device_info&id={1}'>{0}</A></CENTER>".format(dev['hostname'],dev['id'])
  print "</DIV>"
 print "</DIV>"

#
#
#
def info(aWeb):
 from sdcp import PackageContainer as PC
 from os import listdir, path
 id = aWeb['id']

 print "<DIV CLASS='z-frame z-info' STYLE='height:200px;'>"
 print "<FORM ID=rack_info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(id)
 print "<DIV CLASS=title>Rack Info {}</DIV>".format("(new)" if id == 'new' else "")
 print "<DIV CLASS=z-table><DIV CLASS=tbody>"

 with DB() as db:
  if id == 'new':
   rack = { 'id':'new', 'name':'new-name', 'size':'48', 'fk_pdu_1':None, 'fk_pdu_2':None, 'fk_console':None }
  else:
   db.do("SELECT racks.* from racks WHERE id = {}".format(id))
   rack = db.get_row()
  print "<DIV CLASS=tr><DIV CLASS=td>Name:</DIV><DIV CLASS=td><INPUT NAME=name TYPE=TEXT VALUE='{0}'></DIV></DIV>".format(rack['name'])
  print "<DIV CLASS=tr><DIV CLASS=td>Size:</DIV><DIV CLASS=td><INPUT NAME=size TYPE=TEXT VALUE='{0}'></DIV></DIV>".format(rack['size'])
  for key in ['pdu_1','pdu_2','console']:
   dbname = key.partition('_')[0]
   db.do("SELECT id,name from {0}s".format(dbname))
   rows = db.get_rows()
   rows.append({'id':'NULL', 'name':"No {}".format(dbname.capitalize())})
   print "<DIV CLASS=tr><DIV CLASS=td>{0}:</DIV><DIV CLASS=td><SELECT NAME=fk_{1}>".format(key.capitalize(),key)
   for unit in rows:
    extra = " selected" if (rack.get("fk_"+key) == unit['id']) or (not rack.get("fk_"+key) and unit['id'] == 'NULL') else ""
    print "<OPTION VALUE={0} {1}>{2}</OPTION>".format(unit['id'],extra,unit['name'])   
   print "</SELECT></DIV></DIV>"
  print "<DIV CLASS=tr><DIV CLASS=td>Image</DIV><DIV CLASS=td><SELECT NAME=image_url>"
  print "<OPTION VALUE=NULL>No picture</OPTION>"
  for image in listdir(path.join(PC.generic['docroot'],"images")):
   extra = " selected" if (rack.get("image_url") == image) or (not rack.get('image_url') and image == 'NULL') else ""
   if image[-3:] == "png" or image[-3:] == "jpg":
    print "<OPTION VALUE={0} {1}>{2}</OPTION>".format(image,extra,image[:-4])
  print "</SELECT></DIV></DIV>"

 print "</DIV></DIV>"
 print "</FORM>"
 print "<A TITLE='Reload info' CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=sdcp.cgi?call=rack_info&id={0}><IMG SRC='images/btn-reload.png'></A>".format(id)
 print "<A TITLE='Update unit' CLASS='z-btn z-op z-small-btn' DIV=update_results URL=sdcp.cgi?call=rack_update FRM=rack_info_form><IMG SRC='images/btn-save.png'></A>"
 if not id == 'new':
  print "<A TITLE='Delete unit' CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=sdcp.cgi?call=rack_remove&id={0}><IMG SRC='images/btn-delete.png'></A>".format(id)
 print "<SPAN style='float:right; font-size:9px;'ID=update_results></SPAN>"
 print "</DIV>"

#
#
def update(aWeb):
 if aWeb['id'] == 'new':
  print "Creating new rack [new:{}]".format(aWeb['name'])
  sql = "INSERT into racks (name, size, fk_pdu_1, fk_pdu_2, fk_console, image_url) VALUES ('{}','{}',{},{},{},'{}')"
 else:
  print "Updating rack [{}:{}]".format(aWeb['id'],aWeb['name'])
  sql = "UPDATE racks SET name = '{}', size = '{}', fk_pdu_1 = {}, fk_pdu_2 = {}, fk_console = {}, image_url='{}' WHERE id = '{}'"
 with DB() as db:
  res = db.do(sql.format(aWeb['name'],aWeb['size'],aWeb['fk_pdu_1'],aWeb['fk_pdu_2'],aWeb['fk_console'],aWeb['image_url'],aWeb['id']))

#
#
def remove(aWeb):
 with DB() as db:
  db.do("DELETE FROM racks WHERE id = {0}".format(aWeb['id']))
  print "Rack {0} deleted".format(aWeb['id'])

#
#
def rackinfo(aWeb):
 with DB() as db:
  res  = db.do("SELECT rackinfo.*, devices.vm, devices.hostname, devices.ip, INET_NTOA(devices.ip) as ipasc FROM rackinfo LEFT JOIN devices ON devices.id = rackinfo.device_id")
  if res == 0:
   return 
  ris = db.get_rows()
  order = ris[0].keys()
  order.sort()
  db.do("SELECT id, name FROM pdus")
  pdus  = db.get_dict('id')
  db.do("SELECT id, name FROM consoles")
  cons  = db.get_dict('id')
  db.do("SELECT id, name FROM racks")
  racks = db.get_dict('id')
  print "<DIV CLASS=z-frame style='overflow-x:auto;'><DIV CLASS=z-table>"
  print "<DIV CLASS=thead><DIV CLASS=th>Id</DIV><DIV CLASS=th>IP</DIV><DIV CLASS=th>Hostname</DIV><DIV CLASS=th>VM</DIV><DIV CLASS=th>Console</DIV><DIV CLASS=th>Port</DIV><DIV CLASS=th>PEM0-PDU</DIV><DIV CLASS=th>slot</DIV><DIV CLASS=th>unit</DIV><DIV CLASS=th>PEM1-PDU</DIV><DIV CLASS=th>slot</DIV><DIV CLASS=th>unit</DIV><DIV CLASS=th>Rack</DIV><DIV CLASS=th>size</DIV><DIV CLASS=th>unit</DIV></DIV>"
  print "<DIV CLASS=tbody>"
  for ri in ris:
   print "<DIV CLASS=tr>"
   print "<DIV CLASS=td>{}</DIV><DIV CLASS=td><A CLASS=z-op DIV=div_content_right URL=sdcp.cgi?call=device_info&id={}>{}</A></DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV>".format(ri['device_id'],ri['device_id'],ri['ipasc'],ri['hostname'],ri['vm'])
   print "<DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV>".format(cons.get(ri['console_id'],{}).get('name',None),ri['console_port'])
   print "<DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV>".format( pdus.get(ri['pem0_pdu_id'],{}).get('name',None),ri['pem0_pdu_slot'],ri['pem0_pdu_unit'])
   print "<DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV>".format( pdus.get(ri['pem1_pdu_id'],{}).get('name',None),ri['pem1_pdu_slot'],ri['pem1_pdu_unit'])
   print "<DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV>".format(racks.get(ri['rack_id'],{}).get('name',None),ri['rack_size'],ri['rack_unit'])
   print "</DIV>"
  print "</DIV></DIV></DIV>"

