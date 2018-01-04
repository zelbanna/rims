"""Module docstring.

HTML5 Ajax Appformix calls module

"""
__author__= "Zacharias El Banna"
__version__ = "17.11.01GA"
__status__= "Beta"

############################### Openstack #############################
#
#
from sdcp.devices.appformix import Device
from sdcp import PackageContainer as PC

##################################### Report ##################################
#
def report(aWeb):
 from datetime import datetime
 from json import dumps
 # First auth..
 controller  = Device(ctrl)
 res = controller.auth({'username':PC.appformix['username'], 'password':PC.appformix['password'] })
  if not res['result'] == "OK":
  print "Error logging in - {}".format(str(res))
  return

 cookie = aWeb.cookie_unjar('openstack')
 pid    = cookie.get('project_id')
 pname  = cookie.get('project_name')
 ctrl   = cookie.get('appformix')
 resp   = controller.call("reports/project/metadata")

 # Many id's?
 for rep in resp['data']['Metadata']:
  reportid = rep['ReportId']
  report = controller.call("reports/project/{}".format(reportid))['data'].get('UsageReport',None)
  if report['ProjectId'] == pid:
   print "<ARTICLE STYLE='overflow:auto;'>"
   print "<H2>Report: {}</H2>".format(report['ReportId'])
   print "<H3>{} -> {}</H3>".format(datetime.utcfromtimestamp(float(report['Start'])/1e3),datetime.utcfromtimestamp(float(report['End'])/1e3))
   # print "<H3>Created by: {}</H3>".format(report['CreatedBy']) 
   print "<DIV CLASS=table STYLE='display:inline-block;'><DIV CLASS=tbody>"
   for ent in report['Data']:
    #print "<THEAD><TH>Field</TH><TH>Data</TH></THEAD>"
    print "<!-- Ent -->"
    for key,value in ent.iteritems():
     if isinstance(value,dict):
      print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><TD STYLE='white-space:normal; overflow:auto;'><DIV CLASS=table STYLE='width:auto'><DIV CLASS=tbody>".format(key)
      for k,v in value.iteritems():
       print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV></DIV>".format(k,v)
      print "</DIV></DIV></DIV></DIV>"
     elif isinstance(value,list):
      print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><TD STYLE='white-space:normal; overflow:auto;'><DIV CLASS=table STYLE='width:auto'><DIV CLASS=tbody>".format(key)
      for v in value:
       print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV></DIV>".format(v)
      print "</DIV></DIV></DIV></DIV>"
     else:
      print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><TD STYLE='white-space:normal; overflow:auto;'>{}</DIV></DIV>".format(key,value)
   print "</DIV></DIV>"
   print "</ARTICLE>"
