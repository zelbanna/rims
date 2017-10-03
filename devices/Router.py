"""Module docstring.

WLC Base Class

Junos Router Base Class
- Junos (Template Class)
- SRX, EX, QFX, MX sub classes

Uses PackageContainer for login info..

"""
__author__ = "Zacharias El Banna"
__version__ = "17.6.1GA"
__status__ = "Production"

import sdcp.PackageContainer as PC
from GenDevice import GenDevice
from netsnmp import VarList, Varbind, Session

#
# TODO: Widgets should take two args or list of arguments!
#
################################ JUNOS Object #####################################
#
# Connect to Router, a couple of RPCs will be issued from there
#

class Junos(GenDevice):

 @classmethod
 def get_widgets(cls):
  return ['widget_up_interfaces','widget_lldp','widget_archive' ]

 def __init__(self,ahost,adomain = None, atype = 'Junos'):
  GenDevice.__init__(self,ahost,adomain,atype)
  from jnpr.junos import Device
  from jnpr.junos.utils.config import Config
  self._router = Device(self._ip, user=PC.netconf['username'], password=PC.netconf['password'], normalize=True)
  self._config = Config(self._router)
  self._model = ""
  self._version = ""
  self._interfacesname = {}
 
 def __str__(self):
  return "{} Type:{} Model:{} Version:{}".format(str(self._router),  self._type, self._model, self._version)

 def connect(self):
  try:
   self._router.open()
   self._model = self._router.facts['model']
   self._version = self._router.facts['version']
  except Exception as err:
   self.log_msg("System Error - Unable to connect to router: " + str(err))
   return False
  return True

 def close(self):
  try:
   self._router.close()
  except Exception as err:
   self.log_msg("System Error - Unable to properly close router connection: " + str(err))

 def get_rpc(self):
  return self._router.rpc

 def get_dev(self):
  return self._router

 def get_interface_name(self, aifl):
  return self._interfacesname.get(aifl.split('.')[0],None)
 
 #
 # Netconf shit
 # 
 def ping_rpc(self,ip):
  result = self._router.rpc.ping(host=ip, count='1')
  return len(result.xpath("ping-success"))

 def get_facts(self,akey):
  return self._router.facts[akey]

 def load_interfaces_name(self):
  interfaces = self._router.rpc.get_interface_information(descriptions=True)
  for interface in interfaces:
   ifd         = interface.find("name").text
   description = interface.find("description").text
   self._interfacesname[ifd] = description

 def get_up_interfaces(self):
  interfaces = self._router.rpc.get_interface_information()
  result = []
  for ifd in interfaces:
   status = map((lambda pos: ifd[pos].text), [0,2,4,5])
   # Split ge-0/0/0 into ge and 0/0/0, remove extra numbers for aeX interfaces
   tp = status[0].partition('-')[0].rstrip('0123456789')
   if tp in [ 'ge', 'fe', 'xe', 'et','st0','ae' ] and status[1] == "up":
    result.append(status)
  return result

 def get_lldp(self):
  neighbors = self._router.rpc.get_lldp_neighbors_information()
  result = []
  for neigh in neighbors:
   # Remote system always last, remote port second to last, local is always first and pos 3 (2) determines if there is a mac or not
   fields = len(neigh)-1
   result.append([ neigh[fields].text,neigh[3].text if neigh[2].text == "Mac address" else '-',neigh[0].text,neigh[fields-1].text ])
  return result

 #
 # End of NETCONF crap
 # 
 def widget_archive(self):
  print "To be implemented"

 def widget_up_interfaces(self):
  if not self.connect():
   print "Could not connect"
   return
  ifs = self.get_up_interfaces()
  self.close()
  from sdcp.tools.Grapher import Grapher
  graph = Grapher()
  graph.load_conf()
  gdev = graph.get_entry(self._hostname + "." + self._domain)
  if gdev and gdev['update'] == 'yes':
   print "<DIV ID=graph_config></DIV>"
  print "<DIV CLASS=z-frame><DIV CLASS=z-table>"
  print "<DIV CLASS=thead><DIV CLASS=th>Interface</DIV><DIV CLASS=th>State</DIV><DIV CLASS=th>SNMP</DIV><DIV CLASS=th>Description</DIV></DIV>"
  print "<DIV CLASS=tbody>"
  for entry in ifs:
   print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>".format(entry[0],entry[1])
   if gdev and gdev['update'] == 'yes':
    print "<A CLASS='z-op' DIV=graph_config URL='ajax.cgi?call=graph_wm&hostname={1}&domain={2}&index={0}'>{0}</A>".format(entry[2],self._hostname,self._domain)
   else:
    print entry[2]
   print "</DIV><DIV CLASS=td>{}</DIV></DIV>\n".format(entry[3])
  print "</DIV></DIV></DIV>"

 def widget_lldp(self):
  if self.connect():
   neigh = self.get_lldp()
   self.close()
   print "<DIV CLASS=z-frame><DIV CLASS=z-table>"
   print "<DIV CLASS=thead><DIV CLASS=th>Neighbor</DIV><DIV CLASS=th>MAC</DIV><DIV CLASS=th>Local_Port</DIV><DIV CLASS=th>Destination_Port</DIV></DIV>"
   print "<DIV CLASS=tbody>"
   for entry in neigh:
    print "<DIV CLASS=tr><DIV CLASS=td>{0}</DIV><DIV CLASS=td>{1}</DIV><DIV CLASS=td>{2}</DIV><DIV CLASS=td>{3}</DIV></DIV>".format(entry[0],entry[1],entry[2],entry[3])
   print "</DIV></DIV></DIV>"  
  else:
   print "Could not connect"
 #
 # SNMP is much smoother than Netconf for some things :-)
 #
 def quick_load(self):
  try:
   devobjs = VarList(Varbind('.1.3.6.1.2.1.1.1.0'))
   session = Session(Version = 2, DestHost = self._ip, Community = PC.snmp['read_community'], UseNumeric = 1, Timeout = 100000, Retries = 2)
   session.get(devobjs)
   datalist = devobjs[0].val.split()
   self._model = datalist[3]
   self._version = datalist[datalist.index('JUNOS') + 1].strip(',')
   if "ex" in self._model:
    self._type = "ex"
   elif "srx" in self._model:
    self._type = "srx"
   elif "qfx" in self._model:
    self._type = "qfx"
   elif "mx" in self._model:
    self._type = "mx"
  except:
   pass

 def print_conf(self,argdict):
  import sdcp.PackageContainer as PC
  print "set system host-name {}<BR>".format(argdict['name'])
  if PC.netconf['username'] == 'root':
   print "set system root-authentication encrypted-password \"{}\"<BR>".format(PC.netconf['encrypted'])
  else:
   print "set system login user {0} class super-user<BR>".format(PC.netconf['username'])
   print "set system login user {0} authentication encrypted-password \"{1}\"<BR>".format(PC.netconf['username'],PC.netconf['encrypted'])
  base  = "set groups default_system "
  print base + "system domain-name {}<BR>".format(argdict['domain'])
  print base + "system domain-search {}<BR>".format(argdict['domain'])
  print base + "system name-server {}<BR>".format(PC.sdcp['dnssrv'])
  print base + "system services ssh root-login allow<BR>"
  print base + "system services netconf ssh<BR>"
  print base + "system syslog user * any emergency<BR>"
  print base + "system syslog file messages any notice<BR>"
  print base + "system syslog file messages authorization info<BR>"
  print base + "system syslog file interactive-commands interactive-commands any<BR>"
  print base + "system archival configuration transfer-on-commit<BR>"
  print base + "system archival configuration archive-sites ftp://{}/<BR>".format(PC.sdcp['anonftp'])
  print base + "system commit persist-groups-inheritance<BR>"
  print base + "system ntp server {}<BR>".format(PC.sdcp['ntpsrv'])
  print base + "routing-options static route 0.0.0.0/0 next-hop {}<BR>".format(argdict['gateway'])
  print base + "routing-options static route 0.0.0.0/0 no-readvertise<BR>"
  print base + "snmp community {} clients {}/{}<BR>".format(PC.snmp['read_community'],argdict['subnet'],argdict['mask'])
  print base + " protocols lldp port-id-subtype interface-name<BR>"
  print base + " protocols lldp interface all<BR>"
  print base + " class-of-service host-outbound-traffic forwarding-class network-control<BR>"
  print "set apply-groups default_system<BR>"

