"""Module docstring.

Ajax Openstack calls module

"""
__author__= "Zacharias El Banna"
__version__ = "1.0GA"
__status__= "Production"

from sdcp.devices.openstack import OpenstackRPC

############################### Openstack #############################
#
# Assume we've created a token from the pane, so auth is done and we should pick up cookie from /tmp...cookie.json
#

def heat_view(aWeb):
 from sdcp.devices.openstack import OpenstackRPC
 import sdcp.SettingsContainer as SC
 (pid,pname) = aWeb.get_value('project').split('_')
 username = aWeb.get_value('username')
 password = aWeb.get_value('password')
 ctrl_ip  = aWeb.get_value('controller')
 controller = OpenstackRPC(ctrl_ip)
 if not controller.load(SC.openstack_cookietemplate.format(pname)):
  print "Not logged in"
  return
 port,lnk,svc = controller.get_service('heat','public')
 ret = controller.call(port,lnk + "/stacks") 
 print ret['data']['stacks']

 
def heat_add(aWeb):
 print aWeb.get_dict()
