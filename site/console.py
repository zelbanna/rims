"""Module docstring.

Ajax Console calls module

"""
__author__= "Zacharias El Banna"                     
__version__ = "17.11.01GA"
__status__= "Production"

from sdcp.core.dbase import DB
############################################## Consoles ###################################################
#
# View Consoles
#

def inventory(aWeb):
 from sdcp.devices.opengear import Device
 print "<DIV CLASS=z-frame>"
 print "<DIV CLASS=z-table>"
 print "<DIV CLASS=thead><DIV CLASS=th>Server</DIV><DIV CLASS=th>Port</DIV><DIV CLASS=th>Device</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 conlist = aWeb.form.getlist('consolelist')
 config="https://{0}/?form=serialconfig&action=edit&ports={1}&start=&end="
 for con in conlist:
  console = Device(con)
  console.load_snmp()
  for key in console.get_keys():
   port = str(6000 + key)
   value = console.get_entry(key)
   print "<DIV CLASS=tr><DIV CLASS=td><A HREF='https://{0}/'>{0}</A></DIV><DIV CLASS=td><A TITLE='Edit port info' HREF={4}>{1}</A></DIV><DIV CLASS=td><A HREF='telnet://{0}:{2}'>{3}</A></DIV></DIV>".format(con,str(key),port, value, config.format(con,key))
 print "</DIV></DIV></DIV>"

def list(aWeb):
 with DB() as db:
  res  = db.do("SELECT id, INET_NTOA(ip) as ip, name from consoles ORDER by name")
  data = db.get_rows()
 print "<DIV CLASS=z-frame>"
 print "<DIV CLASS=title>Consoles</DIV>"
 print "<A TITLE='Reload List' CLASS='z-btn z-small-btn z-op' DIV=div_content_left URL='sdcp.cgi?call=console_list'><IMG SRC='images/btn-reload.png'></A>"
 print "<A TITLE='Add console' CLASS='z-btn z-small-btn z-op' DIV=div_content_right URL='sdcp.cgi?call=console_info&id=new'><IMG SRC='images/btn-add.png'></A>"
 print "<DIV CLASS=z-table>"
 print "<DIV CLASS=thead><DIV CLASS=th>ID</DIV><DIV CLASS=th>Name</DIV><DIV CLASS=th>IP</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for unit in data:
  print "<DIV CLASS=tr><DIV CLASS=td>{0}</DIV><DIV CLASS=td><A CLASS='z-op' DIV=div_content_right URL='sdcp.cgi?call=console_info&id={0}'>{1}</A></DIV><DIV CLASS=td>{2}</DIV></DIV>".format(unit['id'],unit['name'],unit['ip'])
 print "</DIV></DIV></DIV>"

#
#
#
def info(aWeb):
 from sdcp.core import genlib as GL
 id = aWeb['id']
 ip = aWeb['ip']
 op = aWeb['op']
 name = aWeb['name']
 with DB() as db:
  if op == 'update':
   ipint = GL.ip2int(ip)
   if id == 'new':
    sql = "INSERT into consoles (name, ip) VALUES ('{0}','{1}')".format(name,ipint)
    db.do(sql)
    id = db.get_last_id()
   else:
    sql = "UPDATE consoles SET name = '{0}', ip = '{1}' WHERE id = '{2}'".format(name,ipint,id)
    res = db.do(sql)
  else:
   # Either reload or "new"
   if id == 'new':
    ip = '127.0.0.1' if not ip else ip
    name = 'new-name' if not name else name
   else:
    if id:
     db.do("SELECT id, name, INET_NTOA(ip) as ip FROM consoles WHERE id = '{0}'".format(id))
    else:
     db.do("SELECT id, name, INET_NTOA(ip) FROM consoles WHERE ip = '{0}'".format(ip))
    condata = db.get_row()
    ip   = condata['ip']
    name = condata['name']

 print "<DIV CLASS='z-frame z-info' STYLE='height:185px;'>"
 print "<FORM ID=console_info_form>"
 print "<INPUT TYPE=HIDDEN NAME=id VALUE={}>".format(id)
 print "<DIV CLASS=title>Consoles Info {}</DIV>".format("(new)" if id == 'new' else "")
 print "<DIV CLASS=z-table>"
 print "<DIV CLASS=tbody>"
 print "<DIV CLASS=tr><DIV CLASS=td>IP:</DIV><DIV CLASS=td><INPUT NAME=ip TYPE=TEXT VALUE='{0}'></DIV></DIV>".format(ip)
 print "<DIV CLASS=tr><DIV CLASS=td>Name:</DIV><DIV CLASS=td><INPUT NAME=name TYPE=TEXT VALUE='{0}'></DIV></DIV>".format(name)
 print "</DIV></DIV></FORM>"
 if not id == 'new':
  print "<A TITLE='Reload info' CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=sdcp.cgi?call=console_info&id={}><IMG SRC='images/btn-reload.png'></A>".format(id)
  print "<A TITLE='Delete unit' CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=sdcp.cgi?call=console_delete&id={0}><IMG SRC='images/btn-delete.png'></A>".format(id)
 print "<A TITLE='Update unit'  CLASS='z-btn z-op z-small-btn' DIV=div_content_right URL=sdcp.cgi?call=console_info&op=update FRM=console_info_form><IMG SRC='images/btn-save.png'></A>"
 print "</DIV>"

#
#
#
def delete(aWeb):
 with DB() as db:
  db.do("UPDATE rackinfo SET console_port = 0 WHERE console_id = '{0}'".format(aWeb['id']))
  db.do("DELETE FROM consoles WHERE id = '{0}'".format(aWeb['id']))
  print "<B>Console {0} deleted</B>".format(aWeb['id'])