################################ WLC Object #####################################
#
# Simpler WLC class
#

class WLC(GenDevice):

 @classmethod
 def get_widgets(cls):
  return ['widget_switch_table']

 def __init__(self,ahost, adomain = None):
  GenDevice.__init__(self,ahost, adomain, 'wlc')
  
 def __str__(self):
  return "WLC - {}".format(GenDevice.__str__(self))

 def widget_switch_table(self):
  from socket import gethostbyaddr
  try:
   # Length of below is used to offset ip address (32) + 1 and mac base (33) + 1 
   cssidobjs = VarList(Varbind(".1.3.6.1.4.1.14525.4.4.1.1.1.1.15"))
   cipobjs = VarList(Varbind(".1.3.6.1.4.1.14525.4.4.1.1.1.1.4"))
    
   session = Session(Version = 2, DestHost = self._ip, Community = PC.snmp['read_community'], UseNumeric = 1, Timeout = 100000, Retries = 2)
   session.walk(cssidobjs)
   session.walk(cipobjs)
  except:
   return
        
  ipdict= dict(map(lambda res: (res.tag[33:], res.val) ,cipobjs))
  print "<DIV CLASS=z-frame><DIV CLASS=z-table>"
  print "<DIV CLASS=thead><DIV CLASS=th>Name</DIV><DIV CLASS=th>IP</DIV><DIV CLASS=th>MAC</DIV><DIV CLASS=th>SSid</DIV></DIV>"
  print "<DIV CLASS=tbody>"
  for res in cssidobjs:
   macbase=res.tag[34:]
   mac = (macbase+"."+res.iid).split(".")
   mac = ":".join(map(lambda x: hex(int(x))[2:],mac))
   try:
    clientname = gethostbyaddr(ipdict[macbase])[0]
   except:
    clientname = "unknown"
   print "<DIV CLASS=tr><DIV CLASS=td>" + clientname + "&nbsp;</DIV><DIV CLASS=td>" + ipdict.get(macbase) + "&nbsp;</DIV><DIV CLASS=td>" + mac + "&nbsp;</DIV><DIV CLASS=td>" + res.val + "</DIV></DIV>"
  print "</DIV></DIV></DIV>"

