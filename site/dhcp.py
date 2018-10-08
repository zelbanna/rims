"""Module docstring.

HTML5 Ajax DHCP module

"""
__author__= "Zacharias El Banna"
__version__ = "5.0GA"
__status__= "Production"

#
#
def update(aWeb):
 aWeb.wr("<ARTICLE>DHCP Server Update:%s</ARTICLE>"%(aWeb.rest_call("dhcp_update_server")))

#
#
def leases(aWeb):
 leases = aWeb.rest_call("dhcp_leases",{'type':aWeb['lease']})
 aWeb.wr("<ARTICLE><P>Leases (%s)</P>"%(aWeb['lease']))
 aWeb.wr("<DIV CLASS=table><DIV class=thead><DIV class=th>Ip</DIV><DIV class=th>Mac</DIV><DIV class=th>Hostname</DIV><DIV class=th>Starts</DIV><DIV class=th>Ends</DIV></DIV>")
 aWeb.wr("<DIV CLASS=tbody>")
 for data in leases['data']:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV></DIV>"%(data['ip'],data['mac'],data.get('hostname',"None"),data['starts'],data['ends']))
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</ARTICLE>")
