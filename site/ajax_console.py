"""Moduledocstring.

Ajax Console calls module

"""
__author__= "Zacharias El Banna"                     
__version__= "1.0GA"
__status__= "Production"

from sdcp.core.GenLib import DB, sys_int2ip, sys_ip2int
############################################## Consoles ###################################################
#
# View Consoles
#

def console_list(aWeb):
 from sdcp.devices.RackUtils import OpenGear
 domain = aWeb.get_value('domain')
 conlist = aWeb.get_list('consolelist')
 config="https://{0}/?form=serialconfig&action=edit&ports={1}&start=&end="
 print "<DIV CLASS='z-framed'><DIV CLASS='z-table'><TABLE WIDTH=330>"
 print "<TR><TH>Server</TH><TH>Port</TH><TH>Device</TH></TR>"
 for con in conlist:
  console = OpenGear(con,domain)
  console.load_snmp()
  conip = console._ip
  for key in console.get_keys():
   port = str(6000 + key)
   value = console.get_entry(key)
   print "<TR><TD><A HREF='https://{0}/'>{1}</A></TD><TD><A TITLE='Edit port info' HREF={5}>{2}</A></TD><TD><A HREF='telnet://{0}:{3}'>{4}</A></TD>".format(conip, con,str(key),port, value, config.format(conip,key))
 print "</TABLE></DIV></DIV>"

def console_list_consoles(aWeb):
 db   = DB()
 db.connect()
 print "<DIV CLASS='z-framed'>"
 print "<DIV CLASS='z-table'><TABLE WIDTH=330>"
 print "<TR style='height:20px'><TH COLSPAN=3><CENTER>Consoles</CENTER></TH></TR>"
 print "<TR style='height:20px'><TD COLSPAN=3>"
 print "<A TITLE='Reload List' CLASS='z-btn z-small-btn z-btnop' OP=load DIV=div_navleft LNK='ajax.cgi?call=console_list_consoles'><IMG SRC='images/btn-reboot.png'></A>"
 print "<A TITLE='Add console' CLASS='z-btn z-small-btn z-btnop' OP=load DIV=div_navcont LNK='ajax.cgi?call=console_device_info&id=new'><IMG SRC='images/btn-add.png'></A>"
 print "</TD></TR>"
 res  = db.do("SELECT * from consoles ORDER by name")
 data = db.get_all_rows()
 print "<TR><TH>ID</TH><TH>Name</TH><TH>IP</TH></TR>"
 for unit in data:
  print "<TR><TD>{0}</TD><TD><A CLASS='z-btnop' OP=load DIV=div_navcont LNK='ajax.cgi?call=console_device_info&id={0}'>{1}</A></TD><TD>{2}</TD>".format(unit['id'],unit['name'],sys_int2ip(unit['ip']))
 print "</TABLE></DIV>"
 db.close()

#
#
#
def console_device_info(aWeb):
 id = aWeb.get_value('id')
 ip = aWeb.get_value('ip')
 op = aWeb.get_value('op')
 name = aWeb.get_value('name')
 db = DB()
 db.connect()

 if op == 'update':
  ipint = sys_ip2int(ip)
  if id == 'new':
   sql = "INSERT into consoles (name, ip) VALUES ('{0}','{1}')".format(name,ipint)
   db.do(sql)
   db.commit() 
   db.do("SELECT id FROM consoles WHERE ip = '{0}'".format(ipint))
   res = db.get_row()   
   id  = res['id']
  else:
   sql = "UPDATE consoles SET name = '{0}', ip = '{1}' WHERE id = '{2}'".format(name,ipint,id)
   res = db.do(sql)
   db.commit()  

 print "<DIV CLASS='z-framed z-table' style='resize: horizontal; margin-left:0px; width:420px; z-index:101; height:185px;'>"
 print "<FORM ID=console_device_info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(id)
 print "<TABLE style='width:100%'>"
 print "<TR><TH COLSPAN=2>Consoles Info {}</TH></TR>".format("(new)" if id == 'new' else "")
 if id == 'new':
  condata = { 'id':'new', 'name':'new-name', 'ip':2130706433 }
  if not ip:
   ip = '127.0.0.1'
  if not name:
   name = 'new-name'
 else:
  if id:
   db.do("SELECT * FROM consoles WHERE id = '{0}'".format(id))
  else:
   db.do("SELECT * FROM consoles WHERE ip = '{0}'".format(ip))
  condata = db.get_row()
  ip = sys_int2ip(condata['ip'])
  name = condata['name']
 db.close()
 print "<TR><TD>IP:</TD><TD><INPUT NAME=ip TYPE=TEXT CLASS='z-input' VALUE='{0}'></TD></TR>".format(ip)
 print "<TR><TD>Name:</TD><TD><INPUT NAME=name TYPE=TEXT CLASS='z-input' VALUE='{0}'></TD></TR>".format(name)
 print "</TABLE>"
 if not id == 'new':
  print "<A TITLE='Reload info' CLASS='z-btn z-btnop z-small-btn' DIV=div_navcont LNK=ajax.cgi?call=console_device_info&id={} OP=load><IMG SRC='images/btn-reboot.png'></A>".format(id)
  print "<A TITLE='Remove unit' CLASS='z-btn z-btnop z-small-btn' DIV=div_navcont LNK=ajax.cgi?call=console_remove&id={0} OP=load><IMG SRC='images/btn-remove.png'></A>".format(id)
 print "<A TITLE='Update unit'  CLASS='z-btn z-btnop z-small-btn' DIV=div_navcont LNK=ajax.cgi?call=console_device_info&op=update FRM=console_device_info_form OP=post><IMG SRC='images/btn-save.png'></A>"
 print "</FORM>"
 print "</DIV>"

#
#
#
def console_remove(aWeb):
 type = aWeb.get_value('type')
 id   = aWeb.get_value('id')
 db   = DB()
 db.connect()
 db.do("DELETE FROM consoles WHERE id = '{0}'".format(id))
 db.do("UPDATE devices SET console_id = '0' WHERE console_id = '{0}'".format(id))
 db.do("UPDATE racks SET fk_console = '0' WHERE fk_console = '{0}'".format(id))
 db.commit()
 print "Unit {0} deleted".format(id)
 db.close()