################################ SRX Object #####################################

class SRX(Junos):

 @classmethod
 def get_widgets(cls):
  return Junos.get_widgets()

 def __init__(self,ahost,adomain=None):
  Junos.__init__(self, ahost,adomain,'srx')
  self.dnslist = []
  self.dhcpip = ""
  self.tunnels = 0

 def __str__(self):
  return Junos.__str__(self) + " Resolvers:" + str(self.dnslist) + " IP:" + self.dhcpip + " IPsec:" + str(self.tunnels)

 def load_dhcp(self):
  try:
   result = self._router.rpc.get_dhcp_client_information() 
   addresslist = result.xpath(".//address-obtained")
   if len(addresslist) > 0:
    self.dnslist = result.xpath(".//dhcp-option[dhcp-option-name='name-server']/dhcp-option-value")[0].text.strip('[] ').replace(", "," ").split()
    self.dhcpip = addresslist[0].text
  except Exception as err:
   self.log_msg("System Error - verifying DHCP assignment: " + str(err))
   return False
  return True

 def renew_dhcp(self, interface):
  try:
   return self._router.rpc.cli("request system services dhcp renew " + interface, format='text')
  except Exception as err:
   self.log_msg("System Error - cannot renew DHCP lease: " +str(err))
  return False
   
 def get_ipsec(self,gwname):
  from lxml import etree
  try:
   # Could actually just look at "show security ike security-associations" - len of that result
   # is the number of ikes (not tunnels though) with GW etc
   # If tunnel is down though we don't know if config is aggresive or state down, should check
   self.tunnels = int(self._router.rpc.get_security_associations_information()[0].text)
   ike = self._router.rpc.get_config(filter_xml=etree.XML('<configuration><security><ike><gateway></gateway></ike></security></configuration>'))
   address = ike.xpath(".//gateway[name='" + gwname + "']/address")
   return address[0].text, self.tunnels
  except Exception as err:
   self.log_msg("System Error - getting IPsec data: " + str(err))
   return None, self.tunnels

 def set_ipsec(self,gwname,oldip,newip):
  try:
   self._config.load("set security ike gateway " + gwname + " address " + newip, format = 'set')
   self._config.load("delete security ike gateway " + gwname + " address " + oldip, format = 'set')
   self._config.commit("commit by setIPsec ["+gwname+"]")
  except Exception as err:
   self.log_msg("System Error - modifying IPsec: " + str(err))
   return False
  return True

################################ EX Object #####################################

