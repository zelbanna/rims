"""Module docstring.

HTML5 Ajax Console module

"""
__author__= "Zacharias El Banna"
__version__ = "5.3GA"
__status__= "Production"


def manage(aWeb):
 id = aWeb['id']
 if aWeb['ip']:
  ip = aWeb['ip']
  hostname = aWeb['hostname']
 else:
  data = aWeb.rest_call("device_info",{'id':id,'op':'basics'})
  ip = data['ip']
  hostname = data['info']['hostname']

 aWeb.wr("<NAV><UL>")
 aWeb.wr("<LI CLASS='navinfo'><A>%s</A></LI>"%(hostname))
 aWeb.wr("<LI><A CLASS='z-op reload' DIV=main URL='opengear_main?id=%s&ip=%s&hostname=%s'></A></LI>"%(id,ip,hostname))
 aWeb.wr("</UL></NAV>")
 aWeb.wr("<SECTION CLASS=content ID=div_content>")
 aWeb.wr("<SECTION CLASS=content-left ID=div_content_left>")
 inventory(aWeb,ip)
 aWeb.wr("</SECTION>")
 aWeb.wr("<SECTION CLASS=content-right ID=div_content_right></SECTION>")
 aWeb.wr("</SECTION>")


def inventory(aWeb,aIP = None):
 ip = aWeb['ip'] if not aIP else aIP
 res = aWeb.rest_call("opengear_inventory",{'ip':ip})
 config="https://%s/?form=serialconfig&action=edit&ports={}&start=&end="%ip
 aWeb.wr("<ARTICLE>")
 aWeb.wr("<DIV CLASS=table>")
 aWeb.wr("<DIV CLASS=thead><DIV CLASS=th>Server</DIV><DIV CLASS=th>Port</DIV><DIV CLASS=th>Device</DIV></DIV>")
 aWeb.wr("<DIV CLASS=tbody>")
 for con in res:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td><A HREF='https://{0}/'>{0}</A></DIV><DIV CLASS=td><A TITLE='Edit port info' HREF={4}>{1}</A></DIV><DIV CLASS=td><A HREF='telnet://{0}:{2}'>{3}</A></DIV></DIV>".format(ip,con['interface'],con['port'],con['name'], config.format(con['interface'])))
 aWeb.wr("</DIV></DIV></ARTICLE>")


def info(aWeb):
 aWeb.wr("<ARTICLE CLASS=info><P>Console Info</P>")
 aWeb.wr("No info at the moment")
 aWeb.wr("</ARTICLE>")
