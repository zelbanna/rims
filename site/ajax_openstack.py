"""Module docstring.

Ajax Openstack calls module

"""
__author__= "Zacharias El Banna"
__version__ = "1.0GA"
__status__= "Production"


############################### Openstack #############################
#
# Assume we've created a token from the pane, so auth is done and we should pick up cookie template .. now username is the final thing .. before proper cookies in web reader
#
from sdcp.devices.openstack import OpenstackRPC
import sdcp.SettingsContainer as SC

def _print_info(aName,aData):
 print "<DIV CLASS='z-table' style='overflow:auto'>"
 print "<H1>{}</H1>".format(aName)
 print "<TABLE style='width:99%'>"
 print "<TR><TH>Field</TH><TH>Data</TH></TR>"
 for key,value in aData.iteritems():
  if not isinstance(value,dict):
   print "<TR><TD>{}</TD><TD style='white-space:normal; overflow:auto;'>{}</TD></TR>".format(key,value)
  else:
   print "<TR><TD>{}</TD><TD style='white-space:normal; overflow:auto;'><TABLE style='width:100%'>".format(key)
   for k,v in value.iteritems():
    print "<TR><TD>{}</TD><TD>{}</TD>".format(k,v)
   print "</TABLE></TD></TR>"
 print "</TABLE>"
 print "</DIV>"
 

############################### Heatstack #############################
#
# rename to heat_list
def heat_list(aWeb):
 project = aWeb.get_value('project')
 (pid,pname) = project.split('_')
 controller  = OpenstackRPC("127.0.0.1")
 if not controller.load(SC.openstack_cookietemplate.format(pname)):
  print "Not logged in"
  return
 port,lnk,svc = controller.get_service('heat','public')
 ret = controller.call(port,lnk + "/stacks") 
 print "<DIV CLASS='z-table' style='width:354px'><TABLE style='width:99%'>"
 print "<TR style='height:20px'><TH COLSPAN=3><CENTER>Heat Stacks</CENTER></TH></TR>"
 print "<TR style='height:20px'><TD COLSPAN=3>"
 print "<A TITLE='Reload List' CLASS='z-btn z-small-btn z-op' OP=load DIV=div_navleft LNK='ajax.cgi?call=openstack_heat_list&project={}'><IMG SRC='images/btn-reboot.png'></A>".format(project)
 print "<A TITLE='Add service' CLASS='z-btn z-small-btn z-op' OP=load DIV=div_navcont LNK='ajax.cgi?call=openstack_heat_add&project={}'><IMG SRC='images/btn-add.png'></A>".format(project)
 print "</TR>"
 print "<TR><TH style='width:164px;'>Name</TH><TH style='width:120px;'>Status</TH><TH style='width:94px;'>Operations</TH></TR>"
 for stack in ret['data']['stacks']:
  print "<TR>"
  print "<TD>{}</TD>".format(stack['stack_name'])
  print "<TD>{}</TD>".format(stack['stack_status'])
  print "<TD>"
  print "<A TITLE='Stack info' CLASS='z-btn z-op z-small-btn' DIV=div_navcont LNK=ajax.cgi?call=openstack_heat_action&project={0}&name={1}&id={2}&op=info  OP=load SPIN=true><IMG SRC='images/btn-info.png'></A>".format(project,stack['stack_name'],stack['id'])
  if stack['stack_status'] == "CREATE_COMPLETE" or stack['stack_status'] == "CREATE_FAILED":
   print "<A TITLE='Remove stack' CLASS='z-btn z-op z-small-btn' DIV=div_navcont LNK=ajax.cgi?call=openstack_heat_action&project={0}&name={1}&id={2}&op=remove OP=load SPIN=true><IMG SRC='images/btn-remove.png'></A>".format(project,stack['stack_name'],stack['id'])
  print "</TD>"
  print "</TR>"
 print "</TABLE>"
 print "</DIV>"

#
# Heat Action with op
#
def heat_action(aWeb):
 (pid,pname) = aWeb.get_value('project').split('_')
 name = aWeb.get_value('name')
 id   = aWeb.get_value('id')
 op   = aWeb.get_value('op','info')
 controller = OpenstackRPC("127.0.0.1")
 if not controller.load(SC.openstack_cookietemplate.format(pname)):
  print "Not logged in"
  return
 port,lnk,svc = controller.get_service('heat','public')
 if   op == 'info':
  ret = controller.call(port,lnk + "/stacks/{}/{}".format(name,id))
  _print_info(name,ret['data']['stack'])
 elif op == 'remove':
  ret = controller.call(port,lnk + "/stacks/{}/{}".format(name,id), method='DELETE')
  print "<DIV CLASS='z-table'>"
  print "<H2>Removing {}</H2>".format(name)
  if ret['code'] == 204:
   print "Stack removed"
  else:
   print "Error code: {}".format(ret['code'])
  print "</DIV>"

