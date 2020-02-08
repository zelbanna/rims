"""HTML5 Ajax Location module"""
__author__= "Zacharias El Banna"

################################################# Locations ###############################################
#
#
def list(aWeb):
 args = aWeb.args()
 res  = aWeb.rest_call("location/list",args)
 aWeb.wr("<ARTICLE><P>Location List</P>")
 aWeb.wr(aWeb.button('reload', DIV='div_content_left',  URL='locations_list?%s'%aWeb.get_args(), TITLE='Reload'))
 aWeb.wr(aWeb.button('add',    DIV='div_content_right', URL='locations_info?id=new', TITLE='Add to locations'))
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV>ID</DIV><DIV>Name</DIV><DIV>&nbsp;</DIV></DIV><DIV CLASS=tbody>")
 for row in res['data']:
  aWeb.wr("<DIV><DIV>%s</DIV><DIV STYLE='max-width:180px; overflow-x:hidden'>%s</DIV><DIV STYLE='max-width:20px'>"%(row['id'],row['name']))
  aWeb.wr(aWeb.button('edit', DIV='div_content_right', URL='locations_info?id=%s'%row['id']))
  aWeb.wr(aWeb.button('trash',DIV='div_content_right', URL='locations_delete?id=%s'%row['id'], MSG='Really remove item?'))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</DIV></DIV></ARTICLE>")

def info(aWeb):
 args = aWeb.args()
 info = aWeb.rest_call("location/info",args)['data']
 aWeb.wr("<ARTICLE CLASS='info'><P>Location Info</P>")
 aWeb.wr("<FORM ID='location_info_form'>")
 aWeb.wr("<INPUT TYPE=hidden NAME=id VALUE='%s'>"%info['id'])
 aWeb.wr("<DIV CLASS='info col2'>")
 aWeb.wr("<DIV>Name:</DIV><DIV><INPUT TYPE=TEXT NAME=name VALUE='%s'></DIV>"%info['name'])
 aWeb.wr("</DIV>")
 aWeb.wr(aWeb.button('reload',DIV='div_content_right', URL='locations_info?id=%s'%info['id']))
 if info['id'] != 'new':
  aWeb.wr(aWeb.button('delete',DIV='div_content_right',URL='locations_delete?id=%s'%info['id'], MSG='Really remove item?'))
 aWeb.wr(aWeb.button('save',DIV='div_content_right', URL='locations_info?op=update', FRM='location_info_form'))
 aWeb.wr("</ARTICLE>")

def delete(aWeb):
 args = aWeb.args()
 res  = aWeb.rest_call("location/delete",args)
 aWeb.wr("<ARTICLE>Result: %s</ARTICLE>"%res['status'])
