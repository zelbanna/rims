"""HTML5 Ajax Inventory module"""
__author__= "Zacharias El Banna"


################################################## Inventory #################################################
#
#
def main(aWeb):
 aWeb.wr("<NAV><UL>")
 aWeb.wr("<LI CLASS='dropdown'><A>Inventory</A><DIV CLASS='dropdown-content'>")
 aWeb.wr("<A CLASS=z-op DIV=div_content_left URL='inventory_search'>Search</A>")
 aWeb.wr("<A CLASS=z-op DIV=div_content_left URL='inventory_vendor'>Vendor</A>")
 aWeb.wr("</DIV></LI>")
 aWeb.wr("<LI><A CLASS=z-op DIV=div_content_left URL='locations_list'>Locations</A></LI>")
 aWeb.wr("</UL></NAV>")
 aWeb.wr("<SECTION CLASS=content ID=div_content>")
 aWeb.wr("<SECTION CLASS=content-left ID=div_content_left></SECTION>")
 aWeb.wr("<SECTION CLASS=content-right ID=div_content_right></SECTION>")
 aWeb.wr("</SECTION>")

def list(aWeb):
 args = aWeb.args()
 res = aWeb.rest_call("inventory/list",args)
 aWeb.wr("<ARTICLE><P>Inventory List</P>")
 aWeb.wr(aWeb.button('reload', DIV='div_content_left',  URL='inventory_list?%s'%aWeb.get_args(), TITLE='Reload'))
 aWeb.wr(aWeb.button('search', DIV='div_content_left',  URL='inventory_search', TITLE='Search'))
 aWeb.wr(aWeb.button('add',    DIV='div_content_right', URL='inventory_info?id=new', TITLE='Add to inventory'))
 aWeb.wr("<DIV CLASS=table><DIV CLASS=tbody>")
 for row in res['data']:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%s</DIV><DIV CLASS=td STYLE='max-width:180px; overflow-x:hidden'>%s</DIV><DIV CLASS=td STYLE='max-width:180px; overflow-x:hidden'>%s</DIV><DIV>"%(row['id'],row['serial'],row['model']))
  aWeb.wr(aWeb.button("info", DIV='div_content_right', URL='inventory_info?id=%s'%row['id'], TITLE='Info'))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</DIV></DIV></ARTICLE>")

def search(aWeb):
 aWeb.wr("<ARTICLE><P>Inventor Search</P>")
 aWeb.wr("<FORM ID='inventory_search'>")
 aWeb.wr("<SPAN>Field:</SPAN><SELECT CLASS='background' ID='field' NAME='field'><OPTION VALUE='serial'>Serial</OPTION><OPTION VALUE='vendor'>Vendor</OPTION></SELECT>")
 aWeb.wr("<INPUT CLASS='background' TYPE=TEXT ID='search' NAME='search' STYLE='width:200px' REQUIRED>")
 aWeb.wr("</FORM><DIV CLASS=inline>")
 aWeb.wr(aWeb.button('search', DIV='div_content_left', URL='inventory_list', FRM='inventory_search'))
 aWeb.wr("</DIV>")
 aWeb.wr("</ARTICLE>")

def vendor(aWeb):
 res = aWeb.rest_call("inventory/vendor_list")
 aWeb.wr("<ARTICLE><P>Vendors</P>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Vendor</DIV><DIV CLASS=th>Count</DIV></DIV><DIV CLASS=tbody>")
 for row in res['data']:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td STYLE='max-width:180px; overflow-x:hidden'>%s</DIV><DIV CLASS=td STYLE='max-width:180px; overflow-x:hidden'>%s</DIV></DIV>"%(row['vendor'],row['count']))
 aWeb.wr("</DIV></DIV></ARTICLE>")

