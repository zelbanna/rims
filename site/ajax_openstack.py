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
 print "<DIV CLASS='z-table'><TABLE style='width:1060px'>"
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
  if stack['stack_status'] == "CREATE_COMPLETE":
   print "<A TITLE='Remove stack' CLASS='z-btn z-op z-small-btn' DIV=div_navcont LNK=ajax.cgi?call=openstack_heat_remove&project={0}&name={1}&id={2} OP=load SPIN=true><IMG SRC='images/btn-remove.png'></A>".format(aWeb.get_value('project'),stack['stack_name'],stack['id'])
  print "</TD>"
  print "</TR>"
 print "</TABLE>"
 print "</DIV>"

def heat_remove(aWeb):
 (pid,pname) = aWeb.get_value('project').split('_')
 controller = OpenstackRPC("127.0.0.1")
 if not controller.load(SC.openstack_cookietemplate.format(pname)):
  print "Not logged in"
  return
 print "Removing stack<BR>"
 print aWeb.get_dict()

def heat_add(aWeb):
 print aWeb.get_dict()