def heat_add(aWeb):
 print aWeb.get_dict()

############################### Contrail ##############################
#
def contrail_list(aWeb):
 (pid,pname) = aWeb.get_value('project').split('_')
 controller = OpenstackRPC("127.0.0.1")
 if not controller.load(SC.openstack_cookietemplate.format(pname)):
  print "Not logged in"
  return
 ret = controller.call("8082","virtual-networks")
 # print ret
 print "<DIV CLASS='z-table' style='width:354px'><TABLE style='width:99%'>"
 print "<TR style='height:20px'><TH COLSPAN=3><CENTER>Contrail VNs</CENTER></TH></TR>"
 print "<TR><TH>Owner</TH><TH>Network</TH></TR>"
 for net in ret['data']['virtual-networks']:
  # net['uuid']
  if net['fq_name'][1] == pname:
   print "<TR><TD>{}</TD><TD>{}</TD></TR>".format(pname,net['fq_name'][2])
 print "</TABLE>"
 print "</DIV>"

################################# Nova ###############################
#
def nova_list(aWeb):
 project = aWeb.get_value('project')
 (pid,pname) = project.split('_')
 controller  = OpenstackRPC("127.0.0.1")
 if not controller.load(SC.openstack_cookietemplate.format(pname)):
  print "Not logged in"
  return
 port,lnk,svc = controller.get_service('nova','public')
 ret = controller.call(port,lnk + "/servers")
 print "<DIV CLASS='z-table' style='width:354px'><TABLE style='width:99%'>"
 print "<TR style='height:20px'><TH COLSPAN=3><CENTER>Nova Servers</CENTER></TH></TR>"
 print "<TR style='height:20px'><TD COLSPAN=3>"
 print "<A TITLE='Reload List' CLASS='z-btn z-small-btn z-op' OP=load DIV=div_navleft LNK='ajax.cgi?call=openstack_nova_list&project={}'><IMG SRC='images/btn-reboot.png'></A>".format(project)
 print "</TR>"
 print "<TR><TH>Name</TH><TH style='width:94px;'>Operations</TH></TR>"
 for server in ret['data']['servers']:
  print "<TR>"
  print "<TD>{}</TD>".format(server['name'])
  print "<TD>"
  print "<A TITLE='VM info'   CLASS='z-btn z-op z-small-btn' DIV=div_navcont LNK=ajax.cgi?call=openstack_nova_action&project={0}&name={1}&id={2}&op=info   OP=load SPIN=true><IMG SRC='images/btn-info.png'></A>".format(project,server['name'],server['id'])
  print "<A TITLE='Remove VM' CLASS='z-btn z-op z-small-btn' DIV=div_navcont LNK=ajax.cgi?call=openstack_nova_action&project={0}&name={1}&id={2}&op=remove OP=load SPIN=true><IMG SRC='images/btn-remove.png'></A>".format(project,server['name'],server['id'])
  print "</TD>"
  print "</TR>"
 print "</TABLE>"
 print "</DIV>"

#
# Actions
# 
def nova_action(aWeb):
 (pid,pname) = aWeb.get_value('project').split('_')
 name = aWeb.get_value('name')
 id   = aWeb.get_value('id')
 op   = aWeb.get_value('op','info')
 controller = OpenstackRPC("127.0.0.1")
 if not controller.load(SC.openstack_cookietemplate.format(pname)):
  print "Not logged in"
  return
 port,lnk,svc = controller.get_service('nova','public')

 if   op == 'info':
  # Info
  ret = controller.call(port,lnk + "/servers/{}".format(id))
  _print_info(name,ret['data']['server'])
 elif op == 'remove':
  # Remove VM
  ret = controller.call(port,lnk + "/servers/{}".format(id), method='DELETE')
  print "<DIV CLASS='z-table'>"
  print "<H2>Removing {}</H2>".format(name)
  if ret['code'] == 204:
   print "Server removed"
  else:
   print "Error code: {}".format(ret['code'])
  print "</DIV>"
