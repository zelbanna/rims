"""Module docstring.

Ajax Openstack calls module

"""
__author__= "Zacharias El Banna"
__version__ = "1.0GA"
__status__= "Production"

from sdcp.devices.openstack import OpenstackRPC
import sdcp.SettingsContainer as SC

############################### Openstack #############################
#
# Assume we've created a token from the pane, so auth is done and we should pick up cookie template .. now username is the final thing .. before proper cookies in web reader
#

def heat_view(aWeb):
 (pid,pname) = aWeb.get_value('project').split('_')
 controller = OpenstackRPC("127.0.0.1")
 if not controller.load(SC.openstack_cookietemplate.format(pname)):
  print "Not logged in"
  return
 port,lnk,svc = controller.get_service('heat','public')
 ret = controller.call(port,lnk + "/stacks") 
 print "<DIV CLASS='z-table' style='width:1100px'><TABLE>"
 print "<TR>"
 print "<TH style='width:244px;'>ID</TH><TH style='width:134px;'>Creation Time</TH><TH style='width:124px;'>Status</TH><TH style='width:174px;'>Name</TH><TH style='width:244px;'>Description</TH><TH style='width:30px;'>Operations</TH></TR>"
 for stack in ret['data']['stacks']:
  print "<TR>"
  print "<TD>{}</TD>".format(stack['id'])
  print "<TD>{}</TD>".format(stack['creation_time'].replace("T"," - "))
  print "<TD>{}</TD>".format(stack['stack_status'])
  print "<TD>{}</TD>".format(stack['stack_name'])
  print "<TD>{}</TD>".format(stack['description'])
  print "<TD>"
  print "<A TITLE='Stack info' CLASS='z-btn z-op z-small-btn' DIV=div_navcont LNK=ajax.cgi?call=openstack_heat_info&project={0}&stack_name={1}&id={2} OP=load SPIN=true><IMG SRC='images/btn-info.png'></A>".format(aWeb.get_value('project'),stack['stack_name'],stack['id'])
  if stack['stack_status'] == "CREATE_COMPLETE" or stack['stack_status'] == "CREATE_FAILED":
   print "<A TITLE='Remove stack' CLASS='z-btn z-op z-small-btn' DIV=div_navcont LNK=ajax.cgi?call=openstack_heat_remove&project={0}&stack_name={1}&id={2} OP=load SPIN=true><IMG SRC='images/btn-remove.png'></A>".format(aWeb.get_value('project'),stack['stack_name'],stack['id'])
  print "</TD>"
  print "</TR>"
 print "</TABLE>"
 print "</DIV>"

def heat_remove(aWeb):
 (pid,pname) = aWeb.get_value('project').split('_')
 sname = aWeb.get_value('stack_name')
 sid   = aWeb.get_value('id')
 controller = OpenstackRPC("127.0.0.1")
 if not controller.load(SC.openstack_cookietemplate.format(pname)):
  print "Not logged in"
  return
 print "<DIV CLASS='z-table'>"
 print "<H1>Removing {}</H1>".format(sname)
 port,lnk,svc = controller.get_service('heat','public')
 ret = controller.call(port,lnk + "/stacks/{}/{}".format(sname,sid), arg= {}, method='DELETE')
 if ret['code'] == 204:
  print "Stack removed"
 else:
  print "Error code: {}".format(ret['code'])
 print "</DIV>"

def heat_info(aWeb):
 (pid,pname) = aWeb.get_value('project').split('_')
 sname = aWeb.get_value('stack_name')
 sid   = aWeb.get_value('id')
 controller = OpenstackRPC("127.0.0.1")
 if not controller.load(SC.openstack_cookietemplate.format(pname)):
  print "Not logged in"
  return
 port,lnk,svc = controller.get_service('heat','public')
 ret = controller.call(port,lnk + "/stacks/{}/{}".format(sname,sid))
 print "<DIV CLASS='z-table'>"
 print "<H1>{}</H1>".format(sname)
 print "<TABLE>"
 print "<TR><TH>Field</TH><TH>Data</TH></TR>"
 for key,value in ret['data']['stack'].iteritems():
  if not isinstance(value,dict):
   print "<TR><TD>{}</TD><TD style='white-space:normal; overflow:auto;'>{}</TD></TR>".format(key,value)
  else:
   print "<TR><TD>{}</TD><TD style='white-space:normal; overflow:auto;'><TABLE style='width:100%'>".format(key)
   for k,v in value.iteritems():
    print "<TR><TD>{}</TD><TD>{}</TD>".format(k,v)
   print "</TABLE></TD></TR>"
 print "</TABLE>"
 print "</DIV>"

def heat_add(aWeb):
 print aWeb.get_dict()

def contrail_view(aWeb):
 (pid,pname) = aWeb.get_value('project').split('_')
 controller = OpenstackRPC("127.0.0.1")
 if not controller.load(SC.openstack_cookietemplate.format(pname)):
  print "Not logged in"
  return
 ret = controller.call("8082","virtual-networks")
 print "<DIV CLASS='z-table' style='width:500px;'>"
 print "<H1>Virtual Networks</H1>"
 print "<TABLE>"
 print "<TR><TH>Network</TH><TH>UUID</TH></TR>"
 for net in ret['data']['virtual-networks']:
  if net['fq_name'][1] == pname:
   print "<TR><TD>{}</TD><TD>{}</TD></TR>".format(net['fq_name'][2],net['uuid'])
 print "</TABLE>"
 print "</DIV>"