class EX(Junos):

 @classmethod
 def get_widgets(cls):
  widgets = ['widget_switch_table']
  widgets.extend(Junos.get_widgets())
  return widgets

 def __init__(self,ahost,adomain=None):
  Junos.__init__(self, ahost,adomain,'ex')
  self._style  = None
  self._interfacenames = {}

 def __str__(self):
  return Junos.__str__(self) + " Style:" + str(self._style)

 #
 # should prep for ELS only and send "instance = 'default-instance'" - then id could be retrieved too
 # since grouping is different
 #
 def get_switch_table(self):
  fdblist = []
  try:
   swdata = self._router.rpc.get_ethernet_switching_table_information()
   if swdata.tag == "l2ng-l2ald-rtb-macdb":
    self._style = "ELS"
    for entry in swdata[0].iter("l2ng-mac-entry"):
     vlan = entry.find("l2ng-l2-mac-vlan-name").text
     mac  = entry.find("l2ng-l2-mac-address").text     
     interface = entry.find("l2ng-l2-mac-logical-interface").text
     fdblist.append([ vlan, mac, interface, self.get_interface_name(interface) ])
   elif swdata.tag == "ethernet-switching-table-information":
    self._style = "Legacy"
    for entry in swdata[0].iter("mac-table-entry"):
     vlan = entry.find("mac-vlan").text
     mac  = entry.find("mac-address").text
     interface = entry.find(".//mac-interfaces").text
     if not mac == "*" and not interface == "Router":
      fdblist.append([ vlan, mac, interface, self.get_interface_name(interface) ]) 
  except Exception as err:
   self.log_msg("System Error - fetching FDB: " + str(err))
  return fdblist

 #
 # Widgets should be self contained - connect, load names etc
 #
 def widget_switch_table(self):
  try:
   if self.connect():
    self.load_interfaces_name()
    print "<DIV CLASS=z-frame><DIV CLASS=z-table>"
    print "<DIV CLASS=thead><DIV CLASS=th>VLAN</DIV><DIV CLASS=th>MAC</DIV><DIV CLASS=th>Interface</DIV><DIV CLASS=th>Description</DIV></DIV>"
    print "<DIV CLASS=tbody>"
    fdb = self.get_switch_table()
    for entry in fdb:
     print "<DIV CLASS=tr><DIV CLASS=td>" + "&nbsp;</DIV><DIV CLASS=td>".join(entry) + "</DIV></DIV>\n"
    print "</DIV></DIV></DIV>"
    self.close()
   else:
    print "Could not connect"
  except Exception as err:
   self.log_msg("EX widget switch table: Error [{}]".format(str(err)))
   print "<B>Error - issue loading widget: {}</B>".format(str(err))

################################ QFX Object #####################################

class QFX(Junos):

 @classmethod
 def get_widgets(cls):
  widgets = ['widget_switch_table']
  widgets.extend(Junos.get_widgets())
  return widgets

 def __init__(self,ahost,adomain=None):
  Junos.__init__(self, ahost,adomain,'qfx')
  self._style  = 'els'
  self._interfacenames = {}

 def __str__(self):
  return Junos.__str__(self) + " Style:" + str(self._style)

 #
 # should prep for ELS only and send "instance = 'default-instance'" - then id could be retrieved too
 # since grouping is different
 #
 def get_switch_table(self):
  fdblist = []
  try:
   swdata = self._router.rpc.get_ethernet_switching_table_information()
   for vlan in swdata.iter("l2ng-l2ald-mac-entry-vlan"):
    for entry in vlan.iter("l2ng-mac-entry"):
     vlan = entry.find("l2ng-l2-mac-vlan-name").text
     mac  = entry.find("l2ng-l2-mac-address").text     
     interface = entry.find("l2ng-l2-mac-logical-interface").text
     fdblist.append([ vlan, mac, interface, self.get_interface_name(interface) ])
  except Exception as err:
   self.log_msg("System Error - fetching FDB: " + str(err))
  return fdblist

 #
 # Widgets should be self contained - connect, load names etc
 #
 def widget_switch_table(self):
  try:
   if self.connect():
    self.load_interfaces_name()
    fdb = self.get_switch_table()
    self.close()
    print "<DIV CLASS=z-frame><DIV CLASS=z-table>"
    print "<DIV CLASS=thead><DIV CLASS=th>VLAN</DIV><DIV CLASS=th>MAC</DIV><DIV CLASS=th>Interface</DIV><DIV CLASS=th>Description</DIV></DIV>"
    print "<DIV CLASS=tbody>"
    for n in fdb:
     print "<DIV CLASS=tr><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV><DIV CLASS=td>{}</DIV>".format(n[0],n[1],n[2])
     print "<DIV CLASS=td>{}</DIV>".format(n[3]) if n[3] else "<TD style='border: 1px solid red'>No Description</DIV>"
     print "</DIV>"
    print "</DIV></DIV></DIV>"
   else:
    print "Could not connect"
  except Exception as err:
   self.log_msg("QFX widget switch table: Error [{}]".format(str(err)))
   print "<B>Error - issue loading widget: {}</B>".format(str(err))

################################ MX Object #####################################

class MX(Junos):

 @classmethod
 def get_widgets(cls):
  return Junos.get_widgets()

 def __init__(self,ahost,adomain=None):
  Junos.__init__(self, ahost,adomain,'mx')
  self._interfacenames = {}

 def __str__(self):
  return Junos.__str__(self) + " Style:" + str(self._style)
