"""Module docstring.

HTML5 Ajax Console calls module

"""
__author__= "Zacharias El Banna"
__version__ = "18.02.09GA"
__status__= "Production"


def manage(aWeb):
 id = aWeb['id']
 if aWeb['ip']:
  ip = aWeb['ip']
  hostname = aWeb['hostname']
 else:
  data = aWeb.rest_call("device_info",{'id':id})
  ip = data['ip']
  hostname = data['info']['hostname']

 print "<NAV><UL>"
 print "<LI CLASS='navinfo'><A>%s</A></LI>"%(hostname)
 print "<LI><A CLASS='z-op reload' DIV=main URL='sdcp.cgi?%s'></A></LI>"%(aWeb.get_args())
 print "</UL></NAV>"
 print "<SECTION CLASS=content ID=div_content>"
 print "<SECTION CLASS=content-left ID=div_content_left>"
 inventory(aWeb,ip)
 print "</SECTION>" 
 print "<SECTION CLASS=content-right ID=div_content_right></SECTION>"
 print "</SECTION>"


def inventory(aWeb,aIP = None):
 ip = aWeb['ip'] if not aIP else aIP
 res = aWeb.rest_call("opengear_inventory",{'ip':ip})
 config="https://%s/?form=serialconfig&action=edit&ports={}&start=&end="%ip
 print "<ARTICLE>"
 print "<DIV CLASS=table>"
 print "<DIV CLASS=thead><DIV CLASS=th>Server</DIV><DIV CLASS=th>Port</DIV><DIV CLASS=th>Device</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for con in res:
  print "<DIV CLASS=tr><DIV CLASS=td><A HREF='https://{0}/'>{0}</A></DIV><DIV CLASS=td><A TITLE='Edit port info' HREF={4}>{1}</A></DIV><DIV CLASS=td><A HREF='telnet://{0}:{2}'>{3}</A></DIV></DIV>".format(ip,con['interface'],con['port'],con['name'], config.format(con['interface']))
 print "</DIV></DIV></ARTICLE>"


def info(aWeb):
 print "<ARTICLE CLASS=info><P>Console Info</P>"
 print "No info at the moment"
 print "</ARTICLE>"
