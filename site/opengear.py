"""HTML5 Ajax Console module"""
__author__= "Zacharias El Banna"

def manage(aWeb):
 data = aWeb.rest_call("device/management",{'id':aWeb['id']})['data']
 aWeb.wr("<NAV><UL>")
 aWeb.wr("<LI CLASS='navinfo'><A>%s</A></LI>"%(data['hostname']))
 aWeb.wr("<LI><A CLASS='z-op reload' DIV=main URL='opengear_manage?id=%s'></A></LI>"%aWeb['id'])
 aWeb.wr("</UL></NAV>")
 aWeb.wr("<SECTION CLASS=content ID=div_content>")
 aWeb.wr("<SECTION CLASS=content-left ID=div_content_left>")
 inventory(aWeb,data['ip'])
 aWeb.wr("</SECTION>")
 aWeb.wr("<SECTION CLASS=content-right ID=div_content_right></SECTION>")
 aWeb.wr("</SECTION>")


def inventory(aWeb,aIP = None):
 ip = aWeb['ip'] if not aIP else aIP
 res = aWeb.rest_call("opengear/inventory",{'id':aWeb['id']})
 config="https://%s/?form=serialconfig&action=edit&ports={}&start=&end="%ip
 aWeb.wr("<ARTICLE>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV>Server</DIV><DIV>Port</DIV><DIV>Device</DIV></DIV><DIV CLASS=tbody>")
 for con in res['inventory']:
  aWeb.wr("<DIV><DIV><A HREF='https://{0}/'>{0}</A></DIV><DIV><A TITLE='Edit port info' HREF={4}>{1}</A></DIV><DIV><A HREF='telnet://{0}:{2}'>{3}</A></DIV></DIV>".format(ip,con['interface'],con['port'],con['name'], config.format(con['interface'])))
 aWeb.wr("</DIV></DIV></ARTICLE>")


def info(aWeb):
 aWeb.wr("<ARTICLE CLASS=info><P>Console Info</P>")
 aWeb.wr("No info at the moment")
 aWeb.wr("</ARTICLE>")
