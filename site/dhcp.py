"""HTML5 Ajax DHCP module"""
__author__= "Zacharias El Banna"

#
#
def update(aWeb):
 aWeb.wr("<ARTICLE>DHCP Server Update:%s</ARTICLE>"%(aWeb.rest_call("dhcp/update_server")))

#
#
def leases(aWeb):
 leases = aWeb.rest_call("dhcp/leases",{'type':aWeb['lease']})
 aWeb.wr("<ARTICLE><P>Leases (%s)</P>"%(aWeb['lease']))
 aWeb.wr("<DIV CLASS=table><DIV class=thead><DIV>Ip</DIV><DIV>Mac</DIV><DIV>Hostname</DIV><DIV>Starts</DIV><DIV>Ends</DIV></DIV>")
 aWeb.wr("<DIV CLASS=tbody>")
 for data in leases['data']:
  aWeb.wr("<DIV><DIV>%s</DIV><DIV>%s</DIV><DIV>%s</DIV><DIV>%s</DIV><DIV>%s</DIV></DIV>"%(data['ip'],data['mac'],data.get('hostname',"None"),data['starts'],data['ends']))
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</ARTICLE>")
