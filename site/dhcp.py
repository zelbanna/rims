"""Module docstring.

HTML5 Ajax DHCP calls module

"""
__author__= "Zacharias El Banna"
__version__ = "18.02.09GA"
__status__= "Production"

#
#
def update(aWeb):
 print "<ARTICLE>%s</ARTICLE>"%(aWeb.rest_call("dhcp_update_server"))

#
#
def leases(aWeb):
 leases = aWeb.rest_call("dhcp_leases",{'type':aWeb['type']})
 print "<ARTICLE><P>%s Leases</P>"%(aWeb['type'].title())
 print "<DIV CLASS=table><DIV class=thead><DIV class=th>Ip</DIV><DIV class=th>Mac</DIV><DIV class=th>Hostname</DIV><DIV class=th>Starts</DIV><DIV class=th>Ends</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for data in leases['data']:
  print "<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV><DIV CLASS=td>%s</DIV></DIV>"%(data['ip'],data['mac'],data.get('hostname',"None"),data['starts'],data['ends'])
 print "</DIV></DIV>"
 print "</ARTICLE>"
