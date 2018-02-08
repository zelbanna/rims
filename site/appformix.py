"""Module docstring.

HTML5 Ajax Appformix calls module

"""
__author__= "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__= "Beta"

############################### Openstack #############################
#
#
from ..devices.appformix import Device
from .. import SettingsContainer as SC

##################################### Report ##################################
#
def list(aWeb):
 from datetime import datetime
 # First auth..
 cookie = aWeb.cookie_unjar('openstack')
 ctrl = cookie.get('appformix')
 if not ctrl:
  print "Not logged in"
  return
 controller = Device(ctrl)
 res = controller.auth({'username':SC.appformix['username'], 'password':SC.appformix['password'] })
 if not res['result'] == "OK":
  print "Error logging in - {}".format(str(res))
  return

 pid    = cookie.get('project_id')
 pname  = cookie.get('project_name')
 resp   = controller.call("reports/project/metadata")
 import time
 print "<SECTION CLASS=content-left ID=div_content_left><ARTICLE><P>Usage Reports</P>"
 print "<!-- %s -->"%controller
 print "<DIV CLASS=controls>"
 print aWeb.button('reload', DIV='div_content', URL='sdcp.cgi?call=appformix_list')
 print "</DIV>"
 print "<DIV CLASS=table><DIV CLASS=thead><DIV CLASS=th>Project</DIV><DIV CLASS=th>Created</DIV><DIV CLASS=th STYLE='width:94px;'>&nbsp;</DIV></DIV>"
 print "<DIV CLASS=tbody>"
 for rep in resp['data']['Metadata']:
  print "<DIV CLASS=tr>"
  print "<!-- %s -->"%rep
  print "<DIV CLASS=td>%s</DIV>"%rep['ProjectId']
  print "<DIV CLASS=td>%s</DIV>"%datetime.utcfromtimestamp(float(rep['Start'])/1e3)
  print "<DIV CLASS=td>"
  print aWeb.button('info', DIV='div_content_right', URL='sdcp.cgi?call=appformix_info&report=%s'%(rep['ReportId']))
  print "</DIV></DIV>"
 print "</DIV></DIV>"
 print "</ARTICLE></SECTION>"
 print "<SECTION CLASS=content-right ID=div_content_right></SECTION>"

def info(aWeb):
 cookie = aWeb.cookie_unjar('openstack')
 ctrl = cookie.get('appformix')
 if not ctrl:
  print "Not logged in"
  return
 controller = Device(ctrl)
 res = controller.auth({'username':SC.appformix['username'], 'password':SC.appformix['password'] })
 if not res['result'] == "OK":
  print "Error logging in - {}".format(str(res))
  return
 reports = controller.call("reports/project/%s"%aWeb['report'])['data']['UsageReport']

 from ..site.openstack import dict2html
 for project in reports['Data']:
  if project['Project_Id'] == cookie['project_id']:
   print "<ARTICLE STYLE='overflow:auto;'>"
   print "<H2>Report %s</H2>"%(aWeb['report'])
   dict2html(project['Instances'],"Instances")
   dict2html(project['MetaData'],"MetaData")
   print "</ARTICLE>"
