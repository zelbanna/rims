"""Module docstring.

HTML5 Ajax Console calls module

"""
__author__= "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__= "Production"


def manage(aWeb):
 id = aWeb['id']
 data = aWeb.rest_call(aWeb.resturl,"sdcp.rest.device_info",{'id':id})
 print "<NAV><UL>"
 print "<LI CLASS='right navinfo'><A>%s</A></LI>"%(data['info']['hostname'])
 print "</UL></NAV>"
 print "<SECTION CLASS=content ID=div_content>"
 print "<SECTION CLASS=content-left ID=div_content_left>"
 inventory(aWeb,data['ip'])
 print "</SECTION>" 
 print "<SECTION CLASS=content-right ID=div_content_right></SECTION>"
 print "</SECTION>"


def inventory(aWeb,aIP = None):
 from ..devices.opengear import Device
 print "<ARTICLE>"
 print "<DIV CLASS=table>"
 print "<DIV CLASS=thead><DIV CLASS=th>Server</DIV><DIV CLASS=th>Port</DIV><DIV CLASS=th>Device</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 con = aWeb['ip'] if not aIP else aIP
 config="https://{0}/?form=serialconfig&action=edit&ports={1}&start=&end="
 console = Device(con)
 console.load_snmp()
 for key in console.get_keys():
  port = str(6000 + key)
  value = console.get_entry(key)
  print "<DIV CLASS=tr><DIV CLASS=td><A HREF='https://{0}/'>{0}</A></DIV><DIV CLASS=td><A TITLE='Edit port info' HREF={4}>{1}</A></DIV><DIV CLASS=td><A HREF='telnet://{0}:{2}'>{3}</A></DIV></DIV>".format(con,str(key),port, value, config.format(con,key))
 print "</DIV></DIV></ARTICLE>"


def info(aWeb):
 print "<ARTICLE CLASS=info><P>Console Info</P>"
 print "No info at the moment"
 print "</ARTICLE>"