def info(aWeb):
 args = aWeb.args()
 res = aWeb.rest_call("inventory/info",args)
 info = res['data']
 aWeb.wr("<ARTICLE CLASS='info'><P>Inventory Info</P>")
 aWeb.wr("<FORM ID='inventory_info_form'>")
 aWeb.wr("<INPUT TYPE=hidden VALUE='%s' NAME=id>"%info['id'])
 aWeb.wr("<DIV CLASS=table><DIV CLASS=tbody>")
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Vendor:</DIV><DIV CLASS=td><INPUT TYPE=TEXT ID=vendor NAME=vendor VALUE='%s' REQUIRED></DIV></DIV>"%info['vendor'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Serial:</DIV><DIV CLASS=td><INPUT TYPE=TEXT ID=serial NAME=serial VALUE='%s' REQUIRED></DIV></DIV>"%info['serial'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Product:</DIV><DIV CLASS=td><INPUT TYPE=TEXT ID=product NAME=product VALUE='%s' REQUIRED></DIV></DIV>"%info['product'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Model:</DIV><DIV CLASS=td><INPUT TYPE=TEXT ID=model NAME=model VALUE='%s' REQUIRED></DIV></DIV>"%info['model'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Receive Date:</DIV><DIV CLASS=td><INPUT TYPE=date NAME=receive_date VALUE='%s' REQUIRED></DIV></DIV>"%info['receive_date'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>License:</DIV><DIV CLASS=td><INPUT NAME=license TYPE=checkbox VALUE=1 {0}></DIV></DIV>".format("checked=checked" if info['license'] else ""))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Key:</DIV><DIV CLASS=td><INPUT TYPE=TEXT ID=license_key NAME=license_key VALUE='%s'></DIV></DIV>"%info['license_key'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Purchase Order:</DIV><DIV CLASS=td><INPUT TYPE=TEXT ID=purchase_order NAME=purchase_order VALUE='%s'></DIV></DIV>"%info['purchase_order'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Support:</DIV><DIV CLASS=td><INPUT NAME=support_contract TYPE=checkbox VALUE=1 {0}></DIV></DIV>".format("checked=checked" if info['support_contract'] else ""))
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Contract End:</DIV><DIV CLASS=td><INPUT TYPE=date NAME=support_end_date VALUE='%s'></DIV></DIV>"%info['support_end_date'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Description:</DIV><DIV CLASS=td><INPUT TYPE=TEXT ID=description NAME=description VALUE='%s'></DIV></DIV>"%info['description'])
 aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>Location:</DIV><DIV CLASS=td><SELECT NAME=location_id>")
 for loc in res['locations']:
  aWeb.wr("<OPTION VALUE={0} {1}>{2}</OPTION>".format(loc['id']," selected" if info['location_id'] == loc['id'] else "",loc['name']))
 aWeb.wr("</SELECT></DIV></DIV>")
 aWeb.wr("</DIV></DIV>")
 aWeb.wr(aWeb.button('reload',DIV='div_content_right', URL='inventory_info?id=%s'%info['id']))
 if info['id'] != 'new':
  aWeb.wr(aWeb.button('delete',DIV='div_content_right',URL='inventory_delete?id=%s'%info['id'], MSG='Really remove item?'))
 aWeb.wr(aWeb.button('save',DIV='div_content_right', URL='inventory_info?op=update', FRM='inventory_info_form'))
 aWeb.wr("</ARTICLE>")

#
#
def report(aWeb):
 args = aWeb.args()
 res = aWeb.rest_call("inventory/list",{'extra': ["vendor","product","description"],'sort':'vendor'})
 aWeb.wr("<ARTICLE><P>Inventory</P>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Id</DIV><DIV CLASS=th>Serial</DIV><DIV CLASS=th>Vendor</DIV><DIV CLASS=th>Model</DIV><DIV CLASS=th>Product</DIV><DIV CLASS=th>Description</DIV></DIV><DIV CLASS=tbody>")
 for dev in res['data']:
  aWeb.wr("<DIV CLASS=tr><DIV CLASS=td>%(id)s</DIV><DIV CLASS=td>%(serial)s</DIV><DIV CLASS=td>%(vendor)s</DIV><DIV CLASS=td>%(model)s</DIV><DIV CLASS=td>%(product)s</DIV><DIV CLASS=td>%(description)s</DIV></DIV>"%dev)
 aWeb.wr("</DIV></DIV></ARTICLE>")
