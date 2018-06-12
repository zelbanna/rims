"""Module docstring.

HTML5 Ajax ESXi module

"""
__author__= "Zacharias El Banna"
__version__ = "18.05.31GA"
__status__ = "Production"

#
#
def manage(aWeb):
 id = aWeb['id']
 data = aWeb.rest_call("device_basics",{'id':id})
 print "<NAV><UL>"
 print "<LI><A CLASS=z-op DIV=div_content_left URL=sdcp.cgi?awk_list&hostname={0}&domain={1}>Inventories</A></LI>".format(data['hostname'],data['domain'])
 print "<LI><A CLASS=z-op DIV=div_content_left URL=sdcp.cgi?awk_list&hostname={0}&domain={1}>Hosts</A></LI>".format(data['hostname'],data['domain'])
 print "<LI><A CLASS=z-op HREF=http://%s     target=_blank>UI</A></LI>"%(data['ip'])
 print "<LI><A CLASS='z-op reload' DIV=main URL='sdcp.cgi?awk_manage&id=%s'></A></LI>"%(id)
 print "<LI CLASS='right navinfo'><A>%s</A></LI>"%(data['hostname'])
 print "</UL></NAV>"
 print "<SECTION CLASS=content ID=div_content>"
 print "<SECTION CLASS=content-left ID=div_content_left></SECTION>"
 print "<SECTION CLASS=content-right ID=div_content_right></SECTION>"
 print "</SECTION>"
