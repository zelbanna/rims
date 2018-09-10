"""Module docstring.

HTML5 Ajax Appformix module

"""
__author__= "Zacharias El Banna"
__version__ = "1.0GA"
__status__= "Beta"

##################################### Report ##################################
#
def list(aWeb):
 cookie_openstack = aWeb.cookie('openstack')
 cookie_appformix = aWeb.cookie('appformix')

 if not cookie_appformix.get('appformix_token'):
  res = aWeb.rest_call("appformix_authenticate",{'node':cookie_openstack['appformix']})
  if not res['auth'] == "OK":
   aWeb.wr("Error logging in - {}".format(str(res)))
   return
  else:
   cookie_appformix['token'] = res['token']
   cookie_appformix['node'] =  cookie_openstack['appformix']
   aWeb.put_cookie('appformix',cookie_appformix,res['expires'])

 from datetime import datetime
 res = aWeb.rest_call("appformix_report_projects",{'node':cookie_appformix['node'],'token':cookie_appformix['token'],'project':cookie_openstack['project_id']})
 aWeb.wr("<SECTION CLASS=content-left ID=div_content_left><ARTICLE><P>Usage Reports</P>")
 aWeb.wr(aWeb.button('reload', DIV='div_content', URL='appformix_list'))
 aWeb.wr("<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Report</DIV><DIV CLASS=th>Created</DIV><DIV CLASS=th STYLE='width:94px;'>&nbsp;</DIV></DIV>")
 aWeb.wr("<DIV CLASS=tbody>")
 for rep in res['reports']:
  aWeb.wr("<DIV CLASS=tr>")
  aWeb.wr("<!-- %s -->"%rep)
  aWeb.wr("<DIV CLASS=td STYLE='max-width:180px; overflow-x:hidden;'>%s</DIV>"%rep['ReportId'])
  aWeb.wr("<DIV CLASS=td>%s</DIV>"%datetime.utcfromtimestamp(float(rep['Start'])/1e3))
  aWeb.wr("<DIV CLASS=td>")
  aWeb.wr(aWeb.button('info', DIV='div_content_right', URL='appformix_info?report=%s'%(rep['ReportId'])))
  aWeb.wr("</DIV></DIV>")
 aWeb.wr("</DIV></DIV>")
 aWeb.wr("</ARTICLE></SECTION>")
 aWeb.wr("<SECTION CLASS=content-right ID=div_content_right></SECTION>")

def info(aWeb):
 cookie_openstack = aWeb.cookie('openstack')
 cookie_appformix = aWeb.cookie('appformix')
 reports = aWeb.rest_call("appformix_project_reports",{'node':cookie_appformix['node'],'token':cookie_appformix['token'],'report':aWeb['report']})
 from zdcp.site.openstack import dict2html
 for project in reports['Data']:
  if project['Project_Id'] == cookie_openstack['project_id']:
   aWeb.wr("<ARTICLE STYLE='overflow:auto;'>")
   aWeb.wr("<H2>Report %s</H2>"%(aWeb['report']))
   dict2html(project['Instances'],"Instances")
   dict2html(project['MetaData'],"MetaData")
   aWeb.wr("</ARTICLE>")
