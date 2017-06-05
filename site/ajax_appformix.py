"""Module docstring.

Ajax Appformix calls module

"""
__author__= "Zacharias El Banna"
__version__ = "17.6.1GA"
__status__= "Beta"

############################### Openstack #############################
#
# Assume we've created a token from the pane, so auth is done and we should pick up cookie template .. now username is the final thing .. before proper cookies in web reader
#
from sdcp.devices.appformix import AppformixRPC
import sdcp.SettingsContainer as SC

##################################### Report ##################################
#
def report(aWeb):
 from datetime import datetime
 from json import dumps
 cookie = aWeb.get_cookie()
 pid    = cookie.get('os_project_id')
 pname  = cookie.get('os_project_name')
 ctrl   = cookie.get('af_controller')
 # First auth..
 controller  = AppformixRPC(ctrl)
 res = controller.auth({'username':SC.appformix_username, 'password':SC.appformix_password })
 
 if not res['result'] == "OK":
  print "Error logging in - {}".format(str(res))
  return

 resp = controller.call("reports/project/metadata")
 # Many id's?
 for rep in resp['data']['Metadata']:
  reportid = rep['ReportId']
  report = controller.call("reports/project/{}".format(reportid))['data'].get('UsageReport',None)
  if report['ProjectId'] == pid:
   print "<DIV CLASS='z-table' style='overflow:auto; display:block' ID=div_appformix_info>"
   print "<H2>Report: {}</H2>".format(report['ReportId'])
   print "<H3>{} -> {}</H3>".format(datetime.utcfromtimestamp(float(report['Start'])/1e3),datetime.utcfromtimestamp(float(report['End'])/1e3))
   print "<H3>Created by: {}</H3>".format(report['CreatedBy']) 
   print "<TABLE style='width:99%; display:inline-block;'>"
   for ent in report['Data']:
    #print "<THEAD><TH>Field</TH><TH>Data</TH></THEAD>"
    print "<!-- Ent -->"
    for key,value in ent.iteritems():
     if isinstance(value,dict):
      print "<TR><TD>{}</TD><TD style='white-space:normal; overflow:auto;'><TABLE>".format(key)
      for k,v in value.iteritems():
       print "<TR><TD>{}</TD><TD>{}</TD></TR>".format(k,v)
      print "</TABLE></TD></TR>"
     elif isinstance(value,list):
      print "<TR><TD>{}</TD><TD style='white-space:normal; overflow:auto;'><TABLE>".format(key)
      for v in value:
       print "<TR><TD>{}</TD></TR>".format(v)
      print "</TABLE></TD></TR>"
     else:
      print "<TR><TD>{}</TD><TD style='white-space:normal; overflow:auto;'>{}</TD></TR>".format(key,value)
   print "</TABLE>"
   print "</DIV>"
