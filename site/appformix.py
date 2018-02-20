"""Module docstring.

HTML5 Ajax Appformix calls module

"""
__author__= "Zacharias El Banna"
__version__ = "18.02.09GA"
__status__= "Beta"

##################################### Report ##################################
#
def list(aWeb):
 cookie_openstack = aWeb.cookie_unjar('openstack')
 cookie_appformix = aWeb.cookie_unjar('appformix')

 if not cookie_appformix.get('appformix_token'):
  ctrl = cookie_openstack['appformix']
  res = aWeb.rest_call("appformix_authenticate",{'host':ctrl})
  if not res['auth'] == "OK":
   print "Error logging in - {}".format(str(res))
   return
  else:
   cookie_appformix['token'] = res['token']
   cookie_appformix['lifetime'] = res['lifetime']
   cookie_appformix['controller'] = ctrl
   aWeb.cookie_jar('appformix',cookie_appformix)
   aWeb.put_cookie()

 from datetime import datetime
 res = aWeb.rest_call("appformix_report_projects",{'host':cookie_appformix['controller'],'token':cookie_appformix['token']})
 print "<SECTION CLASS=content-left ID=div_content_left><ARTICLE><P>Usage Reports</P>"
 print "<DIV CLASS=controls>"
 print aWeb.button('reload', DIV='div_content', URL='sdcp.cgi?call=appformix_list')
 print "</DIV>"
 print "<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Project</DIV><DIV CLASS=th>Created</DIV><DIV CLASS=th STYLE='width:94px;'>&nbsp;</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for rep in res['reports']:
  print "<DIV CLASS=tr>"
  print "<!-- %s -->"%rep
  print "<DIV CLASS=td STYLE='max-width:180px; overflow-x:hidden;'>%s</DIV>"%rep['ProjectId']
  print "<DIV CLASS=td>%s</DIV>"%datetime.utcfromtimestamp(float(rep['Start'])/1e3)
  print "<DIV CLASS=td>"
  print aWeb.button('info', DIV='div_content_right', URL='sdcp.cgi?call=appformix_info&report=%s'%(rep['ReportId']))
  print "</DIV></DIV>"
 print "</DIV></DIV>"
 print "</ARTICLE></SECTION>"
 print "<SECTION CLASS=content-right ID=div_content_right></SECTION>"

def info(aWeb):
 cookie_openstack = aWeb.cookie_unjar('openstack')
 cookie_appformix = aWeb.cookie_unjar('appformix')
 reports = aWeb.rest_call("appformix_project_reports",{'host':cookie_appformix['controller'],'token':cookie_appformix['token'],'report':aWeb['report']})
 from ..site.openstack import dict2html
 for project in reports['Data']:
  if project['Project_Id'] == cookie_openstack['project_id']:
   print "<ARTICLE STYLE='overflow:auto;'>"
   print "<H2>Report %s</H2>"%(aWeb['report'])
   dict2html(project['Instances'],"Instances")
   dict2html(project['MetaData'],"MetaData")
   print "</ARTICLE>"
