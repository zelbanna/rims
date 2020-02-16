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
  aWeb.wr("<DIV><DIV>%s</DIV><DIV>%s</DIV><DIV>%s</DIV><DIV>"%(row['id'],row['serial'],row['model']))
  aWeb.wr(aWeb.button("info", DIV='div_content_right', URL='inventory_info?id=%s'%row['id'], TITLE='Info'))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</DIV></DIV></ARTICLE>")

def search(aWeb):
 aWeb.wr("<ARTICLE><P>Inventor Search</P>")
 aWeb.wr("<FORM ID='inventory_search'>")
 aWeb.wr("<SPAN>Field:</SPAN><SELECT ID='field' NAME='field'><OPTION VALUE='serial'>Serial</OPTION><OPTION VALUE='vendor'>Vendor</OPTION></SELECT>")
 aWeb.wr("<INPUT TYPE=TEXT ID='search' NAME='search' STYLE='width:150px' REQUIRED>")
 aWeb.wr("</FORM><DIV CLASS=inline>")
 aWeb.wr(aWeb.button('search', DIV='div_content_left', URL='inventory_list', FRM='inventory_search'))
 aWeb.wr("</DIV>")
 aWeb.wr("</ARTICLE>")

def vendor(aWeb):
 res = aWeb.rest_call("inventory/vendor_list")
 aWeb.wr("<ARTICLE><P>Vendors</P>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV>Vendor</DIV><DIV>Count</DIV></DIV><DIV CLASS=tbody>")
 for row in res['data']:
  aWeb.wr("<DIV><DIV>%s</DIV><DIV>%s</DIV></DIV>"%(row['vendor'],row['count']))
 aWeb.wr("</DIV></DIV></ARTICLE>")

def info(aWeb):
 args = aWeb.args()
 res = aWeb.rest_call("inventory/info",args)
 info = res['data']
 aWeb.wr("<ARTICLE CLASS='info'><P>Inventory Info</P>")
 aWeb.wr("<FORM ID='inventory_info_form'>")
 aWeb.wr("<INPUT TYPE=hidden VALUE='%s' NAME=id>"%info['id'])
 aWeb.wr("<DIV CLASS='info col2'>")
 aWeb.wr("<label for='vendor'>Vendor:</label><INPUT TYPE=TEXT ID=vendor NAME=vendor VALUE='%s' REQUIRED>"%info['vendor'])
 aWeb.wr("<label for='serial'>Serial:</label><INPUT TYPE=TEXT ID=serial NAME=serial VALUE='%s' REQUIRED>"%info['serial'])
 aWeb.wr("<label for='produt'>Product:</label><INPUT TYPE=TEXT ID=product NAME=product VALUE='%s' REQUIRED>"%info['product'])
 aWeb.wr("<label for='model'>Model:</label><INPUT TYPE=TEXT ID=model NAME=model VALUE='%s' REQUIRED>"%info['model'])
 aWeb.wr("<label for='receive_date'>Receive Date:</LABEL><INPUT id='receive_date' TYPE=date NAME=receive_date VALUE='%s' REQUIRED>"%info['receive_date'])
 aWeb.wr("<label for='license'>License:</LABEL><INPUT id='license' NAME=license TYPE=checkbox VALUE=1 {0}>".format("checked=checked" if info['license'] else ""))
 aWeb.wr("<label for='license_key'>Key:</LABEL><INPUT id='license_key' TYPE=TEXT NAME=license_key VALUE='%s'>"%info['license_key'])
 aWeb.wr("<label for='purchase_order'>Purchase Order:</LABEL><INPUT TYPE=TEXT ID=purchase_order NAME=purchase_order VALUE='%s'>"%info['purchase_order'])
 aWeb.wr("<label for='support_contract'>Support:</LABEL><INPUT NAME=support_contract TYPE=checkbox VALUE=1 {0}>".format("checked=checked" if info['support_contract'] else ""))
 aWeb.wr("<label for='support_end_date'>Contract End:</LABEL><INPUT id='support_end_date' TYPE=date NAME=support_end_date VALUE='%s'>"%info['support_end_date'])
 aWeb.wr("<label for='description'>Description:</LABEL><INPUT TYPE=TEXT ID=description NAME=description VALUE='%s'>"%info['description'])
 aWeb.wr("<label for='location_id'>Location:</LABEL><SELECT id='location_id' NAME=location_id>")
 for loc in res['locations']:
  aWeb.wr("<OPTION VALUE={0} {1}>{2}</OPTION>".format(loc['id']," selected" if info['location_id'] == loc['id'] else "",loc['name']))
 aWeb.wr("</SELECT></DIV>")
 aWeb.wr(aWeb.button('reload',DIV='div_content_right', URL='inventory_info?id=%s'%info['id']))
 if info['id'] != 'new':
  aWeb.wr(aWeb.button('trash',DIV='div_content_right',URL='inventory_delete?id=%s'%info['id'], MSG='Really remove item?'))
 aWeb.wr(aWeb.button('save',DIV='div_content_right', URL='inventory_info?op=update', FRM='inventory_info_form'))
 aWeb.wr("</ARTICLE>")

#
#
def report(aWeb):
 args = aWeb.args()
 res = aWeb.rest_call("inventory/list",{'extra': ["vendor","product","description"],'sort':'vendor'})
 aWeb.wr("<ARTICLE><P>Inventory</P>")
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV>Id</DIV><DIV>Serial</DIV><DIV>Vendor</DIV><DIV>Model</DIV><DIV>Product</DIV><DIV>Description</DIV></DIV><DIV CLASS=tbody>")
 for dev in res['data']:
  aWeb.wr("<DIV><DIV>%(id)s</DIV><DIV>%(serial)s</DIV><DIV>%(vendor)s</DIV><DIV>%(model)s</DIV><DIV>%(product)s</DIV><DIV>%(description)s</DIV></DIV>"%dev)
 aWeb.wr("</DIV></DIV></ARTICLE>")
