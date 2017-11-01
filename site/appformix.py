"""Module docstring.

Ajax Appformix calls module

- left and right divs frames (div_content_left/right) needs to be created by ajax call
"""
__author__= "Zacharias El Banna"
__version__ = "17.10.4"
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
 pid    = aWeb.cookie.get('os_project_id')
 pname  = aWeb.cookie.get('os_project_name')
 ctrl   = aWeb.cookie.get('af_controller')
 # First auth..
 controller  = Device(ctrl)
 res = controller.auth({'username':PC.appformix['username'], 'password':PC.appformix['password'] })
 
 if not res['result'] == "OK":
  print "Error logging in - {}".format(str(res))
  return

 resp = controller.call("reports/project/metadata")
 # Many id's?
 for rep in resp['data']['Metadata']:
  reportid = rep['ReportId']
  report = controller.call("reports/project/{}".format(reportid))['data'].get('UsageReport',None)
  if report['ProjectId'] == pid:
   print "<DIV CLASS=z-frame style='overflow:auto; display:block' ID=div_appformix_info>"
   print "<H2>Report: {}</H2>".format(report['ReportId'])
   print "<H3>{} -> {}</H3>".format(datetime.utcfromtimestamp(float(report['Start'])/1e3),datetime.utcfromtimestamp(float(report['End'])/1e3))
   # print "<H3>Created by: {}</H3>".format(report['CreatedBy']) 
   print "<DIV CLASS=z-table style='display:inline-block;'><DIV CLASS=tbody>"
   for ent in report['Data']:
    #print "<THEAD><TH>Field</TH><TH>Data</TH></THEAD>"
    print "<!-- Ent -->"
    for key,value in ent.iteritems():
     if isinstance(value,dict):
      print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><TD style='white-space:normal; overflow:auto;'><DIV CLASS=z-table style='width:auto'><DIV CLASS=tbody>".format(key)
      for k,v in value.iteritems():
       print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV></DIV>".format(k,v)
      print "</DIV></DIV></DIV></DIV>"
     elif isinstance(value,list):
      print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><TD style='white-space:normal; overflow:auto;'><DIV CLASS=z-table style='width:auto'><DIV CLASS=tbody>".format(key)
      for v in value:
       print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV></DIV>".format(v)
      print "</DIV></DIV></DIV></DIV>"
     else:
      print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><TD style='white-space:normal; overflow:auto;'>{}</DIV></DIV>".format(key,value)
   print "</DIV></DIV>"
   print "</DIV>"
