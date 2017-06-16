"""Module docstring.

Ajax Openstack Neutron/Contrail calls module

"""
__author__= "Zacharias El Banna"
__version__ = "17.6.15GA"
__status__= "Production"

from sdcp.devices.openstack import OpenstackRPC
import sdcp.SettingsContainer as SC

def _print_info(aData):
 print "<TABLE style='width:99%'>"
 print "<THEAD><TH>Field</TH><TH>Data</TH></THEAD>"
 for key,value in aData.iteritems():
  if not isinstance(value,dict):
   print "<TR><TD>{}</TD><TD style='white-space:normal; overflow:auto;'>{}</TD></TR>".format(key,value)
  else:
   print "<TR><TD>{}</TD><TD style='white-space:normal; overflow:auto;'><TABLE style='width:100%'>".format(key)
   for k,v in value.iteritems():
    print "<TR><TD>{}</TD><TD>{}</TD></TR>".format(k,v)
   print "</TABLE></TD></TR>"
 print "</TABLE>"

############################### Neutron ##############################
#
def list(aWeb):
 cookie = aWeb.get_cookie()
 token  = cookie.get('os_user_token')
 if not token:
  print "Not logged in"
  return
 controller = OpenstackRPC(cookie.get('os_controller'),token)
 pname = cookie.get("os_project_name")

 ret = controller.call("8082","virtual-networks?fields=name,display_name,virtual_network_properties,network_ipam_refs")
 if not ret['result'] == "OK":
  print "Error retrieving list"
  return

 print "<DIV CLASS='z-table' style='width:394px'><TABLE style='width:99%'>"
 print "<THEAD style='height:20px'><TH COLSPAN=3><CENTER>Contrail VNs</CENTER></TH></THEAD>"
 print "<TR style='height:20px'><TD COLSPAN=3>"
 print "<A TITLE='Reload List' CLASS='z-btn z-small-btn z-op' OP=load DIV=div_navleft URL='ajax.cgi?call=neutron_list'><IMG SRC='images/btn-reboot.png'></A>"
 print "</TR>"
 print "<THEAD><TH>Network</TH><TH>Subnet</TH><TH>Operations</TH></THEAD>"
 for net in ret['data']['virtual-networks']:
  if not net.get('display_name'):
   continue
  print "<TR>"
  print "<!-- {} -->".format(str(net))
  print "<TD><A TITLE='Info' CLASS='z-op' DIV=div_navcont URL=ajax.cgi?call=neutron_action&id={0}&name={1}&op=info OP=load SPIN=true>{1}</A></TD>".format(net['uuid'],net['display_name'])
  print "<TD>"
  if net.get('network_ipam_refs'):
   for ipam in net['network_ipam_refs']:
    for sub in ipam['attr']['ipam_subnets']:
     print "{}/{}".format(sub['subnet']['ip_prefix'],sub['subnet']['ip_prefix_len'])
  print "</TD>"
  print "<TD>"
  #tmpl = "<A TITLE='{}' CLASS='z-btn z-op z-small-btn' DIV=div_navcont URL=ajax.cgi?call=neutron_action&name=" + net['name'] + "&id=" + net['id'] + "&op={} OP=load SPIN=true>{}</A>"
  #print tmpl.format('Network info','info','<IMG SRC=images/btn-info.png>')
  print "</TD>" 
 print "</TR>"
 print "</TABLE>"
 print "</DIV>"

def action(aWeb):
 cookie = aWeb.get_cookie()
 token  = cookie.get('os_user_token')
 if not token:
  print "Not logged in"
  return
 controller = OpenstackRPC(cookie.get('os_controller'),token)

 port  = cookie.get('os_neutron_port')
 url   = cookie.get('os_neutron_url')
 name = aWeb.get_value('name')
 id   = aWeb.get_value('id')
 op   = aWeb.get_value('op','info')

 if   op == 'info':
  print "<DIV CLASS='z-table' style='overflow:auto' ID=div_os_info>"
  ret = controller.call("8082","virtual-network/{}".format(id))
  print "<H2>{} ({})</H2>".format(name,id)
  _print_info(ret['data']['virtual-network'])
  print "</DIV>"
